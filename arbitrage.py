import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, types
from db import get_conn
from datetime import datetime

BINANCE_P2P_URL = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

async def fetch_binance_p2p(session, trade_type):
    payload = {
        "asset": "USDT",
        "fiat": "UAH",
        "tradeType": trade_type,
        "page": 1,
        "rows": 1
    }
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
        buy_link, buy_price = await fetch_binance_p2p(session, "BUY")
        sell_link, sell_price = await fetch_binance_p2p(session, "SELL")
        if buy_price > 0 and sell_price > 0:
            spread = (sell_price - buy_price) / buy_price * 100
            now = datetime.now().strftime("%H:%M:%S")
            msg = (
                f"*Арбитражная возможность найдена!*\n\n"
                f"🛒 *Покупка*: Binance P2P\n"
                f"💵 *Курс*: {buy_price:.2f} UAH\n\n"
                f"💰 *Продажа*: Binance P2P\n"
                f"💵 *Курс*: {sell_price:.2f} UAH\n\n"
                f"📊 *Потенциальная прибыль*: +{spread:.2f}%\n"
                f"⏰ *Обновлено*: {now}"
            )
            keyboard = types.InlineKeyboardMarkup()
            if buy_link:
                keyboard.add(types.InlineKeyboardButton("Открыть оффер на покупку", url=buy_link))
            if sell_link:
                keyboard.add(types.InlineKeyboardButton("Открыть оффер на продажу", url=sell_link))
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM settings")
            rows = cur.fetchall()
            conn.close()
            for row in rows:
                try:
                    await bot.send_message(
                        row['user_id'],
                        msg,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                except Exception as ex:
                    logging.error(f"Failed to send update to {row['user_id']}: {ex}")

async def schedule_arbitrage_checks(bot: Bot):
    while True:
        try:
            await analyze_and_notify(bot)
        except Exception as exc:
            logging.error(f"Scheduler error: {exc}")
        await asyncio.sleep(CHECK_INTERVAL)
