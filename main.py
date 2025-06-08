import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import setup_application
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Логика ответа на сообщения
@dp.message()
async def handle_message(message: types.Message):
    print(f"💬 Сообщение от: {message.from_user.id} — {message.text}")
    await message.answer("✅ ArbitPRO работает через Webhook!")

# Обработка старта и выключения
async def on_startup(app):
    print("🚀 Запуск и установка Webhook...")
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    print("⛔️ Отключение Webhook...")
    await bot.delete_webhook()

# Инициализация веб-приложения
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# Подключаем aiogram к серверу AIOHTTP
setup_application(app, dp, path="/webhook")

# Дополнительный маршрут для проверки
async def healthcheck(request):
    return web.Response(text="OK")

app.router.add_get("/", healthcheck)

# Запуск приложения
if __name__ == "__main__":
    web.run_app(app, port=int(os.environ.get("PORT", 5000)))
