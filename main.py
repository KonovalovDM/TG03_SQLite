import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from googletrans import Translator
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()



@dp.message(CommandStart)
async def start(message: Message):
    await message.answer(f'Приветики, {message.from_user.first_name}! Я бот! Могу показать погоду, фотки и многое другое!')



async def main():
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())