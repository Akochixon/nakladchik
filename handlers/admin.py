# handlers/admin.py
import io
import pandas as pd
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models import Invoice
from config import ADMIN_IDS

router = Router()

@router.message(Command("report"))
async def export_excel_report(message: types.Message, session: AsyncSession):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Ushbu komanda faqat adminlar uchun!")
        return

    await message.answer("📊 Excel hisobot shakllantirilmoqda, kuting...")

    stmt = select(Invoice).options(
        selectinload(Invoice.items),
        selectinload(Invoice.customer),
        selectinload(Invoice.sales_agent),
        selectinload(Invoice.expediter)
    )
    result = await session.execute(stmt)
    invoices = result.scalars().all()

    if not invoices:
        await message.answer("Bazada hali nakladnoylar mavjud emas.")
        return

    data = []
    for inv in invoices:
        for item in inv.items:
            data.append({
                "Nakladnoy №": inv.invoice_number,
                "Sana": inv.date_str,
                "Xaridor": inv.customer.name if inv.customer else "-",
                "Xaridor Kodi": inv.customer.client_code if inv.customer else "-",
                "Agent": inv.sales_agent.full_name if inv.sales_agent else "-",
                "Ekspeditor": inv.expediter.full_name if inv.expediter else "-",
                "Tovar kodi": item.product.code if item.product else "-",
                "Tovar nomi": item.product.name if item.product else "-",
                "Soni (Case)": item.quantity,
                "Narxi": item.unit_price,
                "Jami qator summasi": item.line_total,
                "Hujjat Jami Summasi": inv.total_sum,
                "Kiritilgan vaqti": inv.created_at.strftime("%Y-%m-%d %H:%M")
            })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Nakladnoylar')
        
    output.seek(0)

    file = BufferedInputFile(output.read(), filename="nakladnoylar_hisoboti.xlsx")
    await message.answer_document(file, caption="📈 Barcha nakladnoylar bo'yicha hisobot.")