# app/keyboards/inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional

def main_menu_keyboard(gettext) -> InlineKeyboardMarkup:
    """Клавиатура главного меню"""
    buttons = [
        [InlineKeyboardButton(text=gettext("buy_vpn"), callback_data="buy_vpn")],
        [InlineKeyboardButton(text=gettext("my_vpns"), callback_data="my_vpns")],
        [InlineKeyboardButton(text=gettext("instructions"), callback_data="instructions")],
        [InlineKeyboardButton(text=gettext("support"), callback_data="support")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_keyboard(gettext) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    buttons = [
        [InlineKeyboardButton(text=gettext("back"), callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def vpn_actions_keyboard(gettext, vpn_client_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с VPN"""
    buttons = [
        [
            InlineKeyboardButton(text=gettext("renew"), callback_data=f"renew:{vpn_client_id}"),
            InlineKeyboardButton(text=gettext("get_link"), callback_data=f"get_link:{vpn_client_id}")
        ],
        [
            InlineKeyboardButton(text=gettext("delete"), callback_data=f"delete:{vpn_client_id}")
        ],
        [
            InlineKeyboardButton(text=gettext("back"), callback_data="my_vpns")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_delete_keyboard(gettext, vpn_client_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    buttons = [
        [
            InlineKeyboardButton(text=gettext("yes"), callback_data=f"confirm_delete:{vpn_client_id}"),
            InlineKeyboardButton(text=gettext("no"), callback_data="my_vpns")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_menu_keyboard(gettext) -> InlineKeyboardMarkup:
    """Клавиатура админ панели"""
    buttons = [
        [InlineKeyboardButton(text=gettext("admin_stats"), callback_data="admin_stats")],
        [InlineKeyboardButton(text=gettext("admin_broadcast"), callback_data="admin_broadcast")],
        [InlineKeyboardButton(text=gettext("back"), callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
