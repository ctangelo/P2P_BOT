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
        with conn:
            cur.execute("""
                        INSERT 
                        INTO user_data 
                        VALUES (%s, %s, %s, %s)
                        """, tuple(data.values()))


# push wallet button (show user info to user)
async def sql_user_data(user_id):
    with conn:
        cur.execute("""
                    SELECT * 
                    FROM user_data 
                    WHERE user_id = %s
                    """, (user_id,))
        return cur.fetchone()


# delete user info
async def sql_del_data(user_id):
    with conn:
        cur.execute("""
                    DELETE FROM user_data
                    WHERE user_id = %s
                    """, (user_id,))


# check if user info in database
async def sql_is_user_in_data(user_id):
    with conn:
        cur.execute("""
                    SELECT EXISTS 
                    (SELECT * 
                    FROM user_data 
                    WHERE user_id = %s)
                    """, (user_id,))
        return cur.fetchone()


# count user's orders
async def sql_count_user_orders(user_id):
    with conn:
        cur.execute("""
                    SELECT COUNT(user_id)
                    FROM orders_data
                    WHERE user_id = %s and garant_pay = false
                    """, (user_id, ))
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
async def sql_read_own_orders(user_id):
    with conn:
        cur.execute("""
                    SELECT *
                    FROM orders_data
                    WHERE user_id = %s and garant_pay = false
                    """, (user_id,))
        return cur.fetchall()


# push on user's order button
async def sql_one_order(order_id):
    with conn:
        cur.execute("""
                    SELECT *
                    FROM orders_data
                    WHERE order_id = %s
                    """, (order_id,))
        return cur.fetchone()


# delete user's order button
async def sql_delete_order_button(order_id):
    with conn:
        cur.execute("""
                    DELETE
                    FROM orders_data
                    WHERE order_id = %s
                    """, (order_id,))


async def sql_add_user_id2(callback):
    with conn:
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
        return cur.fetchone()


async def sql_upd_ready_user(order_id):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET ready_user_id = True
                    WHERE order_id = %s
                    """, (order_id, ))


async def sql_upd_pay_from_user(order_id):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET pay_from_user_id = True
                    WHERE order_id = %s
                    """, (order_id, ))


async def sql_upd_pay_from_user2(order_id):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET pay_from_user_id2 = True
                    WHERE order_id = %s
                    """, (order_id, ))


async def sql_check_pay(order_id):
    with conn:
        cur.execute("""
                    SELECT pay_from_user_id, pay_from_user_id2
                    FROM orders_data
                    WHERE order_id = %s
                    """, (order_id, ))
        return cur.fetchone()


async def sql_delete_order(order_id):
    with conn:
        cur.execute("""
                    DELETE
                    FROM orders_data
                    WHERE order_id = %s
                    """, (order_id, ))


# order data
async def sql_order_data(order_id):
    with conn:
        cur.execute("""
                        SELECT *
                        FROM orders_data
                        WHERE order_id = %s
                        """, (order_id, ))
        return cur.fetchone()


async def sql_cancel_order(order_id):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET user_id2 = NULL
                    WHERE order_id = %s
                    """, (order_id, ))


async def sql_find_user_id2(order_id, user_id):
    with conn:
        cur.execute("""
                    SELECT *
                    FROM orders_data
                    WHERE order_id = %s and user_id = %s
                    """, (order_id, user_id))
        return cur.fetchone()


async def sql_set_garant_pay(callback):
    with conn:
        cur.execute("""
                    UPDATE orders_data
                    SET garant_pay = true
                    WHERE order_id = %s
                    """, (callback, ))


async def sql_all_orders(user_id, buy_or_sell):
    with conn:
        cur.execute("""
                    SELECT *
                    FROM orders_data
                    WHERE buy_or_sell = %s and user_id <> %s and ready_user_id = false
                    """, (buy_or_sell, user_id))
        return cur.fetchall()


async def sql_admin_active_orders():
    with conn:
        cur.execute("""
                    SELECT *
                    FROM orders_data
                    WHERE user_id2 IS NOT NULL and ready_user_id = true and pay_from_user_id = true and 
                    pay_from_user_id2 = true and garant_pay = false
                    """, )
        return cur.fetchall()


async def sql_all_users():
    with conn:
        cur.execute("""
                    SELECT user_id
                    FROM user_data
                    WHERE user_id <> 245955512
                    """)
        return cur.fetchall()
