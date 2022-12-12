from aiogram import types, Dispatcher
from bot.keyboard import kb_client, client_kb
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import bot_db
import random
from dispatcher import bot

from bot.keyboard.client_kb import urlkb_3, urlkb_4, urlkb_5, urlkb_2, urlkb


# for add user info to database
class FSMUserInfo(StatesGroup):
    name = State()
    vista_num = State()
    binance_id = State()


# for add buy order to database
class FSMAddUserOrder(StatesGroup):
    vst_amount = State()
    usdt_amount = State()


# for add sell order to database
class FSMAddSellOrder(StatesGroup):
    vst_amount = State()
    usdt_amount = State()


async def message_start(message: types.Message):
    await message.answer('Привет! Я бот обменник! Чтоб узнать больше о функционале, нажми HELP',
                         reply_markup=kb_client)


# add sell order to database
async def add_sell_order(callback: types.CallbackQuery):
    await FSMAddSellOrder.vst_amount.set()
    await callback.message.answer('Сколько VST хотите продать?')


async def add_sell_vst_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order_id'] = random.randint(1000, 100000)
        data['user_id'] = message.from_user.id
        data['buy_or_sell'] = 0
        data['vst_amount'] = message.text
    await FSMAddSellOrder.next()
    await message.answer('Сколько USDT хотите получить?')


async def add_sell_usdt_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['usdt_amount'] = message.text
    await message.reply('ОРДЕР НА ПРОДАЖУ VST ДОБАВЛЕН')
    await bot_db.sql_add_order(state)
    await state.finish()


# add buy order to database
async def add_buy_order(callback: types.CallbackQuery):
    await FSMAddUserOrder.usdt_amount.set()
    await callback.message.answer('Сколько VST хотите купить?')


async def add_usdt_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order_id'] = random.randint(1000, 100000)
        data['user_id'] = message.from_user.id
        data['buy'] = 1
        data['vst_amount'] = message.text
    await FSMAddUserOrder.next()
    await message.answer('Сколько USDT у вас есть?')


async def add_vst_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['usdt_amount'] = message.text
    await message.reply('ОРДЕР НА ПОКУПКУ VST ДОБАВЛЕН')
    await bot_db.sql_add_order(state)
    await state.finish()


# show user info
async def message_wallet(message: types.Message):
    true_false = await bot_db.is_user_id_in_data(message)
    if true_false:
        data = await bot_db.sql_read_data(message)

        await bot.send_message(message.from_user.id, f'*Имя: {data[1]}\n\n'
                                                     f'VST-счет:{data[2]}\n\n'
                                                     f'BinanceID: {data[-1]}*',
                               parse_mode="Markdown", reply_markup=urlkb)
    else:
        await message.answer("Вы не добавили данные", reply_markup=urlkb_2)


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


# inline button delete order
async def del_button(callback: types.CallbackQuery):
    await bot_db.delete_order_button(callback)


# We catch clicking on the inline button with our own order
async def push_own_order_button(callback: types.CallbackQuery):
    await bot_db.order_push_button(callback)


# Check all orders buy/sell
async def check_all_orders(callback: types.CallbackQuery):
    if 'sell' in callback.data:
        await bot_db.all_orders(callback, 0)
    else:
        await bot_db.all_orders(callback, 1)


def register_client_handler(dp: Dispatcher):
    dp.register_message_handler(message_start, commands=['start'])
    dp.register_message_handler(message_wallet, lambda message: message.text.startswith('💼 Кошелек'))
    dp.register_callback_query_handler(cm_start, state=None, text=['add_data'])
    dp.register_message_handler(load_name, state=FSMUserInfo.name)
    dp.register_message_handler(load_vst, state=FSMUserInfo.vista_num)
    dp.register_message_handler(load_binance, state=FSMUserInfo.binance_id)
    dp.register_callback_query_handler(change_data, text=['change_data'])
    dp.register_callback_query_handler(del_data, text=['del_data'])
    dp.register_message_handler(peer_to_peer, lambda message: message.text.startswith('🔁 P2P Обмен'))
    dp.register_callback_query_handler(buy_vst, text=['buy_vst'])
    dp.register_callback_query_handler(sell_vst, text=['sell_vst'])
    dp.register_callback_query_handler(add_buy_order, state=None, text=['add_buy_order'])
    dp.register_message_handler(add_usdt_amount, state=FSMAddUserOrder.vst_amount)
    dp.register_message_handler(add_vst_amount, state=FSMAddUserOrder.usdt_amount)
    dp.register_callback_query_handler(read_own_orders, text=['my_orders'])
    dp.register_callback_query_handler(del_button, lambda x: x.data and x.data.startswith('sdel'))
    dp.register_callback_query_handler(add_sell_order, state=None, text=['add_sell_order'])
    dp.register_message_handler(add_sell_vst_amount, state=FSMAddSellOrder.vst_amount)
    dp.register_message_handler(add_sell_usdt_amount, state=FSMAddSellOrder.usdt_amount)
    dp.register_callback_query_handler(push_own_order_button, lambda x: x.data and x.data.startswith('sbuy'))
    dp.register_callback_query_handler(check_all_orders, lambda x: x.data and x.data.startswith('check_'))
