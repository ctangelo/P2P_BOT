from aiogram import executor
from dispatcher import dp
from database import bot_db


async def on_startup(_):
    print('Bot online')
    bot_db.sql_start()


from handlers import client

client.register_client_handler(dp)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
