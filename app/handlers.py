from aiogram import types, F, Router, Dispatcher
from aiogram.types import BufferedInputFile, \
    ReplyKeyboardRemove
from googletrans import Translator
from functions import *
from aiogram.filters import Command, or_f
from db import *
from config import *
import gtts
from text2ipa import get_IPA
import asyncio
import logging
from keyboard import *
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont



router = Router()

class CheckWordHandler(StatesGroup):
    check_word_handler = State()


class FSMFillForm(StatesGroup):
    add_word_handler = State()
    state_word = State()
    state_translater = State()
    state_transcription = State()
    fimage_data = State()
    state_audio = State()
    fuser_id = State()


class DeleteWord(StatesGroup):
    delete_word = State()


class KnowWord(StatesGroup):
    know_word = State()


class YourNextStepHandlerName(StatesGroup):
    waiting_for_text = State()


@router.message(Command(commands='start'))
async def starting(message: types.Message):
    if await check_black_list_func(message.from_user.id) is False:
        username = message.from_user.username
        user_id = message.from_user.id
        if add_user(user_id, username) is True:
            await bot.send_message(message.chat.id, 'А я тебя уже знаю, начнём?', reply_markup=menu)
        else:
            await bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=menu)
    else:
        await message.answer('Вы добавлены в чёрный список администрацией! ')

@router.message(Command(commands='sendall'), StateFilter(default_state))
async def process_sendall_command(message: types.Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите ваш текст рассылки')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(YourNextStepHandlerName.waiting_for_text)


@router.message(YourNextStepHandlerName.waiting_for_text)
async def process_sendall_message(message: types.Message, state: FSMContext):
    text = message.text
    result_of_users = await get_users()
    for i in result_of_users:
        print(i[0])
        await bot.send_message(chat_id=i[0], text=text)
    await message.answer("Рассылка выполнена.")
    await state.clear()


@router.message(Command(commands='stat'))
async def stat(message: types.Message):
    await message.answer(f'Статистика: \nКоличество слов{await stat_of_user(message.from_user.id)}')

@router.message(Command(commands='blacklist'))
async def connection_with_admins(message: types.Message):
    if await check_admin_func(message.from_user.id) is True:
        text = message.text.replace('/blacklist', '')
        await add_to_black_list("".join(text.split()))
        con.commit()
        await message.answer(f'Пользователь - {"".join(text.split())} - успешно добавлен в чёрный список!',
                             reply_markup=menu)
    else:
        await message.answer('Вам недоступна эта команда! Проверьте свой уровень доступа.', reply_markup=menu)

@router.message(Command(commands='whitelist'))
async def connection_with_admins(message: types.Message):
    if await check_admin_func(message.from_user.id) is True:
        text = message.text.replace('/whitelist', '')
        await add_to_white_list("".join(text.split()))
        con.commit()
        await message.answer(f'Пользователь - {"".join(text.split())} - успешно выведен из чёрного списка!',
                             reply_markup=menu)
    else:
        await message.answer('Вам недоступна эта команда! Проверьте свой уровень доступа.', reply_markup=menu)


@router.message(Command(commands='con'))
async def connection_with_admins(message: types.Message):
    if await check_black_list_func(message.from_user.id) is False:
        text = message.text.replace('/con', '')
        [await bot.send_message(admins, text=f"Сообщение от пользователя - {message.from_user.username}: {text}") for
         admins in admins_chat_id]
    else:
        await message.answer('Вы добавлены в чёрный список администрацией! ')


@router.message(F.text == "Назад", FSMFillForm.add_word_handler)
async def some_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Мы вернулись в главное меню.", reply_markup=menu)


@router.callback_query(F.data == "backing")
async def back_handler(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await callback_query.message.answer('Мы вернулись в меню!', reply_markup=menu)


@router.message(F.text == 'Добавить слово', StateFilter(default_state))
async def add_word_func_main(message: types.Message, state: FSMContext):
    if await check_black_list_func(message.from_user.id) is False:
        check_list_add = list_add(message.from_user.id)
        if check_list_add < 10 or await check_subscribe_func(message.from_user.id) is True:
            await message.answer(text='Можете вводить слово!', reply_markup=back2)
            await state.set_state(FSMFillForm.add_word_handler)
        else:
            await message.answer('Доступ на ввод слов ограничен, купите полную версию!')
    else:
        await message.answer('Вы добавлены в чёрный список администрацией!')


@router.message(F.text == 'Учить')
async def learning_word_func_main(message: types.Message):
    if await check_black_list_func(message.from_user.id) is False:
        if await check_indicators(message.from_user.id):
            await update_all_indicators(message.from_user.id)
        if list_add(message.from_user.id) != 0:
            current_word = await learning_func_first(message.from_user.id)
            await message.answer(
                f'{"-" * len(current_word)}<i>{current_word}</i>{"-" * len(current_word)}', reply_markup=keyboard_learning)
        else:
            await message.answer('У вас ещё нет ни одного слова.')
    else:
        await message.answer('Вы добавлены в чёрный список администрацией!')


@router.callback_query(or_f(F.data == 'know_word', F.data == 'unknown'))
async def process_know_command(callback_query: types.CallbackQuery):
    current_word = callback_query.message.text.replace('-', '')
    if callback_query.data == 'unknown':
        imagination = image_learning_func(callback_query.from_user.id, current_word)
        image_stream = BytesIO(imagination)
        image_bytes = image_stream.read()
        audio = audio_learning_func(callback_query.from_user.id, current_word)
        audio_stream = BytesIO(audio)
        audio_bytes = audio_stream.read()
        await callback_query.message.answer_photo(BufferedInputFile(image_bytes, filename=f"{current_word}.png"))
        await callback_query.message.answer_audio(BufferedInputFile(audio_bytes, filename=f"{current_word}.mp3"))
    elif callback_query.data == 'know_word':
        await change_indicator(callback_query.from_user.id, current_word)
    else:
        await callback_query.message.answer('Возникла ошибка! Повторите позже!')
    next_word = await learning_func_next(callback_query.from_user.id, current_word)
    if next_word is None and current_word is not None:
        await callback_query.message.answer('Мы закончили!', reply_markup=menu)
    else:
        await callback_query.message.answer(f'{"-" * len(next_word)}<i>{next_word}</i>{"-" * len(next_word)}',
                                            reply_markup=keyboard_learning)


@router.callback_query(F.data == 'delete_word', StateFilter(default_state))
async def delete_word_from_fsm(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Отправьте число того слова, которое вы хотите удалить.',
                           reply_markup=ReplyKeyboardRemove())
    await state.set_state(DeleteWord.delete_word)


@router.message(DeleteWord.delete_word)
async def delete_word_from_list_func(message: types.Message, state: FSMContext):
    word_for_deleting = message.text
    await delete_word_from_list(word_for_deleting, message.from_user.id)
    con.commit()
    await message.answer(f'Вы удалили слово и вернулись в меню!', reply_markup=menu)
    await state.clear()


@router.message(F.text == 'Список слов')
async def list_of_word_func_main(message: types.Message):
    if await check_black_list_func(message.from_user.id) is False:
        if list_add(message.from_user.id) != 0:
            listing = []
            for item in await list_add_func(message.from_user.id):
                listing.extend(item)
            resulting = "".join(
                [f"{listing[i + 2]}. {listing[i + 1]} - {listing[i]}\n" for i in range(0, len(listing), 3)])
            await message.answer(text=markdown.text(resulting), reply_markup=back)
        else:
            await message.answer('У вас ещё не добавлены слова! Вы можете добавить их из главного меню.',
                                 reply_markup=menu)
    else:
        await message.answer('Вы добавлены в чёрный список администрацией!')


@router.callback_query(F.data == 'confirm')
async def confirm_add_handler(callback_query: types.CallbackQuery, state: FSMContext):
    check_list_add = list_add(callback_query.from_user.id)
    if check_list_add < 10 or await check_subscribe_func(callback_query.from_user.id) is True:
        data = await state.get_data()
        word = data.get('state_word')
        translater = data.get('state_translater')
        transcription = data.get('state_transcription')
        image_data = data.get('fimage_data')
        audio_data = data.get('state_audio_data')
        user_id = data.get('fuser_id')
        await add_word(word, translater, transcription, image_data, audio_data, user_id)
        con.commit()
        await callback_query.answer('Слово успешно добавлено! Продолжайте!')
        await callback_query.message.edit_reply_markup()
    else:
        await callback_query.message.answer('Доступ ограничен, купите подписку!')


@router.callback_query(F.data == 'exit')
async def exit_add_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.answer('Вы вернулись в меню', reply_markup=menu)
    await callback_query.message.edit_reply_markup()


@router.callback_query(F.data == 'delete')
async def cancel_add_handler(callback_query: types.CallbackQuery):
    await callback_query.answer('Добавление отменено! Продолжайте!')
    await callback_query.message.edit_reply_markup()

def create_image(translater: str, transcription: str) -> bytes:
    weight, height = (800, 600)
    image = Image.new('RGB', (weight, height), color=(40, 178, 252))
    draw = ImageDraw.Draw(image)
    font_size = 50
    fonter = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 60)
    w, h = font.getsize(translater)
    w1, h1 = fonter.getsize(transcription)
    h = font.getlength(translater)
    stroke_color = (0, 0, 255)
    word1_x = (weight - w) // 2
    word1_y = (height - h - h1) // 2
    word2_x = (weight - w1) // 2
    word2_y = word1_y + h
    draw.text(
        (word1_x, word1_y), translater, fill=(255, 255, 255), font=font, antialias=False, stroke_width=1,
        stroke_fill=stroke_color)
    draw.text(
        (word2_x, word2_y), transcription, fill=(255, 255, 255), font=fonter, antialias=False,
        stroke_width=1, stroke_fill=stroke_color)
    image_stream = BytesIO()
    image.save(image_stream, 'PNG', quality=95)
    image_stream.seek(0)
    return image_stream.getvalue()



@router.message(FSMFillForm.add_word_handler, ~StateFilter(default_state))
async def translating_word(message: types.Message, state: FSMContext):
    await state.update_data(fuser_id=message.from_user.id)
    word = message.text.lower()
    await state.update_data(state_word=word)
    translator = Translator()
    translation = translator.translate(word, dest='en', src='ru')
    translater = translation.text
    await state.update_data(state_translater=translater)
    transcription = get_IPA(translater, language)
    transcription = transcription.replace('ᵊ', 'ə')
    await state.update_data(state_transcription=transcription)
    # Создание объекта BytesIO для хранения аудиофайла в памяти
    buffer = BytesIO()
    # Создание аудио-произношения
    tts = gtts.gTTS(translater, lang='en')
    tts.write_to_fp(buffer)
    # Получение данных аудиофайла в виде байтовой строки
    audio_data = buffer.getvalue()
    await state.update_data(state_audio_data=audio_data)
    # Создание изображения с текстом перевода
    image_data = create_image(translater, transcription)
    await state.update_data(fimage_data=image_data)
    # Отправка изображения пользователю
    await message.answer_photo(BufferedInputFile(image_data, filename=f"{translater}.png"))
    await message.answer_audio(BufferedInputFile(audio_data, filename=f"{translater}.mp3"), reply_markup=confirm_add)
    # Удаление временного файла изображения
    buffer.close()
