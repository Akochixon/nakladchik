from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import TelegramUser
from config import ADMIN_IDS

router = Router()

class RegisterState(StatesGroup):
    waiting_for_name = State()
    waiting_for_jshshir = State()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id
    
    # Admin bo'lsa birdan o'tkazish
    if user_id in ADMIN_IDS:
        await message.answer("👋 Xush kelibsiz, Admin! Nakladnoy rasmini yuborishingiz mumkin.")
        return

    # Foydalanuvchi bazada borligini tekshirish
    stmt = select(TelegramUser).where(TelegramUser.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if user:
        if user.status == "approved":
            await message.answer("✅ Siz tasdiqlangansiz! Nakladnoy rasmini yuborishingiz mumkin.")
        elif user.status == "pending":
            await message.answer("⏳ Sizning so'rovingiz adminlar ko'rib chiqish jarayonida. Kuting...")
        else:
            await message.answer("🚫 Sizning so'rovingiz rad etilgan.")
        return

    await message.answer("Assalomu alaykum! Tizimdan foydalanish uchun Ism va Familyangizni kiriting:")
    await state.set_state(RegisterState.waiting_for_name)

@router.message(RegisterState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Rahmat. Endi JSHSHIR (ID card raqamingiz) ni kiriting:")
    await state.set_state(RegisterState.waiting_for_jshshir)

@router.message(RegisterState.waiting_for_jshshir)
async def process_jshshir(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    full_name = data.get("full_name")
    jshshir = message.text

    new_user = TelegramUser(
        telegram_id=message.from_user.id,
        full_name=full_name,
        id_number=jshshir,
        status="pending"
    )
    session.add(new_user)
    await session.commit()
    await state.clear()

    await message.answer("✅ So'rovingiz adminga yuborildi. Tasdiqlanishini kuting.")

    # Adminlarga inline tugma bilan xabar yuborish
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"user_approve_{new_user.id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"user_reject_{new_user.id}")
        ]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"👤 <b>Yangi foydalanuvchi so'rovi:</b>\n\n"
                f"<b>Ismi:</b> {full_name}\n"
                f"<b>JSHSHIR:</b> {jshshir}\n"
                f"<b>Telegram ID:</b> {message.from_user.id}",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Admin notification error: {e}")

@router.callback_query(F.data.startswith("user_"))
async def handle_user_approval(call: types.CallbackQuery, session: AsyncSession):
    action, target_user_id = call.data.split("_")[1:]
    target_user_id = int(target_user_id)

    stmt = select(TelegramUser).where(TelegramUser.id == target_user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        await call.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    if action == "approve":
        user.status = "approved"
        await session.commit()
        await call.message.edit_text(f"✅ <b>{user.full_name}</b> tasdiqlandi!", parse_mode="HTML")
        try:
            await call.bot.send_message(user.telegram_id, "🎉 So'rovingiz tasdiqlandi! Endi nakladnoy rasmlarini yuborishingiz mumkin.")
        except Exception:
            pass
    else:
        user.status = "rejected"
        await session.commit()
        await call.message.edit_text(f"❌ <b>{user.full_name}</b> rad etildi.", parse_mode="HTML")
        try:
            await call.bot.send_message(user.telegram_id, "❌ Afsuski, so'rovingiz admin tomonidan rad etildi.")
        except Exception:
            pass
    await call.answer()