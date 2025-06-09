import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.utils.executor import start_webhook
from arbitrage import schedule_arbitrage_checks
import handlers

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment
BOT_TOKEN    = os.getenv("BOT_TOKEN")
WEBHOOK_URL  = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
PORT         = int(os.environ.get("PORT", 8443))

# Initialize bot and dispatcher
bot  = Bot(token=BOT_TOKEN)
dp   = Dispatcher(bot)

# Register handlers
handlers.register_handlers(dp)

# Startup/shutdown
async def on_startup(_):
    logging.info("Setting webhook...")
    await bot.set_webhook(WEBHOOK_URL)
    # start periodic arbitrage checks
    asyncio.create_task(schedule_arbitrage_checks(bot))

async def on_shutdown(_):
    logging.info("Deleting webhook...")
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher   = dp,
        webhook_path = WEBHOOK_PATH,
        on_startup   = on_startup,
        on_shutdown  = on_shutdown,
        host         = "0.0.0.0",
        port         = PORT,
    )



