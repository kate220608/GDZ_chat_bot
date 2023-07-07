from dotenv import find_dotenv, load_dotenv
from telebot.async_telebot import AsyncTeleBot
import asyncio
import os
import requests
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')
bot = AsyncTeleBot(TOKEN, parse_mode='HTML')


def generate_markup2(buttons, n):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(*buttons, row_width=n)
    return markup


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
    markup = generate_markup({"Помощь": 'help', "Уравнение": 'sol', "Пример": 'task'})
    await bot.send_message(user_id, "Добро пожаловать!\nЯ бот, помогающий решать математические задачи.\nВыберите "
                                    "дальнейшую команду:\n", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    chat_id = call.message.chat.id
    button_call = call.data
    if button_call == 'help':
        sign_list = ['+ сложение', '- вычетание', '* умнoжение', '/ деление', '// деление нацело(только в примерах)', '** возведение в степень(только в примерах)', '^ возведение в степень(только в уравнениях)', '% деление с остатком', '√ корень', '= равно']
        await bot.send_message(chat_id, f"Знаки:\n" + '\n'.join(sign_list))
    if button_call == 'sol':
        await bot.send_message(chat_id, 'Введите уравнение')
    if button_call == 'task':
        await bot.send_message(chat_id, 'Введите пример')


@bot.message_handler(content_types=['text'])
async def send_sol(message):
    oper = ['=', '-', '%', '+', '/', '^', '*', '√']
    chat_id = message.chat.id
    print(message)
    if message.reply_to_message is not None:
        if message.reply_to_message.text == 'Введите уравнение':
            if any(map(str.isdigit, message.text)) and any(map(lambda x: x.lower() == 'x', message.text)):
                res = get_solution(message.text)
                if res is not None:
                    await bot.send_message(chat_id, res)
                else:
                    await bot.send_message(chat_id, "Решения нет.")
            else:
                await bot.send_message(chat_id, "Это не уравнение")
        else:
            if any(map(str.isdigit, message.text)) and any(map(lambda x: x in oper, message.text)):
                if '√' in message.text:
                    await bot.send_message(chat_id, int(message.text[1]) ** 0.5)
                else:
                    await bot.send_message(chat_id, eval(message.text))
            else:
                await bot.send_message(chat_id, 'Это не пример')
        markup = generate_markup2(['да', 'нет'], 2)
        await bot.send_message(chat_id, 'Хотите вернутся в начало?', reply_markup=markup)
    else:
        if message.text == 'да':
            await send_hello(message)
        elif message.text == 'нет':
            pass
        else:
            await bot.send_photo(chat_id, open('photo_5273788290220280301_y.jpg', 'rb'), 'Ответьте на '
                                                                                     'сообщение, которое отправил бот.')


asyncio.run(bot.polling())   
