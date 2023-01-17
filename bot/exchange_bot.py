from aiogram import executor
from dispatcher import dp
from database import bot_db


async def on_startup(_):
    print('Bot online')
    bot_db.sql_start()


from handlers import client
from handlers import admin

client.register_client_handler(dp)
admin.register_admin_handler(dp)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
