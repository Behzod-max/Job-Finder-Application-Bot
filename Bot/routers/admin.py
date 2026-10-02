from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from Bot.config import ADMIN_ID

from Bot.database.admin import get_statistics

from Bot.database.applications import (
    get_pending_applications,
    get_application_by_id,
    update_application_status,
)

from Bot.database.jobs import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    delete_job,
    update_job,
)


router = Router()


# =========================================================
# ➕ ADD JOB STATES
# =========================================================

class AddJobState(StatesGroup):

    waiting_for_title = State()
    waiting_for_company = State()
    waiting_for_location = State()
    waiting_for_salary = State()
    waiting_for_description = State()
    waiting_for_requirements = State()


# =========================================================
# ✏️ EDIT JOB STATE
# =========================================================

class EditJobState(StatesGroup):

    waiting_for_value = State()


# =========================================================
# 👨‍💼 ADMIN MENU
# =========================================================

def admin_menu_keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(
        text="📊 Statistics",
        callback_data="admin_statistics"
    )

    builder.button(
        text="📋 Applications",
        callback_data="admin_applications"
    )

    builder.button(
        text="➕ Add Job",
        callback_data="admin_add_job"
    )

    builder.button(
        text="💼 Manage Jobs",
        callback_data="admin_manage_jobs"
    )

    builder.adjust(1)

    return builder.as_markup()


# =========================================================
# 👨‍💼 /admin
# =========================================================

@router.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "❌ Siz admin emassiz."
        )

        return

    await message.answer(
        "👨‍💼 Admin panel\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=admin_menu_keyboard()
    )


# =========================================================
# 📊 STATISTICS
# =========================================================

@router.callback_query(
    F.data == "admin_statistics"
)
async def admin_statistics(
    callback: CallbackQuery,
    pool
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    stats = await get_statistics(pool)

    builder = InlineKeyboardBuilder()

    builder.button(
        text="📋 Applications",
        callback_data="admin_applications"
    )

    builder.button(
        text="➕ Add Job",
        callback_data="admin_add_job"
    )

    builder.button(
        text="💼 Manage Jobs",
        callback_data="admin_manage_jobs"
    )

    builder.button(
        text="🔄 Yangilash",
        callback_data="admin_statistics"
    )

    builder.button(
        text="⬅️ Admin panel",
        callback_data="admin_panel"
    )

    builder.adjust(1)

    text = (
        "📊 Statistics\n\n"
        f"👥 Users: {stats['users']}\n"
        f"💼 Jobs: {stats['jobs']}\n"
        f"📄 Applications: {stats['applications']}\n\n"
        f"⏳ Pending: {stats['pending']}\n"
        f"✅ Accepted: {stats['accepted']}\n"
        f"❌ Rejected: {stats['rejected']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 📋 APPLICATIONS
# =========================================================

@router.callback_query(
    F.data == "admin_applications"
)
async def admin_applications(
    callback: CallbackQuery,
    pool
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    applications = await get_pending_applications(pool)

    if not applications:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="⬅️ Admin panel",
            callback_data="admin_panel"
        )

        await callback.message.edit_text(
            "📋 Hozircha pending arizalar yo‘q.",
            reply_markup=builder.as_markup()
        )

        await callback.answer()

        return

    builder = InlineKeyboardBuilder()

    for application in applications:

        builder.button(
            text=(
                f"📄 #{application['id']} "
                f"{application['title']} — "
                f"{application['company']}"
            ),
            callback_data=(
                f"admin_application_{application['id']}"
            )
        )

    builder.button(
        text="⬅️ Admin panel",
        callback_data="admin_panel"
    )

    builder.adjust(1)

    await callback.message.edit_text(
        "📋 Pending Applications:\n\n"
        "Arizani tanlang:",
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 📄 APPLICATION DETAIL
# =========================================================

@router.callback_query(
    F.data.startswith("admin_application_")
)
async def application_detail(
    callback: CallbackQuery,
    pool
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    application_id = int(
        callback.data.replace(
            "admin_application_",
            ""
        )
    )

    application = await get_application_by_id(
        pool,
        application_id
    )

    if not application:

        await callback.answer(
            "❌ Ariza topilmadi.",
            show_alert=True
        )

        return

    builder = InlineKeyboardBuilder()

    builder.button(
        text="📎 CV ni olish",
        callback_data=f"admin_cv_{application_id}"
    )

    builder.button(
        text="✅ Accept",
        callback_data=f"accept_{application_id}"
    )

    builder.button(
        text="❌ Reject",
        callback_data=f"reject_{application_id}"
    )

    builder.button(
        text="⬅️ Applications",
        callback_data="admin_applications"
    )

    builder.adjust(1)

    text = (
        f"📄 Application #{application['id']}\n\n"
        f"👤 User ID: {application['user_id']}\n"
        f"💼 Kasb: {application['title']}\n"
        f"🏢 Company: {application['company']}\n"
        f"📍 Viloyat: {application['location'].title()}\n"
        f"💰 Salary: {application['salary'] or 'Kelishiladi'}\n"
        f"📊 Status: {application['status']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 📎 CV
# =========================================================

@router.callback_query(
    F.data.startswith("admin_cv_")
)
async def send_cv(
    callback: CallbackQuery,
    pool
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    application_id = int(
        callback.data.replace(
            "admin_cv_",
            ""
        )
    )

    application = await get_application_by_id(
        pool,
        application_id
    )

    if not application:

        await callback.answer(
            "❌ Ariza topilmadi.",
            show_alert=True
        )

        return

    await callback.message.answer_document(
        application["cv_file_id"],
        caption=(
            f"📄 Application #{application_id}\n"
            f"💼 {application['title']}\n"
            f"🏢 {application['company']}"
        )
    )

    await callback.answer(
        "📎 CV yuborildi."
    )


# =========================================================
# ✅ ACCEPT
# =========================================================

@router.callback_query(
    F.data.startswith("accept_")
)
async def accept_application(
    callback: CallbackQuery,
    pool,
    bot: Bot
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    application_id = int(
        callback.data.replace(
            "accept_",
            ""
        )
    )

    application = await get_application_by_id(
        pool,
        application_id
    )

    if not application:

        await callback.answer(
            "❌ Ariza topilmadi.",
            show_alert=True
        )

        return

    await update_application_status(
        pool,
        application_id,
        "accepted"
    )

    await bot.send_message(
        application["user_id"],
        "✅ Arizangiz qabul qilindi!\n\n"
        f"💼 {application['title']}\n"
        f"🏢 {application['company']}\n\n"
        "🎉 Ish beruvchi arizangizni qabul qildi."
    )

    await callback.message.edit_text(
        f"✅ Application #{application_id} qabul qilindi.\n\n"
        f"👤 User: {application['user_id']}\n"
        f"💼 {application['title']}"
    )

    await callback.answer(
        "✅ Accepted"
    )


# =========================================================
# ❌ REJECT
# =========================================================

@router.callback_query(
    F.data.startswith("reject_")
)
async def reject_application(
    callback: CallbackQuery,
    pool,
    bot: Bot
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    application_id = int(
        callback.data.replace(
            "reject_",
            ""
        )
    )

    application = await get_application_by_id(
        pool,
        application_id
    )

    if not application:

        await callback.answer(
            "❌ Ariza topilmadi.",
            show_alert=True
        )

        return

    await update_application_status(
        pool,
        application_id,
        "rejected"
    )

    await bot.send_message(
        application["user_id"],
        "❌ Afsuski, arizangiz rad etildi.\n\n"
        f"💼 {application['title']}\n"
        f"🏢 {application['company']}\n\n"
        "Boshqa vakansiyalarga ham ariza yuborishingiz mumkin."
    )

    await callback.message.edit_text(
        f"❌ Application #{application_id} rad etildi.\n\n"
        f"👤 User: {application['user_id']}\n"
        f"💼 {application['title']}"
    )

    await callback.answer(
        "❌ Rejected"
    )


# =========================================================
# ➕ ADD JOB
# =========================================================

@router.callback_query(
    F.data == "admin_add_job"
)
async def admin_add_job(
    callback: CallbackQuery,
    state: FSMContext
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    await state.set_state(
        AddJobState.waiting_for_title
    )

    await callback.message.edit_text(
        "💼 Vakansiya nomini kiriting:"
    )

    await callback.answer()


@router.message(
    AddJobState.waiting_for_title,
    F.text
)
async def add_job_title(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        title=message.text.strip()
    )

    await state.set_state(
        AddJobState.waiting_for_company
    )

    await message.answer(
        "🏢 Kompaniya nomini kiriting:"
    )


@router.message(
    AddJobState.waiting_for_company,
    F.text
)
async def add_job_company(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        company=message.text.strip()
    )

    await state.set_state(
        AddJobState.waiting_for_location
    )

    await message.answer(
        "📍 Viloyatni kiriting:"
    )


@router.message(
    AddJobState.waiting_for_location,
    F.text
)
async def add_job_location(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        location=message.text.strip().lower()
    )

    await state.set_state(
        AddJobState.waiting_for_salary
    )

    await message.answer(
        "💰 Maoshni kiriting:"
    )


@router.message(
    AddJobState.waiting_for_salary,
    F.text
)
async def add_job_salary(
    message: Message,
    state: FSMContext
):

    salary_text = message.text.strip()

    # Maosh faqat musbat raqam bo'lishi kerak
    if not salary_text.isdigit() or int(salary_text) <= 0:

        await message.answer(
            "❌ Maosh faqat raqamlardan iborat bo'lishi kerak.\n\n"
            "Masalan:\n"
            "5000000\n"
            "7500000\n"
            "12000000"
        )

        return

    await state.update_data(
        salary=salary_text
    )

    await state.set_state(
        AddJobState.waiting_for_description
    )

    await message.answer(
        "📝 Description kiriting:"
    )


@router.message(
    AddJobState.waiting_for_description,
    F.text
)
async def add_job_description(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        description=message.text.strip()
    )

    await state.set_state(
        AddJobState.waiting_for_requirements
    )

    await message.answer(
        "📋 Requirements kiriting:"
    )


@router.message(
    AddJobState.waiting_for_requirements,
    F.text
)
async def add_job_requirements(
    message: Message,
    state: FSMContext,
    pool
):

    requirements = message.text.strip()

    data = await state.get_data()

    job_id = await create_job(
        pool,
        data["title"],
        data["company"],
        data["location"],
        data["salary"],
        data["description"],
        requirements
    )

    await state.clear()

    await message.answer(
        "✅ Vakansiya muvaffaqiyatli qo‘shildi!\n\n"
        f"🆔 ID: {job_id}\n"
        f"💼 {data['title']}\n"
        f"🏢 {data['company']}\n"
        f"📍 {data['location'].title()}\n"
        f"💰 {data['salary']}"
    )


# =========================================================
# 💼 MANAGE JOBS
# =========================================================

@router.callback_query(
    F.data == "admin_manage_jobs"
)
async def admin_manage_jobs(
    callback: CallbackQuery,
    pool
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    jobs = await get_all_jobs(pool)

    if not jobs:

        builder = InlineKeyboardBuilder()

        builder.button(
            text="⬅️ Admin panel",
            callback_data="admin_panel"
        )

        await callback.message.edit_text(
            "💼 Hozircha vakansiyalar yo‘q.",
            reply_markup=builder.as_markup()
        )

        await callback.answer()

        return

    builder = InlineKeyboardBuilder()

    for job in jobs:

        builder.button(
            text=(
                f"💼 #{job['id']} "
                f"{job['title']} — "
                f"{job['company']}"
            ),
            callback_data=f"manage_job_{job['id']}"
        )

    builder.button(
        text="⬅️ Admin panel",
        callback_data="admin_panel"
    )

    builder.adjust(1)

    await callback.message.edit_text(
        "💼 Manage Jobs\n\n"
        "Vakansiyani tanlang:",
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# 💼 ADMIN JOB DETAIL
# =========================================================

@router.callback_query(
    F.data.startswith("manage_job_")
)
async def manage_job_detail(
    callback: CallbackQuery,
    pool
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    job_id = int(
        callback.data.replace(
            "manage_job_",
            ""
        )
    )

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

    builder = InlineKeyboardBuilder()

    builder.button(
        text="✏️ Edit",
        callback_data=f"edit_job_{job_id}"
    )

    builder.button(
        text="🗑 Delete",
        callback_data=f"delete_job_{job_id}"
    )

    builder.button(
        text="⬅️ Manage Jobs",
        callback_data="admin_manage_jobs"
    )

    builder.adjust(1)

    text = (
        f"💼 {job['title']}\n\n"
        f"🏢 Company: {job['company']}\n"
        f"📍 Viloyat: {job['location'].title()}\n"
        f"💰 Salary: {job['salary'] or 'Kelishiladi'}\n\n"
        f"📝 Description:\n"
        f"{job['description'] or '-'}\n\n"
        f"📋 Requirements:\n"
        f"{job['requirements'] or '-'}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# ✏️ EDIT JOB MENU
# =========================================================

@router.callback_query(
    F.data.startswith("edit_job_")
)
async def edit_job(
    callback: CallbackQuery,
    state: FSMContext,
    pool
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    job_id = int(
        callback.data.replace(
            "edit_job_",
            ""
        )
    )

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

    builder = InlineKeyboardBuilder()

    builder.button(
        text="💼 Title",
        callback_data=f"editfield_title_{job_id}"
    )

    builder.button(
        text="🏢 Company",
        callback_data=f"editfield_company_{job_id}"
    )

    builder.button(
        text="📍 Location",
        callback_data=f"editfield_location_{job_id}"
    )

    builder.button(
        text="💰 Salary",
        callback_data=f"editfield_salary_{job_id}"
    )

    builder.button(
        text="📝 Description",
        callback_data=f"editfield_description_{job_id}"
    )

    builder.button(
        text="📋 Requirements",
        callback_data=f"editfield_requirements_{job_id}"
    )

    builder.button(
        text="⬅️ Orqaga",
        callback_data=f"manage_job_{job_id}"
    )

    builder.adjust(1)

    await callback.message.edit_text(
        "✏️ Qaysi ma'lumotni o‘zgartirasiz?",
        reply_markup=builder.as_markup()
    )

    await callback.answer()


# =========================================================
# ✏️ EDIT FIELD
# =========================================================

@router.callback_query(
    F.data.startswith("editfield_")
)
async def edit_field(
    callback: CallbackQuery,
    state: FSMContext
):

    parts = callback.data.split("_")

    field = parts[1]

    job_id = int(parts[-1])

    field_names = {
        "title": "💼 Yangi vakansiya nomini",
        "company": "🏢 Yangi kompaniya nomini",
        "location": "📍 Yangi viloyatni",
        "salary": "💰 Yangi maoshni",
        "description": "📝 Yangi descriptionni",
        "requirements": "📋 Yangi requirementsni",
    }

    if field not in field_names:

        await callback.answer(
            "❌ Maydon topilmadi.",
            show_alert=True
        )

        return

    await state.set_state(
        EditJobState.waiting_for_value
    )

    await state.update_data(
        job_id=job_id,
        field=field
    )

    await callback.message.edit_text(
        f"{field_names[field]} kiriting:"
    )

    await callback.answer()


# =========================================================
# 💾 EDIT VALUE SAQLASH
# =========================================================

@router.message(
    EditJobState.waiting_for_value,
    F.text
)
async def save_edit(
    message: Message,
    state: FSMContext,
    pool
):

    data = await state.get_data()

    job_id = data["job_id"]

    field = data["field"]

    value = message.text.strip()

    job = await get_job_by_id(
        pool,
        job_id
    )

    if not job:

        await message.answer(
            "❌ Vakansiya topilmadi."
        )

        await state.clear()

        return

    title = job["title"]

    company = job["company"]

    location = job["location"]

    salary = job["salary"]

    description = job["description"]

    requirements = job["requirements"]

    if field == "title":

        title = value

    elif field == "company":

        company = value

    elif field == "location":

        location = value.lower()

    elif field == "salary":

        # Edit pay: faqat musbat raqam
        if not value.isdigit() or int(value) <= 0:

            await message.answer(
                "❌ Maosh faqat raqamlardan iborat bo'lishi kerak.\n\n"
                "Masalan:\n"
                "5000000\n"
                "7500000\n"
                "12000000"
            )

            return

        salary = value

    elif field == "description":

        description = value

    elif field == "requirements":

        requirements = value

    await update_job(
        pool,
        job_id,
        title,
        company,
        location,
        salary,
        description,
        requirements
    )

    await state.clear()

    await message.answer(
        "✅ Vakansiya muvaffaqiyatli yangilandi!\n\n"
        f"🆔 ID: {job_id}\n"
        f"💼 {title}\n"
        f"🏢 {company}\n"
        f"📍 {location.title()}\n"
        f"💰 {salary}\n\n"
        f"📝 {description}\n\n"
        f"📋 {requirements}"
    )


# =========================================================
# 🗑 DELETE JOB
# =========================================================

@router.callback_query(
    F.data.startswith("delete_job_")
)
async def admin_delete_job(
    callback: CallbackQuery,
    pool
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Siz admin emassiz.",
            show_alert=True
        )

        return

    job_id = int(
        callback.data.replace(
            "delete_job_",
            ""
        )
    )

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

    await delete_job(
        pool,
        job_id
    )

    await callback.message.edit_text(
        "✅ Vakansiya o‘chirildi!\n\n"
        f"💼 {job['title']}\n"
        f"🏢 {job['company']}"
    )

    await callback.answer(
        "🗑 O‘chirildi"
    )