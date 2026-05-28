import asyncio
import logging
from app.bot import bot, dp
from app.handlers.user import router as user_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_routers():
    dp.include_routers(user_router)


async def main():
    register_routers()
    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())