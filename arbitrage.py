import os
import asyncio
import logging
import aiohttp
from aiogram import Bot
from db import get_conn

BINANCE_P2P_URL = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

async def fetch_binance_p2p(session):
    payload = {"asset":"USDT","fiat":"UAH","tradeType":"BUY","page":1,"rows":1}
    try:
        async with session.post(BINANCE_P2P_URL, json=payload) as resp:
            if resp.status != 200:
                logging.error(f"Binance HTTP {resp.status}")
                return '', 0.0
            data = await resp.json()
            advs = data.get('data', [])
            if advs:
                adv = advs[0].get('adv', {})
                price = float(adv.get('price', 0))
                link = adv.get('advUrl', '')
                return link, price
    except Exception as e:
        logging.error(f"Fetch error: {e}")
    return '', 0.0

async def analyze_and_notify(bot: Bot):
    async with aiohttp.ClientSession() as session:
        link, price = await fetch_binance_p2p(session)
        if price > 0:
            msg = f"Лимит ордера Binance P2P USDT/UAH: {price:.2f} UAH"
            if link:
                msg += f"\nПерейти к ордеру: {link}"
            conn = get_conn(); cur = conn.cursor()
            cur.execute("SELECT user_id FROM settings")
            rows = cur.fetchall(); conn.close()
            for r in rows:
                try: await bot.send_message(r['user_id'], msg)
                except Exception as e: logging.error(e)

async def schedule_arbitrage_checks(bot: Bot):
    while True:
        await analyze_and_notify(bot)
        await asyncio.sleep(CHECK_INTERVAL)
