import itertools
from data.sqlite_db import save_pairs_and_reversed_pairs_to_db, get_random_place
from datetime import datetime

import itertools
from datetime import datetime

async def generate_unique_pairs(nicknames, saved_pairs):
    # Создайте все возможные уникальные пары из никнеймов
    all_possible_pairs = list(itertools.combinations(nicknames, 2))
    print(all_possible_pairs)
    # Если nicknames имеет нечетное количество никнеймов, добавляем одного пользователя в одиночный кортеж
    if len(nicknames) % 2 != 0:
        single_nicknames = [(nickname,) for nickname in nicknames]
        all_possible_pairs.extend(single_nicknames)  
    
    # Если saved_pairs пуст, создаем его как пустой список
    if not saved_pairs:
        saved_pairs = []
    print(saved_pairs)
    print("**************")
    print(all_possible_pairs)
    # Уберите из списка all_possible_pairs кортежи, которые есть в saved_pairs
    all_possible_pairs = [pair for pair in all_possible_pairs if pair not in saved_pairs]
    
    # Если all_possible_pairs пустой, вернуть None
    if not all_possible_pairs:
        return "Нет больше уникальных пар для генерации."
    
    # Убедитесь, что каждый никнейм встречается только один раз в парах
    unique_pairs = []
    used_nicknames = set()

    # Сегодняшняя дата в формате 'dd/mm/yy'
    date = datetime.now().strftime("%d/%m/%y")

    for pair in all_possible_pairs:
        if len(pair) == 2:
            nickname1, nickname2 = pair

            # Получите случайное место для этой пары
            random_place = await get_random_place()

            if nickname1 not in used_nicknames and nickname2 not in used_nicknames:
                unique_pairs.append((nickname1, nickname2, random_place))
                used_nicknames.add(nickname1)
                used_nicknames.add(nickname2)
        elif len(pair) == 1:
            nickname = pair[0]

            if nickname not in used_nicknames:
                random_place = await get_random_place()
                unique_pairs.append((nickname, random_place))
                used_nicknames.add(nickname)

        # Если удалось получить случайное место, сохраните его в базе данных
        
    await save_pairs_and_reversed_pairs_to_db(unique_pairs, date)

    return unique_pairs
