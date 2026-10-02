from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from Bot.keyboards.main_menu import main_menu


router = Router()


# =========================================================
# 🚀 START
# =========================================================

@router.message(CommandStart())
async def start_handler(
    message: Message
):

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "💼 Job Finder botiga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=main_menu
    )


# =========================================================
# 🏠 BOSH MENYU
# =========================================================

@router.callback_query(
    F.data == "main_menu"
)
async def back_to_main_menu(
    callback: CallbackQuery
):

    await callback.message.edit_text(
        "👋 Bosh menyu\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=main_menu
    )

    await callback.answer()