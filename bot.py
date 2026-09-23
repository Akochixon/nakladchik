# bot.py
import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import BOT_TOKEN, GEMINI_API_KEY
from database import engine, AsyncSessionLocal
from ocr import GeminiOCR
from handlers import start, invoice, admin
from services.scheduler import send_daily_summary

async def main():
    # --- Supabase'da jadvallarni avtomatik yaratish ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # --------------------------------------------------
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # OCR servisini tayyorlash
    ocr_service = GeminiOCR(api_key=GEMINI_API_KEY)

    # Middleware orqali har bir handlerga DB session va OCR servisini uzatish
    @dp.update.outer_middleware()
    async def db_session_middleware(handler, event, data):
        async with AsyncSessionLocal() as session:
            data["session"] = session
            data["ocr_service"] = ocr_service
            return await handler(event, data)

    # Routerlarni ro'yxatdan o'tkazish
    dp.include_router(start.router)
    dp.include_router(invoice.router)
    dp.include_router(admin.router)

    # Kunlik avtomatik hisobot (har kuni soat 20:00 da)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_summary,
        trigger=CronTrigger(hour=20, minute=0),
        kwargs={"bot": bot, "session_pool": AsyncSessionLocal}
    )
    scheduler.start()

    print("🚀 Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())