import os
import logging
from aiogram import types, Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

# Placeholder for real DB fetch
def get_buy_sell_rates_from_db():
    return 41.0, 40.5

@dp.message_handler(commands=['start', 'menu'])
async def send_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📈 Калькулятор")
    keyboard.add("🔔 Подписаться на арбитраж")
    await message.answer("Меню: выберите функцию", reply_markup=keyboard)

@dp.message_handler(Text(equals="📈 Калькулятор"))
async def calc_start(message: types.Message):
    await message.answer("Введите сумму в USDT:")

@dp.message_handler(lambda msg: msg.text and msg.text.replace('.', '', 1).isdigit())
async def calc_compute(message: types.Message):
    b, s = get_buy_sell_rates_from_db()
    amount = float(message.text)
    result_ua = amount * b
    result_usd = amount * s
    await message.answer(f"Калькулятор: buy rate={b:.2f}, sell rate={s:.2f}")
    await message.answer(f"Прибыль: {result_ua:.2f} UAH, {result_usd:.2f} USDT")

@dp.message_handler(Text(equals="🔔 Подписаться на арбитраж"))
async def subscribe_arbitrage(message: types.Message):
    from db import get_conn
    conn = get_conn()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS settings (user_id INTEGER PRIMARY KEY)"
    )
    try:
        conn.execute(
            "INSERT OR IGNORE INTO settings(user_id) VALUES(?)",
            (message.from_user.id,)
        )
        conn.commit()
        await message.answer("Вы подписались на арбитражные уведомления.")
    except Exception as e:
        logging.error(f"DB error on subscribe: {e}")
        await message.answer("Не удалось подписаться, повторите позже.")
    finally:
        conn.close()

def register_handlers(dispatcher: Dispatcher):
    return

__all__ = ['bot', 'dp', 'register_handlers']
