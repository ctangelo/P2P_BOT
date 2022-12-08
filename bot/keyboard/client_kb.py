from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup

exchange_button = KeyboardButton(text="/P2P_Обмен")
data_button = KeyboardButton(text="/Кошелек")


kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.row(exchange_button, data_button)


urlkb = InlineKeyboardMarkup(row_width=1)
inline_data_button = InlineKeyboardButton('Изменить данные', callback_data='change_data')
inline_del_data_button = InlineKeyboardButton('Удалить данные', callback_data='del_data')
urlkb.add(inline_data_button).add(inline_del_data_button)


urlkb_2 = InlineKeyboardMarkup(row_width=1)
inline_add_data_button = InlineKeyboardButton('Добавить данные', callback_data='add_data')
urlkb_2.add(inline_add_data_button)


urlkb_3 = InlineKeyboardMarkup(row_width=1)
inline_sell_vst_button = InlineKeyboardButton('📉 Продать VST', callback_data='sell_vst')
inline_buy_vst_button = InlineKeyboardButton('📈 Купить VST', callback_data='buy_vst')
inline_my_orders_button = InlineKeyboardButton('💼 Мои объявления', callback_data='my_orders')
urlkb_3.row(inline_sell_vst_button, inline_buy_vst_button)
urlkb_3.add(inline_my_orders_button)


urlkb_4 = InlineKeyboardMarkup(row_width=1)
inline_add_buy_order_button = InlineKeyboardButton('🖋 Создать объявление о покупке', callback_data='add_buy_order')
inline_see_sell_orders = InlineKeyboardButton('Посмотреть объявления на продажу', callback_data='check_sell_orders')
urlkb_4.row(inline_add_buy_order_button, inline_see_sell_orders)


urlkb_5 = InlineKeyboardMarkup(row_width=1)
inline_add_sell_order_button = InlineKeyboardButton('🖋 Создать объявление на продажу', callback_data='add_sell_order')
inline_see_buy_orders = InlineKeyboardButton('Посмотреть объявления на продажу', callback_data='check_sell_orders')
urlkb_5.row(inline_see_buy_orders, inline_add_sell_order_button)


def gen_inline_kb_my_orders(data):
    dict_orders = {1: 'Покупка', 2: 'Продажа'}
    urlkb_my_orders = InlineKeyboardMarkup(row_width=1)
    for i in data:
        urlkb_my_orders.add(InlineKeyboardButton(f'{dict_orders[2]} {i[4]} VST за {i[3]} USDT', callback_data=i[0]))
    return urlkb_my_orders


urlkb_del = InlineKeyboardMarkup(row_width=1)
inline_del_button = InlineKeyboardButton('Удалить', callback_data='delete_btn')
urlkb_del.add(inline_del_button)