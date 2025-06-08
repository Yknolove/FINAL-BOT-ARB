import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8009525449:AAEX6AHzI-mwVBDBJTxml9GVti2lG0YOa7Y")
WEBHOOK_URL = os.getenv("https://final-bot-arb.onrender.com/webhook")

bot = Bot(token=BOT_TOKEN)

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook установлен:", WEBHOOK_URL)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
