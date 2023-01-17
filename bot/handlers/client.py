from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboard import kb_client, client_kb
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import bot_db
import random
from dispatcher import bot

from bot.keyboard.client_kb import urlkb_3, urlkb_2, urlkb, urlkb4, urlkb5


# for add user info to database
class FSMUserInfo(StatesGroup):
    name = State()
    vista_num = State()
    binance_id = State()


# for add buy order to database
class FSMAddBuyOrder(StatesGroup):
    vst_amount = State()
    usdt_amount = State()


# for add sell order to database
class FSMAddSellOrder(StatesGroup):
    vst_amount = State()
    usdt_amount = State()


# dp.message_handlers(commands=['start'])
async def message_start(message: types.Message):
    await message.answer('Привет! Я бот обменник, помогу вам обменять VST/USDT\nПеред тем как приступить к обмену - '
                         'добавь свои кошельки.',
                         reply_markup=kb_client)


# add sell order to database
# dp.callback_query_handlers(state=None, text=['add_sell_order'])
async def add_sell_order(callback: types.CallbackQuery):
    x = await bot_db.sql_count_user_orders(callback.from_user.id)
    if x[0] < 5:
        await FSMAddSellOrder.vst_amount.set()
        await callback.message.answer('Сколько VST хотите продать?')
    else:
        await callback.message.delete()
        await callback.message.answer('Извините, но вы можете добавить максимум 5 заявок на покупку/продажу. '
                                      'Удалить заявку вы можете в разделе "Мои объявления".',
                                      reply_markup=InlineKeyboardMarkup().add
                                      (InlineKeyboardButton(f'Мои объявления', callback_data='my_orders')))


# dp.message_handlers(state=FSMAddSellOrder.vst_amount)
async def add_sell_vst_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order_id'] = random.randint(1000, 100000)
        data['user_id'] = message.from_user.id
        data['buy_or_sell'] = 0
        data['vst_amount'] = message.text
    await FSMAddSellOrder.next()
    await message.answer('Сколько USDT хотите получить?')


# dp.message_handlers(state=FSMAddSellOrder.usdt_amount)
async def add_sell_usdt_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['usdt_amount'] = message.text
    await message.reply(f'Ваша заявка на продажу {data["vst_amount"]} VST принята')
    await bot_db.sql_add_order(state)
    await state.finish()
    await peer_to_peer(message)


# add buy order to database
# dp.callback_query_handlers(state=None, text=['add_buy_order'])
async def add_buy_order(callback: types.CallbackQuery):
    x = await bot_db.sql_count_user_orders(callback.from_user.id)
    if x[0] < 5:
        await FSMAddBuyOrder.vst_amount.set()
        await callback.message.answer('Сколько VST хотите купить?')
    else:
        await callback.message.delete()
        await callback.message.answer('Извините, но вы можете добавить максимум 5 заявок на покупку/продажу. '
                                      'Удалить заявку вы можете в разделе "Мои объявления".',
                                      reply_markup=InlineKeyboardMarkup().add
                                      (InlineKeyboardButton(f'Мои объявления', callback_data='my_orders')))


# dp.message_handlers(state=FSMAddUserOrder.vst_amount)
async def add_usdt_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order_id'] = random.randint(1000, 100000)
        data['user_id'] = message.from_user.id
        data['buy'] = 1
        data['vst_amount'] = message.text
    await FSMAddBuyOrder.next()
    await message.answer(f'Покупка. {data["vst_amount"]} VST\nСколько USDT у вас есть?')


# dp.message_handlers(state=FSMAddUserOrder.usdt_amount)
async def add_vst_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['usdt_amount'] = message.text
    await message.reply(f'Ваша заявка на покупку {data["vst_amount"]} VST принята')
    await bot_db.sql_add_order(state)
    await state.finish()
    await peer_to_peer(message)


# show user info
# dp.message_handlers(lambda message: message.text.startswith('💼 Кошелек'))
async def message_wallet(message: types.Message):
    true_false = await bot_db.sql_is_user_in_data(message.from_user.id)
    if true_false[0]:
        data = await bot_db.sql_user_data(message.from_user.id)
        await message.answer(f'💼 Кошелек\n\n*Имя: {data[1]}\n\nVST-счет:{data[2]}\n\nBinanceID: {data[-1]}*',
                             parse_mode="Markdown", reply_markup=urlkb)
    else:
        await message.answer("💼 Кошелек\n\nВы не добавили данные", reply_markup=urlkb_2)


# add user info to database
# dp.callback_query_handlers(state=None, text=['add_data'])
async def cm_start(callback: types.CallbackQuery):
    await callback.message.delete()
    await FSMUserInfo.name.set()
    await callback.message.answer('Как вас зовут?', reply_markup=InlineKeyboardMarkup().
                                  add(InlineKeyboardButton(f'Отмена', callback_data=f'cancel_state')))


# dp.message_handlers(state=FSMUserInfo.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['name'] = message.text
    await FSMUserInfo.next()
    await message.reply('Введите ваш VST счет\nПример: VST-00000000-000000-000', reply_markup=InlineKeyboardMarkup().
                        add(InlineKeyboardButton(f'Отмена', callback_data=f'cancel_state')))


# dp.message_handlers(state=FSMUserInfo.vista_num)
async def load_vst(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['VST'] = message.text
    await FSMUserInfo.next()
    await message.reply('Введите ваш Binance ID:\nПример: 000000', reply_markup=InlineKeyboardMarkup().
                        add(InlineKeyboardButton(f'Отмена', callback_data=f'cancel_state')))


# dp.message_handlers(state=FSMUserInfo.binance_id)
async def load_binance(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['BinanceID'] = message.text
    await message.reply('Готово')
    await bot_db.sql_add_data(state)
    await state.finish()
    await message_wallet(message)


# cancel state
# @dp.callback_query_handlers(state="*", text='cancel_state')
async def cancel_state(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.message.answer('OK')


# inline button 'change' in wallet
# dp.callback_query_handlers(text=['change_data'])
async def change_data(callback: types.CallbackQuery):
    await bot_db.sql_del_data(callback.from_user.id)
    await cm_start(callback)


# inline button 'delete' in wallet
# dp.callback_query_handlers(text=['del_data'])
async def del_data(callback: types.CallbackQuery):
    await bot_db.sql_del_data(callback.from_user.id)
    await callback.message.answer('Данные удалены')


# button P2P
# dp.message_handlers(lambda message: message.text.startswith('🔁 P2P Обмен'))
async def peer_to_peer(message: types.Message):
    await message.answer("🔁 *Peer-to-peer обмен*\n\nПокупайте и продавайте VST удобным способом.\n\n"
                         "Выберите направление для просмотра объявлений на покупку и продажу VST.",
                         parse_mode="Markdown", reply_markup=urlkb_3)


# inline button 'buy'
# dp.callback_query_handlers(text=['buy_vst'])
async def buy_vst(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("🔁 *Peer-to-peer обмен*\n\nКупить VST \n\nЗдесь вы можете посмотреть список всех "
                                  "активных объявлений или создать свое", parse_mode="Markdown",
                                  reply_markup=urlkb4(callback))


# inline button 'sell'
# dp.callback_query_handlers(text=['sell_vst'])
async def sell_vst(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("🔁 *Peer-to-peer обмен*\n\nПродать VST \n\nЗдесь вы можете посмотреть список всех "
                                  "активных объявлений или создать свое", parse_mode="Markdown",
                                  reply_markup=urlkb5(callback))


# show all user's orders
# dp.callback_query_handler(read_own_orders, text=['my_orders'])
async def read_own_orders(callback: types.CallbackQuery):
    data = await bot_db.sql_read_own_orders(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer('Список ваших заявок: ', reply_markup=client_kb.gen_inline_kb_my_orders(data).
                                  add(InlineKeyboardButton('◀️ Назад', callback_data='back_to_menu')))


# inline button delete order
# dp.callback_query_handlers(lambda x: x.data and x.data.startswith('sdel/'))
async def del_button(callback: types.CallbackQuery):
    await bot_db.sql_delete_order_button(callback.data.split('/')[1])
    await callback.message.answer(f'Заявка №{callback.data.split("/")[1]} успешна отменена')
    await read_own_orders(callback)


# user's orders
# dp.callback_query_handlers(lambda x: x.data and x.data.startswith('sbuy/'))
async def push_own_order_button(callback: types.CallbackQuery):
    await callback.message.delete()
    order_info = await bot_db.sql_one_order(callback.data.split("/")[1])
    await callback.message.answer(f'Заявка №{order_info[0]} на покупку {order_info[3]} VST за {order_info[4]} USDT',
                                  reply_markup=InlineKeyboardMarkup().
                                  add(InlineKeyboardButton(f'Удалить заявку', callback_data=f'sdel/{order_info[0]}')).
                                  add(InlineKeyboardButton('◀️ Назад', callback_data='my_orders')))


# all orders (max 5 orders on page)
# @dp.callback_query_handlers(text_startswith="check_")
async def all_orders_pages(callback: types.CallbackQuery):
    dict_orders = {1: 'покупку', 0: 'продажу'}
    data = callback.data.split(sep='/')
    remover = int(data[1])
    user_id = int(data[2])
    buy_or_sell = int(data[-1])
    await callback.message.edit_text(f'🔁 *Peer-to-peer обмен*\n\nЗдесь отображен список всех доступных объявлений на '
                                     f'{dict_orders[buy_or_sell]} VST.\n\nВыберите подходящее объявление и откройте '
                                     f'сделку.',
                                     parse_mode="Markdown",
                                     reply_markup=await client_kb.orders_swipe_fp(remover, user_id, buy_or_sell))


# Approve order to buy/sell
# dp.callback_query_handlers(lambda x: x.data and x.data.startswith('select'))
async def select_order(callback: types.CallbackQuery):
    await callback.message.delete()
    dict_orders = {1: 'продажу', 0: 'покупку'}

    order_info = await bot_db.sql_one_order(callback.data.split('/')[1])
    if order_info[2] == 0:
        await bot.send_message(callback.from_user.id, f'Заявка №{order_info[0]} на {dict_orders[order_info[2]]} '
                                                      f'{order_info[3]} VST '
                                                      f'за {order_info[4]} USDT', reply_markup=InlineKeyboardMarkup().
                               add(InlineKeyboardButton(f'Принять заявку', callback_data=f'order1{order_info[0]}')).
                               add(InlineKeyboardButton('Назад',
                                                        callback_data=f'all_orders/{0}/{callback.from_user.id}/{0}')))

    elif order_info[2] == 1:
        await bot.send_message(callback.from_user.id, f'Заявка №{order_info[0]} на {dict_orders[order_info[2]]} '
                                                      f'{order_info[3]} VST '
                                                      f'за {order_info[4]} USDT', reply_markup=InlineKeyboardMarkup().
                               add(InlineKeyboardButton(f'Принять заявку', callback_data=f'order1{order_info[0]}')).
                               add(InlineKeyboardButton('Назад',
                                                        callback_data=f'all_orders/{0}/{callback.from_user.id}/{1}')))


# waiting approve from other user
# dp.callback_query_handlers(lambda x: x.data and x.data.startswith('order1'))
async def approve_order(callback: types.CallbackQuery):
    await callback.message.delete()
    # проверка есть ли у него другие активные заявки
    await callback.message.answer('Ожидайте ответа от второго юзера')
    user_id = await bot_db.sql_add_user_id2(callback)

    await bot.send_message(user_id, f'Вашу заявку №{callback.data[6:]} выбрали, готовы приступить к сделке?',
                           reply_markup=InlineKeyboardMarkup().
                           add(InlineKeyboardButton(f'Готов', callback_data=f'order_ready/{callback.data[6:]}'),
                               (InlineKeyboardButton(f'Отмена', callback_data=f'cancel_order/{callback.data[6:]}'))))


# dp.callback_query_handlers(lambda x: x.data and x.data.startswith('cancel_order/'))
async def cancel_order(callback: types.CallbackQuery):
    await callback.message.delete()
    data = await bot_db.sql_find_user_id2(callback.data.split('/')[1], callback.message.from_user.id)
    await bot.send_message(data[5], 'Пользователь отменил заявку, попробуйте выбрать другую')
    await bot_db.sql_cancel_order(callback.data.split('/')[1])
    await callback.message.answer('Вы отменили заявку, хотите ее удалить?', reply_markup=InlineKeyboardMarkup().
                                  add(InlineKeyboardButton(f'Да', callback_data=f'sdel{callback.data.split("/")[1]}'),
                                      (InlineKeyboardButton(f'Нет', callback_data=f'back_to_menu'))))


# dp.callback_query_handlers(lambda x: x.data and x.data.startswith('back_to_menu'))
async def go_to_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("🔁 *Peer-to-peer обмен*\n\nПокупайте и продавайте VST удобным способом.\n\n"
                                  "Выберите направление для просмотра объявлений на покупку и продажу VST.",
                                  parse_mode="Markdown", reply_markup=urlkb_3)


# dp.callback_query_handlers(lambda x: x.data and x.data.startswith('order_ready'))
async def order_ready(callback: types.CallbackQuery):
    order_id = callback.data.split('/')[1]
    await callback.message.delete()
    await bot_db.sql_upd_ready_user(order_id)
    data = await bot_db.sql_order_data(order_id)
    if data[2] == 1:
        await callback.message.answer(f'Переводите {data[3]} USDT на\nTestBinanceID',
                                      reply_markup=InlineKeyboardMarkup().
                                      add(InlineKeyboardButton(f'Перевел',
                                                               callback_data=f'pay_order/{callback.data.split("/")[1]}/'
                                                                             f'{callback.from_user.id}/{1}')))
        await bot.send_message(data[5], f'Переводите {data[4]} VST на\nTestVST', reply_markup=InlineKeyboardMarkup().
                               add(InlineKeyboardButton(f'Перевел', callback_data=
                                                        f'pay_order/{callback.data.split("/")[1]}/{data[5]}/{2}')))
    else:
        await callback.message.answer(f'Переводите {data[3]} VST на\nTestVST', reply_markup=InlineKeyboardMarkup().
                                      add(
            InlineKeyboardButton(f'Перевел', callback_data=f'pay_order/{callback.data.split("/")[1]}/'
                                                           f'{callback.from_user.id}/{1}')))
        await bot.send_message(data[5], f'Переводите {data[4]} USDT на\nTestBinanceID',
                               reply_markup=InlineKeyboardMarkup().
                               add(InlineKeyboardButton(f'Перевел', callback_data=f'pay_order/{callback.data.split("/")[1]}/'
                                                                                  f'{data[5]}/{2}')))


# dp.callback_query_handlers(lambda x: x.data and x.data.startswith('pay_order/'))
async def check_pay(callback: types.CallbackQuery):
    await callback.message.delete()
    data = callback.data.split(sep='/')
    if data[-1] == '2':
        await bot_db.sql_upd_pay_from_user(data[1])

    elif data[-1] == '1':
        await bot_db.sql_upd_pay_from_user2(data[1])

    check = await bot_db.sql_check_pay(data[1])

    if check[0] and check[1]:

        user_data = []
        order_data = await bot_db.sql_order_data(data[1])
        user_data.append(order_data[1])
        user_data.append(order_data[5])

        if data[-1] == '3':
            await bot.send_message(order_data[1], 'Перевод выполнен')
            await bot.send_message(order_data[5], 'Перевод выполнен')
            await bot_db.sql_set_garant_pay(data[1])
            # await bot_db.sql_delete_order(data[1])

        else:
            await bot.send_message(order_data[1], 'Ожидайте перевод от Гаранта, это займет не больше 5 минут')
            await bot.send_message(order_data[5], 'Ожидайте перевод от Гаранта, это займет не больше 5 минут')

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

    else:
        await callback.message.answer('Ожидаем оплату от второго пользователя')


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
    dp.register_message_handler(add_usdt_amount, state=FSMAddBuyOrder.vst_amount)
    dp.register_message_handler(add_vst_amount, state=FSMAddBuyOrder.usdt_amount)
    dp.register_callback_query_handler(read_own_orders, text=['my_orders'])
    dp.register_callback_query_handler(del_button, lambda x: x.data and x.data.startswith('sdel'))
    dp.register_callback_query_handler(add_sell_order, state=None, text=['add_sell_order'])
    dp.register_message_handler(add_sell_vst_amount, state=FSMAddSellOrder.vst_amount)
    dp.register_message_handler(add_sell_usdt_amount, state=FSMAddSellOrder.usdt_amount)
    dp.register_callback_query_handler(push_own_order_button, lambda x: x.data and x.data.startswith('sbuy'))
    dp.register_callback_query_handler(all_orders_pages, lambda x: x.data and x.data.startswith('all_orders/'))
    dp.register_callback_query_handler(select_order, lambda x: x.data and x.data.startswith('select'))
    dp.register_callback_query_handler(approve_order, lambda x: x.data and x.data.startswith('order1'))
    dp.register_callback_query_handler(check_pay, lambda x: x.data and x.data.startswith('pay_order/'))
    dp.register_callback_query_handler(cancel_order, lambda x: x.data and x.data.startswith('cancel_order'))
    dp.register_callback_query_handler(go_to_menu, lambda x: x.data and x.data.startswith('back_to_menu'))
    dp.register_callback_query_handler(order_ready, lambda x: x.data and x.data.startswith('order_ready'))
    dp.register_callback_query_handler(cancel_state, state="*", text=['cancel_state'])
