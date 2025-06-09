import logging
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import init_db, ensure_user, set_rates, get_rates, add_deal, get_history, get_top_deals

# Initialize DB
init_db()

# Persistent reply keyboard with menu options
default_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
default_kb.row(KeyboardButton("⚙️ Настройки"), KeyboardButton("📈 Калькулятор"))
default_kb.row(KeyboardButton("📜 История"), KeyboardButton("🔥 Топ-сделки"))

async def start_cmd(message: types.Message):
    ensure_user(message.from_user.id, None)
    await message.answer("Добро пожаловать в ArbitPRO!", reply_markup=default_kb)

async def settings_cmd(message: types.Message):
    await message.answer(
        "Введите курс покупки и продажи через пробел (например, `42.5 43.0`):",
        reply_markup=default_kb
    )

async def process_rates(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) == 2 and all(p.replace('.', '', 1).isdigit() for p in parts):
        buy, sell = map(float, parts)
        set_rates(message.from_user.id, buy, sell)
        await message.answer(f"Установлено: покупка={buy}, продажа={sell}", reply_markup=default_kb)

async def calculator_cmd(message: types.Message):
    buy, sell = get_rates(message.from_user.id)
    if not buy or not sell:
        await message.answer("Сначала задайте курсы через ⚙️ Настройки.", reply_markup=default_kb)
    else:
        await message.answer(
            f"Текущие курсы: покупка={buy}, продажа={sell}\nВведите сумму (USD):",
            reply_markup=default_kb
        )

async def process_calculation(message: types.Message):
    text = message.text.strip()
    if text.replace('.', '', 1).isdigit():
        amt = float(text)
        buy, sell = get_rates(message.from_user.id)
        profit = amt * (sell - buy) if buy and sell else 0.0
        add_deal(message.from_user.id, amt, buy, sell, profit)
        await message.answer(f"Профит: {profit:.2f} USDT", reply_markup=default_kb)

async def history_cmd(message: types.Message):
    rows = get_history(message.from_user.id)
    if rows:
        text = "История сделок:\n" + "\n".join(
            f"{r['timestamp'][:19]}: {r['amount']}@{r['buy_price']}->{r['sell_price']} (profit={r['profit']:.2f})"
            for r in rows
        )
    else:
        text = "Нет сделок"
    await message.answer(text, reply_markup=default_kb)

async def top_cmd(message: types.Message):
    rows = get_top_deals()
    if rows:
        text = "Топ сделки сегодня:\n" + "\n".join(
            f"{r['timestamp'][11:19]} {r['user_id']}: profit={r['profit']:.2f}" for r in rows
        )
    else:
        text = "Нет данных"
    await message.answer(text, reply_markup=default_kb)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=["start"])
    dp.register_message_handler(settings_cmd, lambda m: m.text == "⚙️ Настройки")
    dp.register_message_handler(process_rates, lambda m: len(m.text.split()) == 2 and all(p.replace('.', '', 1).isdigit() for p in m.text.split()))
    dp.register_message_handler(calculator_cmd, lambda m: m.text == "📈 Калькулятор")
    dp.register_message_handler(process_calculation, lambda m: m.text.replace('.', '', 1).isdigit())
    dp.register_message_handler(history_cmd, lambda m: m.text == "📜 История")
    dp.register_message_handler(top_cmd, lambda m: m.text == "🔥 Топ-сделки")
