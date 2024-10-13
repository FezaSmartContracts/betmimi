import asyncio
import logging
from datetime import timezone, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, MetaData, String, Table, insert, select

from ..app.core.config import settings
from ..app.core.db.database import AsyncSession, async_engine, local_session
from ..app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_first_user(session: AsyncSession) -> None:
    try:
        public_address = settings.ADMIN_PUBLIC_ADDRESS
        email = settings.ADMIN_EMAIL

        query = select(User).filter_by(public_address=public_address)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            metadata = MetaData()
            user_table = Table(
                "user",
                metadata,
                Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
                Column("public_address", String(42), nullable=False, unique=True, index=True),
                Column("email", String(50), nullable=True, unique=True, index=True),
                Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False),
                Column("updated_at", DateTime, nullable=True),
                Column("is_superuser", Boolean, default=True),
            )

            data = {
                "public_address": public_address,
                "email": email,
                "is_superuser": True,
                "created_at": datetime.now(timezone.utc),
            }

            stmt = insert(user_table).values(data)
            async with async_engine.connect() as conn:
                await conn.execute(stmt)
                await conn.commit()

            logger.info(f"Admin user with public address {public_address} created successfully.")

        else:
            logger.info(f"Admin user with public address {public_address} already exists.")

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")

async def main():
    async with local_session() as session:
        await create_first_user(session)

if __name__ == "__main__":
    asyncio.run(main())
