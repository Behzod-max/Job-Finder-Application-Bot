from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💼 Find Jobs",
                callback_data="find_jobs"
            )
        ],
        [
            InlineKeyboardButton(
                text="📄 My Applications",
                callback_data="my_applications"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 My Profile",
                callback_data="my_profile"
            )
        ]
    ]
)