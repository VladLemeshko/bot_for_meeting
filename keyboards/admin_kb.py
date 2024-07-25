from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_keyboard():
    kb_admin_panel = ReplyKeyboardMarkup(keyboard=[
                    [KeyboardButton("Пользователи")],
                    [KeyboardButton("Места")],
                    [KeyboardButton("Сгенерированные пары")]
                    ], resize_keyboard=True)
    
    return kb_admin_panel