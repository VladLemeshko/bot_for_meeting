import sqlite3 as sq 
import os
from create_bot import bot
import random
import aiogram



# Получаем путь к текущей директории, где находится этот файл
current_directory = os.path.dirname(os.path.abspath(__file__))

# Создаем путь к папке "data" в корневой папке проекта
data_directory = os.path.join(current_directory, "..", "data")

# Создаем полный путь к файлу базы данных в папке "data"
db_path = os.path.join(data_directory, "user.db")

# Если папка "data" не существует, создаем ее
if not os.path.exists(data_directory):
    os.makedirs(data_directory)
    
db = None
cur = None




# Инициализация базы данных и курсора для выполнения запросов
async def users_db_start():
    global db, cur
    
    db = sq.connect(db_path)  # Подключаемся к базе данных
    cur = db.cursor()
    
    # Создаем таблицу "profiles" с полями: user_id, nickname
    cur.execute("CREATE TABLE IF NOT EXISTS profiles(user_id TEXT PRIMARY KEY, nickname TEXT)")
    
    db.commit()  # Сохраняем изменения в базе данных

async def remove_null_records():

    # Удаляем записи, где nickname равен NULL
    cur.execute("DELETE FROM profiles WHERE nickname IS NULL")

    db.commit()
    
async def get_all_user_ids():

    # Получаем все user_id из таблицы "profiles"
    cur.execute("SELECT user_id FROM profiles")
    user_ids = cur.fetchall()

    return [user_id[0] for user_id in user_ids]

# Создание профиля пользователя
async def create_profile(user_id, nickname):
    user = cur.execute("SELECT 1 FROM profiles WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profiles VALUES(?, ?)", (user_id, nickname))
        db.commit()
 
# Получение списка всех никнеймов
async def get_all_nicknames():
    cur.execute('SELECT nickname FROM profiles')
    nicknames = cur.fetchall()
    nickname_list = [row[0] for row in nicknames]
    return nickname_list
   
# Отправка сообщения всем пользователям
async def send_message_to_all_users(message_text):
    cur.execute('SELECT user_id FROM profiles')
    user_ids = cur.fetchall()
    
    for user_id in user_ids:
        await bot.send_message(user_id[0], message_text)

# Удаление пользователя
async def remove_user(nickname):
    cur.execute("DELETE FROM profiles WHERE nickname=?", (nickname,))
    db.commit()

# Получение chat_id для никнейма
async def get_chat_id_for_nickname(nickname):
    cur.execute("SELECT user_id FROM profiles WHERE nickname=?", (nickname,))
    result = cur.fetchone()
    if result:
        return result[0]  # Возвращаем user_id как chat_id
    else:
        return None  # Никнейм не найден, возвращаем None или другое значение по умолчанию
    
async def check_and_remove_blocked_users():
    user_ids = await get_all_user_ids()

    for user_id in user_ids:
        try:
            # Проверяем, существует ли пользователь в базе данных
            await bot.get_chat(user_id)
        except aiogram.utils.exceptions.ChatNotFound:
            # Если возникает исключение ChatNotFound, значит, пользователь заблокировал бота
            # и мы можем удалить его из базы данных
            cur.execute("DELETE FROM profiles WHERE user_id=?", (user_id,))
            db.commit()
        except Exception as e:
            # Обработка других ошибок
            print(f"Error checking user {user_id}: {str(e)}")





    

# Создание таблицы для всех пар
async def create_all_pairs_table():
    cur.execute("CREATE TABLE IF NOT EXISTS all_pairs (pairs TEXT, reversed_pairs TEXT, date TEXT, place TEXT)")
    db.commit()

async def delete_data_by_date(date_to_delete):
    cur.execute("DELETE FROM all_pairs WHERE date=?", (date_to_delete,))
    db.commit()

    
async def get_pairs_by_date(date):
    # Выполняем SQL-запрос для выбора пар по указанной дате
    cur.execute("SELECT pairs FROM all_pairs WHERE date=?", (date,))
    pairs_data = cur.fetchall()

    # Преобразование данных в список кортежей
    pairs_list = [pair[0].strip('"').split(', ') for pair in pairs_data]
    
    return pairs_list
  
# Сохранение пар и их перевернутых версий в базу данных
async def save_pairs_and_reversed_pairs_to_db(pairs, date):
    # Вставляем пары и их перевернутые версии в таблицу all_pairs
    for pair in pairs:
        pair_str = ', '.join(pair[:-1])  # Исключаем место из строки
        reversed_pair_str = ', '.join(reversed(pair[:-1]))  # Исключаем место из перевернутой строки
        place_str = ', '.join(pair[-1])  # Преобразуем место в строку
        cur.execute("INSERT INTO all_pairs (pairs, reversed_pairs, date, place) VALUES (?, ?, ?, ?)",
                    (pair_str, reversed_pair_str, date, place_str))  # Передаем место как строку
    db.commit()

# Очистка таблицы всех пар
async def clear_all_pairs_table():
    cur.execute("DELETE FROM all_pairs")
    db.commit()

# Получение пар и их перевернутых версий
async def get_pairs_and_places_pairs(date):
    if date is None:
        # Если дата не указана, выбираем все данные
        cur.execute("SELECT pairs, reversed_pairs, place FROM all_pairs")
    else:
        # Если указана дата, выбираем данные только для этой даты
        cur.execute("SELECT pairs, reversed_pairs, place FROM all_pairs WHERE date=?", (date,))

    pairs_data = cur.fetchall()

    # Преобразование данных
    pairs_data_as_tuples = []
    for pair in pairs_data:
        pairs = pair[0].strip('"').split(', ')
        reversed_pairs = pair[1].strip('"').split(', ')
        place_data = pair[2].strip('"').split('", "')  # Разделяем по двойным кавычкам и запятой
        place = (place_data[0], place_data[1], place_data[2])  # Создаем кортеж из данных

        for p1, p2 in zip(pairs, reversed_pairs):
            if p1 == p2:
                pairs_data_as_tuples.append((p1, place))
            else:
                pairs_data_as_tuples.append((p1, p2, place))

    return pairs_data_as_tuples

# Получение пар и их перевернутых версий
async def get_pairs_and_reversed_pairs(date):
    if date is None:
        # Если дата не указана, выбираем все данные
        cur.execute("SELECT pairs, reversed_pairs FROM all_pairs")
    else:
        # Если указана дата, выбираем данные только для этой даты
        cur.execute("SELECT pairs, reversed_pairs FROM all_pairs WHERE date=?", (date,))

    pairs_data = cur.fetchall()

    # Преобразование данных
    pairs_data_as_tuples = []
    for pair in pairs_data:
        pairs = pair[0].strip('"').split(', ')
        reversed_pairs = pair[1].strip('"').split(', ')
    
        for p1, p2 in zip(pairs, reversed_pairs):
            if p1 == p2:
                pairs_data_as_tuples.append((p1))
            else:
                pairs_data_as_tuples.append((p1, p2))

    return pairs_data_as_tuples

    

# Создание таблицы для мест
async def create_places_table():
    cur.execute("CREATE TABLE IF NOT EXISTS places (name TEXT, address TEXT, link TEXT)")
    db.commit()
    
# Функция для сохранения места в таблицу "places"
async def save_place(name, address, link):
    cur.execute("INSERT INTO places (name, address, link) VALUES (?, ?, ?)", (name, address, link))
    db.commit()

# Функция для извлечения всех названий мест из таблицы "places"
async def get_all_place_names():
    cur.execute("SELECT name FROM places")
    place_names = cur.fetchall()
    place_name_list = [row[0] for row in place_names]
    return place_name_list

# Функция для удаления строки из таблицы "places" по названию места
async def remove_place_by_name(place_name):
    cur.execute("DELETE FROM places WHERE name=?", (place_name,))
    db.commit()

async def get_random_place():
    cur.execute("SELECT name, address, link FROM places")
    places_data = cur.fetchall()

    if places_data:
        random_place = random.choice(places_data)
        name, address, link = random_place
        return (f'"{name}"', f'"{address}"', f'"{link}"')
    else:
        return None