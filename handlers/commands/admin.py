from create_bot import dp, bot 
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data.config import is_admin
from keyboards.admin_kb import get_admin_keyboard

# Обработчик команды /admin
@dp.message_handler(lambda message: message.text in ["/admin", "Панель администратора"])
async def admin_panel(message: types.Message):
    message.delete
    if is_admin(message.from_user.id):
        # Пользователь - администратор
        await message.answer("Вы находитесь в панели управления администратора, пожалуйста, выберите действие на клавиатуре:",
                             reply_markup=get_admin_keyboard())
    else:
        # Пользователь не является администратором
        await message.answer("Вы не являетесь администратором")