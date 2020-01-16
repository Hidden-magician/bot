import asyncio
import io
import logging
import threading
import time
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputMediaDocument, KeyboardButton, ReplyKeyboardMarkup
from urllib.request import urlopen
import json
import sqlite3
#--------------------Настройки бота-------------------------

# Ваш токен от BotFather
TOKEN = '850219369:AAEiyhnQ_Yc4iJXm-4z1kmRfeNAqYZrfupQ'

# Логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Ваш айди аккаунта администратора и айди сообщения где хранится файл с данными
admin_id = 851789066
config_id = 1541

conn = sqlite3.connect(":memory:")  # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()

s = ['753951460', '789321461', '984532642', '795831253', '586425844', '880055535', '290319999']


async def em_all(eml, pers):
    f = open('users/id_list.txt', 'r')
    st = '404 not found'
    if pers.setdefault('Status') == 'офицер':
        st = 'Приказ отдал '
    elif pers.setdefault('Status') == 'создатель':
        st = 'Сообщение отправил '
    for line in f:
        if int(line) != pers.setdefault('id'):
            try:
                bot.send_message(int(line), eml + '\nP.S\n ' + st + str(pers.setdefault('Obr')) + ' ' +
                                 str(pers.setdefault('Sename')) + '!')
            except:
                print(line)


def check_Code(kod):
    for line in s:
        print(line[0:8])
        if kod == line[0:8]:
            if line[8] == '0':
                return 'офицер'
            elif line[8] == '1':
                return 'старшина'
            elif line[8] == '2':
                return 'канцеляр'
            elif line[8] == '3':
                return 'замок'
            elif line[8] == '4':
                return 'комод'
            elif line[8] == '5':
                return 'курсант'
            elif line[8] == '9':
                return 'создатель'
    return 'error'


async def check_correct(message):
    try:
        sql = "SELECT * FROM users where id={}".format(message.chat.id)
        cursor.execute(sql)
        data = cursor.fetchone()  # or use fetchone()
    except Exception:
        data = await get_data()
        cursor.execute("CREATE TABLE users (id INTEGER , name TEXT, sename TEXT, status TEXT, point INTEGER,"
                       " groups INTEGER, kurs INTEGER, kod INTEGER, obr TEXT)")
        cursor.executemany("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)", data)
        conn.commit()
        sql = "SELECT * FROM users where id={}".format(message.chat.id)
        cursor.execute(sql)
        data = cursor.fetchone()  # or use fetchone()

    sql = "SELECT * FROM users where id"
    cursor.execute(sql)
    pers = cursor.fetchone()  # or use fetchone()
    rating = 'Необходимо ввести: '
    if pers[2] is None:
        rating = rating + 'фамилию, '
    if pers[5] is None:
        rating = rating + 'группу, '
    if pers[6] is None:
        rating = rating + 'курс, '
    if pers[8] is None:
        rating = rating + 'звание, '
    if pers[3] is None:
        rating = rating + 'код доступа, '
    if rating != 'Необходимо ввести: ':
        rating += 'данные подаются в формате: ключ-значение. Пример: код-78541369, фамилия-Иванов.' \
                 ' Каждую ' \
                 'пару отправлять в отдельном сообщении.'
        await bot.send_message(message.from_user.id, rating)


def create_pers(message):
    s = message.text[6:].rsplit(sep=',')
    print(s)
    pers = dict(id=message.from_user.id, Name=s[2], Sename=s[1], Status=check_Code(s[4]), point='1', Groups=s[3],
                Kod=0, obr=s[5])
    with open("users/user_" + str(message.from_user.id) + ".json", "w", encoding="utf-8") as fh:
        fh.write(json.dumps(pers))
        fh.close()
    f = open('users/id_list.txt', 'a')
    f.write('\n' + str(message.from_user.id))
    f.close()
# осталось дохуя! надо сделать: отчет о прочитаном, вывод зарегестрированных, защита от спама, подпправить рассылку


def check_Stat(persSt):
    if persSt == 'старшина' or persSt == 'создатель' or persSt == 'офицер' or persSt == 'канцеляр':
        return True
    return False


def check_json(us_id):
    if os.path.exists("users/user_" + str(us_id) + ".json"):
        return True
    return False


def updateJson(lip, us_id):
    with open("users/user_" + str(us_id) + ".json", "w", encoding="utf-8") as fh:
        fh.write(json.dumps(lip))
        fh.close()


def check_id_list(us_id):
    f = open('users/id_list.txt', 'r')
    for line in f:
        print(str(us_id) + ' ' + str(line))
        if int(line) == int(us_id):
            f.close()
            return False

    f.close()
    return True


async def get_user(us_id):
    with open("users/user_" + str(us_id) + ".json", "r", encoding="utf-8") as fh:
        data = json.load(fh)
        fh.close()
        return data


async def log(message):
    f = open('text.txt', 'a')
    f.write("<!------!>" + '\n')
    print("<!------!>")
    from datetime import datetime
    valma = str(datetime.today())
    f.write(valma + ' ')
    print(datetime.now())
    f.write("Сообщение от {0} {1} (id = {2}) \n {3} \n".format(message.from_user.first_name,
                                                               message.from_user.last_name,
                                                               str(message.from_user.id), message.text))
    print("Сообщение от {0} {1} (id = {2}) \n {3}".format(message.from_user.first_name,
                                                          message.from_user.last_name,
                                                          str(message.from_user.id), message.text))
    f.close()


# #--------------------Получение данных-------------------------
async def get_data():
    to = time.time()
    # Пересылаем сообщение в данными от админа к админу
    forward_data = await bot.forward_message(admin_id, admin_id, config_id)

    # Получаем путь к файлу, который переслали
    file_data = await bot.get_file(forward_data.document.file_id)

    # Получаем файл по url
    file_url_data = bot.get_file_url(file_data.file_path)

    # Считываем данные с файла
    json_file= urlopen(file_url_data).read()
    print('Время получения бекапа :=' + str(time.time() - to))
    # Переводим данные из json в словарь и возвращаем
    return json.loads(json_file)


#--------------------Сохранение данных-------------------------
async def save_data():
    to = time.time()
    sql = "SELECT * FROM users "
    cursor.execute(sql)
    data = cursor.fetchall()  # or use fetchone()
    try:
        # Переводим словарь в строку
        str_data=json.dumps(data)

        # Обновляем  наш файл с данными
        await bot.edit_message_media(InputMediaDocument(io.StringIO(str_data)), admin_id, config_id)

    except Exception as ex:
        print(ex)
    print('Время сохранения бекапа:='+str(time.time() - to))

#--------------------Метод при нажатии start-------------------------
@dp.message_handler(commands='start')
async def start(message: types.Message):
    # Добавляем нового пользователя
    sql_select = "SELECT * FROM users where id={}".format(message.chat.id)
    sql_insert = "INSERT INTO users VALUES ({}, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL" \
                 " )".format(message.chat.id, message.chat.first_name)
    try:
        cursor.execute(sql_select)
        data = cursor.fetchone()
        if data is None:
            cursor.execute(sql_insert)
            conn.commit()
            await save_data()
    except Exception:
        data = await get_data()
        cursor.execute("CREATE TABLE users (id INTEGER , name TEXT, sename TEXT, status TEXT, point INTEGER,"
                       " groups INTEGER, kurs INTEGER, kod INTEGER, obr TEXT)")
        cursor.executemany("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)", data)
        conn.commit()
        cursor.execute(sql_select)
        data = cursor.fetchone()
        if data is None:
            cursor.execute(sql_insert)
            conn.commit()
            await save_data()
        # Создаем кнопки
    button = KeyboardButton('Клик')
    button2 = KeyboardButton('Рейтинг')
    # Добавляем
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button).add(button2)
    # Отправляем сообщение с кнопкой
    await bot.send_message(message.chat.id, 'Приветствую {}'.format(message.from_user.first_name))
    await check_correct(message)



#--------------------Основная логика бота-------------------------
@dp.message_handler()
async def main_logic(message: types.Message):

    to=time.time()
# Логика для администратора
    if message.text == 'admin':
        cursor.execute("CREATE TABLE users (id INTEGER , name TEXT, sename TEXT, status TEXT, point INTEGER,"
                       " groups INTEGER, kurs INTEGER, kod INTEGER, obr TEXT)")
        cursor.execute("INSERT INTO users VALUES (1234, 'eee', NULL, NULL, NULL, NULL, NULL, NULL, NULL)")
        conn.commit()
        sql = "SELECT * FROM users "
        cursor.execute(sql)
        data = cursor.fetchall()
        str_data = json.dumps(data)
        await bot.send_document(message.chat.id, io.StringIO(str_data))
        await bot.send_message(message.chat.id, 'admin_id = {}'.format(message.chat.id))
        await bot.send_message(message.chat.id, 'config_id = {}'.format(message.message_id+1))

# Логика для пользователя
    try:
        sql = "SELECT * FROM users where id={}".format(message.chat.id)
        cursor.execute(sql)
        data = cursor.fetchone()  # or use fetchone()
    except Exception:
        data = await get_data()
        cursor.execute("CREATE TABLE users (id INTEGER , name TEXT, sename TEXT, status TEXT, point INTEGER,"
                       " groups INTEGER, kurs INTEGER, kod INTEGER, obr TEXT)")
        cursor.executemany("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)", data)
        conn.commit()
        sql = "SELECT * FROM users where id={}".format(message.chat.id)
        cursor.execute(sql)
        data = cursor.fetchone()  # or use fetchone()


    #При нажатии кнопки клик увеличиваем значение click на один и сохраняем
    if data is not None:
        if message.text == 'Клик':
            sql = "UPDATE users SET click = {} WHERE id = {}".format(data[2]+1, message.chat.id)
            cursor.execute(sql)
            conn.commit()
            await bot.send_message(message.chat.id, 'Кликов: {} 🏆'.format(data[2]+1))

        # При нажатии кнопки Рейтинг выводим пользователю топ 10
        if message.text == 'Список':
            sql = "SELECT * FROM users ORDER BY id"
            cursor.execute(sql)
            newlist = cursor.fetchall()  # or use fetchone()
            sql_count = "SELECT COUNT(id) FROM users"
            cursor.execute(sql_count)
            count = cursor.fetchone()
            rating = 'Всего: {}\n'.format(count[0])
            i = 1
            for user in newlist:
                rating = rating+str(i)+': '+user[1]+' - '+str(user[3])+'\n'
                i += 1
            await bot.send_message(message.chat.id, rating)

        if message.text[0:3] == 'код':
            st = check_Code(message.text[4:])
            if st != 'error':
                sql = "UPDATE users SET status = '{}' WHERE id = {}".format(st, message.from_user.id)
                cursor.execute(sql)
                conn.commit()
                await bot.send_message(message.chat.id, 'Успешно! Вам выдан статус \"{}\"'.format(st))
                await check_correct(message)

        if message.text[0:7] == 'фамилия':
            st = message.text[8:]
            sql = "UPDATE users SET sename = '{}' WHERE id = {}".format(st, message.from_user.id)
            cursor.execute(sql)
            conn.commit()
            await bot.send_message(message.chat.id, 'Успешно! Присвоенна фамилия \"{}\"'.format(st))
            await check_correct(message)

        if message.text[0:6] == 'группа':
            st = message.text[7:]
            sql = "UPDATE users SET groups = '{}' WHERE id = {}".format(st, message.from_user.id)
            cursor.execute(sql)
            conn.commit()
            await bot.send_message(message.chat.id, 'Успешно! Ваша группа \"{}\"'.format(st))
            await check_correct(message)

        if message.text[0:4] == 'курс':
            st = message.text[5:]
            sql = "UPDATE users SET kurs = '{}' WHERE id = {}".format(st, message.from_user.id)
            cursor.execute(sql)
            conn.commit()
            await bot.send_message(message.chat.id, 'Успешно! Ваш курс \"{}\"'.format(st))
            await check_correct(message)

        if message.text[0:6] == 'звание':
            st = message.text[7:]
            sql = "UPDATE users SET obr = '{}' WHERE id = {}".format(st, message.from_user.id)
            cursor.execute(sql)
            conn.commit()
            await bot.send_message(message.chat.id, 'Успешно!')
            await check_correct(message)

    else:
        await bot.send_message(message.chat.id, 'Вы не зарегистрированы')

    print(time.time()-to)


def timer_start():
    threading.Timer(30.0, timer_start).start()
    try:
        asyncio.run_coroutine_threadsafe(save_data(), bot.loop)
    except Exception as exc:
        pass


#--------------------Запуск бота-------------------------
if __name__ == '__main__':
    timer_start()
    executor.start_polling(dp, skip_updates=True)
