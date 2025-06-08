import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import setup_application
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

print(f"🔐 TOKEN: {'OK' if BOT_TOKEN else 'MISSING'}")
print(f"🌐 WEBHOOK_URL: {WEBHOOK_URL}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    print(f"📩 Получено сообщение от {message.from_user.id}: {message.text}")
    await message.answer("✅ ArbitPRO работает через Webhook!")

async def on_startup(app):
    try:
        print("🚀 Старт on_startup...")
        await bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook установлен: {WEBHOOK_URL}")
    except Exception as e:
        print(f"❌ Ошибка при установке Webhook: {e}")

async def on_shutdown(app):
    print("⛔️ Отключение Webhook...")
    await bot.delete_webhook()

async def healthcheck(request):
    return web.Response(text="OK")

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

setup_application(app, dp, path="/webhook")
app.router.add_get("/", healthcheck)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌍 Запуск бота на порту {port}...")
    web.run_app(app, port=port)


