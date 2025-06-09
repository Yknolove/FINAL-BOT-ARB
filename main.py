import os
import logging
import asyncio
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from handlers import dp, register_handlers, bot
from arbitrage import schedule_arbitrage_checks

API_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', 'https://final-bot-arb.onrender.com')
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', '10000'))

logging.basicConfig(level=logging.INFO)

async def on_startup(dispatcher: Dispatcher):
    register_handlers(dispatcher)
    logging.info("Setting webhook: %s", WEBHOOK_URL)
    await bot.set_webhook(WEBHOOK_URL)
    # Start arbitrage checks
    dispatcher.loop.create_task(schedule_arbitrage_checks(bot))

async def on_shutdown(dispatcher: Dispatcher):
    logging.info("Deleting webhook")
    await bot.delete_webhook()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
