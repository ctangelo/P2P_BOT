from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
TOKEN = YOUR_TELEGRAM_TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

