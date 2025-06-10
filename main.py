# -*- coding: utf-8 -*-
"""Minimal Telegram bot for P2P arbitrage notifications."""

import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor


BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your.domain/webhook
WEBHOOK_PATH = "/webhook"
PORT = int(os.getenv("PORT", 8443))

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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
