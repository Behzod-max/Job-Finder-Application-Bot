# =========================================================
# 📄 APPLICATIONS DATABASE
# =========================================================


# =========================================================
# 👤 USERNING BARCHA ARIZALARI
# =========================================================

async def get_user_applications(
    pool,
    user_id
):
    query = """
        SELECT
            a.id,
            a.status,
            a.created_at,
            a.cv_file_id,

            j.id AS job_id,
            j.title,
            j.company,
            j.location,
            j.salary

        FROM applications a

        JOIN jobs j
            ON a.job_id = j.id

        WHERE a.user_id = $1

        ORDER BY a.created_at DESC
    """

    return await pool.fetch(
        query,
        user_id
    )


# =========================================================
# 👨‍💼 ADMIN UCHUN PENDING ARIZALAR
# =========================================================

async def get_pending_applications(
    pool
):
    query = """
        SELECT
            a.id,
            a.user_id,
            a.job_id,
            a.cv_file_id,
            a.status,
            a.created_at,

            u.full_name,
            u.username,
            u.phone,
            u.email,

            j.title,
            j.company,
            j.location,
            j.salary

        FROM applications a

        JOIN users u
            ON a.user_id = u.telegram_id

        JOIN jobs j
            ON a.job_id = j.id

        WHERE a.status = 'pending'

        ORDER BY a.created_at DESC
    """

    return await pool.fetch(
        query
    )


# =========================================================
# 📄 ADMIN UCHUN BITTA APPLICATION
# =========================================================

async def get_application_by_id(
    pool,
    application_id
):
    query = """
        SELECT
            a.id,
            a.user_id,
            a.job_id,
            a.cv_file_id,
            a.status,
            a.created_at,

            u.full_name,
            u.username,
            u.phone,
            u.email,

            j.title,
            j.company,
            j.location,
            j.salary,
            j.description,
            j.requirements

        FROM applications a

        JOIN users u
            ON a.user_id = u.telegram_id

        JOIN jobs j
            ON a.job_id = j.id

        WHERE a.id = $1
    """

    return await pool.fetchrow(
        query,
        application_id
    )


# =========================================================
# 👤 USER UCHUN BITTA APPLICATION
# =========================================================

async def get_user_application_by_id(
    pool,
    application_id,
    user_id
):
    query = """
        SELECT
            a.id,
            a.user_id,
            a.job_id,
            a.cv_file_id,
            a.status,
            a.created_at,

            j.title,
            j.company,
            j.location,
            j.salary,
            j.description,
            j.requirements

        FROM applications a

        JOIN jobs j
            ON a.job_id = j.id

        WHERE a.id = $1
          AND a.user_id = $2
    """

    return await pool.fetchrow(
        query,
        application_id,
        user_id
    )


# =========================================================
# 🔄 APPLICATION STATUSINI O'ZGARTIRISH
# =========================================================

async def update_application_status(
    pool,
    application_id,
    status
):
    query = """
        UPDATE applications
        SET status = $1
        WHERE id = $2
    """

    await pool.execute(
        query,
        status,
        application_id
    )


# =========================================================
# 📝 YANGI APPLICATION YARATISH
# =========================================================

async def create_application(
    pool,
    user_id,
    job_id,
    cv_file_id
):
    query = """
        INSERT INTO applications (
            user_id,
            job_id,
            cv_file_id,
            status
        )
        VALUES (
            $1,
            $2,
            $3,
            'pending'
        )
        RETURNING id
    """

    return await pool.fetchval(
        query,
        user_id,
        job_id,
        cv_file_id
    )


# =========================================================
# 🔎 USERNING SHU VAKANSIYAGA ARIZASINI TEKSHIRISH
# =========================================================

async def get_user_job_application(
    pool,
    user_id,
    job_id
):
    query = """
        SELECT
            id,
            status,
            created_at,
            cv_file_id

        FROM applications

        WHERE user_id = $1
          AND job_id = $2

        ORDER BY created_at DESC

        LIMIT 1
    """

    return await pool.fetchrow(
        query,
        user_id,
        job_id
    )


# =========================================================
# 📊 BARCHA APPLICATIONLAR SONI
# =========================================================

async def get_applications_count(
    pool
):
    query = """
        SELECT COUNT(*)
        FROM applications
    """

    return await pool.fetchval(
        query
    )


# =========================================================
# 🟡 PENDING APPLICATIONLAR SONI
# =========================================================

async def get_pending_applications_count(
    pool
):
    query = """
        SELECT COUNT(*)
        FROM applications
        WHERE status = 'pending'
    """

    return await pool.fetchval(
        query
    )


# =========================================================
# 🟢 ACCEPTED APPLICATIONLAR SONI
# =========================================================

async def get_accepted_applications_count(
    pool
):
    query = """
        SELECT COUNT(*)
        FROM applications
        WHERE status = 'accepted'
    """

    return await pool.fetchval(
        query
    )


# =========================================================
# 🔴 REJECTED APPLICATIONLAR SONI
# =========================================================

async def get_rejected_applications_count(
    pool
):
    query = """
        SELECT COUNT(*)
        FROM applications
        WHERE status = 'rejected'
    """

    return await pool.fetchval(
        query
    )