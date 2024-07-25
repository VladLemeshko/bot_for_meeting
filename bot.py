from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from create_bot import dp
from handlers import *
from data.sqlite_db import users_db_start, create_all_pairs_table, create_places_table
from data.config import BOT_TOKEN #авторизованный токен для подключения к телеграм API
from schedule_msg.abvgd import *
from schedule_msg.sunday import *
from schedule_msg.thursday import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


dp.middleware.setup(LoggingMiddleware())

# Создаем экземпляр AsyncIOScheduler
scheduler = AsyncIOScheduler()

scheduler.add_job(send_tuesday_message, CronTrigger(day_of_week=0, hour=22, minute=00, second=00, timezone='Europe/Moscow', week='*'))
scheduler.add_job(send_sunday_message, CronTrigger(day_of_week=6, hour=12, minute=00, second=00, timezone='Europe/Moscow', week='*'))
scheduler.add_job(send_thursday_message, CronTrigger(day_of_week=3, hour=12, minute=00, second=00, timezone='Europe/Moscow', week='*'))

async def on_startup(_):
    await users_db_start()
    await create_places_table()
    await create_all_pairs_table()
    
    # Запускаем планировщик
    scheduler.start()
    
    print("Бот запущен, подключение к БД выполнено успешно")   


# запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)