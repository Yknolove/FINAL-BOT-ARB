import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN    = os.getenv("BOT_TOKEN")
WEBHOOK_URL  = os.getenv("WEBHOOK_URL")  # https://…/webhook
WEBHOOK_PATH = "/webhook"
PORT         = int(os.environ.get("PORT", 8443))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


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
    """
    Отправляет в чат форматированное сообщение об арбитражной возможности:
    текст с HTML-разметкой, эмодзи и две inline-кнопки.
    """
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
        reply_markup=keyboard
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
#  Логика сканирования арбитража
# ---------------------------
# Вместо простого send_message теперь используйте:
#
# await send_arbitrage_notification(
#     chat_id=chat_id,
#     buy_source=buy_source,
#     buy_rate=buy_rate,
#     buy_min=buy_min,
#     sell_source=sell_source,
#     sell_rate=sell_rate,
#     sell_max=sell_max,
#     profit_pct=profit_pct,
#     updated_time=updated_time,
#     buy_url=buy_offer_url,
#     sell_url=sell_offer_url,
# )
#
# Пример:
# async def check_and_notify():
#     # ... ваш код получения данных ...
#     await send_arbitrage_notification(
#         chat_id=123456789,
#         buy_source="Binance P2P",
#         buy_rate=41.30,
#         buy_min=250,
#         sell_source="ByBit P2P",
#         sell_rate=42.05,
#         sell_max=500,
#         profit_pct=3.6,
#         updated_time="16:25",
#         buy_url="https://p2p.binance.com/offer/…",
#         sell_url="https://p2p.bybit.com/offer/…",
#     )


# Startup and shutdown
async def on_startup(_):
    logging.info("Setting webhook…")
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(_):
    logging.info("Deleting webhook…")
    await bot.delete_webhook()


if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host="0.0.0.0",
        port=PORT,
    )
