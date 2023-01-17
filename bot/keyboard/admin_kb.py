from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup


def admin_active_orders_kb(data):
    keyboard = InlineKeyboardMarkup()
    for i in data:
        keyboard.add(InlineKeyboardButton(f'{i[0]}',
                                          callback_data=f'admin/{i[0]}'))
        return keyboard

