from dotenv import find_dotenv, load_dotenv
from telebot.async_telebot import AsyncTeleBot
import asyncio
import os
import requests
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')
bot = AsyncTeleBot(TOKEN, parse_mode='HTML')


def generate_markup(buttons):
    markup = InlineKeyboardMarkup()
    for el1, el2 in buttons.items():
        button = InlineKeyboardButton(el1, callback_data=el2)
        markup.add(button)
    return markup


def get_solution(question):
    app_id = 'PKP57J-LKJRVT8HHV'
    if '+' in question:
        question = question.replace('+', '%2B')
    elif '*' in question:
        question = question.replace('*', '×')

    api_url = f'http://api.wolframalpha.com/v2/query?input={question}&appid={app_id}'

    try:
        response = requests.get(api_url)
        data = response.text
        print(data)
        solution = ''
        while True:
            # Извлекаем решение из ответа
            start_index = data.find('<plaintext>') + len('<plaintext>')
            if data.find('<plaintext>') != -1:
                end_index = data.find('</plaintext>')
                solution += data[start_index:end_index].strip() + '\n'
                data = data.replace('<plaintext>', '', 1)
                data = data.replace('</plaintext>', '', 1)
            else:
                break

        return solution
    except requests.exceptions.RequestException:
        print('Произошла ошибка при отправке запроса.')
        return None


@bot.message_handler(commands=['start'])
async def send_hello(message):
    user_id = message.from_user.id
    markup = generate_markup({"решение": 'sol', "помощь": 'help'})

    await bot.send_message(user_id, "Добро пожаловать!\nЯ бот, помогающий решать математические задачи.\nВыберите дальнейшую команду:\n", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    chat_id = call.message.chat.id
    button_call = call.data
    if button_call == 'help':
        sign_list = ['+ сложение', '- вычетание', '* умнoжение', '/ деление', '^ возведение в степень', '% деление с остатком',]
        await bot.send_message(chat_id, f"Знаки:\n" + '\n'.join(sign_list))
    if button_call == 'sol':
        await bot.send_message(chat_id, 'введите уравнение')


@bot.message_handler(func=lambda message: True)
async def send_sol(message):
    oper = ['=', '-', '%', '+', '/', '^', '*']
    chat_id = message.chat.id
    if any(map(str.isdigit, message.text)) and any(map(lambda x: x in oper, message.text)):
        res = get_solution(message.text)
        if res is not None:
            await bot.send_message(chat_id, res)
        else:
            await bot.send_message(chat_id, "Решения нет.")
    else:
        await bot.send_message(chat_id, "Это не пример")



asyncio.run(bot.polling())


