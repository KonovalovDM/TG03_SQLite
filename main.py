import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()  # Хранилище состояний
dp = Dispatcher(storage=storage)

# Определяем состояния
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Вызываем функцию для создания базы данных
init_db()


# Хэндлер для команды /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logging.debug(f"Проверка текущего состояния: {current_state}")

    # Если пользователь уже в процессе регистрации
    if current_state == Form.name.state:
        await message.answer("Ты уже начал регистрацию. Как тебя зовут?")
    elif current_state == Form.age.state:
        await message.answer("Ты уже начал регистрацию. Сколько тебе лет?")
    elif current_state == Form.grade.state:
        await message.answer("Ты уже начал регистрацию. В каком ты классе?")
    else:
        # Если регистрации нет, начинаем заново
        await state.clear()
        logging.debug("Состояние сброшено.")
        await message.answer("Приветики, я Школьный Бот! А тебя как зовут?")
        await state.set_state(Form.name)
        logging.debug("Состояние установлено: Form.name")


# Хэндлер для ввода имени
@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    logging.debug(f"Состояние: Form.name. Сообщение: {message.text}")
    if not message.text.strip():  # Проверяем, что текст не пустой
        await message.answer('Пожалуйста, введи свое имя.')
        return
    await state.update_data(name=message.text.strip())  # Сохраняем имя
    await message.answer('Сколько тебе лет?')
    await state.set_state(Form.age)
    logging.debug(f"Имя сохранено: {message.text.strip()}, состояние: {await state.get_state()}")


# Хэндлер для ввода возраста
@dp.message(Form.age)
async def get_age(message: Message, state: FSMContext):
    logging.debug(f"Состояние: Form.age. Сообщение: {message.text}")
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введи число для возраста.')
        return
    await state.update_data(age=int(message.text))
    await message.answer('В каком ты классе?')
    await state.set_state(Form.grade)
    logging.debug(f"Возраст сохранен: {message.text}, состояние: {await state.get_state()}")


# Хэндлер для ввода класса
@dp.message(Form.grade)
async def get_grade(message: Message, state: FSMContext):
    logging.debug(f"Состояние: Form.grade. Сообщение: {message.text}")
    if not message.text.strip():  # Проверяем, что текст не пустой
        await message.answer('Пожалуйста, введи свой класс.')
        return
    await state.update_data(grade=message.text.strip())
    student_data = await state.get_data()
    logging.debug(f"Данные ученика: {student_data}")

    # Сохраняем данные в базу данных
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO students (name, age, grade) VALUES (?, ?, ?)
    ''', (student_data['name'], student_data['age'], student_data['grade']))
    conn.commit()
    conn.close()

    await message.answer(f"Отлично, {student_data['name']}! Твои данные внесены в базу школы.")
    await state.clear()
    logging.debug(f"Состояние очищено: {await state.get_state()}")



# Глобальный хэндлер: работает только для сообщений вне состояний
@dp.message()
async def debug_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logging.debug(f"Получено сообщение: {message.text}, текущее состояние: {current_state}")

    # Если пользователь находится в состоянии, пропускаем обработку этим хэндлером
    if current_state:
        return
    await message.answer("Я тебя не понимаю. Используй команду /start, чтобы начать.")


# Запуск бота
async def main():
    try:
        logging.debug("Запуск бота...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка во время работы бота: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
