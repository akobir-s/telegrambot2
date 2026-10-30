from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def menu_buttons():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📗 Menu'), KeyboardButton(text='🛒 My Orders')],
            [KeyboardButton(text='🤙 About us'), KeyboardButton(text='➕ Add Item')],
        ], resize_keyboard=True
    )

def cancel_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='❌ Cancel')]
        ], resize_keyboard=True
    )
