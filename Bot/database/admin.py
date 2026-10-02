async def get_statistics(pool):

    users = await pool.fetchval(
        "SELECT COUNT(*) FROM users"
    )

    jobs = await pool.fetchval(
        "SELECT COUNT(*) FROM jobs"
    )

    applications = await pool.fetchval(
        "SELECT COUNT(*) FROM applications"
    )

    pending = await pool.fetchval(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE status = 'pending'
        """
    )

    accepted = await pool.fetchval(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE status = 'accepted'
        """
    )

    rejected = await pool.fetchval(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE status = 'rejected'
        """
    )

    return {
        "users": users,
        "jobs": jobs,
        "applications": applications,
        "pending": pending,
        "accepted": accepted,
        "rejected": rejected,
    }