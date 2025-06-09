import logging
from aiogram import types, Dispatcher
from db import init_db, ensure_user, set_rates, get_rates, add_deal, get_history, get_top_deals

# Initialize DB
init_db()

def menu_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        types.InlineKeyboardButton("📈 Калькулятор", callback_data="calculator"),
    )
    kb.add(
        types.InlineKeyboardButton("📜 История", callback_data="history"),
        types.InlineKeyboardButton("🔥 Топ-сделки", callback_data="top_deals"),
    )
    return kb

# /start and /menu to show menu
async def cmd_start(message: types.Message):
    payload = message.get_args() or None
    ref = int(payload) if payload and payload.isdigit() else None
    ensure_user(message.from_user.id, ref)
    await message.answer("Добро пожаловать в ArbitPRO! Выберите опцию:", reply_markup=menu_kb())

async def cmd_menu(message: types.Message):
    await message.answer("Меню:", reply_markup=menu_kb())

# Menu button callback
async def menu_cb(callback: types.CallbackQuery):
    await callback.message.answer("Меню:", reply_markup=menu_kb())
    await callback.answer()

# Settings via callback
async def settings_cb(callback: types.CallbackQuery):
    await callback.message.edit_text("Введите курс покупки и продажи через пробел (например, `42.5 43.0`):")
    await callback.answer()

# Rate input handler
async def process_rates(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) == 2 and all(p.replace('.', '', 1).isdigit() for p in parts):
        buy, sell = map(float, parts)
        set_rates(message.from_user.id, buy, sell)
        await message.answer(f"Установлено: покупка={buy}, продажа={sell}")

# Calculator via callback or slash
async def calculator_cb(callback: types.CallbackQuery):
    buy, sell = get_rates(callback.from_user.id)
    if not buy or not sell:
        await callback.message.edit_text("Сначала задайте курсы в Настройках.")
    else:
        await callback.message.edit_text(f"Текущие курсы: покупка={buy}, продажа={sell}\nВведите сумму (USD):")
    await callback.answer()

async def cmd_calculator(message: types.Message):
    buy, sell = get_rates(message.from_user.id)
    if not buy or not sell:
        await message.answer("Сначала задайте курсы в Настройках.")
    else:
        await message.answer(f"Текущие курсы: покупка={buy}, продажа={sell}\nВведите сумму (USD):")

# Profit input via message
async def process_calc(message: types.Message):
    text = message.text.strip()
    if text.replace('.', '', 1).isdigit():
        amt = float(text)
        buy, sell = get_rates(message.from_user.id)
        if buy and sell:
            profit = amt * (sell - buy)
            add_deal(message.from_user.id, amt, buy, sell, profit)
            await message.answer(f"Профит: {profit:.2f} USDT")

# History via callback or slash
async def history_cb(callback: types.CallbackQuery):
    rows = get_history(callback.from_user.id)
    text = "История сделок:\n" + ("\n".join(
        f"{r['timestamp'][:19]}: {r['amount']}@{r['buy_price']}->{r['sell_price']} (profit={r['profit']:.2f})"
        for r in rows) if rows else "Нет сделок")
    await callback.message.edit_text(text)
    await callback.answer()

async def cmd_history(message: types.Message):
    rows = get_history(message.from_user.id)
    text = "История сделок:\n" + ("\n".join(
        f"{r['timestamp'][:19]}: {r['amount']}@{r['buy_price']}->{r['sell_price']} (profit={r['profit']:.2f})"
        for r in rows) if rows else "Нет сделок")
    await message.answer(text)

# Top deals via callback
async def top_cb(callback: types.CallbackQuery):
    rows = get_top_deals()
    text = "Топ сделки сегодня:\n" + ("\n".join(
        f"{r['timestamp'][11:19]} {r['user_id']}: profit={r['profit']:.2f}" for r in rows) if rows else "Нет данных")
    await callback.message.edit_text(text)
    await callback.answer()

# Fallback for unknown callbacks
async def unknown_cb(callback: types.CallbackQuery):
    await callback.answer("Нажата неизвестная кнопка")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_menu, commands=["menu"])
    dp.register_callback_query_handler(menu_cb, lambda c: c.data == "menu")
    dp.register_callback_query_handler(settings_cb, lambda c: c.data == "settings")
    dp.register_message_handler(process_rates, lambda m: len(m.text.split()) == 2 and all(p.replace('.', '', 1).isdigit() for p in m.text.split()))
    dp.register_callback_query_handler(calculator_cb, lambda c: c.data == "calculator")
    dp.register_message_handler(cmd_calculator, commands=["calculator"])
    dp.register_message_handler(process_calc, lambda m: m.text.replace('.', '', 1).isdigit())
    dp.register_callback_query_handler(history_cb, lambda c: c.data == "history")
    dp.register_message_handler(cmd_history, commands=["history"])
    dp.register_callback_query_handler(top_cb, lambda c: c.data == "top_deals")
    dp.register_callback_query_handler(unknown_cb)
