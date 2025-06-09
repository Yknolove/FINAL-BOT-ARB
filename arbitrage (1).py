import os
import asyncio
import aiohttp
import logging
from db import get_conn

# Exchange P2P REST endpoints returning JSON
ENDPOINTS = {
    'binance': 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search?asset=USDT&fiat=UAH&tradeType=BUY',
    'bybit':   'https://api.bybit.com/v5/spot/quote/ticker?symbol=USDTUSDT',  # placeholder, adjust if needed
    'bitget':  'https://api.bitget.com/api/spot/v1/market/depth?symbol=USDT_USDT'  # placeholder, adjust if needed
}

# thresholds and intervals
MIN_SPREAD = float(os.getenv('MIN_SPREAD', '0.5'))       # % minimum for notification
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds

async def fetch_price(session, url):
    try:
        async with session.get(url) as resp:
            # Try forcing JSON, regardless of content-type
            try:
                data = await resp.json(content_type=None)
            except Exception as e:
                logging.error(f"JSON parse error from {url}: {e}")
                return 0.0
            # Extract price for each exchange
            if 'binance.com' in url:
                advs = data.get('data', [])
                if advs:
                    return float(advs[0]['adv']['price'])
            elif 'bybit.com' in url:
                tick = data.get('result', {}).get('list', [{}])[0]
                return float(tick.get('lastPrice', 0))
            elif 'bitget.com' in url:
                bids = data.get('data', {}).get('bids', [])
                if bids:
                    return float(bids[0][0])
    except Exception as e:
        logging.error(f"Error fetching price from {url}: {e}")
    return 0.0

async def analyze_and_notify(bot):
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(fetch_price(session, url) for url in ENDPOINTS.values()))
        prices = dict(zip(ENDPOINTS.keys(), results))

        # Compare each pair for arbitrage
        for ex1, price1 in prices.items():
            if price1 <= 0:
                continue
            for ex2, price2 in prices.items():
                if ex1 == ex2 or price2 <= 0:
                    continue
                spread = (price2 - price1) / price1 * 100
                if spread >= MIN_SPREAD:
                    msg = (
                        f"Арбитраж: купить на {ex1} по {price1:.2f} UAH, "
                        f"продать на {ex2} по {price2:.2f} UAH, "
                        f"спред {spread:.2f}%"
                    )
                    logging.info(msg)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("SELECT user_id FROM settings")
                    for row in cur.fetchall():
                        try:
                            await bot.send_message(row['user_id'], msg)
                        except Exception as e:
                            logging.error(f"Failed to send alert to {row['user_id']}: {e}")
                    conn.close()

async def schedule_arbitrage_checks(bot):
    while True:
        try:
            await analyze_and_notify(bot)
        except Exception as e:
            logging.error(f"Arbitrage check error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
