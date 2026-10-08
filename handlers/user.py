import html
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards import get_main_keyboard, get_cancel_keyboard, get_moderation_keyboard
from utils import format_user_profile

user_router = Router()

class UserQuestionState(StatesGroup):
    waiting_for_question = State()

@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    
    # Foydalanuvchini bazaga saqlash
    await db.add_or_update_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    is_admin = await db.is_admin(user.id)
    is_teacher = await db.is_teacher(user.id)

    full_name = html.escape(user.full_name)
    welcome_text = (
        f"Assalomu alaykum, <b>{full_name}</b>!\n\n"
        f"Ushbu bot orqali siz <b>Ustozga o'z savollaringizni</b> yo'llashingiz mumkin.\n\n"
        f"📝 Savol berish uchun quyidagi <b>«✍️ Ustozga savol yo'llash»</b> tugmasini bosing."
    )
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher),
        parse_mode="HTML"
    )

@user_router.message(F.text == "ℹ️ Bot haqida")
async def cmd_about(message: Message):
    about_text = (
        "🤖 <b>Ustozga Savol Yo'llash Boti</b>\n\n"
        "Ushbu bot foydalanuvchilar va ustozlar o'rtasida qulay savol-javob ko'prigini ta'minlaydi.\n\n"
        "🔹 <b>Qanday ishlaydi?</b>\n"
        "1. Siz savolingizni yo'llaysiz (matn, audio, rasm va h.k.).\n"
        "2. Savol moderatsiyadan o'tib, ustozga yetkaziladi.\n"
        "3. Ustoz javob bergach, javob to'g'ridan-to'g'ri sizga xabar qilinadi."
    )
    await message.answer(about_text, parse_mode="HTML")

@user_router.message(F.text == "❌ Bekor qilish")
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    
    is_admin = await db.is_admin(message.from_user.id)
    is_teacher = await db.is_teacher(message.from_user.id)
    
    await message.answer(
        "❌ Amaliyot bekor qilindi.",
        reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher)
    )

@user_router.message(F.text == "📋 Mening savollarim")
async def cmd_my_questions(message: Message):
    user_id = message.from_user.id
    questions = await db.get_user_questions(user_id, limit=5)
    
    if not questions:
        await message.answer("Siz hali birorta ham savol yubormagansiz.")
        return
    
    text = "📋 <b>Oxirgi yuborgan savollaringiz:</b>\n\n"
    status_emojis = {
        "pending": "⏳ Ko'rib chiqilmoqda (Kutilmoqda)",
        "approved": "✅ Ustozga yetkazildi (Javob kutilmoqda)",
        "rejected": "❌ Rad etildi",
        "answered": "🎓 Javob berildi"
    }

    for q in questions:
        q_id = q['id']
        status_str = status_emojis.get(q['status'], q['status'])
        q_type = q['question_type']
        short_content = html.escape((q['text_content'] or q['media_caption'] or f"[{q_type} xabar]")[:60])
        
        text += (
            f"<b>Savol #{q_id}</b> ({q['created_at']})\n"
            f"🔸 <b>Holat:</b> {status_str}\n"
            f"🔸 <b>Mazmun:</b> {short_content}...\n"
        )
        if q['status'] == 'answered' and q.get('answer_text'):
            ans_short = html.escape(q['answer_text'][:80])
            text += f"💬 <b>Ustoz javobi:</b> {ans_short}...\n"
        text += "────────────────────\n"
        
    await message.answer(text, parse_mode="HTML")

@user_router.message(F.text == "✍️ Ustozga savol yo'llash")
async def start_question_flow(message: Message, state: FSMContext):
    await state.set_state(UserQuestionState.waiting_for_question)
    await message.answer(
        "✍️ <b>Savolingizni yozing yoki ovozli xabar/rasm ko'rinishida yuboring:</b>\n\n"
        "<i>(Savolni batafsil va tushunarli qilib yozing)</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

@user_router.message(UserQuestionState.waiting_for_question)
async def process_question_input(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    full_name = user.full_name
    username = user.username
    user_id = user.id

    # Savol turi va mazmunini aniqlash
    q_type = "text"
    text_content = None
    media_file_id = None
    media_caption = None

    if message.text:
        q_type = "text"
        text_content = message.text
    elif message.photo:
        q_type = "photo"
        media_file_id = message.photo[-1].file_id
        media_caption = message.caption
    elif message.voice:
        q_type = "voice"
        media_file_id = message.voice.file_id
        media_caption = message.caption
    elif message.audio:
        q_type = "audio"
        media_file_id = message.audio.file_id
        media_caption = message.caption
    elif message.video:
        q_type = "video"
        media_file_id = message.video.file_id
        media_caption = message.caption
    elif message.document:
        q_type = "document"
        media_file_id = message.document.file_id
        media_caption = message.caption
    else:
        await message.answer("Iltimos, matn, rasm, ovozli xabar yoki hujjat ko'rinishida yuboring.")
        return

    # Bazaga saqlash
    q_id = await db.create_question(
        user_telegram_id=user_id,
        user_full_name=full_name,
        username=username,
        question_type=q_type,
        text_content=text_content,
        media_file_id=media_file_id,
        media_caption=media_caption
    )

    await state.clear()

    # Foydalanuvchiga tasdiq xabari
    is_admin = await db.is_admin(user_id)
    is_teacher = await db.is_teacher(user_id)
    await message.answer(
        f"✅ <b>Savolingiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"Savol raqami: <b>#{q_id}</b>\n"
        f"Hozirda savolingiz adminlar tomonidan ko'rib chiqilmoqda. Tasdiqlangach, ustozga yetkaziladi.",
        reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher),
        parse_mode="HTML"
    )

    # Barcha adminlarga yuborish
    admins = await db.get_all_admins()
    user_card = format_user_profile(
        user_id=user_id,
        full_name=full_name,
        username=username,
        question_id=q_id
    )

    admin_keyboard = get_moderation_keyboard(q_id)

    for admin in admins:
        adm_id = admin['telegram_id']
        try:
            if q_type == "text":
                admin_msg = (
                    f"📩 <b>YANGI SAVOL KELDI (#{q_id})</b>\n\n"
                    f"{user_card}\n"
                    f"📝 <b>Savol mazmuni:</b>\n"
                    f"{html.escape(text_content)}"
                )
                await bot.send_message(
                    chat_id=adm_id,
                    text=admin_msg,
                    reply_markup=admin_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "photo":
                cap = f"📩 <b>YANGI SAVOL KELDI (#{q_id})</b>\n\n{user_card}"
                if media_caption:
                    cap += f"\n📝 <b>Izoh:</b> {html.escape(media_caption)}"
                await bot.send_photo(
                    chat_id=adm_id,
                    photo=media_file_id,
                    caption=cap,
                    reply_markup=admin_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "voice":
                cap = f"📩 <b>YANGI SAVOL (OVOZLI) (#{q_id})</b>\n\n{user_card}"
                await bot.send_voice(
                    chat_id=adm_id,
                    voice=media_file_id,
                    caption=cap,
                    reply_markup=admin_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "audio":
                cap = f"📩 <b>YANGI SAVOL (AUDIO) (#{q_id})</b>\n\n{user_card}"
                await bot.send_audio(
                    chat_id=adm_id,
                    audio=media_file_id,
                    caption=cap,
                    reply_markup=admin_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "video":
                cap = f"📩 <b>YANGI SAVOL (VIDEO) (#{q_id})</b>\n\n{user_card}"
                if media_caption:
                    cap += f"\n📝 <b>Izoh:</b> {html.escape(media_caption)}"
                await bot.send_video(
                    chat_id=adm_id,
                    video=media_file_id,
                    caption=cap,
                    reply_markup=admin_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "document":
                cap = f"📩 <b>YANGI SAVOL (HUJJAT) (#{q_id})</b>\n\n{user_card}"
                if media_caption:
                    cap += f"\n📝 <b>Izoh:</b> {html.escape(media_caption)}"
                await bot.send_document(
                    chat_id=adm_id,
                    document=media_file_id,
                    caption=cap,
                    reply_markup=admin_keyboard,
                    parse_mode="HTML"
                )
        except Exception as e:
            # Agar biror admin botni bloklagan bo'lsa
            print(f"Error sending question #{q_id} to admin {adm_id}: {e}")
