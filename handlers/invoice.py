from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

class InvoiceState(StatesGroup):
    waiting_for_confirmation = State()
    duplicate_handling = State()

@router.message(F.photo)
async def handle_invoice_photo(message: types.Message, state: FSMContext, session: AsyncSession, ocr_service):
    await message.answer("🔍 Nakladnoy skanerlanmoqda, kuting...")
    
    # Rasmni yuklab olish
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file_info.file_path)
    
    # OCR orqali o'qish
    parsed_data = await ocr_service.parse_invoice_image(file_bytes.read())
    parsed_data["photo_file_id"] = photo.file_id
    
    # DB'da dublikatni tekshirish
    stmt = select(Invoice).where(Invoice.invoice_number == parsed_data["invoice_number"])
    result = await session.execute(stmt)
    existing_invoice = result.scalars().first()
    
    if existing_invoice:
        await state.update_data(parsed_data=parsed_data, existing_id=existing_invoice.id)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, dublikat sifatida saqlash", callback_data="dup_yes"),
                InlineKeyboardButton(text="❌ Yo'q, yangi alohida hujjat", callback_data="dup_no")
            ]
        ])
        text = (
            f"⚠️ <b>Diqqat! Dublikat aniqlandi!</b>\n"
            f"<b>№{parsed_data['invoice_number']}</b> raqamli nakladnoy allaqachon DB'da mavjud.\n"
            f"Xaridor: {parsed_data['customer']['name']}\n"
            f"Jami summa: {parsed_data['total_sum']:,.2f} so'm\n\n"
            f"Siz ham shu hujjatni topshirmoqchimisiz?"
        )
        await state.set_state(InvoiceState.duplicate_handling)
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        return

    # Yangi hujjat preview ko'rsatish
    await show_invoice_preview(message, state, parsed_data)

async def show_invoice_preview(message_or_call, state: FSMContext, data: dict):
    items_text = ""
    for idx, item in enumerate(data.get("items", []), 1):
        items_text += f"{idx}. {item['name']} - {item['quantity']} dona x {item['unit_price']:,.0f} = {item['line_total']:,.0f}\n"

    preview_text = (
        f"📄 <b>Nakladnoy № {data.get('invoice_number')}</b>\n"
        f"📅 Sana: {data.get('date')}\n"
        f"🏢 Xaridor: {data.get('customer', {}).get('name')}\n"
        f"👤 Agent: {data.get('sales_agent')}\n"
        f"🚚 Ekspeditor: {data.get('expediter')}\n\n"
        f"<b>Tovarlar:</b>\n{items_text}\n"
        f"📊 <b>Jami dona:</b> {data.get('total_qty')}\n"
        f"💰 <b>Jami summa:</b> {data.get('total_sum'):,.2f} so'm"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ To'g'ri (Saqlash)", callback_data="confirm_save"),
            InlineKeyboardButton(text="❌ Xato (Qayta kiritish)", callback_data="reject_edit")
        ]
    ])
    
    await state.update_data(parsed_data=data)
    await state.set_state(InvoiceState.waiting_for_confirmation)
    
    if isinstance(message_or_call, types.Message):
        await message_or_call.answer(preview_text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message_or_call.message.edit_text(preview_text, reply_markup=keyboard, parse_mode="HTML")