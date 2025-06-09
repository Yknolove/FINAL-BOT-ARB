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

# Initialize bot and dispatcher with Markdown parse mode
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)

# Persistent main menu keyboard (reply keyboard)
def persistent_menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        types.KeyboardButton("⚙️ Настройки"), types.KeyboardButton("📈 Калькулятор")
    )
    kb.add(
        types.KeyboardButton("📜 История"), types.KeyboardButton("🔥 Топ-сделки")
    )
    return kb

# Inline keyboard for arbitrage offer links
def offers_inline_keyboard(buy_url: str, sell_url: str):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Открыть оффер на покупку", url=buy_url),
        types.InlineKeyboardButton("Открыть оффер на продажу", url=sell_url),
    )
    return kb

# Function to send arbitrage notification
async def send_arbitrage_notification(chat_id: int, buy_exchange: str, buy_price: float, buy_volume: float, buy_url: str,
                                      sell_exchange: str, sell_price: float, sell_volume: float, sell_url: str,
                                      profit: float, updated_at: str):
    text = (
        "🚀 *Арбитражная возможность найдена!*\n\n"
        f"🛒 *Покупка*: {buy_exchange}\n"
        f"💱 *Курс*: {buy_price} ₴\n"
        f"📦 *Объём*: от {buy_volume}$\n\n"
        f"💰 *Продажа*: {sell_exchange}\n"
        f"💱 *Курс*: {sell_price} ₴\n"
        f"📦 *Объём*: до {sell_volume}$\n\n"
        f"📊 *Потенциальная прибыль*: +{profit}%\n"
        f"🕒 *Обновлено*: {updated_at}"
    )
    await bot.send_message(
        chat_id,
        text,
        reply_markup=offers_inline_keyboard(buy_url, sell_url),
    )

# Handlers
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Я ArbitPRO-бот. Выберите действие:",
        reply_markup=persistent_menu_keyboard()
    )

@dp.message_handler(commands=["ping"])
async def cmd_ping(message: types.Message):
    await message.reply("pong", reply_markup=persistent_menu_keyboard())

# Demo notification command
@dp.message_handler(commands=["notify"])
async def cmd_notify(message: types.Message):
    # Demo data for the notification
    await send_arbitrage_notification(
        chat_id=message.chat.id,
        buy_exchange="Binance P2P",
        buy_price=41.30,
        buy_volume=250,
        buy_url="https://p2p.binance.com/ru/offer/example_buy",
        sell_exchange="ByBit P2P",
        sell_price=42.05,
        sell_volume=500,
        sell_url="https://p2p.bybit.com/ru/offer/example_sell",
        profit=3.6,
        updated_at="16:25"
    )
    # Restore persistent menu keyboard
    await message.reply("💡 Меню", reply_markup=persistent_menu_keyboard())

# Handlers for persistent menu text buttons
@dp.message_handler(lambda message: message.text in ["⚙️ Настройки", "📈 Калькулятор", "📜 История", "🔥 Топ-сделки"])
async def menu_text_handler(message: types.Message):
    if message.text == "⚙️ Настройки":
        text = "Здесь будут настройки пользователя."
    elif message.text == "📈 Калькулятор":
        text = "Здесь калькулятор прибыли."
    elif message.text == "📜 История":
        text = "Здесь история сделок."
    else:
        text = "Архив топ-сделок дня."
    await message.reply(text, reply_markup=persistent_menu_keyboard())

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
