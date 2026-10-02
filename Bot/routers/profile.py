from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Bot.database.users import (
    get_user,
    update_cv,
)


router = Router()


# =========================================================
# 📎 CV STATE
# =========================================================

class ProfileCVState(StatesGroup):

    waiting_for_cv = State()


# =========================================================
# 👤 MY PROFILE
# =========================================================

@router.callback_query(
    F.data == "my_profile"
)
async def my_profile(
    callback: CallbackQuery,
    pool
):

    user = await get_user(
        pool,
        callback.from_user.id
    )

    if not user:

        await callback.answer(
            "❌ Profil topilmadi.",
            show_alert=True
        )

        return

    cv_file_id = user["cv_file_id"]

    if cv_file_id:

        cv_status = "✅ Mavjud"

    else:

        cv_status = "❌ Mavjud emas"

    first_name = (
        callback.from_user.first_name
        or "Noma'lum"
    )

    builder = InlineKeyboardBuilder()

    builder.button(
        text="📎 CV ni almashtirish",
        callback_data="profile_change_cv"
    )

    if cv_file_id:

        builder.button(
            text="🗑 CV ni o‘chirish",
            callback_data="profile_delete_cv"
        )

    builder.button(
        text="⬅️ Bosh menyu",
        callback_data="main_menu"
    )

    builder.adjust(1)

    text = (
        "👤 My Profile\n\n"

        f"🆔 User ID: "
        f"{callback.from_user.id}\n"

        f"👤 Ism: "
        f"{first_name}\n"

        f"📄 CV: "
        f"{cv_status}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 📎 CHANGE CV
# =========================================================

@router.callback_query(
    F.data == "profile_change_cv"
)
async def profile_change_cv(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(
        ProfileCVState.waiting_for_cv
    )

    await callback.message.edit_text(
        "📎 Yangi CV yuboring.\n\n"
        "Qabul qilinadigan formatlar:\n"
        "• PDF\n"
        "• DOCX"
    )

    await callback.answer()


# =========================================================
# 📄 RECEIVE NEW CV
# =========================================================

@router.message(
    ProfileCVState.waiting_for_cv,
    F.document
)
async def receive_profile_cv(
    message: Message,
    state: FSMContext,
    pool
):

    document = message.document

    file_name = (
        document.file_name or ""
    ).lower()

    if not (
        file_name.endswith(".pdf")
        or file_name.endswith(".docx")
    ):

        await message.answer(
            "❌ Noto‘g‘ri format.\n\n"
            "Faqat PDF yoki DOCX yuboring."
        )

        return

    await update_cv(
        pool,
        message.from_user.id,
        document.file_id
    )

    await state.clear()

    await message.answer(
        "✅ CV muvaffaqiyatli yangilandi!\n\n"
        f"📄 Fayl: {document.file_name}"
    )


# =========================================================
# ❌ WRONG CV MESSAGE
# =========================================================

@router.message(
    ProfileCVState.waiting_for_cv
)
async def wrong_profile_cv(
    message: Message
):

    await message.answer(
        "📎 Iltimos, CV faylini yuboring.\n\n"
        "Qabul qilinadi:\n"
        "• PDF\n"
        "• DOCX"
    )


# =========================================================
# 🗑 DELETE CV
# =========================================================

@router.callback_query(
    F.data == "profile_delete_cv"
)
async def profile_delete_cv(
    callback: CallbackQuery,
    state: FSMContext,
    pool
):

    user = await get_user(
        pool,
        callback.from_user.id
    )

    if not user:

        await callback.answer(
            "❌ Profil topilmadi.",
            show_alert=True
        )

        return

    if not user["cv_file_id"]:

        await callback.answer(
            "ℹ️ Profilingizda CV mavjud emas.",
            show_alert=True
        )

        return

    await update_cv(
        pool,
        callback.from_user.id,
        None
    )

    await state.clear()

    await callback.message.edit_text(
        "🗑 CV muvaffaqiyatli o‘chirildi."
    )

    await callback.answer(
        "✅ CV o‘chirildi"
    )


# =========================================================
# ⬅️ BACK TO PROFILE
# =========================================================

@router.callback_query(
    F.data == "profile_back"
)
async def profile_back(
    callback: CallbackQuery,
    pool
):

    await my_profile(
        callback,
        pool
    )