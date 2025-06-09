import os
import logging
from aiogram import types, Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

def get_buy_sell_rates_from_db():
    # Заглушка; замените реальным запросом к БД
    return 41.0, 40.5

@dp.message_handler(Text(equals="📈 Калькулятор"))
async def calc_start(message: types.Message):
    await message.answer("Введите сумму в USDT:")

@dp.message_handler(lambda message: message.text and message.text.replace('.', '', 1).isdigit())
async def calc_compute(message: types.Message):
    b, s = get_buy_sell_rates_from_db()
    amount = float(message.text)
    result_ua = amount * b
    result_usd = amount * s
    await message.answer(f"Калькулятор: buy rate={b}, sell rate={s}")
    await message.answer(f"Прибыль: {result_ua:.2f} UAH, {result_usd:.2f} USDT")

# Добавляем register_handlers, чтобы main.py не падал
def register_handlers(dispatcher: Dispatcher):
    # handlers уже зарегистрированы через декораторы, но функция обязана существовать
    return

# Экспорт dp, если понадобится
__all__ = ['bot', 'dp', 'register_handlers']
