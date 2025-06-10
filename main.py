BOT_TOKEN = os.getenv( "BOT_TOKEN" )
WEBHOOK_URL = os.getenv( "WEBHOOK_URL" )    # https://your.domain/webhook
"""Минимальный бот Telegram для уведомлений об арбитраже P2P."""

импортировать​
из импорта aiogram Bot, Dispatcher, типы
из импортного исполнителя
 aiogram.utils


BOT_TOKEN = os.getenv( "BOT_TOKEN" )
WEBHOOK_URL = os.getenv( "WEBHOOK_URL" )   # https://your.domain/webhook
WEBHOOK_PATH = "/webhook"
ПОРТ         = int (os.getenv( "ПОРТ" , 8443 ))
ПОРТ= int (os.getenv( "PORT" , 8443 ))

# Инициализируем бота и диспетчера
бот = Бот(токен=BOT_TOKEN)
dp = Диспетчер(бот)

# Клавиатура главного меню
def main_menu_keyboard () -> types.InlineKeyboardMarkup:
 
    кб = типы.InlineKeyboardMarkup(row_width= 2 )
    кб.добавить(
        types.InlineKeyboardButton( "⚙️ Настройки" , callback_data= "settings" ),
        types.InlineKeyboardButton("📈 Калькулятор", callback_data="calculator"),
    ).добавлять(
        types.InlineKeyboardButton( "📜 История" , callback_data= "history" ),
        types.InlineKeyboardButton( "🔥 Топ-сделки" , callback_data= "top_deals" ),
    )
    вернуть кб

# /запустить обработчик
@dp.message_handler( команды=[ "старт" ] )
async def cmd_start ( сообщение: типы.Сообщение ):
  
    приветственный_текст = (
        "<b>👋 Приветствуем в ArbitPRO!</b>

"
        "Я ваш помощник в мире P2P-арбитража.

"
        "🔍 Отслеживаю лучшие предложения по покупке и продаже USDT.
"
        "⚙️ Настраивайте свои лимиты и получайте уведомления.

"
        "<b>👋 Приветствуем в ArbitPRO!</b>\n"
        "Я ваш помощник в мире P2P-арбитража.\n"
        "🔍 Отслеживаю лучшие предложения по покупке и продаже USDT.\n"
        "⚙️ Настраивайте свои лимиты и получайте уведомления.\n"
        "<i>Выберите действие ниже:</i>"
    )
    ожидание сообщения.ответ(
        приветственный_текст,
        parse_mode=types.ParseMode.HTML,
        reply_markup=главное_меню_клавиатура(),
        disable_web_page_preview= Правда
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
):
    текст = (
        "<b>🪙 Арбитражная возможность найдена!</b>

"
        "<b>🪙 Арбитражная возможность найдена!</b>\n"
        f"💰 <b>Покупка:</b> {buy_source}\n"
        f"🏷️ <b>Курс:</b> {buy_rate: .2 f} ₴\n"
        f"📦 <b>Объём:</b> от {buy_min}$\n\n"
        f"💼 <b>Продажа:</b> {sell_source} \n"
        f"🏷️ <b>Курс:</b> {sell_rate: .2 f} ₴\n"
        f"📦 <b>Объём:</b> до {sell_max}$\n\n"
        f"📈 <b>Потенциальная прибыль:</b> +{profit_pct:.1f}%\n"
        f"⏰ <b>Обновлено:</b> {updated_time}\n\n"
        "#арбитраж #bybit #binance #p2p"
    )

    клавиатура = типы.InlineKeyboardMarkup(row_width= 2 )
    клавиатура.добавить(
        types.InlineKeyboardButton("🔗 Оферт на покупку", url=buy_url),
        types.InlineKeyboardButton( "🔗 Предложение о продаже" , url=sell_url),
    )

    ожидание bot.send_message(
        chat_id=chat_id,
        текст=текст,
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview= Правда ,
        reply_markup=клавиатура,
    )


если __name__ == "__main__" :
    executor.start_polling(dp, skip_updates= True )
