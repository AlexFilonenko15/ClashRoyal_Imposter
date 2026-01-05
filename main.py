import telebot
import os
from dotenv import load_dotenv
import requests
from telebot import types
import json
import random


load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]
API_TOKEN = os.environ['API_TOKEN']


bot = telebot.TeleBot(BOT_TOKEN)


value = {}


url = "https://api.clashroyale.com/v1/cards"
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in value:
        value[message.chat.id] = {
            'number': 0,
            'counter': 0,
            'card': None,
            'players': 0,
            'imposter': 0,
            'photo': None
        }
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('3', callback_data='3')
    btn2 = types.InlineKeyboardButton('4', callback_data='4')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Привет👋\nМы начинаем игру в шпиона по игре Clash Royale🃏\nВыбери количество игроков, которое вам нужно🎮' , parse_mode='html', reply_markup=markup)



@bot.callback_query_handler(func=lambda callback:True)
def game(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('Next', callback_data='next')
    markup.add(btn1)
    if call.data not in ['next', 'hide']:
        value[call.message.chat.id]['players'] = int(call.data)
        value[call.message.chat.id]['number'] = random.randint(0, 120)
        value[call.message.chat.id]['imposter'] = random.randint(0, value[call.message.chat.id]['players'] - 1)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            cards = json.loads(response.text)
            value[call.message.chat.id]['card'] = cards['items'][value[call.message.chat.id]['number']]['name']
            value[call.message.chat.id]['photo'] = cards['items'][value[call.message.chat.id]['number']]['iconUrls']['medium']
            bot.send_message(call.message.chat.id, 'Хорошо игра начинаеться,нажмите на кнопку чтоби продолжить игру.', reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, 'Какие-то неполодки, мы уже работаем над ними.\nПриносим наши извинения', parse_mode='html')
            return

    if call.data == 'next':
        markup1 = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Hide', callback_data='hide')
        markup1.add(btn1)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if value[call.message.chat.id]['counter'] < value[call.message.chat.id]['players']:
            if value[call.message.chat.id]['counter'] == value[call.message.chat.id]['imposter']:
                bot.send_message(call.message.chat.id, f'Игрок {value[call.message.chat.id]['counter'] + 1},Ти шпион', reply_markup=markup1, parse_mode='html')
                value[call.message.chat.id]['counter'] += 1
            else:
                bot.send_photo(chat_id=call.message.chat.id, photo=value[call.message.chat.id]['photo'], caption=f'Игрок {value[call.message.chat.id]['counter'] + 1 },ваша карта {value[call.message.chat.id]['card']}',reply_markup=markup1)
                value[call.message.chat.id]['counter'] += 1
        else:
            bot.send_message(call.message.chat.id, 'Да начнется битва,если хотите сиграть снова воспользуйтесь /start')
            value[call.message.chat.id]['counter'] = 0
            value[call.message.chat.id]['imposter'] = 0

    if call.data == 'hide':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Передайте телефон следуйщему игроку', reply_markup=markup)
    


bot.polling(none_stop=True)






