import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import setup_application
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

print(f"🔐 ТОКЕН: {'ОК' if BOT_TOKEN else '❌ МISSING'}")
print(f"🌐 WEBHOOK_URL: {WEBHOOK_URL}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    await message.answer("✅ ArbitPRO работает через Webhook!")


async def on_startup(app):
    print("🚀 Старт on_startup...")
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Вебхук установлен: {WEBHOOK_URL}")


# УДАЛЕНО отключение webhook при остановке, чтобы не было сброса:
# async def on_shutdown(app):
#     await bot.delete_webhook()

app = web.Application()
app.on_startup.append(on_startup)
# app.on_shutdown.append(on_shutdown)

setup_application(app, dp, path="/webhook")

async def healthcheck(request):
    return web.Response(text="OK")

app.router.add_get("/", healthcheck)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌍 Запуск бота на порт {port}...")
    web.run_app(app, port=port)
