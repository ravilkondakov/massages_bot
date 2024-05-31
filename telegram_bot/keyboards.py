# Клавиатура для основных команд
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton('Виды массажа'), KeyboardButton('Записаться на прием'))

# Inline-клавиатура для видов массажа
massage_menu = InlineKeyboardMarkup(row_width=2)
massage_menu.add(InlineKeyboardButton('Массаж 1', callback_data='massage_1'))
massage_menu.add(InlineKeyboardButton('Массаж 2', callback_data='massage_2'))
admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add(KeyboardButton('Добавить массаж'), KeyboardButton('Посмотреть записи'))