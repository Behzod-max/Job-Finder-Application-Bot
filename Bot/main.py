import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from Bot.config import BOT_TOKEN
from Bot.database.connection import create_pool

from Bot.routers.start import router as start_router
from Bot.routers.jobs import router as jobs_router
from Bot.routers.applications import router as applications_router
from Bot.routers.admin import router as admin_router
from Bot.routers.profile import router as profile_router


# =========================================================
# 📝 LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(__name__)


# =========================================================
# 🛡 GLOBAL ERROR HANDLER
# =========================================================

async def global_error_handler(
    event: ErrorEvent
):

    logger.exception(
        "Botda xatolik yuz berdi: %s",
        event.exception
    )

    # Foydalanuvchiga xato haqida umumiy xabar
    try:

        if event.update:

            message = getattr(
                event.update,
                "message",
                None
            )

            callback_query = getattr(
                event.update,
                "callback_query",
                None
            )

            if message:

                await message.answer(
                    "⚠️ Kutilmagan xatolik yuz berdi.\n\n"
                    "Iltimos, birozdan keyin qayta urinib ko‘ring."
                )

            elif callback_query:

                await callback_query.answer(
                    "⚠️ Xatolik yuz berdi. "
                    "Qaytadan urinib ko‘ring.",
                    show_alert=True
                )

    except Exception as error:

        logger.exception(
            "Error handler ichida ham xatolik: %s",
            error
        )


# =========================================================
# 🚀 MAIN
# =========================================================

async def main():

    bot = Bot(
        token=BOT_TOKEN
    )

    dp = Dispatcher()

    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    pool = await create_pool()

    dp["pool"] = pool

    # -----------------------------------------------------
    # ROUTERS
    # -----------------------------------------------------

    dp.include_router(
        start_router
    )

    dp.include_router(
        jobs_router
    )

    dp.include_router(
        applications_router
    )

    dp.include_router(
        admin_router
    )

    dp.include_router(
        profile_router
    )

    # -----------------------------------------------------
    # ERROR HANDLER
    # -----------------------------------------------------

    dp.errors.register(
        global_error_handler
    )

    print("Bot ishga tushdi!")

    logger.info(
        "Bot polling boshlanmoqda..."
    )

    # -----------------------------------------------------
    # POLLING
    # -----------------------------------------------------

    try:

        await dp.start_polling(
            bot
        )

    except Exception as error:

        logger.exception(
            "Polling vaqtida xatolik: %s",
            error
        )

    finally:

        logger.info(
            "Bot resurslari yopilmoqda..."
        )

        await pool.close()

        await bot.session.close()

        logger.info(
            "Bot to‘xtadi."
        )


# =========================================================
# ▶️ START
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )