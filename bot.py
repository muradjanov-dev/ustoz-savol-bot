import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, SUPER_ADMINS
from database import db
from handlers import user_router, admin_router, teacher_router

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Bot ishga tushganda ma'lumotlar bazasini initsializatsiya qilish"""
    logger.info("Initializing database...")
    await db.init_db()
    
    bot_info = await bot.get_me()
    logger.info(f"Bot successfully started as @{bot_info.username} (ID: {bot_info.id})")
    logger.info(f"Super Admins configured: {SUPER_ADMINS}")

    await notify_admins_started(bot, bot_info.username)

async def notify_admins_started(bot: Bot, bot_username: str):
    """Bot ishga tushgani haqida barcha adminlarga xabar yuborish"""
    admin_ids = set(SUPER_ADMINS)
    admin_ids.update(admin["telegram_id"] for admin in await db.get_all_admins())

    text = (
        "✅ <b>Bot endi ishlayapti!</b>\n\n"
        "Uni kanallarda e'lon qilishingiz mumkin.\n\n"
        f"🤖 @{bot_username}\n"
        f"🔗 https://t.me/{bot_username}"
    )

    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text)
            logger.info(f"Startup notification sent to admin {admin_id}")
        except Exception as e:
            # Admin botni hali /start qilmagan yoki bloklagan bo'lishi mumkin
            logger.warning(f"Could not notify admin {admin_id}: {e}")

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error("BOT_TOKEN aniqlanmadi! Iltimos .env faylini yoki muhit o'zgaruvchilarini tekshiring.")
        return

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Routerni ro'yxatga olish
    dp.include_router(admin_router)
    dp.include_router(teacher_router)
    dp.include_router(user_router)

    dp.startup.register(on_startup)

    logger.info("Starting polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
