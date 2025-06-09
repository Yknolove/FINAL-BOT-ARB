import logging
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import init_db, ensure_user, set_rates, get_rates, add_deal, get_history, get_top_deals

init_db()
kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb.row(KeyboardButton("⚙️ Настройки"), KeyboardButton("📈 Калькулятор"))
kb.row(KeyboardButton("📜 История"), KeyboardButton("🔥 Топ-сделки"))

async def start_cmd(msg: types.Message):
    ensure_user(msg.from_user.id, None)
    await msg.answer("Бот запущен, меню внизу.", reply_markup=kb)

async def settings_cmd(msg: types.Message):
    await msg.answer("Введите курсы покупки/продажи через пробел (42.5 43.0):", reply_markup=kb)

async def process_rates(msg: types.Message):
    parts = msg.text.split()
    if len(parts)==2 and all(p.replace('.','',1).isdigit() for p in parts):
        b,s = map(float, parts); set_rates(msg.from_user.id,b,s)
        await msg.answer(f"Установлено: buy={b}, sell={s}", reply_markup=kb)

async def calculator_cmd(msg: types.Message):
    b,s = get_rates(msg.from_user.id)
    if not b or not s:
        await msg.answer("Сначала через ⚙️ Настройки", reply_markup=kb)
    else:
        await msg.answer(f"Курсы: buy={b}, sell={s}. Введите USDT:", reply_markup=kb)

async def process_calc(msg: types.Message):
    t = msg.text.strip()
    if t.replace('.','',1).isdigit():
        amt = float(t); b,s = get_rates(msg.from_user.id)
        profit_ua = amt*(s-b); profit_usdt = profit_ua/s if s else 0
        add_deal(msg.from_user.id, amt, b, s, profit_ua)
        await msg.answer(f"Профит: {profit_ua:.2f} UAH (~{profit_usdt:.2f} USDT)", reply_markup=kb)

async def history_cmd(msg: types.Message):
    rows = get_history(msg.from_user.id)
    text = "История:\n" + ("\n".join(f"{r['timestamp'][:19]} {r['amount']}@{r['buy_price']}->{r['sell_price']} profit={r['profit']:.2f}" for r in rows) if rows else "Нет")
    await msg.answer(text, reply_markup=kb)

async def top_cmd(msg: types.Message):
    rows = get_top_deals()
    text = "Топ сегодня:\n" + ("\n".join(f"{r['timestamp'][11:19]} {r['user_id']} pr={r['profit']:.2f}" for r in rows) if rows else "Нет")
    await msg.answer(text, reply_markup=kb)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=["start"])
    dp.register_message_handler(settings_cmd, lambda m: m.text=="⚙️ Настройки")
    dp.register_message_handler(process_rates, lambda m: len(m.text.split())==2)
    dp.register_message_handler(calculator_cmd, lambda m: m.text=="📈 Калькулятор")
    dp.register_message_handler(process_calc, lambda m: m.text.replace('.','',1).isdigit())
    dp.register_message_handler(history_cmd, lambda m: m.text=="📜 История")
    dp.register_message_handler(top_cmd, lambda m: m.text=="🔥 Топ-сделки")
