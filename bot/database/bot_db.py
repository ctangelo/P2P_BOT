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


# count user's orders
async def sql_count_user_orders(callback):
    with conn:
        cur.execute("""
                    SELECT COUNT(user_id)
                    FROM orders_data
                    WHERE user_id = %s
                    """, (callback.from_user.id, ))
        return cur.fetchone()


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
                WHERE user_id = %s and garant_pay = false
                """, (message.from_user.id,))
    data = cur.fetchall()
    await bot.send_message(message.from_user.id, 'Список ваших заявок: ',
                           reply_markup=client_kb.gen_inline_kb_my_orders(data).add
                           (InlineKeyboardButton('◀️ Назад', callback_data='back_to_menu')))
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

    await bot.send_message(callback.from_user.id, f'Заявка №{order_info[0]} на покупку {order_info[3]} VST '
                                                  f'за {order_info[4]} USDT', reply_markup=InlineKeyboardMarkup().
                           add(InlineKeyboardButton(f'Удалить заявку', callback_data=f'sdel{order_info[0]}')).
                           add(InlineKeyboardButton('◀️ Назад', callback_data='my_orders')))
    conn.commit()


# delete user's order button
async def delete_order_button(callback):
    # await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    with conn:
        cur.execute("""
                    DELETE
                    FROM orders_data
                    WHERE order_id = %s
                    """, (callback.data[4:],))


# order inline button
async def one_order_btn(callback):
    with conn:
        cur.execute("""
                        SELECT *
                        FROM orders_data
                        WHERE order_id = %s
                        """, (callback,))
        return cur.fetchone()


async def sql_add_user_id2(callback):
    cur.execute("""
                UPDATE orders_data
                SET user_id2 = %s
                WHERE order_id = %s
                """, (callback.from_user.id, callback.data[6:]))
    conn.commit()
    cur.execute("""
                SELECT *
                FROM orders_data
                WHERE order_id = %s
                """, (callback.data[6:],))
    for ret in cur.fetchall():
        return ret[1]
    conn.commit()


async def sql_change_data_1(callback):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET ready_user_id = True
                    WHERE order_id = %s
                    """, (callback.data[11:], ))


async def sql_change_data_2(callback):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET pay_from_user_id = True
                    WHERE order_id = %s
                    """, (callback, ))


async def sql_change_data_3(callback):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET pay_from_user_id2 = True
                    WHERE order_id = %s
                    """, (callback, ))


async def sql_check_pay(callback):
    with conn:
        cur.execute("""
                    SELECT pay_from_user_id, pay_from_user_id2
                    FROM orders_data
                    WHERE order_id = %s
                    """, (callback, ))
        return cur.fetchone()


async def sql_delete_order(callback):
    with conn:
        cur.execute("""
                    DELETE
                    FROM orders_data
                    WHERE order_id = %s
                    """, (callback, ))


# order data
async def sql_order_data(callback):
    # await bot.answer_callback_query(callback.id)
    with conn:
        cur.execute("""
                        SELECT *
                        FROM orders_data
                        WHERE order_id = %s
                        """, (callback, ))
        return cur.fetchone()


async def sql_cancel_order(callback):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET user_id2 = NULL
                    WHERE order_id = %s
                    """, (callback.data[12:], ))


async def sql_find_user_id2(callback):
    with conn:
        cur.execute("""
                    SELECT *
                    FROM orders_data
                    WHERE order_id = %s and user_id = %s
                    """, (callback.data[12:], callback.from_user.id))
        return cur.fetchone()


async def sql_user_data(callback):
    with conn:
        cur.execute("""
                    SELECT *
                    FROM user_data
                    WHERE user_id = %s
                    """, (callback, ))
        return cur.fetchone()


async def sql_set_garant_pay(callback):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET garant_pay = true
                    WHERE order_id = %s
                    """, (callback, ))


async def sql_all_orders(callback, x):
    with conn:
        cur.execute("""
                    SELECT *
                    FROM orders_data
                    WHERE buy_or_sell = %s and user_id <> %s and ready_user_id = false
                    """, (x, callback))
        return cur.fetchall()
