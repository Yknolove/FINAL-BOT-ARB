import os
import asyncio
import logging
import aiohttp
from aiogram import types
from db import get_conn

# Only Binance P2P endpoint configured for reliable JSON response
BINANCE_P2P_URL = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'

# thresholds and interval
MIN_SPREAD = float(os.getenv('MIN_SPREAD', '0.5'))       # % minimum for notification
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds

async def fetch_binance_p2p(session):
    payload = {
        "asset": "USDT",
        "fiat": "UAH",
        "tradeType": "BUY",
        "page": 1,
        "rows": 1
    }
    try:
        async with session.post(BINANCE_P2P_URL, json=payload) as resp:
            if resp.status != 200:
                logging.error(f"Binance P2P HTTP {resp.status}")
                return 0.0
            data = await resp.json()
            advs = data.get('data', [])
            if advs:
                price = advs[0].get('adv', {}).get('price')
                return float(price or 0)
    except Exception as e:
        logging.error(f"Error fetching Binance P2P price: {e}")
    return 0.0

async def analyze_and_notify(bot):
    async with aiohttp.ClientSession() as session:
        binance_price = await fetch_binance_p2p(session)
        if binance_price > 0:
            msg = f"Binance P2P USDT/UAH price: {binance_price:.2f} UAH"
            logging.info(msg)
            # prepare small menu button
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(types.InlineKeyboardButton("💡 Меню", callback_data="menu"))
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM settings")
            rows = cur.fetchall()
            conn.close()
            for row in rows:
                try:
                    await bot.send_message(row['user_id'], msg, reply_markup=kb)
                except Exception as e:
                    logging.error(f"Failed to send update to {row['user_id']}: {e}")

async def schedule_arbitrage_checks(bot):
    while True:
        try:
            await analyze_and_notify(bot)
        except Exception as e:
            logging.error(f"Arbitrage scheduler error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
