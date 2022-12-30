from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
TOKEN = '5970102419:AAGARGEl1fYwjlDCt3OoDRiKJ9SbyJHFDGQ'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

