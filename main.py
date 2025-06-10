import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

_token = BOT_TOKEN if BOT_TOKEN and ":" in BOT_TOKEN else "0:dummy"
bot = Bot(token=_token, validate_token=False)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message) -> None:
    """Reply to the /start command."""
    await message.answer(
        "Bot is running. Use this chat to receive notifications.",
        disable_web_page_preview=True,
    )


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
) -> None:
    """Send an arbitrage notification."""
    text = (
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
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔗 Buy offer", url=buy_url),
        InlineKeyboardButton("🔗 Sell offer", url=sell_url),
    )
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def main() -> None:
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
