from create_bot import dp, bot 
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import is_admin
from data.sqlite_db import get_all_nicknames, remove_user
from keyboards.admin_kb import get_admin_keyboard

class UsersStates(StatesGroup):
    remove_user_state = State()
    
def get_users_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Вернуться к списку")],
        [KeyboardButton("Панель администратора")]],
        resize_keyboard=True)
    
# Обработчик кнопки "Пользователи"
@dp.message_handler(lambda message: message.text == "Пользователи" or message.text == "Вернуться к списку")
async def users_handler(message: types.Message):
    # Проверяем, является ли пользователь администратором
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("Вы не являетесь администратором.")
        return

    # Получаем список всех никнеймов из БД
    all_nicknames = await get_all_nicknames()

    # Формируем пронумерованный список
    formatted_list = "\n".join([f"{index + 1}. {nickname}" for index, nickname in enumerate(all_nicknames)])

    # Создаем клавиатуру с кнопками "Добавить пользователя" и "Удалить пользователя"
    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Удалить пользователя")],
        [KeyboardButton("Панель администратора")]],
        resize_keyboard=True)

    # Отправляем сообщение с пронумерованным списком и клавиатурой
    await message.answer(f"Список пользователей:\n\n{formatted_list}", reply_markup=markup)


# Обработчик кнопки "Удалить пользователя"
@dp.message_handler(lambda message: message.text == "Удалить пользователя")
async def remove_user_handler(message: types.Message):
    await message.answer("Введите никнейм пользователя, которого хотите удалить:", reply_markup=ReplyKeyboardMarkup(keyboard = [[KeyboardButton("Вернуться к списку")]], resize_keyboard=True))

    # Устанавливаем состояние "remove_user" для пользователя
    await UsersStates.remove_user_state.set()

# Обработчик для ввода никнейма при удалении пользователя
@dp.message_handler(state=UsersStates.remove_user_state)
async def process_remove_user(message: types.Message, state: FSMContext):
    if message.text == "Вернуться к списку":
        await state.finish()
        await users_handler(message)  # Вызываем обработчик "Пользователи"
        return
    
    else:
        async with state.proxy() as data:
            data["remove_user_nickname"] = message.text

        # Удаляем пользователя из БД
        nickname = data["remove_user_nickname"]
        await remove_user(nickname)
        
        await message.answer(f"Пользователь {nickname} успешно удален.", reply_markup=get_users_keyboard())
        
        await state.finish()