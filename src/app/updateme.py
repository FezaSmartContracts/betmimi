
import asyncio
import logging
from sqlalchemy import select

from app.core.config import settings
from app.core.db.database import AsyncSession, local_session
from app.models.user import User

#-------------NOTE------------#
# For testing purposes only. Should be deleted after
# docker-compose run --rm web python -m app.updateme

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_first_user(session: AsyncSession) -> None:
    try:
        public_address = settings.ADMIN_PUBLIC_ADDRESS

        query = select(User).filter_by(public_address=public_address)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            user.public_address = user.public_address.lower()
            await session.commit()

            logger.info(f"Admin user with public address {public_address} Updated successfully.")

        else:
            logger.info(f"Admin user with public address {public_address} doesn't exist.")

    except Exception as e:
        logger.error(f"Error Updating admin user: {e}")

async def main():
    async with local_session() as session:
        await create_first_user(session)

if __name__ == "__main__":
    asyncio.run(main())
