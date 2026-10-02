from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, Document
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from Bot.database.jobs import (
    get_all_jobs,
    get_job_by_id,
    search_jobs,
    get_jobs_by_location,
)

from Bot.database.users import get_user

from Bot.database.applications import (
    create_application,
    get_user_job_application,
)

router = Router()


# =========================================================
# 📝 APPLY STATES
# =========================================================

class ApplyState(StatesGroup):
    waiting_for_cv = State()


# =========================================================
# 🔎 SEARCH / FILTER STATES
# =========================================================

class JobSearchState(StatesGroup):
    waiting_for_keyword = State()
    waiting_for_location = State()


# =========================================================
# 💼 FIND JOBS MENU
# =========================================================

@router.callback_query(F.data == "find_jobs")
async def find_jobs(callback: CallbackQuery):

    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔎 Search Jobs",
        callback_data="search_jobs"
    )

    builder.button(
        text="📍 Location",
        callback_data="filter_location"
    )

    builder.button(
        text="📋 All Jobs",
        callback_data="all_jobs"
    )

    builder.button(
        text="⬅️ Bosh menyu",
        callback_data="main_menu"
    )

    builder.adjust(1)

    await callback.message.edit_text(
        "💼 Find Jobs\n\n"
        "Vakansiya qidirish usulini tanlang:",
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 📋 ALL JOBS
# =========================================================

@router.callback_query(F.data == "all_jobs")
async def all_jobs(
    callback: CallbackQuery,
    pool
):

    jobs = await get_all_jobs(pool)

    if not jobs:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="⬅️ Find Jobs",
            callback_data="find_jobs"
        )

        await callback.message.edit_text(
            "❌ Hozircha vakansiyalar mavjud emas.",
            reply_markup=builder.as_markup()
        )

        await callback.answer()
        return

    builder = InlineKeyboardBuilder()

    for job in jobs:

        builder.button(
            text=(
                f"💼 {job['title']} — "
                f"{job['company']}"
            ),
            callback_data=f"job_{job['id']}"
        )

    builder.button(
        text="⬅️ Find Jobs",
        callback_data="find_jobs"
    )

    builder.adjust(1)

    await callback.message.edit_text(
        "📋 Barcha vakansiyalar:\n\n"
        "Vakansiyani tanlang:",
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 🔎 SEARCH START
# =========================================================

@router.callback_query(F.data == "search_jobs")
async def search_jobs_start(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(
        JobSearchState.waiting_for_keyword
    )

    await callback.message.edit_text(
        "🔎 Vakansiya nomi yoki keyword kiriting.\n\n"
        "Masalan:\n"
        "Python\n"
        "Django\n"
        "Backend\n"
        "Developer"
    )

    await callback.answer()


# =========================================================
# 🔎 SEARCH RESULT
# =========================================================

@router.message(
    JobSearchState.waiting_for_keyword,
    F.text
)
async def search_job_result(
    message: Message,
    state: FSMContext,
    pool
):

    keyword = message.text.strip()

    if not keyword:

        await message.answer(
            "❌ Qidiruv so‘zi bo‘sh bo‘lmasin."
        )

        return

    jobs = await search_jobs(
        pool,
        keyword
    )

    await state.clear()

    if not jobs:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="🔎 Qayta qidirish",
            callback_data="search_jobs"
        )

        builder.button(
            text="⬅️ Find Jobs",
            callback_data="find_jobs"
        )

        builder.adjust(1)

        await message.answer(
            f"❌ «{keyword}» bo‘yicha "
            "vakansiya topilmadi.",
            reply_markup=builder.as_markup()
        )

        return

    builder = InlineKeyboardBuilder()

    for job in jobs:

        builder.button(
            text=(
                f"💼 {job['title']} — "
                f"{job['company']}"
            ),
            callback_data=f"job_{job['id']}"
        )

    builder.button(
        text="🔎 Yangi qidiruv",
        callback_data="search_jobs"
    )

    builder.button(
        text="⬅️ Find Jobs",
        callback_data="find_jobs"
    )

    builder.adjust(1)

    await message.answer(
        f"🔎 «{keyword}» bo‘yicha "
        f"{len(jobs)} ta vakansiya topildi:\n\n"
        "Vakansiyani tanlang:",
        reply_markup=builder.as_markup()
    )


# =========================================================
# 📍 LOCATION FILTER
# =========================================================

@router.callback_query(F.data == "filter_location")
async def filter_location(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(
        JobSearchState.waiting_for_location
    )

    await callback.message.edit_text(
        "📍 Viloyat yoki shahar nomini kiriting.\n\n"
        "Masalan:\n"
        "Toshkent\n"
        "Samarqand\n"
        "Andijon\n"
        "Buxoro"
    )

    await callback.answer()


# =========================================================
# 📍 LOCATION RESULT
# =========================================================

@router.message(
    JobSearchState.waiting_for_location,
    F.text
)
async def location_job_result(
    message: Message,
    state: FSMContext,
    pool
):

    location = message.text.strip()

    if not location:

        await message.answer(
            "❌ Location bo‘sh bo‘lmasin."
        )

        return

    jobs = await get_jobs_by_location(
        pool,
        location
    )

    await state.clear()

    if not jobs:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="📍 Qayta qidirish",
            callback_data="filter_location"
        )

        builder.button(
            text="⬅️ Find Jobs",
            callback_data="find_jobs"
        )

        builder.adjust(1)

        await message.answer(
            f"❌ «{location}»da "
            "vakansiya topilmadi.",
            reply_markup=builder.as_markup()
        )

        return

    builder = InlineKeyboardBuilder()

    for job in jobs:

        builder.button(
            text=(
                f"💼 {job['title']} — "
                f"{job['company']}"
            ),
            callback_data=f"job_{job['id']}"
        )

    builder.button(
        text="📍 Boshqa location",
        callback_data="filter_location"
    )

    builder.button(
        text="⬅️ Find Jobs",
        callback_data="find_jobs"
    )

    builder.adjust(1)

    await message.answer(
        f"📍 «{location.title()}» bo‘yicha "
        f"{len(jobs)} ta vakansiya topildi:\n\n"
        "Vakansiyani tanlang:",
        reply_markup=builder.as_markup()
    )


# =========================================================
# 💼 JOB DETAIL
# =========================================================

@router.callback_query(F.data.startswith("job_"))
async def job_detail(
    callback: CallbackQuery,
    pool
):

    try:

        job_id = int(
            callback.data.replace(
                "job_",
                ""
            )
        )

    except (ValueError, TypeError):

        await callback.answer(
            "❌ Noto‘g‘ri vakansiya ID.",
            show_alert=True
        )

        return

    job = await get_job_by_id(
        pool,
        job_id
    )

    if not job:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="⬅️ Find Jobs",
            callback_data="find_jobs"
        )

        await callback.message.edit_text(
            "❌ Bu vakansiya mavjud emas "
            "yoki o‘chirib tashlangan.",
            reply_markup=builder.as_markup()
        )

        await callback.answer()
        return

    builder = InlineKeyboardBuilder()

    builder.button(
        text="📩 Apply",
        callback_data=f"apply_{job_id}"
    )

    builder.button(
        text="⬅️ Find Jobs",
        callback_data="find_jobs"
    )

    builder.adjust(1)

    location = (
        job["location"]
        or "Ko‘rsatilmagan"
    )

    salary = (
        job["salary"]
        or "Kelishiladi"
    )

    description = (
        job["description"]
        or "-"
    )

    requirements = (
        job["requirements"]
        or "-"
    )

    text = (
        f"💼 {job['title']}\n\n"

        f"🏢 Company: {job['company']}\n"
        f"📍 Location: {location.title()}\n"
        f"💰 Salary: {salary}\n\n"

        f"📝 Description:\n"
        f"{description}\n\n"

        f"📋 Requirements:\n"
        f"{requirements}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 📩 APPLY
# =========================================================

@router.callback_query(F.data.startswith("apply_"))
async def apply_job(
    callback: CallbackQuery,
    state: FSMContext,
    pool
):

    try:

        job_id = int(
            callback.data.replace(
                "apply_",
                ""
            )
        )

    except (ValueError, TypeError):

        await callback.answer(
            "❌ Noto‘g‘ri vakansiya ID.",
            show_alert=True
        )

        return

    job = await get_job_by_id(
        pool,
        job_id
    )

    if not job:

        await callback.answer(
            "❌ Bu vakansiya mavjud emas "
            "yoki o‘chirib tashlangan.",
            show_alert=True
        )

        return

    existing_application = (
        await get_user_job_application(
            pool,
            callback.from_user.id,
            job_id
        )
    )

    if existing_application:

        status = existing_application["status"]

        if status == "accepted":

            status_text = "🟢 Accepted"

        elif status == "rejected":

            status_text = "🔴 Rejected"

        else:

            status_text = "🟡 Pending"

        builder = InlineKeyboardBuilder()

        if status == "rejected":

            builder.button(
                text="📩 Qayta ariza yuborish",
                callback_data=f"apply_again_{job_id}"
            )

        builder.button(
            text="⬅️ Vakansiya",
            callback_data=f"job_{job_id}"
        )

        builder.adjust(1)

        await callback.message.edit_text(
            "⚠️ Siz bu vakansiyaga allaqachon "
            "ariza yuborgansiz.\n\n"
            f"📄 Application "
            f"#{existing_application['id']}\n"
            f"📊 Status: {status_text}",
            reply_markup=builder.as_markup()
        )

        await callback.answer()
        return

    user = await get_user(
        pool,
        callback.from_user.id
    )

    if user and user["cv_file_id"]:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="📎 Use Profile CV",
            callback_data=f"use_profile_cv_{job_id}"
        )

        builder.button(
            text="📤 Upload New CV",
            callback_data=f"new_cv_{job_id}"
        )

        builder.button(
            text="⬅️ Vakansiya",
            callback_data=f"job_{job_id}"
        )

        builder.adjust(1)

        await callback.message.edit_text(
            "📄 Ariza yuborish\n\n"
            "CV tanlang:",
            reply_markup=builder.as_markup()
        )

        await callback.answer()
        return

    await state.set_state(
        ApplyState.waiting_for_cv
    )

    await state.update_data(
        job_id=job_id
    )

    await callback.message.edit_text(
        "📄 Profilingizda CV mavjud emas.\n\n"
        "📤 Iltimos, CV faylingizni yuboring.\n\n"
        "Faqat PDF fayl yuboring."
    )

    await callback.answer()


# =========================================================
# 📩 REJECTED APPLICATIONNI QAYTA YUBORISH
# =========================================================

@router.callback_query(F.data.startswith("apply_again_"))
async def apply_again(
    callback: CallbackQuery,
    state: FSMContext,
    pool
):

    try:

        job_id = int(
            callback.data.replace(
                "apply_again_",
                ""
            )
        )

    except (ValueError, TypeError):

        await callback.answer(
            "❌ Noto‘g‘ri vakansiya ID.",
            show_alert=True
        )

        return

    job = await get_job_by_id(
        pool,
        job_id
    )

    if not job:

        await callback.answer(
            "❌ Vakansiya topilmadi.",
            show_alert=True
        )

        return

    user = await get_user(
        pool,
        callback.from_user.id
    )

    if user and user["cv_file_id"]:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="📎 Use Profile CV",
            callback_data=f"use_profile_cv_{job_id}"
        )

        builder.button(
            text="📤 Upload New CV",
            callback_data=f"new_cv_{job_id}"
        )

        builder.button(
            text="⬅️ Vakansiya",
            callback_data=f"job_{job_id}"
        )

        builder.adjust(1)

        await callback.message.edit_text(
            "📄 Qayta ariza yuborish\n\n"
            "CV tanlang:",
            reply_markup=builder.as_markup()
        )

        await callback.answer()
        return

    await state.set_state(
        ApplyState.waiting_for_cv
    )

    await state.update_data(
        job_id=job_id
    )

    await callback.message.edit_text(
        "📄 Profilingizda CV mavjud emas.\n\n"
        "📤 CV faylingizni yuboring.\n\n"
        "Faqat PDF fayl yuboring."
    )

    await callback.answer()


# =========================================================
# 📎 PROFILE CV
# =========================================================

@router.callback_query(F.data.startswith("use_profile_cv_"))
async def use_profile_cv(
    callback: CallbackQuery,
    pool
):

    try:

        job_id = int(
            callback.data.replace(
                "use_profile_cv_",
                ""
            )
        )

    except (ValueError, TypeError):

        await callback.answer(
            "❌ Noto‘g‘ri vakansiya ID.",
            show_alert=True
        )

        return

    job = await get_job_by_id(
        pool,
        job_id
    )

    if not job:

        await callback.answer(
            "❌ Vakansiya topilmadi.",
            show_alert=True
        )

        return

    existing_application = (
        await get_user_job_application(
            pool,
            callback.from_user.id,
            job_id
        )
    )

    if existing_application:

        status = existing_application["status"]

        if status != "rejected":

            if status == "accepted":

                status_text = "🟢 Accepted"

            else:

                status_text = "🟡 Pending"

            await callback.message.edit_text(
                "⚠️ Siz bu vakansiyaga allaqachon "
                "ariza yuborgansiz.\n\n"
                f"📄 Application "
                f"#{existing_application['id']}\n"
                f"📊 Status: {status_text}"
            )

            await callback.answer()
            return

    user = await get_user(
        pool,
        callback.from_user.id
    )

    if not user or not user["cv_file_id"]:

        await callback.answer(
            "❌ Profilingizda CV mavjud emas.",
            show_alert=True
        )

        return

    application_id = await create_application(
        pool,
        callback.from_user.id,
        job_id,
        user["cv_file_id"]
    )

    await callback.message.edit_text(
        "✅ Ariza muvaffaqiyatli yuborildi!\n\n"
        f"📄 Application #{application_id}\n"
        "📊 Status: 🟡 Pending"
    )

    await callback.answer()


# =========================================================
# 📤 YANGI CV
# =========================================================

@router.callback_query(F.data.startswith("new_cv_"))
async def new_cv(
    callback: CallbackQuery,
    state: FSMContext
):

    try:

        job_id = int(
            callback.data.replace(
                "new_cv_",
                ""
            )
        )

    except (ValueError, TypeError):

        await callback.answer(
            "❌ Noto‘g‘ri vakansiya ID.",
            show_alert=True
        )

        return

    await state.set_state(
        ApplyState.waiting_for_cv
    )

    await state.update_data(
        job_id=job_id
    )

    await callback.message.edit_text(
        "📤 Yangi CV yuboring.\n\n"
        "Faqat PDF fayl yuboring."
    )

    await callback.answer()


# =========================================================
# 📤 CV QABUL QILISH
# =========================================================

@router.message(
    ApplyState.waiting_for_cv,
    F.document
)
async def receive_new_cv(
    message: Message,
    state: FSMContext,
    pool
):

    document: Document = message.document

    if document.mime_type != "application/pdf":

        await message.answer(
            "❌ Faqat PDF fayl qabul qilinadi.\n\n"
            "Iltimos, PDF CV yuboring."
        )

        return

    data = await state.get_data()

    job_id = data.get("job_id")

    if not job_id:

        await state.clear()

        await message.answer(
            "❌ Ariza ma'lumotlari topilmadi.\n"
            "Iltimos, qaytadan urinib ko‘ring."
        )

        return

    job = await get_job_by_id(
        pool,
        job_id
    )

    if not job:

        await state.clear()

        await message.answer(
            "❌ Bu vakansiya mavjud emas "
            "yoki o‘chirib tashlangan."
        )

        return

    existing_application = (
        await get_user_job_application(
            pool,
            message.from_user.id,
            job_id
        )
    )

    if existing_application:

        if existing_application["status"] != "rejected":

            await state.clear()

            await message.answer(
                "⚠️ Siz bu vakansiyaga "
                "allaqachon ariza yuborgansiz."
            )

            return

    application_id = await create_application(
        pool,
        message.from_user.id,
        job_id,
        document.file_id
    )

    await state.clear()

    await message.answer(
        "✅ Ariza muvaffaqiyatli yuborildi!\n\n"
        f"📄 Application #{application_id}\n"
        "📊 Status: 🟡 Pending"
    )


# =========================================================
# ❌ NOTO‘G‘RI CV
# =========================================================

@router.message(
    ApplyState.waiting_for_cv
)
async def wrong_cv(
    message: Message
):

    await message.answer(
        "❌ Iltimos, CVni PDF fayl ko‘rinishida yuboring."
    )