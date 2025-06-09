import logging
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
from aiogram.dispatcher.filters import Text

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

# ... (other imports and handlers)

@dp.message_handler(Text(equals="📈 Калькулятор"))
async def calc_start(message: types.Message):
    await message.answer("Введите сумму в USDT:")
    # set state, etc.

# Handler where syntax error occurred - fixed
@dp.message_handler(lambda message: message.text.isdigit())
async def calc_compute(message: types.Message):
    b, s = get_buy_sell_rates_from_db()  # your function to fetch rates
    amount = float(message.text)
    result_ua = amount * b
    result_usd = amount * s
    await message.answer(f"Калькулятор: buy rate={b}, sell rate={s}")
    await message.answer(f"Прибыль: {result_ua:.2f} UAH, {result_usd:.2f} USDT")

# ... (rest of handlers)
