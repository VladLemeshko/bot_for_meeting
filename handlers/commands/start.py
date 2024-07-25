from create_bot import dp, bot 
from aiogram import types
from data.sqlite_db import *
from data.algorithm import generate_unique_pairs
from schedule_msg.sunday import send_sunday_message
from schedule_msg.thursday import send_thursday_message


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.message):
    
    greeting = "Привет! Рады приветствовать тебя в боте для еженедельных встреч <b>Y Club.</b>\n\n\
Каждое <em>воскресенье</em> тебе будут приходить уведомления с контактами резидентов, чтобы вы смогли назначить встречу в любое удобное время.\n\
Кроме того, наш бот предложит вам не только провести встречу, но и подберет идеи для совместного времяпровождения😉.\n\n\
Желаем хорошо провести время! Команда <b>Y Club</b>💜"

    user_id=message.from_user.id
    user = message.from_user  # Получаем объект пользователя из сообщения
    if user.username:
        username = user.username
    else:
        username = None
        
    
    await create_profile(user_id=user_id, nickname=username)
    await message.answer(greeting, parse_mode = "HTML")
    
    
@dp.message_handler(commands=["generate_sunday"])
async def generate_cmd(message: types.message):

    await send_sunday_message()

@dp.message_handler(commands=["generate_thursday"])
async def generate_cmd(message: types.message):

    await send_thursday_message()
    
@dp.message_handler(commands=["delete"])
async def delete_cmd(message: types.message):

    await remove_null_records()
    await check_and_remove_blocked_users()
    
    await message.answer("Все пустые никнеймы удалены")