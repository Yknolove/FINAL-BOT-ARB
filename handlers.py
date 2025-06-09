import logging
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import init_db, ensure_user, set_rates, get_rates, add_deal, get_history, get_top_deals

# Init
init_db()
kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb.row(KeyboardButton("⚙️ Настройки"), KeyboardButton("📈 Калькулятор"))
kb.row(KeyboardButton("📜 История"), KeyboardButton("🔥 Топ-сделки"))

# State
awaiting_calc = set()

async def start_cmd(msg: types.Message):
    ensure_user(msg.from_user.id, None)
    awaiting_calc.discard(msg.from_user.id)
    await msg.answer("Бот запущен ✅ Меню внизу.", reply_markup=kb)

async def settings_cmd(msg: types.Message):
    awaiting_calc.discard(msg.from_user.id)
    await msg.answer("Введите курс покупки/продажи через пробел (например, 42.5 43.0):", reply_markup=kb)

async def process_rates(msg: types.Message):
    parts = msg.text.strip().split()
    if len(parts) == 2 and all(p.replace('.','',1).isdigit() for p in parts):
        b,s = map(float, parts)
        set_rates(msg.from_user.id, b, s)
        awaiting_calc.discard(msg.from_user.id)
        await msg.answer(f"Установлено: buy={b}, sell={s}", reply_markup=kb)

async def calculator_cmd(msg: types.Message):
    b,s = get_rates(msg.from_user.id)
    if not b or not s:
        await msg.answer("Сначала задайте курсы через ⚙️ Настройки", reply_markup=kb)
    else:
        awaiting_calc.add(msg.from_user.id)
        await msg.answer(f"Курсы: buy={b}, sell={s}
Введите сумму (USDT):", reply_markup=kb)

async def process_calc(msg: types.Message):
    if msg.from_user.id not in awaiting_calc:
        return
    text = msg.text.strip()
    if text.replace('.','',1).isdigit():
        amt = float(text)
        b,s = get_rates(msg.from_user.id)
        profit_uah = amt * (s - b)
        profit_usdt = profit_uah / s if s else 0
        add_deal(msg.from_user.id, amt, b, s, profit_uah)
        awaiting_calc.discard(msg.from_user.id)
        await msg.answer(f"Профит: {profit_uah:.2f} UAH (~{profit_usdt:.2f} USDT)", reply_markup=kb)

async def history_cmd(msg: types.Message):
    awaiting_calc.discard(msg.from_user.id)
    rows = get_history(msg.from_user.id)
    if rows:
        text = "История сделок:
" + "\n".join(
            f"{r['timestamp'][:19]}: {r['amount']}@{r['buy_price']}->{r['sell_price']} profit={r['profit']:.2f}"
            for r in rows
        )
    else:
        text = "Нет сделок"
    await msg.answer(text, reply_markup=kb)

async def top_cmd(msg: types.Message):
    awaiting_calc.discard(msg.from_user.id)
    rows = get_top_deals()
    if rows:
        text = "Топ сделки сегодня:
" + "\n".join(
            f"{r['timestamp'][11:19]} {r['user_id']}: profit={r['profit']:.2f}"
            for r in rows
        )
    else:
        text = "Нет данных"
    await msg.answer(text, reply_markup=kb)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=["start"])
    dp.register_message_handler(settings_cmd, lambda m: m.text=="⚙️ Настройки")
    dp.register_message_handler(process_rates, lambda m: len(m.text.split())==2)
    dp.register_message_handler(calculator_cmd, lambda m: m.text=="📈 Калькулятор")
    dp.register_message_handler(process_calc, lambda m: m.text.replace('.','',1).isdigit())
    dp.register_message_handler(history_cmd, lambda m: m.text=="📜 История")
    dp.register_message_handler(top_cmd, lambda m: m.text=="🔥 Топ-сделки")
