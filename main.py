"""Telegram bot for P2P arbitrage notifications."""

import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app
from aiogram.utils import executor
from aiohttp import web


BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your.domain/webhook
WEBHOOK_PATH = "/webhook"
PORT = int(os.getenv("PORT", 8443))


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


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
async def cmd_start(message: types.Message) -> None:
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
        disable_web_page_preview=True,
    )


@dp.callback_query_handler(lambda c: c.data in [
    "settings", "calculator", "history", "top_deals"])
async def menu_handler(callback: types.CallbackQuery) -> None:
    text_map = {
        "settings": "🔧 Здесь вы можете настроить желаемые курсы и объёмы.",
        "calculator": "🧮 Введите сумму, и я посчитаю потенциальный профит.",
        "history": "📚 История ваших совершённых сделок появится здесь.",
        "top_deals": "🔥 Топ P2P-сделки за сегодня.",
    }
    await callback.message.edit_text(
        text_map.get(callback.data, "Раздел в разработке."),
        parse_mode=types.ParseMode.HTML,
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


async def handle_root(_: web.Request) -> web.Response:
    return web.Response(text="OK")


async def on_startup(_: web.Application) -> None:
    logging.info("Setting webhook...")
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(_: web.Application) -> None:
    logging.info("Deleting webhook...")
    await bot.delete_webhook()
    await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
    app.router.add_get("/", handle_root)
    app.router.add_head("/", handle_root)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=PORT)
