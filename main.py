import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")  # from .env
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://final-bot-arb.onrender.com/webhook/<token>
PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Handlers
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply("Привет! Я ArbitPRO-бот. Готов к работе.")

@dp.message_handler(commands=["ping"])
async def cmd_ping(message: types.Message):
    await message.reply("pong")

# Startup and shutdown
async def on_startup(_dp):
    logging.info("Setting webhook...")
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(_dp):
    logging.info("Deleting webhook...")
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host="0.0.0.0",
        port=PORT,
    )



