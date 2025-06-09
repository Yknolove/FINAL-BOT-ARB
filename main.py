import os
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app

# — Конфиг логирования
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
        types.InlineKeyboardButton("🔗 Открыть оффер на покупку", url=buy_url),
        types.InlineKeyboardButton("🔗 Открыть оффер на продажу", url=sell_url),
    )

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


# ---------------------------
# Ваши хэндлеры /start, меню, калькулятор, история, топ-сделки
# ---------------------------
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
async def process_menu(callback: types.CallbackQuery):
    mapping = {
        "settings":   "Здесь будут настройки пользователя.",
        "calculator": "Здесь калькулятор прибыли.",
        "history":    "Здесь история сделок.",
        "top_deals":  "Архив топ-сделок дня."
    }
    await callback.message.edit_text(mapping[callback.data], reply_markup=main_menu_keyboard())
    await callback.answer()


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
# Собираем и запускаем aiohttp-приложение
# ---------------------------
if __name__ == "__main__":
    # Конфигурируем приложение с маршрутом /webhook
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)

    # Добавляем health-check
    app.router.add_route("GET",  "/", handle_root)
    app.router.add_route("HEAD", "/", handle_root)

    # Регистрируем хуки
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Запускаем сервер
    web.run_app(app, host="0.0.0.0", port=PORT)
