import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import setup_application
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    await message.answer("✅ ArbitPRO работает через Webhook!")

async def on_startup(app):
    print("🚀 Старт on_startup...")
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Вебхук установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    print("⛔️ Отключение Webhook...")
    await bot.delete_webhook()

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# ❗️Это ключевая строка: подключение Webhook
setup_application(app, dp, path="/webhook")

# Healthcheck (по корню)
async def healthcheck(request):
    return web.Response(text="OK")

app.router.add_get("/", healthcheck)

if __name__ == "__main__":
    web.run_app(app, port=int(os.environ.get("PORT", 10000)))

