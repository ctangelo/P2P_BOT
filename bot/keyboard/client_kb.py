import math

from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup

from bot.database import bot_db
from bot.dispatcher import bot

exchange_button = KeyboardButton(text="🔁 P2P Обмен")
data_button = KeyboardButton(text="💼 Кошелек")


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


def urlkb4(callback):
    urlkb_4 = InlineKeyboardMarkup(row_width=1)
    inline_add_buy_order_button = InlineKeyboardButton('🖋 Создать объявление', callback_data='add_buy_order')
    inline_see_sell_orders = InlineKeyboardButton('📈 Посмотреть объявления о покупке',
                                                  callback_data=f'all_orders/{0}/{callback.from_user.id}/{0}')
    inline_back_btn = InlineKeyboardButton('◀️ Назад', callback_data='back_to_menu')
    return urlkb_4.add(inline_add_buy_order_button, inline_see_sell_orders, inline_back_btn)


def urlkb5(callback):
    urlkb_5 = InlineKeyboardMarkup(row_width=1)
    inline_add_sell_order_button = InlineKeyboardButton('🖋 Создать объявление', callback_data='add_sell_order')
    inline_see_buy_orders = InlineKeyboardButton('📉 Посмотреть объявления на продажу',
                                                 callback_data=f'all_orders/{0}/{callback.from_user.id}/{1}')
    inline_back_btn = InlineKeyboardButton('◀️ Назад', callback_data='back_to_menu')
    return urlkb_5.add(inline_add_sell_order_button, inline_see_buy_orders, inline_back_btn)


def gen_inline_kb_my_orders(data):
    dict_orders = {1: 'Покупка', 0: 'Продажа'}
    urlkb_my_orders = InlineKeyboardMarkup(row_width=1)
    for i in data:
        urlkb_my_orders.add(InlineKeyboardButton(f'{dict_orders[i[2]]} {i[4]} VST за {i[3]} USDT',
                                                 callback_data=f'sbuy {i[0]}'))
    return urlkb_my_orders


async def orders_swipe_fp(remover, user_id, buy_or_sell):
    get_categories = await bot_db.sql_all_orders(user_id, buy_or_sell)
    keyboard = InlineKeyboardMarkup()
    dict_orders = {0: 'Покупка', 1: 'Продажа'}
    if remover >= len(get_categories):
        remover -= 5

    elif not get_categories:
        await bot.send_message(user_id, 'Пусто', reply_markup=InlineKeyboardButton('Вернуться в меню', callback_data='back_to_menu'))

    else:
        for count, a in enumerate(range(remover, len(get_categories))):
            if count < 5:
                keyboard.add(InlineKeyboardButton(f'{dict_orders[buy_or_sell]} '
                                                  f'{get_categories[a][3]} VST за '
                                                  f'{get_categories[a][4]} USDT',
                                                  callback_data=f"select/{get_categories[a][0]}/{user_id}/{buy_or_sell}"))

    if len(get_categories) <= 5:
        keyboard.add(InlineKeyboardButton('Вернуться в меню', callback_data='back_to_menu'))

    elif len(get_categories) > 5 > remover:
        keyboard.add(
            InlineKeyboardButton(f"💎 1/{math.ceil(len(get_categories) / 5)} 💎", callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"all_orders/{remover + 5}/{user_id}/{buy_or_sell}"),
        ).add(InlineKeyboardButton('Вернуться в меню', callback_data='back_to_menu'))
    elif remover + 5 >= len(get_categories):
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"all_orders/{remover - 5}/{user_id}/{buy_or_sell}"),
            InlineKeyboardButton(f"💎 {str((remover + 5))}/{math.ceil(len(get_categories) / 5)} 💎",
                                 callback_data="..."),
        ).add(InlineKeyboardButton('Вернуться в меню', callback_data='back_to_menu'))
    else:
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"all_orders/{remover - 5}/{user_id}/{buy_or_sell}"),
            InlineKeyboardButton(f"💎 {str(remover + 5)[:-1]}/{math.ceil(len(get_categories) / 5)} 💎",
                                 callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"all_orders/{remover + 5}/{user_id}/{buy_or_sell}"),
        ).add(InlineKeyboardButton('Вернуться в меню', callback_data='back_to_menu'))

    return keyboard
