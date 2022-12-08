import psycopg2
from dispatcher import bot, dp

from bot.keyboard import client_kb
from bot.keyboard.client_kb import urlkb, urlkb_2, urlkb_del


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
        cur.execute("INSERT INTO user_data VALUES (%s, %s, %s, %s)", tuple(data.values()))
        conn.commit()


# push wallet button (show user info to user)
async def sql_read_data(message):
    cur.execute("""
                SELECT * 
                FROM user_data 
                WHERE user_id = %s
                """, (message.from_user.id,))
    one_line = cur.fetchall()
    for ret in one_line:
        await bot.send_message(message.from_user.id, f'*Имя: {ret[1]}\n\nVST-счет: {ret[2]}\n\nBinanceID: {ret[-1]}*',
                               parse_mode="Markdown", reply_markup=urlkb)
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
        if ret:
            await sql_read_data(message)
        else:
            await message.answer("Вы не добавили данные", reply_markup=urlkb_2)
    conn.commit()


# add buy order to database
async def sql_add_buy_order(state):
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


# push on user's order button
async def order_push_button(callback):
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    cur.execute("""
                SELECT *
                FROM orders_data
                WHERE order_id = %s
                """, (callback.data, ))
    order_info = cur.fetchone()
    await bot.send_message(callback.from_user.id, f'Заявка №{order_info[0]} на покупку {order_info[4]} VST '
                                                  f'за {order_info[3]} USDT', reply_markup=urlkb_del)
