import types

import psycopg2
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dispatcher import bot, dp

from bot.keyboard import client_kb


# launch database
def sql_start():
    global conn, cur
    conn = psycopg2.connect(dbname="exchange_bot", user="postgres", password="ыефкщ4лшт")
    cur = conn.cursor()
    if conn:
        print('DataBase connected')

    conn.commit()


# add user info in database
async def sql_add_data(state):
    async with state.proxy() as data:
        cur.execute("""
                    INSERT 
                    INTO user_data 
                    VALUES (%s, %s, %s, %s)
                    """, tuple(data.values()))
        conn.commit()


# push wallet button (show user info to user)
async def sql_read_data(message):
    cur.execute("""
                SELECT * 
                FROM user_data 
                WHERE user_id = %s
                """, (message.from_user.id,))
    for ret in cur.fetchall():
        return ret
    conn.commit()


# delete user info
async def sql_del_data(message):
    cur.execute("""
                DELETE FROM user_data
                WHERE user_id = %s
                """, (message.from_user.id,))
    conn.commit()


# check if user info in database
async def is_user_id_in_data(message):
    cur.execute("""
                SELECT EXISTS (SELECT * from user_data WHERE user_id = %s)
                """, (message.from_user.id,))
    for ret in cur.fetchone():
        return ret
    conn.commit()


# add buy order to database
async def sql_add_order(state):
    async with state.proxy() as data:
        cur.execute("""
                    INSERT INTO orders_data
                    VALUES (%s, %s, %s, %s, %s)
                    """, tuple(data.values()))
        conn.commit()


# read all orders from user
async def sql_read_own_orders(message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    cur.execute("""
                SELECT *
                FROM orders_data
                WHERE user_id = %s
                """, (message.from_user.id,))
    data = cur.fetchall()
    await bot.send_message(message.from_user.id, 'Список ваших заявок: ',
                           reply_markup=client_kb.gen_inline_kb_my_orders(data))
    conn.commit()


# push on user's order button
async def order_push_button(callback):
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    cur.execute("""
                SELECT *
                FROM orders_data
                WHERE order_id = %s
                """, (callback.data[4:],))
    order_info = cur.fetchone()

    await bot.send_message(callback.from_user.id, f'Заявка №{order_info[0]} на покупку {order_info[4]} VST '
                                                  f'за {order_info[3]} USDT', reply_markup=InlineKeyboardMarkup().
                           add(InlineKeyboardButton(f'Удалить заявку', callback_data=f'sdel{order_info[0]}')))
    conn.commit()


# delete user's order button
async def delete_order_button(callback):
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    cur.execute("""
                DELETE
                FROM orders_data
                WHERE order_id = %s
                """, (callback.data[4:],))
    await bot.send_message(callback.from_user.id, f'Заявка №{callback.data[4:]} успешна отменена')

    conn.commit()


# check all orders
async def all_orders(callback, x):
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    cur.execute("""
                SELECT *
                FROM orders_data
                WHERE buy_or_sell = %s and user_id <> %s
                """, (x, callback.from_user.id))
    data = cur.fetchall()
    await bot.send_message(callback.from_user.id, 'Список заявок: ',
                           reply_markup=client_kb.gen_inline_kb_all_orders(data))
    conn.commit()


# order inline button
async def one_order_btn(callback):
    dict_orders = {1: 'Покупка', 0: 'Продажа'}
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    cur.execute("""
                    SELECT *
                    FROM orders_data
                    WHERE order_id = %s
                    """, (callback.data[6:],))
    order_info = cur.fetchone()

    await bot.send_message(callback.from_user.id, f'Заявка №{order_info[0]} на {dict_orders[order_info[2]]} '
                                                  f'{order_info[4]} VST '
                                                  f'за {order_info[3]} USDT', reply_markup=InlineKeyboardMarkup().
                           add(InlineKeyboardButton(f'Принять заявку', callback_data=f'order{order_info[0]}')))
    conn.commit()


async def sql_add_user_id2(callback):
    cur.execute("""
                UPDATE orders_data
                SET user_id2 = %s
                WHERE order_id = %s
                """, (callback.from_user.id, callback.data[5:]))
    conn.commit()
    cur.execute("""
                SELECT *
                FROM orders_data
                WHERE order_id = %s
                """, (callback.data[5:],))
    for ret in cur.fetchall():
        return ret[1]
    conn.commit()
