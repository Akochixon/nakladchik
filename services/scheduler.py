# services/scheduler.py
from datetime import datetime, time
from aiogram import Bot
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from models import Invoice
from config import ADMIN_IDS

async def send_daily_summary(bot: Bot, session_pool: async_sessionmaker):
    """Har kuni soat 20:00 da adminlarga kunlik summary yuborish"""
    async with session_pool() as session:
        today_start = datetime.combine(datetime.utcnow().date(), time.min)
        
        stmt = select(Invoice).where(Invoice.created_at >= today_start)
        result = await session.execute(stmt)
        today_invoices = result.scalars().all()
        
        count = len(today_invoices)
        total_sum = sum(inv.total_sum for inv in today_invoices)
        
        msg = (
            f"📊 <b>Kunlik Hisobot Summary ({datetime.now().strftime('%d.%m.%Y')})</b>\n\n"
            f"📥 Bugun qabul qilingan nakladnoylar: <b>{count} ta</b>\n"
            f"💰 Bugungi umumiy summa: <b>{total_sum:,.2f} so'm</b>\n\n"
            f"Batafsil ma'lumot olish uchun /report komandasini yuboring."
        )
        
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, msg, parse_mode="HTML")
            except Exception as e:
                print(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")