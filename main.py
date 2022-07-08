import telebot
import sqlite3
import json
from telebot import types


with open('config.json', 'r', encoding='utf-8') as f:
  data = json.load(f)
  

bot = telebot.TeleBot(data['api'])
conn = sqlite3.connect('database.db', check_same_thread=False)
db = conn.cursor()


def getMoney(id: int) -> int:
    db.execute("""SELECT money FROM users WHERE id = ?""", (id,))
    return db.fetchone()[0]


def addMoney(id: int, money: int) -> None:
    bal = getMoney(id)
    db.execute("""UPDATE users SET money = ? WHERE id = ?""", (bal + money, id))
    conn.commit()


def addUser(id: int):
    db.execute("""INSERT INTO users (id, money) VALUES (?, ?);""", (id, 0))
    conn.commit()


def isUserRegistered(id: int) -> bool:
    db.execute("""SELECT id FROM users WHERE id = ?""", (id,))
    if db.fetchone() is None:
        return False
    else:
        return True


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    item1 = types.KeyboardButton('Заработать')
    item2 = types.KeyboardButton('Мой баланс')
    item3 = types.KeyboardButton('Вывод')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, data['start_message'], reply_markup=markup)
    if not isUserRegistered(message.from_user.id):
        addUser(message.from_user.id)


@bot.message_handler(content_types=['text'])
def handle(message):
    if message.text == "Заработать":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item1 = types.KeyboardButton('КЛИК')
        item2 = types.KeyboardButton('НАЗАД')
        markup.add(item1, item2)
        bot.send_message(message.chat.id, data['zarabotat_message'], reply_markup=markup)
    elif message.text == "Мой баланс":
        bot.send_message(message.chat.id, data['balance_message'] + str(getMoney(message.from_user.id)) + " руб")
    elif message.text == "Вывод":
        bot.send_message(message.chat.id, data['vivod_message'])
    elif message.text == "КЛИК":
        bot.send_message(message.chat.id, data['click_message'])
        addMoney(message.from_user.id, 1)
    elif message.text == "НАЗАД":
        start(message)


if __name__ == "__main__":
    db.execute("""CREATE TABLE IF NOT EXISTS users(
        id INT PRIMARY KEY,
        money INT
    );""")
    bot.polling(non_stop=True)

