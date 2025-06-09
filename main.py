import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN    = os.getenv("BOT_TOKEN")
WEBHOOK_URL  = os.getenv("WEBHOOK_URL")  # If empty, polling will be used
WEBHOOK_PATH = "/webhook"
PORT         = int(os.environ.get("PORT", 8443))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)

# Main menu keyboard (reply keyboard)
def main_menu_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        types.InlineKeyboardButton("📈 Калькулятор", callback_data="calculator"),
    )
    kb.add(
        types.InlineKeyboardButton("📜 История", callback_data="history"),
        types.InlineKeyboardButton("🔥 Топ-сделки", callback_data="top_deals"),
    )
    return kb

# Health check handler
async def handle_root(request):
    return web.Response(text="OK")

# Handlers
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Я ArbitPRO-бот. Выберите действие:",
        reply_markup=main_menu_keyboard()
    )

@dp.message_handler(commands=["ping"])
async def cmd_ping(message: types.Message):
    await message.reply("pong")

@dp.callback_query_handler(lambda c: c.data in ["settings", "calculator", "history", "top_deals"])
async def process_menu_callback(callback: types.CallbackQuery):
    data = callback.data
    if data == "settings":
        await callback.message.edit_text("Здесь будут настройки пользователя.")
    elif data == "calculator":
        await callback.message.edit_text("Здесь калькулятор прибыли.")
    elif data == "history":
        await callback.message.edit_text("Здесь история сделок.")
    elif data == "top_deals":
        await callback.message.edit_text("Архив топ-сделок дня.")
    await callback.answer()

# Startup and shutdown
async def on_startup(app):
    # Add health check route for Render
    app.router.add_get("/", handle_root)
    logging.info("Setting webhook…")
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(app):
    logging.info("Deleting webhook…")
    if WEBHOOK_URL:
        await bot.delete_webhook()

if __name__ == "__main__":
    if WEBHOOK_URL:
        # Webhook mode
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host="0.0.0.0",
            port=PORT,
        )
    else:
        # Polling fallback
        logging.info("Starting in polling mode")
        from aiogram.utils.executor import start_polling
        start_polling(dp, skip_updates=True)
