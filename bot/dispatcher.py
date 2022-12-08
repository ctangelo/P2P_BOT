from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

TOKEN = '2146493358:AAH4lkALC3NYXoWbWNYxz5M0HkuT0AuIYVo'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
