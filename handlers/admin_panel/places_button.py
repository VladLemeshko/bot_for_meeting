from create_bot import dp, bot 
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import is_admin
from data.sqlite_db import get_all_place_names, remove_place_by_name, save_place


class PlacesStates(StatesGroup):
    add_place_name_state = State()
    add_place_addres_state = State()
    add_place_link_state = State()
    remove_place_state = State()
    
def get_places_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Вернуться к списку мест")],
        [KeyboardButton("Панель администратора")]],
        resize_keyboard=True)
    
# Обработчик кнопки "Места"
@dp.message_handler(lambda message: message.text == "Места" or message.text == "Вернуться к списку мест")
async def places_handler(message: types.Message):
    # Проверяем, является ли пользователь администратором
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("Вы не являетесь администратором.")
        return

    # Получаем список всех никнеймов из БД
    all_places = await get_all_place_names()

    # Формируем пронумерованный список
    formatted_list = "\n".join([f"{index + 1}. {name}" for index, name in enumerate(all_places)])

    # Создаем клавиатуру с кнопками "Добавить место" и "Удалить место"
    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Добавить место")],
        [KeyboardButton("Удалить место")],
        [KeyboardButton("Панель администратора")]],
        resize_keyboard=True)

    # Отправляем сообщение с пронумерованным списком и клавиатурой
    await message.answer(f"Список мест:\n\n{formatted_list}", reply_markup=markup)
    
    
# Обработчик кнопки "добавить место"
@dp.message_handler(lambda message: message.text == "Добавить место")
async def add_place_handler(message: types.Message):
    await message.answer("Введите точное название места, которое хотите добавить:", reply_markup=ReplyKeyboardMarkup(keyboard = [[KeyboardButton("Вернуться к списку мест")]], resize_keyboard=True))

    # Устанавливаем состояние "remove_user" для пользователя
    await PlacesStates.add_place_name_state.set()

# Обработчик для ввода места при добавлении места
@dp.message_handler(state=PlacesStates.add_place_name_state)
async def process_add_place(message: types.Message, state: FSMContext):
    if message.text == "Вернуться к списку мест":
        await state.finish()
        await places_handler(message)  # Вызываем обработчик "Места"
        return
    
    else:
        async with state.proxy() as data:
            data["add_place"] = message.text

        await message.answer(f"Теперь введите адрес места, которое хотите добавить", reply_markup=get_places_keyboard())
        
        await PlacesStates.add_place_addres_state.set()

# Обработчик для ввода адреса места при добавлении места
@dp.message_handler(state=PlacesStates.add_place_addres_state)
async def process_add_place_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["add_place_address"] = message.text

    await message.answer("Теперь введите ссылку на место, которое хотите добавить", reply_markup=get_places_keyboard())
    await PlacesStates.add_place_link_state.set()
    
# Обработчик для ввода ссылки на место при добавлении места
@dp.message_handler(state=PlacesStates.add_place_link_state)
async def process_add_place_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["add_place_link"] = message.text

        # Получаем данные о месте из состояния
        name = data["add_place"]
        address = data["add_place_address"]
        link = data["add_place_link"]

        # Сохраняем место в базе данных
        await save_place(name, address, link)

    await message.answer(f"Место \"{name}\" успешно добавлено!", reply_markup=get_places_keyboard())
    await state.finish()
    
# Обработчик кнопки "Удалить место"
@dp.message_handler(lambda message: message.text == "Удалить место")
async def remove_place_handler(message: types.Message):
    await message.answer("Введите точное название места, которое хотите удалить:", reply_markup=ReplyKeyboardMarkup(keyboard = [[KeyboardButton("Вернуться к списку мест")]], resize_keyboard=True))

    # Устанавливаем состояние "remove_user" для пользователя
    await PlacesStates.remove_place_state.set()

# Обработчик для ввода никнейма при удалении пользователя
@dp.message_handler(state=PlacesStates.remove_place_state)
async def process_remove_place(message: types.Message, state: FSMContext):
    if message.text == "Вернуться к списку мест":
        await state.finish()
        await places_handler(message)  # Вызываем обработчик "Пользователи"
        return
    
    else:
        async with state.proxy() as data:
            data["remove_place"] = message.text

        # Удаляем пользователя из БД
        place = data["remove_place"]
        await remove_place_by_name(place)
        
        await message.answer(f"Место {place} успешно удален.", reply_markup=get_places_keyboard())
        
        await state.finish()