import os
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app

# — Логирование
logging.basicConfig(level=logging.INFO)

# — Переменные окружения
BOT_TOKEN    = os.getenv("BOT_TOKEN")
WEBHOOK_URL  = os.getenv("WEBHOOK_URL")   # e.g. https://your.domain/webhook
WEBHOOK_PATH = "/webhook"
PORT         = int(os.getenv("PORT", 8443))

# — Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(bot)


# ---------------------------
# Debug: логируем все callback_query
# ---------------------------
@dp.callback_query_handler()
async def debug_all_callbacks(callback: types.CallbackQuery):
    logging.info(f"Received callback_query: {callback.data}")
    # Отвечаем, чтобы убрать спиннер
    await callback.answer("Callback received")


# ---------------------------
# Утилита: отправка embed-сообщения об арбитраже
# ---------------------------
async def send_arbitrage_notification(
    chat_id: int,
    buy_source: str,
    buy_rate: float,
    buy_min: int,
    sell_source: str,
    sell_rate: float,
    sell_max: int,
    profit_pct: float,
    updated_time: str,
    buy_url: str,
    sell_url: str,
):
    text = (
        "<b>🪙 Арбитражная возможность найдена!</b>\n\n"
        f"💰 <b>Покупка:</b> {buy_source}\n"
        f"🏷️ <b>Курс:</b> {buy_rate:.2f} ₴\n"
        f"📦 <b>Объём:</b> от {buy_min}$\n\n"
        f"💼 <b>Продажа:</b> {sell_source}\n"
        f"🏷️ <b>Курс:</b> {sell_rate:.2f} ₴\n"
        f"📦 <b>Объём:</b> до {sell_max}$\n\n"
        f"📈 <b>Потенциальная прибыль:</b> +{profit_pct:.1f}%\n"
        f"⏰ <b>Обновлено:</b> {updated_time}\n\n"
        "#арбитраж #bybit #binance #p2p"
    )

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        types.InlineKeyboardButton("📈 Калькулятор", callback_data="calculator"),
    ).add(
        types.InlineKeyboardButton("📜 История", callback_data="history"),
        types.InlineKeyboardButton("🔥 Топ-сделки", callback_data="top_deals"),
    )

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


# ---------------------------
# Health-check для Render (GET/HEAD / → 200 OK)
# ---------------------------
async def handle_root(request: web.Request) -> web.Response:
    return web.Response(text="OK")


# ---------------------------
# Startup и Shutdown
# ---------------------------
async def on_startup(app: web.Application):
    logging.info("Setting webhook…")
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("Deleting webhook…")
    await bot.delete_webhook()
    logging.info("Closing bot HTTP session…")
    session = await bot.get_session()
    await session.close()


# ---------------------------
# Сборка и запуск aiohttp-приложения
# ---------------------------
if __name__ == "__main__":
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)

    app.router.add_route("GET",  "/", handle_root)
    app.router.add_route("HEAD", "/", handle_root)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=PORT)

