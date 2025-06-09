import os
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN   = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")           # e.g. https://your.domain/webhook
WEBHOOK_PATH = "/webhook"
PORT        = int(os.getenv("PORT", 8443))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(bot)


# ---------------------------
#  Утилита для красивого уведомления
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
        f"🏷 <b>Курс:</b> {buy_rate:.2f} ₴\n"
        f"📦 <b>Объём:</b> от {buy_min}$\n\n"
        f"💼 <b>Продажа:</b> {sell_source}\n"
        f"🏷 <b>Курс:</b> {sell_rate:.2f} ₴\n"
        f"📦 <b>Объём:</b> до {sell_max}$\n\n"
        f"📈 <b>Потенциальная прибыль:</b> +{profit_pct:.1f}%\n"
        f"⏰ <b>Обновлено:</b> {updated_time}\n\n"
        "#арбитраж #bybit #binance #p2p"
    )
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("Открыть оффер на покупку", url=buy_url),
        types.InlineKeyboardButton("Открыть оффер на продажу", url=sell_url),
    )
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=types.ParseMode.HTML,
        reply_markup=keyboard,
    )


# ---------------------------
#  Ваши хендлеры меню, настройки, калькулятор, история, топ-сделки
# ---------------------------
@dp.callback_query_handler(lambda c: True)
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


# ---------------------------
#  Startup и Shutdown
# ---------------------------
async def on_startup(app: web.Application):
    logging.info("Setting webhook…")
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("Deleting webhook…")
    await bot.delete_webhook()


# ---------------------------
#  Собираем aiohttp-приложение
# ---------------------------
app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)

# Health check
app.router.add_route('GET',  '/',  lambda request: web.Response(text="OK"))
app.router.add_route('HEAD', '/',  lambda request: web.Response(text="OK"))

# Подключаем startup/shutdown hooks
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)


if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=PORT)
