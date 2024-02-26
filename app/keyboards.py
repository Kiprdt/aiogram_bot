from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

url_button_1: KeyboardButton = KeyboardButton(
        text='Добавить слово',
        callback_data='add_word')

url_button_2: KeyboardButton = KeyboardButton(
        text='Список слов',
        callback_data='list_word')

url_button_3: KeyboardButton = KeyboardButton(
        text='Учить',
        callback_data='learn_word')

menu: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[url_button_1], [url_button_2],
                                                                   [url_button_3]], one_time_keyboard=True, resize_keyboard=True)

url_button_start: InlineKeyboardButton = InlineKeyboardButton(
        text='Начнём',
        callback_data='start_using')
starting_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[url_button_start]], one_time_keyboard=True)

url_button_back: InlineKeyboardButton = InlineKeyboardButton(
        text='Back',
        callback_data='backing')
url_button_delete: InlineKeyboardButton = InlineKeyboardButton(
        text='Удалить слово',
        callback_data='delete_word')
back: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[url_button_back], [url_button_delete]])


url_button_back2: KeyboardButton = KeyboardButton(
        text='Назад',
        resize_keyboard=True)
back2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[url_button_back2]], resize_keyboard=True)

url_button_1: InlineKeyboardButton = InlineKeyboardButton(
        text='Подтвердить',
        callback_data='confirm')
url_button_2: InlineKeyboardButton = InlineKeyboardButton(
        text='Удалить',
        callback_data='delete')
url_button_3: InlineKeyboardButton = InlineKeyboardButton(
        text='Выход',
        callback_data='exit')
confirm_add: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[url_button_1], [url_button_2], [url_button_3]], one_time_keyboard=True)


url_button_know: InlineKeyboardButton = InlineKeyboardButton(
        text="I remember",
        callback_data="know_word",

)
url_button_unknown: InlineKeyboardButton = InlineKeyboardButton(
        text="Show word",
        callback_data="unknown"
)

keyboard_learning: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[url_button_know, url_button_unknown, url_button_back]])

url_continue: InlineKeyboardButton = InlineKeyboardButton(text="Продолжить",
                                                          callback_data='cont')
keyboard_continue: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[url_continue], ])


url_button_freq_sch: KeyboardButton = KeyboardButton(
        text='Every',
        resize_keyboard=True)
url_button_freq_sch1: KeyboardButton = KeyboardButton(
        text='Only',
        resize_keyboard=True)

freq_sch: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[url_button_freq_sch, url_button_freq_sch1]], resize_keyboard=True)

url_monday: KeyboardButton = KeyboardButton(text='Monday')
url_tuesday: KeyboardButton = KeyboardButton(text='Tuesday')
url_wednesday: KeyboardButton = KeyboardButton(text='Wednesday')
url_thursday: KeyboardButton = KeyboardButton(text='Thursday')
url_friday: KeyboardButton = KeyboardButton(text='Friday')
url_saturday: KeyboardButton = KeyboardButton(text='Saturday')
url_sunday: KeyboardButton = KeyboardButton(text='Sunday')

day_sch: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[url_monday, url_tuesday, url_wednesday],
                                                             [url_thursday, url_friday, url_saturday],
                                                             [url_sunday]], resize_keyboard=True)

