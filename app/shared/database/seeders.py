from sqlalchemy import select
from dh_shared.models.people.person import Person
from dh_shared.models.auth.user import AuthUser
from dh_shared.enums import EVerificationStatus
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.security import hash_password
from app.shared.utils.logger import logger

async def seed_admin_user():
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        query = select(AuthUser).where(AuthUser.username == "admin")
        result = await session.execute(query)
        if result.scalar_one_or_none():
            await logger.info("Admin user already exists. Skipping...", event="db.seed.skip")
            return

        await logger.info("Seeding admin user...", event="db.seed.start")
        # 1. Create Person
        person = Person(
            first_name="System",
            last_name="Admin",
            verification_status=EVerificationStatus.APPROVED
        )
        session.add(person)
        await session.flush() # Get id_person

        # 2. Create AuthUser
        admin = AuthUser(
            id_person=person.id,
            username="admin",
            password_hash=hash_password("admin123"),
            is_active=True
        )
        session.add(admin)
        await session.commit()
        await logger.info("Admin user seeded successfully!", event="db.seed.success")
