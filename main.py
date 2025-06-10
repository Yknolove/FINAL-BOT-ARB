BOT_TOKEN = os.getenv( "BOT_TOKEN" )
WEBHOOK_URL = os.getenv( "WEBHOOK_URL" )    # https://your.domain/webhook
# -*- кодировка: utf-8 -*-
"""Минимальный бот Telegram для уведомлений об арбитраже P2P."""
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

импортировать​
из импорта aiogram Bot, Dispatcher, типы
из импортного исполнителя
 aiogram.utils


BOT_TOKEN = os.getenv( "BOT_TOKEN" )
WEBHOOK_URL = os.getenv( "WEBHOOK_URL" )   # https://your.domain/webhook
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your.domain/webhook
WEBHOOK_PATH = "/webhook"
ПОРТ         = int (os.getenv( "ПОРТ" , 8443 ))
ПОРТ= int (os.getenv( "PORT" , 8443 ))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))
WEBHOOK_PATH = "/webhook"
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

# Инициализируем бота и диспетчера
бот = Бот(токен=BOT_TOKEN)
dp = Диспетчер(бот)
bot = Bot(token=BOT_TOKEN)
# Create bot even if token is missing or invalid.
_token = BOT_TOKEN if (BOT_TOKEN and ':' in BOT_TOKEN) else '0:dummy'
_token = BOT_TOKEN if BOT_TOKEN and ":" in BOT_TOKEN else "0:dummy"
bot = Bot(token=_token, validate_token=False)
dp = Dispatcher(bot)

# Клавиатура главного меню
def main_menu_keyboard () -> types.InlineKeyboardMarkup:
 
    кб = типы.InlineKeyboardMarkup(row_width= 2 )
    кб.добавить(
        types.InlineKeyboardButton( "⚙️ Настройки" , callback_data= "settings" ),

def main_menu_keyboard() -> types.InlineKeyboardMarkup:
    """Return the inline keyboard for the main menu."""
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        types.InlineKeyboardButton("📈 Калькулятор", callback_data="calculator"),
    ).добавлять(
        types.InlineKeyboardButton( "📜 История" , callback_data= "history" ),
        types.InlineKeyboardButton( "🔥 Топ-сделки" , callback_data= "top_deals" ),
    ).add(
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        types.InlineKeyboardButton("📈 Calculator", callback_data="calculator"),
    )
    kb.add(
        types.InlineKeyboardButton("📜 История", callback_data="history"),
        types.InlineKeyboardButton("🔥 Топ-сделки", callback_data="top_deals"),
        types.InlineKeyboardButton("📜 History", callback_data="history"),
        types.InlineKeyboardButton("🔥 Top deals", callback_data="top_deals"),
    )
    вернуть кб

# /запустить обработчик
@dp.message_handler( команды=[ "старт" ] )
async def cmd_start ( сообщение: типы.Сообщение ):
  
    приветственный_текст = (
        "<b>👋 Приветствуем в ArbitPRO!</b>

"
        "Я ваш помощник в мире P2P-арбитража.
    return kb

"
        "🔍 Отслеживаю лучшие предложения по покупке и продаже USDT.
"
        "⚙️ Настраивайте свои лимиты и получайте уведомления.

"
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
async def cmd_start(message: types.Message) -> None:
    """Handle the /start command."""
    welcome_text = (
        "<b>👋 Приветствуем в ArbitPRO!</b>\n"
        "Я ваш помощник в мире P2P-арбитража.\n"
        "🔍 Отслеживаю лучшие предложения по покупке и продаже USDT.\n"
        "⚙️ Настраивайте свои лимиты и получайте уведомления.\n"
        "<i>Выберите действие ниже:</i>"
    text = (
        "<b>👋 Welcome to ArbitPRO!</b>\n"
        "I am your assistant for P2P arbitrage.\n"
        "🔍 I track the best buy and sell offers for USDT.\n"
        "⚙️ Configure your limits and get notifications.\n"
        "<i>Select an action below:</i>"
    )
    ожидание сообщения.ответ(
        приветственный_текст,
    await message.answer(
        welcome_text,
        text,
        parse_mode=types.ParseMode.HTML,
        reply_markup=главное_меню_клавиатура(),
        disable_web_page_preview= Правда
        reply_markup=main_menu_keyboard(),
        disable_web_page_preview=True,
    )

# Утилита: отправка уведомления об арбитраже в стиле встраивания с кнопками URL
асинхронная деф send_arbitrage_notification (  
    chat_id: целое число ,
    источник_покупки: ул ,
    buy_rate: плавающий ,
    buy_min: целое ,
    источник_продажи: ул ,
    sell_rate: плавающий ,
    sell_max: целое число ,
    profit_pct: плавающий ,
    время_обновления: ул ,
    buy_url: ул ,
    sell_url: ул ,

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
    текст = (
        "<b>🪙 Арбитражная возможность найдена!</b>

"
) -> None:
    """Send an arbitrage notification to a chat."""
    text = (
        "<b>🪙 Арбитражная возможность найдена!</b>\n"
        f"💰 <b>Покупка:</b> {buy_source}\n"
        f"🏷️ <b>Курс:</b> {buy_rate: .2 f} ₴\n"
        f"🏷️ <b>Курс:</b> {buy_rate:.2f} ₴\n"
        f"📦 <b>Объём:</b> от {buy_min}$\n\n"
        f"💼 <b>Продажа:</b> {sell_source} \n"
        f"🏷️ <b>Курс:</b> {sell_rate: .2 f} ₴\n"
        f"💼 <b>Продажа:</b> {sell_source}\n"
        f"🏷️ <b>Курс:</b> {sell_rate:.2f} ₴\n"
        f"📦 <b>Объём:</b> до {sell_max}$\n\n"
        f"📈 <b>Потенциальная прибыль:</b> +{profit_pct:.1f}%\n"
        f"⏰ <b>Обновлено:</b> {updated_time}\n\n"
        "#арбитраж #bybit #binance #p2p"
        "<b>🪙 Arbitrage opportunity found!</b>\n"
        f"💰 <b>Buy:</b> {buy_source}\n"
        f"🏷️ <b>Rate:</b> {buy_rate:.2f} ₴\n"
        f"📦 <b>Volume:</b> from {buy_min}$\n\n"
        f"💼 <b>Sell:</b> {sell_source}\n"
        f"🏷️ <b>Rate:</b> {sell_rate:.2f} ₴\n"
        f"📦 <b>Volume:</b> up to {sell_max}$\n\n"
        f"📈 <b>Potential profit:</b> +{profit_pct:.1f}%\n"
        f"⏰ <b>Updated:</b> {updated_time}\n\n"
        "#arbitrage #p2p"
    )

    клавиатура = типы.InlineKeyboardMarkup(row_width= 2 )
    клавиатура.добавить(
        types.InlineKeyboardButton("🔗 Оферт на покупку", url=buy_url),
        types.InlineKeyboardButton( "🔗 Предложение о продаже" , url=sell_url),
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🔗 Оферта на покупку", url=buy_url),
        types.InlineKeyboardButton("🔗 Предложение о продаже", url=sell_url),
        types.InlineKeyboardButton("🔗 Buy offer", url=buy_url),
        types.InlineKeyboardButton("🔗 Sell offer", url=sell_url),
    )

    ожидание bot.send_message(
    await bot.send_message(
        chat_id=chat_id,
        текст=текст,
        text=text,
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview= Правда ,
        reply_markup=клавиатура,
        disable_web_page_preview=True,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


если __name__ == "__main__" :
    executor.start_polling(dp, skip_updates= True )
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
