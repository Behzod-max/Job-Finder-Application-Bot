from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Bot.database.applications import (
    get_user_applications,
    get_user_application_by_id,
)


router = Router()


# =========================================================
# 📋 MY APPLICATIONS
# =========================================================

@router.callback_query(
    F.data == "my_applications"
)
async def my_applications(
    callback: CallbackQuery,
    pool
):

    applications = await get_user_applications(
        pool,
        callback.from_user.id
    )

    # -----------------------------------------------------
    # Arizalar mavjud emas
    # -----------------------------------------------------

    if not applications:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="⬅️ Bosh menyu",
            callback_data="main_menu"
        )

        await callback.message.edit_text(
            "📋 Sizda hozircha arizalar mavjud emas.",
            reply_markup=builder.as_markup()
        )

        await callback.answer()

        return

    # -----------------------------------------------------
    # Application tugmalari
    # -----------------------------------------------------

    builder = InlineKeyboardBuilder()

    for application in applications:

        status = application["status"]

        if status == "accepted":

            status_text = "🟢 Accepted"

        elif status == "rejected":

            status_text = "🔴 Rejected"

        else:

            status_text = "🟡 Pending"

        builder.button(
            text=(
                f"📄 #{application['id']} "
                f"{application['title']} "
                f"— {status_text}"
            ),
            callback_data=(
                f"user_application_{application['id']}"
            )
        )

    builder.button(
        text="⬅️ Bosh menyu",
        callback_data="main_menu"
    )

    builder.adjust(1)

    await callback.message.edit_text(
        "📋 My Applications\n\n"
        "Quyidagi arizalardan birini tanlang:",
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 📄 APPLICATION DETAIL
# =========================================================
#
# MUHIM:
# user_application_cv_6 ham
# user_application_ bilan boshlanadi.
#
# Shuning uchun CV callbackini bu handlerga
# kiritmaslik uchun ~ ishlatyapmiz.
# =========================================================

@router.callback_query(
    F.data.startswith("user_application_")
    & ~F.data.startswith("user_application_cv_")
)
async def user_application_detail(
    callback: CallbackQuery,
    pool
):

    # =====================================================
    # 🔒 APPLICATION ID TEKSHIRISH
    # =====================================================

    try:

        application_id = int(
            callback.data.replace(
                "user_application_",
                ""
            )
        )

    except (ValueError, TypeError):

        await callback.answer(
            "❌ Noto‘g‘ri application ID.",
            show_alert=True
        )

        return

    # =====================================================
    # 🔎 APPLICATIONNI OLISH
    # =====================================================

    application = await get_user_application_by_id(
        pool,
        application_id,
        callback.from_user.id
    )

    # =====================================================
    # ❌ APPLICATION TOPILMADI
    # =====================================================

    if not application:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="⬅️ My Applications",
            callback_data="my_applications"
        )

        await callback.message.edit_text(
            "❌ Ariza topilmadi.\n\n"
            "Bu ariza mavjud emas yoki "
            "sizga tegishli emas.",
            reply_markup=builder.as_markup()
        )

        await callback.answer()

        return

    # =====================================================
    # 📊 STATUS
    # =====================================================

    status = application["status"]

    if status == "accepted":

        status_text = "🟢 Accepted"

    elif status == "rejected":

        status_text = "🔴 Rejected"

    else:

        status_text = "🟡 Pending"

    # =====================================================
    # 📅 SANA
    # =====================================================

    created_at = application["created_at"]

    if created_at:

        created_at = created_at.strftime(
            "%d.%m.%Y %H:%M"
        )

    else:

        created_at = "-"

    # =====================================================
    # 📍 LOCATION
    # =====================================================

    location = (
        application["location"]
        or "Ko‘rsatilmagan"
    )

    # =====================================================
    # 💰 SALARY
    # =====================================================

    salary = (
        application["salary"]
        or "Kelishiladi"
    )

    # =====================================================
    # 📝 DESCRIPTION
    # =====================================================

    description = (
        application["description"]
        or "-"
    )

    # =====================================================
    # 📋 REQUIREMENTS
    # =====================================================

    requirements = (
        application["requirements"]
        or "-"
    )

    # =====================================================
    # 📎 CV
    # =====================================================

    cv_file_id = application.get(
        "cv_file_id"
    )

    if cv_file_id:

        cv_text = "✅ Mavjud"

    else:

        cv_text = "❌ Mavjud emas"

    # =====================================================
    # 📄 APPLICATION TEXT
    # =====================================================

    text = (
        f"📄 Application #{application['id']}\n\n"

        "💼 Vakansiya\n"
        f"├─ {application['title']}\n"
        f"├─ 🏢 Company: "
        f"{application['company']}\n"
        f"├─ 📍 Location: "
        f"{location.title()}\n"
        f"└─ 💰 Salary: {salary}\n\n"

        f"📊 Status: {status_text}\n"
        f"📅 Submitted: {created_at}\n"
        f"📎 CV: {cv_text}\n\n"

        "📝 Description\n"
        f"{description}\n\n"

        "📋 Requirements\n"
        f"{requirements}"
    )

    # =====================================================
    # 🔘 BUTTONS
    # =====================================================

    builder = InlineKeyboardBuilder()

    if cv_file_id:

        builder.button(
            text="📎 CV ni ko‘rish",
            callback_data=(
                f"user_application_cv_{application_id}"
            )
        )

    builder.button(
        text="⬅️ My Applications",
        callback_data="my_applications"
    )

    builder.button(
        text="🏠 Bosh menyu",
        callback_data="main_menu"
    )

    builder.adjust(1)

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 📎 APPLICATION CV
# =========================================================

@router.callback_query(
    F.data.startswith("user_application_cv_")
)
async def user_application_cv(
    callback: CallbackQuery,
    pool
):

    # =====================================================
    # 🔒 APPLICATION ID TEKSHIRISH
    # =====================================================

    try:

        application_id = int(
            callback.data.replace(
                "user_application_cv_",
                ""
            )
        )

    except (ValueError, TypeError):

        await callback.answer(
            "❌ Noto‘g‘ri application ID.",
            show_alert=True
        )

        return

    # =====================================================
    # 🔎 APPLICATIONNI OLISH
    # =====================================================

    application = await get_user_application_by_id(
        pool,
        application_id,
        callback.from_user.id
    )

    # =====================================================
    # ❌ APPLICATION TOPILMADI
    # =====================================================

    if not application:

        await callback.answer(
            "❌ Ariza topilmadi.",
            show_alert=True
        )

        return

    # =====================================================
    # 📎 CV TEKSHIRISH
    # =====================================================

    cv_file_id = application.get(
        "cv_file_id"
    )

    if not cv_file_id:

        await callback.answer(
            "❌ Bu arizada CV mavjud emas.",
            show_alert=True
        )

        return

    # =====================================================
    # 📤 CV YUBORISH
    # =====================================================

    try:

        await callback.message.answer_document(
            document=cv_file_id,
            caption=(
                f"📄 Application "
                f"#{application['id']}\n\n"
                f"💼 {application['title']}\n"
                f"🏢 {application['company']}"
            )
        )

    except Exception:

        await callback.answer(
            "❌ CVni yuborishda xatolik yuz berdi.",
            show_alert=True
        )

        return

    await callback.answer(
        "📎 CV yuborildi."
    )