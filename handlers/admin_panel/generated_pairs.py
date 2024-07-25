from create_bot import dp, bot 
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import is_admin, admin_user_ids
from data.sqlite_db import get_pairs_by_date


class GenPairsStates(StatesGroup):
    find_pairs_state = State()

@dp.message_handler(lambda message: message.text == "Сгенерированные пары" )
async def places_handler(message: types.Message):
    # Проверяем, является ли пользователь администратором
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("Вы не являетесь администратором.")
        return
    else:
        await message.answer(f"Пожалуйста введите дату в формате дд/мм/гг")
        await GenPairsStates.find_pairs_state.set()
        
@dp.message_handler(state=GenPairsStates.find_pairs_state)
async def process_find_pairs(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["find_pair"] = message.text
        find_pair_date = data["find_pair"]
        
          # Извлекаем пары по указанной дате
        pairs_list = await get_pairs_by_date(find_pair_date)

        if not pairs_list:
            await message.answer(f"На {find_pair_date} нет данных о партнерах.")
        else:
            formatted_pairs = []
            for i, pair in enumerate(pairs_list):
                if len(pair) == 2:
                    formatted_pairs.append(f"{i + 1}. @{pair[0]} x @{pair[1]}")
                elif len(pair) == 1:
                    formatted_pairs.append(f"{i + 1}. @{pair[0]} (без пары)")

            # Преобразуем список в одну строку с переносами
            formatted_pairs_text = "\n".join(formatted_pairs)

            await message.answer(f"Список всех пар за {find_pair_date}:\n\n{formatted_pairs_text}")

    # Сбрасываем состояние FSM
    await state.finish()