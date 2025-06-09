import os
import asyncio
import aiohttp
import logging
from db import get_conn
from datetime import datetime

# Exchange endpoints (REST)
ENDPOINTS = {
    'binance': 'https://api.binance.com/api/v3/ticker/price?symbol=USDTUSDT',  # placeholder
    'bybit':   'https://api.bybit.com/v2/public/tickers?symbol=USDTUSDT',     # placeholder
    'bitget':  'https://api.bitget.com/api/spot/v1/market/ticker?symbol=USDT_USDT' # placeholder
}
# thresholds
MIN_SPREAD = float(os.getenv('MIN_SPREAD', '0.5'))   # % minimum for notification
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds

async def fetch_price(session, url):
    try:
        async with session.get(url) as resp:
            data = await resp.json()
            # extract price depending on exchange format
            # TODO: adjust for real API responses
            price = float(
                data.get('price')
                or data.get('ticker', {}).get('last_price')
                or 0
            )
            return price
    except Exception as e:
        logging.error(f"Error fetching price from {url}: {e}")
        return 0.0

async def analyze_and_notify(bot):
    async with aiohttp.ClientSession() as session:
        # collect prices
        tasks = [fetch_price(session, url) for url in ENDPOINTS.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        prices = []
        # Filter out exceptions and ensure float
        for res in results:
            if isinstance(res, Exception):
                prices.append(0.0)
            else:
                prices.append(res)

        # simple pairwise check
        for ex1, price1 in zip(ENDPOINTS.keys(), prices):
            if price1 <= 0:
                continue
            for ex2, price2 in zip(ENDPOINTS.keys(), prices):
                if ex1 == ex2 or price2 <= 0:
                    continue
                try:
                    spread = (price2 - price1) / price1 * 100
                except ZeroDivisionError:
                    continue
                if spread >= MIN_SPREAD:
                    text = (
                        f"Арбитраж: купить на {ex1} по {price1:.4f}, "
                        f"продать на {ex2} по {price2:.4f}, спред {spread:.2f}%"
                    )
                    logging.info(text)
                    # notify all users who set rates
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("SELECT user_id FROM settings")
                    rows = cur.fetchall()
                    conn.close()
                    for row in rows:
                        try:
                            await bot.send_message(row['user_id'], text)
                        except Exception as e:
                            logging.error(f"Failed to send message to {row['user_id']}: {e}")

async def schedule_arbitrage_checks(bot):
    while True:
        try:
            await analyze_and_notify(bot)
        except Exception as e:
            logging.error(f"Arbitrage check error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
