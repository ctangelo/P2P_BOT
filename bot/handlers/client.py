from aiogram import types, Dispatcher
from bot.keyboard import kb_client
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import bot_db
import random
from dispatcher import bot, dp

from bot.keyboard.client_kb import urlkb_3, urlkb_4, urlkb_5


# for add user info to database
class FSMUserInfo(StatesGroup):
    name = State()
    vista_num = State()
    binance_id = State()


# for add buy order to database
class FSMAddUserOrder(StatesGroup):
    usdt_amount = State()
    vst_amount = State()


async def message_start(message: types.Message):
    await message.answer('Привет! Я бот обменник! Чтоб узнать больше о функционале, нажми HELP',
                         reply_markup=kb_client)


# add buy order to database
async def add_buy_order(callback: types.CallbackQuery):
    await FSMAddUserOrder.usdt_amount.set()
    await callback.message.answer('Сколько у вас USDT?')


async def add_usdt_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order_id'] = random.randint(1000, 100000)
        data['user_id'] = message.from_user.id
        data['buy'] = 1
        data['usdt_amount'] = message.text
    await FSMAddUserOrder.next()
    await message.answer('Сколько хотите получить VST?')


async def add_vst_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vst_amount'] = message.text
    await message.reply('ОРДЕР НА ПОКУПКУ VST ДОБАВЛЕН')
    await bot_db.sql_add_buy_order(state)
    await state.finish()


# show user info
async def message_wallet(message: types.Message):
    await bot_db.is_user_id_in_data(message)


# add user info to database
async def cm_start(callback: types.CallbackQuery):
    await FSMUserInfo.name.set()
    await callback.message.answer('Как вас зовут?')


async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['name'] = message.text
    await FSMUserInfo.next()
    await message.reply('Введите ваш VST счет:')


async def load_vst(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['VST'] = message.text
    await FSMUserInfo.next()
    await message.reply('Введите ваш Binance ID:')


async def load_binance(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['BinanceID'] = message.text
    await message.reply('Готово')
    await bot_db.sql_add_data(state)
    await bot_db.sql_read_data(message)
    await state.finish()


# inline button 'change' in wallet
async def change_data(callback: types.CallbackQuery):
    await callback.message.delete()
    await bot_db.sql_del_data(callback)
    await cm_start(callback)


# inline button 'delete' in wallet
async def del_data(callback: types.CallbackQuery):
    await bot_db.sql_del_data(callback)
    await callback.message.answer('Данные удалены')


# button P2P
async def peer_to_peer(message: types.Message):
    await message.answer("🔁 *Peer-to-peer обмен*\nПокупайте и продавайте VST удобным способом.\n\n"
                         "Выберите направление для просмотра объявлений на покупку и продажу VST.",
                         parse_mode="Markdown", reply_markup=urlkb_3)


# inline button 'buy'
async def buy_vst(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Купить VST \n\nЗдесь вы можете посмотреть список всех "
                                  "активных объявлений или создать свое", reply_markup=urlkb_4)


# inline button 'sell'
async def sell_vst(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Продать VST \n\nЗдесь вы можете посмотреть список всех "
                                  "активных объявлений или создать свое", reply_markup=urlkb_5)


# show all user's orders
async def read_own_orders(callback: types.CallbackQuery):
    await bot_db.sql_read_own_orders(callback)


# We catch clicking on the inline button with our own order
async def push_own_order_button(callback: types.CallbackQuery):
    await bot_db.order_push_button(callback)


def register_client_handler(dp: Dispatcher):
    dp.register_message_handler(message_start, commands=['start'])
    dp.register_message_handler(message_wallet, commands=['Кошелек'])
    dp.register_callback_query_handler(cm_start, state=None, text=['add_data'])
    dp.register_message_handler(load_name, state=FSMUserInfo.name)
    dp.register_message_handler(load_vst, state=FSMUserInfo.vista_num)
    dp.register_message_handler(load_binance, state=FSMUserInfo.binance_id)
    dp.register_callback_query_handler(change_data, text=['change_data'])
    dp.register_callback_query_handler(del_data, text=['del_data'])
    dp.register_message_handler(peer_to_peer, commands=['P2P_Обмен'])
    dp.register_callback_query_handler(buy_vst, text=['buy_vst'])
    dp.register_callback_query_handler(sell_vst, text=['sell_vst'])
    dp.register_callback_query_handler(add_buy_order, state=None, text=['add_buy_order'])
    dp.register_message_handler(add_usdt_amount, state=FSMAddUserOrder.usdt_amount)
    dp.register_message_handler(add_vst_amount, state=FSMAddUserOrder.vst_amount)
    dp.register_callback_query_handler(read_own_orders, text=['my_orders'])
    dp.register_callback_query_handler(push_own_order_button, lambda call: True)
