import os
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN    = os.getenv("BOT_TOKEN")
WEBHOOK_URL  = os.getenv("WEBHOOK_URL")   # https://your.domain/webhook
WEBHOOK_PATH = "/webhook"
PORT         = int(os.getenv("PORT", 8443))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(bot)

# Main menu keyboard
def main_menu_keyboard() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        types.InlineKeyboardButton("📈 Калькулятор", callback_data="calculator"),
    ).add(
        types.InlineKeyboardButton("📜 История", callback_data="history"),
        types.InlineKeyboardButton("🔥 Топ-сделки", callback_data="top_deals"),
    )
    return kb

# /start handler
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    welcome_text = (
        "<b>👋 Приветствуем в ArbitPRO!</b>\n"
        "Я ваш помощник в мире P2P-арбитража.\n"
        "🔍 Отслеживаю лучшие предложения по покупке и продаже USDT.\n"
        "⚙️ Настраивайте свои лимиты и получайте уведомления.\n"
        "<i>Выберите действие ниже:</i>"
    )
    await message.answer(
        welcome_text,
        parse_mode=types.ParseMode.HTML,
        reply_markup=main_menu_keyboard(),
        disable_web_page_preview=True
    )

# Utility: send embed-style arbitrage notification with URL buttons
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
        "<b>🪙 Арбитражная возможность найдена!</b>\n"
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
        types.InlineKeyboardButton("🔗 Оферт на покупку", url=buy_url),
        types.InlineKeyboardButton("🔗 Оффер на продажу", url=sell_url),
    )

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )

# Callback-query handlers for menu buttons
@dp.callback_query_handler(lambda c: c.data in ["settings", "calculator", "history", "top_deals"])
async def process_menu(callback: types.CallbackQuery):
    mapping = {
        "settings":   "🔧 Здесь вы можете настроить желаемые курсы и объёмы.",
        "calculator": "🧮 Введите сумму, и я посчитаю потенциальный профит.",
        "history":    "📚 История ваших совершённых сделок появится здесь.",
        "top_deals":  "🔥 Топ P2P-сделки за сегодня."
    }
    text = mapping.get(callback.data, "Выбранный раздел в разработке.")
    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode=types.ParseMode.HTML
    )
    await callback.answer()

# Health-check for Render
async def handle_root(request: web.Request) -> web.Response:
    return web.Response(text="OK")

# Startup and shutdown events
async def on_startup(app: web.Application):
    logging.info("Setting webhook…")
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("Deleting webhook…")
    await bot.delete_webhook()
    session = await bot.get_session()
    await session.close()
    logging.info("HTTP session closed")

if __name__ == "__main__":
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
    app.router.add_route("GET",  "/", handle_root)
    app.router.add_route("HEAD", "/", handle_root)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=PORT)
