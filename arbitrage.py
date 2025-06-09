import os
import asyncio
import logging
import aiohttp
from aiogram import Bot
from db import get_conn

# Binance P2P endpoint for USDT/UAH
BINANCE_P2P_URL = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'

# Configuration via environment
MIN_SPREAD = float(os.getenv('MIN_SPREAD', '0.5'))       # % minimum spread (unused currently)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds between checks

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
                return '', 0.0
            data = await resp.json()
            advs = data.get('data', [])
            if advs:
                adv = advs[0].get('adv', {})
                price = float(adv.get('price', 0))
                link = adv.get('advUrl', '') or adv.get('advertiserOpinionUrl', '')
                return link, price
    except Exception as e:
        logging.error(f"Error fetching Binance P2P price: {e}")
    return '', 0.0

async def analyze_and_notify(bot: Bot):
    async with aiohttp.ClientSession() as session:
        link, price = await fetch_binance_p2p(session)
        if price > 0:
            # build message
            msg = f"Binance P2P USDT/UAH price: {price:.2f} UAH"
            if link:
                msg += "\nПерейти к ордеру: " + link
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
                    logging.error(f"Failed to send update to {row['user_id']}: {e}")

async def schedule_arbitrage_checks(bot: Bot):
    while True:
        try:
            await analyze_and_notify(bot)
        except Exception as e:
            logging.error(f"Arbitrage scheduler error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
