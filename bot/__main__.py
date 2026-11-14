import asyncio
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
import sys
from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.handlers import registration, user
from bot.config import config
from bot.middleware.db import DbSessionMiddleware
from bot.database.engine import create_db, session_maker

logger = logging.getLogger(__name__)

async def on_startup(bot: Bot) -> None:
    await create_db()
    await bot.set_my_commands([BotCommand(command="start", description="Запуск и регистрация")])
    print("База данных успешно подключена и инициализирована.")

async def main():
    try:
        bot = Bot( 
            token=config.bot_token.get_secret_value(), 
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        )

        dp = Dispatcher()

        dp.startup.register(on_startup)

        dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
        dp.include_router(registration.registration_router)
        dp.include_router(user.user_router)
        
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot started successfully")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
