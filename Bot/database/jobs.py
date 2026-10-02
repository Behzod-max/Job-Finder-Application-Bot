# =========================================================
# 💼 JOBS DATABASE
# =========================================================


# =========================================================
# 🔎 JOB QIDIRISH
# =========================================================

async def get_jobs(
    pool,
    title,
    location
):
    query = """
        SELECT
            id,
            title,
            company,
            location,
            salary,
            description,
            requirements,
            created_at
        FROM jobs
        WHERE title ILIKE $1
          AND LOWER(location) = LOWER($2)
        ORDER BY created_at DESC
    """

    return await pool.fetch(
        query,
        f"%{title}%",
        location
    )


# =========================================================
# 🔎 FAQAT TITLE BO‘YICHA QIDIRISH
# =========================================================

async def search_jobs(
    pool,
    keyword
):
    query = """
        SELECT
            id,
            title,
            company,
            location,
            salary,
            description,
            requirements,
            created_at
        FROM jobs
        WHERE
            title ILIKE $1
            OR company ILIKE $1
            OR description ILIKE $1
            OR requirements ILIKE $1
        ORDER BY created_at DESC
    """

    return await pool.fetch(
        query,
        f"%{keyword}%"
    )


# =========================================================
# 📍 LOCATION BO‘YICHA QIDIRISH
# =========================================================

async def get_jobs_by_location(
    pool,
    location
):
    query = """
        SELECT
            id,
            title,
            company,
            location,
            salary,
            description,
            requirements,
            created_at
        FROM jobs
        WHERE LOWER(location) = LOWER($1)
        ORDER BY created_at DESC
    """

    return await pool.fetch(
        query,
        location
    )


# =========================================================
# 💼 BARCHA VAKANSIYALARNI OLISH
# =========================================================

async def get_all_jobs(
    pool
):
    query = """
        SELECT
            id,
            title,
            company,
            location,
            salary,
            description,
            requirements,
            created_at
        FROM jobs
        ORDER BY id DESC
    """

    return await pool.fetch(
        query
    )


# =========================================================
# 🔎 BIRTA VAKANSIYANI OLISH
# =========================================================

async def get_job_by_id(
    pool,
    job_id
):
    query = """
        SELECT
            id,
            title,
            company,
            location,
            salary,
            description,
            requirements,
            created_at
        FROM jobs
        WHERE id = $1
    """

    return await pool.fetchrow(
        query,
        job_id
    )


# =========================================================
# ➕ YANGI VAKANSIYA QO‘SHISH
# =========================================================

async def create_job(
    pool,
    title,
    company,
    location,
    salary,
    description,
    requirements
):
    query = """
        INSERT INTO jobs (
            title,
            company,
            location,
            salary,
            description,
            requirements
        )
        VALUES (
            $1,
            $2,
            $3,
            $4,
            $5,
            $6
        )
        RETURNING id
    """

    return await pool.fetchval(
        query,
        title,
        company,
        location,
        salary,
        description,
        requirements
    )


# =========================================================
# ✏️ JOBNI YANGILASH
# =========================================================

async def update_job(
    pool,
    job_id,
    title,
    company,
    location,
    salary,
    description,
    requirements
):
    query = """
        UPDATE jobs
        SET
            title = $1,
            company = $2,
            location = $3,
            salary = $4,
            description = $5,
            requirements = $6
        WHERE id = $7
    """

    await pool.execute(
        query,
        title,
        company,
        location,
        salary,
        description,
        requirements,
        job_id
    )


# =========================================================
# 🗑 VAKANSIYANI O‘CHIRISH
# =========================================================

async def delete_job(
    pool,
    job_id
):
    query = """
        DELETE FROM jobs
        WHERE id = $1
    """

    return await pool.execute(
        query,
        job_id
    )