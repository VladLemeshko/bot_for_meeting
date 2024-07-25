from create_bot import dp,bot
from datetime import datetime
from data.sqlite_db import *
from data.algorithm import generate_unique_pairs
import aiogram
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_inline_map_button(map_url):
    keyboard = InlineKeyboardMarkup()
    map_button = InlineKeyboardButton(text="Открыть карту", url=map_url)
    keyboard.add(map_button)
    return keyboard

async def send_thursday_message():
    await remove_null_records()
    await check_and_remove_blocked_users()
    # Получаем текущую дату
    current_date = datetime.now()

    # Вычисляем новую дату, сместив текущую дату на 4 дня назад
    new_date = current_date - timedelta(days=4)

    # Преобразуем новую дату в строку в нужном формате
    formatted_date = new_date.strftime("%d/%m/%y")

    # Теперь можно использовать formatted_date в запросе к БД
    pairs_data = await get_pairs_and_places_pairs(formatted_date)

    for pair in pairs_data:
        if len(pair) == 3:
            nickname_1, nickname_2, place = pair
            print(nickname_1, nickname_2, place)
            chat_id_1 = await get_chat_id_for_nickname(nickname_1)
            
            try:
                map_url = place[2]  # Извлекаем ссылку на карту из данных о месте

                message_text = f'☕️ Привет!\n\n❗️Напоминаем, что на этой неделе у тебя встреча с @{nickname_2}. Если вы ее еще не назначили, сделай это прямо сейчас\n\n💫Идея для встречи: {place[0]} - {place[1]}\n\nЖелаем хорошо провести время! 🚀'
                await bot.send_message(chat_id_1, message_text, reply_markup=create_inline_map_button(map_url))
            except aiogram.utils.exceptions.BotBlocked:
                print(f"The bot is blocked by user {nickname_1}. Skipping message.")
                await remove_user(nickname_1)

        elif len(pair) == 2:
            nickname = pair[0]
            chat_id = await get_chat_id_for_nickname(nickname)

            try:
                message_text = 'Вам пара не досталась. Можете расслабиться и наслаждаться свободным временем. 🏖️'
                await bot.send_message(chat_id, message_text)
            except aiogram.utils.exceptions.BotBlocked:
                print(f"The bot is blocked by user {nickname}. Skipping message.")
                await remove_user(nickname_1)


