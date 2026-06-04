# app/keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def remove_keyboard() -> ReplyKeyboardMarkup:
    """Удаление клавиатуры"""
    return ReplyKeyboardMarkup(resize_keyboard=True, remove_keyboard=True)
