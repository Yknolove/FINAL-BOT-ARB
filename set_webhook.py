import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN)

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook установлен:", WEBHOOK_URL)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
