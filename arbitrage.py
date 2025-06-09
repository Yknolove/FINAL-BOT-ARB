import os
import asyncio
import aiohttp
import logging
from db import get_conn

# P2P/Spot endpoints returning JSON
ENDPOINTS = {
    'binance': 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search?asset=USDT&fiat=UAH&tradeType=BUY',
    'bybit':   'https://api.bybit.com/v5/spot/quote/ticker?symbol=USDTUSDT',
    'bitget':  'https://api.bitget.com/api/spot/v1/market/depth?symbol=USDT_USDT'
}

# thresholds and interval
MIN_SPREAD = float(os.getenv('MIN_SPREAD', '0.5'))       # % minimum for notification
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds

async def fetch_price(session, url):
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                logging.error(f"HTTP {resp.status} from {url}")
                return 0.0
            try:
                data = await resp.json(content_type=None)
            except Exception as e:
                logging.error(f"JSON parse error from {url}: {e}")
                return 0.0

            if 'binance.com' in url:
                advs = data.get('data') or []
                if isinstance(advs, list) and advs:
                    price = advs[0].get('adv', {}).get('price')
                    return float(price or 0)

            elif 'bybit.com' in url:
                result = data.get('result', {})
                lst = result.get('list') or []
                if isinstance(lst, list) and lst:
                    first = lst[0]
                    price = first.get('lastPrice') or first.get('last_price')
                    return float(price or 0)

            elif 'bitget.com' in url:
                bit_data = data.get('data') or {}
                bids = bit_data.get('bids') or []
                if isinstance(bids, list) and bids:
                    top = bids[0]
                    if isinstance(top, list) and top:
                        return float(top[0])
                    if isinstance(top, dict):
                        return float(top.get('price', 0))
    except Exception as e:
        logging.error(f"Error fetching price from {url}: {e}")
    return 0.0

async def analyze_and_notify(bot):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, url) for url in ENDPOINTS.values()]
        results = await asyncio.gather(*tasks)
        prices = dict(zip(ENDPOINTS.keys(), results))

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
                    rows = cur.fetchall()
                    conn.close()
                    for row in rows:
                        try:
                            await bot.send_message(row['user_id'], msg)
                        except Exception as e:
                            logging.error(f"Failed to send alert to {row['user_id']}: {e}")

async def schedule_arbitrage_checks(bot):
    while True:
        try:
            await analyze_and_notify(bot)
        except Exception as e:
            logging.error(f"Arbitrage check error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
