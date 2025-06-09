import os
from aiogram import Bot, Dispatcher, types

bot = Bot(token=os.getenv("BOT_TOKEN"))

def get_buy_rate():
    # TODO: Реализуйте получение курса покупки
    return 0

def get_sell_rate():
    # TODO: Реализуйте получение курса продажи
    return 0

@bot.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    buy = get_buy_rate()
    sell = get_sell_rate()
    await message.answer(f"Курсы: buy={buy}, sell={sell}")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    # TODO: Регистрируйте остальные хэндлеры здесь
