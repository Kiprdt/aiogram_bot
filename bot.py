import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from googletrans import Translator
from func import *
import requests
from bs4 import BeautifulSoup
import sqlite3


bot = Bot('6301969067:AAFTSPUex8x_HkfV-42ob5L8YI5wTr-17wk')
dp = Dispatcher(bot=bot)

bot_info_button = InlineKeyboardButton('Продолжить', callback_data='bot_info_continue')
bot_learning_button = KeyboardButton('Учить', callback_data='bot_learning')
bot_add_button = KeyboardButton('Добавить', callback_data='bot_add')
bot_delete_button = KeyboardButton('Удалить', callback_data='bot_delete')
bot_back_button = KeyboardButton('Назад', callback_data='bot_back')
# Создание изображения с текстом перевода
conn = sqlite3.connect('mydatabase.db')
conn.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT, chat_id INTEGER)''')

conn.execute('''CREATE TABLE IF NOT EXISTS words
             (id INTEGER PRIMARY KEY, word_id INTEGER, word TEXT, definition TEXT, transcription TEXT, audio BLOB)''')

conn.execute('''CREATE TABLE IF NOT EXISTS images
             (id INTEGER PRIMARY KEY, word_id INTEGER, image BLOB)''')


def add_user(username, chat_id):
    conn.execute("INSERT INTO users (username, chat_id) VALUES (?, ?)", (username, chat_id))
    conn.commit()


def add_word(word_id, word, definition, transcription, audio):
    conn.execute("INSERT INTO words (word_id, word, definition, transcription, audio) VALUES (?, ?, ?, ?, ?)", (word_id, word, definition, transcription, audio))
    conn.commit()


def add_image(word_id, image):
    conn.execute("INSERT INTO images (word_id, image) VALUES (?, ?)", (word_id, image))
    conn.commit()


local = None


@dp.message_handler(commands='start')
async def starting(message: types.Message):
    username = message.from_user.username
    chat_id = message.chat.id
    add_user(username, chat_id)
    keyboard_start = InlineKeyboardMarkup().add(bot_info_button)
    await bot.send_message(message.chat.id, 'Привет, этот бот создан......................', reply_markup=keyboard_start)


@dp.callback_query_handler(lambda query: query.data == 'bot_info_continue')
async def show_bot_info(query: CallbackQuery):
    global local
    keyboard_info = ReplyKeyboardMarkup(resize_keyboard=True).add(bot_learning_button, bot_add_button, bot_delete_button)
    await bot.send_message(query.message.chat.id, 'Выбери, что тебе нужно', reply_markup=keyboard_info)
    local = keyboard_info


@dp.message_handler(lambda message: message.text == 'bot_learning')
async def add(message: types.Message):
    global local
    keyboard_add = ReplyKeyboardMarkup(resize_keyboard=True).add(bot_learning_button, bot_add_button, bot_delete_button, bot_back_button)
    await bot.send_message(message.chat.id, '', reply_markup=keyboard_add)
    local = keyboard_add


@dp.callback_query_handler(lambda query: query.data == 'bot_back')
async def back(query: CallbackQuery):
    global local
    if local:
        await bot.send_message(query.message.chat.id, 'Выбери, что тебе нужно', reply_markup=local)


if __name__ == '__main__':
    executor.start_polling(dp)










start_button = KeyboardButton('Начать')
exit_button = KeyboardButton('Выход')
keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(start_button, exit_button)


@dp.message_handler()
async def translating_word(message: types.Message):
    word = message.text.lower()
    translator = Translator()
    translation = translator.translate(word, dest='en')
    if 'a' in translation.text:
        translater = re.sub(r'[a]+\s', '', translation.text).strip()
        print(translater)
    elif 'the' in translation.text:
        translater = translation.text.replace('the', '')
    else:
        translater = translation.text
    url = "https://dictionary.cambridge.org/dictionary/english/" + translater
    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    site = 'https://dictionary.cambridge.org'
    # Отправляем GET-запрос на сервер и получаем HTML-код страницы
    transcription = get_transcription(headers, url)
    response = requests.get(url, headers=headers)
    html = response.content
    # Используем BeautifulSoup для парсинга HTML-кода страницы
    soup = BeautifulSoup(html, 'html.parser')
    # Ищем определение слова на странице
    audio = soup.find('source', {'type': 'audio/mpeg'})['src']
    audio_url = site + audio
    print(audio_url)
    req = requests.get(audio_url, headers=headers)
    # Создание объекта BytesIO для хранения аудиофайла в памяти
    buffer = BytesIO()
    # Запись данных аудиофайла в объект BytesIO
    buffer.write(req.content)
    # Получение данных аудиофайла в виде байтовой строки
    audio_data = buffer.getvalue()
    # Создание изображения с текстом перевода
    image_data = create_image(translater, transcription)
    # Отправка изображения пользователю
    await bot.send_photo(message.chat.id, image_data)
    add_image(message.chat.id, image_data)
    await bot.send_audio(message.chat.id, audio=audio_data, title=f'{translater}.mp3')
    add_word(message.chat.id, word, translater, transcription, audio_data)
    # Удаление временного файла изображения
    buffer.close()
