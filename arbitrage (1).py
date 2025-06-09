import os
import asyncio
from aiogram import Bot

async def analyze_and_notify(bot: Bot):
    pair = "BTC/USDT"  # пример
    price_a = 0  # TODO: вставьте логику получения цен
    price_b = 0
    chat_id = os.getenv("ADMIN_CHAT_ID")
    message = (
        f"*Арбитражная возможность найдена!*\n"
        f"Пара: {pair}\n"
        f"Биржа A: {price_a}\n"
        f"Биржа B: {price_b}\n"
    )
    await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

async def schedule_arbitrage_checks(bot: Bot):
    while True:
        try:
            await analyze_and_notify(bot)
        except Exception as e:
            print("Scheduler error:", e)
        await asyncio.sleep(60)
