# =========================================================
# 👤 USERS DATABASE
# =========================================================


# =========================================================
# 👤 USER YARATISH / YANGILASH
# =========================================================

async def create_user(
    pool,
    telegram_id,
    full_name=None,
    username=None,
    phone=None,
    email=None
):
    query = """
        INSERT INTO users (
            telegram_id,
            full_name,
            username,
            phone,
            email
        )
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (telegram_id)
        DO UPDATE SET
            full_name = EXCLUDED.full_name,
            username = EXCLUDED.username,
            phone = EXCLUDED.phone,
            email = EXCLUDED.email
        RETURNING *
    """

    return await pool.fetchrow(
        query,
        telegram_id,
        full_name,
        username,
        phone,
        email
    )


# =========================================================
# 👤 USERNI OLISH
# =========================================================

async def get_user(
    pool,
    telegram_id
):
    query = """
        SELECT
            id,
            telegram_id,
            full_name,
            username,
            phone,
            email,
            created_at,
            cv_file_id
        FROM users
        WHERE telegram_id = $1
    """

    return await pool.fetchrow(
        query,
        telegram_id
    )


# =========================================================
# 📄 CV YANGILASH
# =========================================================

async def update_cv(
    pool,
    telegram_id,
    cv_file_id
):
    query = """
        UPDATE users
        SET cv_file_id = $1
        WHERE telegram_id = $2
    """

    await pool.execute(
        query,
        cv_file_id,
        telegram_id
    )


# =========================================================
# 📄 CV OLISH
# =========================================================

async def get_user_cv(
    pool,
    telegram_id
):
    query = """
        SELECT cv_file_id
        FROM users
        WHERE telegram_id = $1
    """

    return await pool.fetchval(
        query,
        telegram_id
    )


# =========================================================
# ✏️ USER MA'LUMOTLARINI YANGILASH
# =========================================================

async def update_user(
    pool,
    telegram_id,
    full_name=None,
    username=None,
    phone=None,
    email=None
):
    query = """
        UPDATE users
        SET
            full_name = $1,
            username = $2,
            phone = $3,
            email = $4
        WHERE telegram_id = $5
    """

    await pool.execute(
        query,
        full_name,
        username,
        phone,
        email,
        telegram_id
    )


# =========================================================
# 🗑 CV NI O‘CHIRISH
# =========================================================

async def delete_cv(
    pool,
    telegram_id
):
    query = """
        UPDATE users
        SET cv_file_id = NULL
        WHERE telegram_id = $1
    """

    await pool.execute(
        query,
        telegram_id
    )


# =========================================================
# 🔎 USER MAVJUDLIGINI TEKSHIRISH
# =========================================================

async def user_exists(
    pool,
    telegram_id
):
    query = """
        SELECT EXISTS(
            SELECT 1
            FROM users
            WHERE telegram_id = $1
        )
    """

    return await pool.fetchval(
        query,
        telegram_id
    )


# =========================================================
# 📋 USER PROFILI
# =========================================================

async def get_user_profile(
    pool,
    telegram_id
):
    query = """
        SELECT
            id,
            telegram_id,
            full_name,
            username,
            phone,
            email,
            created_at,
            cv_file_id
        FROM users
        WHERE telegram_id = $1
    """

    return await pool.fetchrow(
        query,
        telegram_id
    )