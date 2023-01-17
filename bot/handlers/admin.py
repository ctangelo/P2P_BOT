from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.database import bot_db
from bot.dispatcher import dp, bot
from bot.keyboard import admin_kb

ADMIN = 245955512


class FSMMessageToUsers(StatesGroup):
    message = State()


# @dp.message_handler(commands='Orders')
async def admin_active_orders(message: types.Message):
    if message.from_user.id == ADMIN:
        data = await bot_db.sql_admin_active_orders()
        await message.answer("Список заявок, ожидающих оплаты: ", reply_markup=admin_kb.admin_active_orders_kb(data))


# @dp.callback_query_handlers(lambda x: x.data.startswith('admin/'))
async def active_order(callback: types.CallbackQuery):
    order_id = callback.data.split('/')[1]
    order_data = await bot_db.sql_order_data(order_id)

    user_data = [order_data[1], order_data[5]]

    if order_data[2] == 1:
        requisites_1 = await bot_db.sql_user_data(user_data[0])
        requisites_2 = await bot_db.sql_user_data(user_data[1])
        await bot.send_message(245955512,
                               f'Оба пользователя подтвердили оплату\nПереведите {order_data[3]} VST на счет: '
                               f'{requisites_1[2]}\nПереведите {order_data[4]} USDT на счет: '
                               f'{requisites_2[3]}', reply_markup=InlineKeyboardMarkup().
                               add(InlineKeyboardButton(f'Перевел', callback_data=f'pay_order/{order_data[0]}/3')))

    elif order_data[2] == 0:
        requisites_1 = await bot_db.sql_user_data(user_data[0])
        requisites_2 = await bot_db.sql_user_data(user_data[1])
        await bot.send_message(245955512,
                               f'Оба пользователя подтвердили оплату\nПереведите {order_data[4]} USDT на счет: '
                               f'{requisites_1[3]}\nПереведите {order_data[3]} VST на счет: '
                               f'{requisites_2[2]}', reply_markup=InlineKeyboardMarkup().
                               add(InlineKeyboardButton(f'Перевел', callback_data=f'pay_order/{order_data[0]}/3')))


# @dp.message_handlers(state=None, commands=['text'])
async def text_to_all_users(message: types.Message):
    await FSMMessageToUsers.message.set()
    await message.answer('Что вы хотите написать?')


# @dp.message_handlers(state=FSMMessageToUsers.message)
async def add_message(message: types.Message, state: FSMContext):
    user_id = await bot_db.sql_all_users()
    async with state.proxy() as data:
        data['message'] = message.text
        for i in user_id:
            await message.answer(i[0])
            await bot.send_message(i[0], data['message'])
        await state.finish()


def register_admin_handler(dp: Dispatcher):
    dp.register_message_handler(admin_active_orders, commands=['Orders'])
    dp.register_callback_query_handler(active_order, lambda x: x.data.startswith('admin/'))
    dp.register_message_handler(text_to_all_users, state=None, commands=['text'])
    dp.register_message_handler(add_message, state=FSMMessageToUsers.message)
