import html
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards import get_main_keyboard, get_cancel_keyboard

teacher_router = Router()

class TeacherReplyState(StatesGroup):
    waiting_for_answer = State()

@teacher_router.message(F.text == "👨‍🏫 Ustoz Paneli")
async def open_teacher_panel(message: Message):
    user_id = message.from_user.id
    if not await db.is_teacher(user_id):
        await message.answer("Siz ustozlar ro'yxatida emassiz.")
        return

    text = (
        "👨‍🏫 <b>Ustoz Paneli</b>\n\n"
        "Sizga adminlar tomonidan tasdiqlangan savollar to'g'ridan-to'g'ri xabar sifatida yuboriladi.\n"
        "Har bir savol ostidagi <b>«💬 Javob berish»</b> tugmasi orqali o'quvchiga javob yo'llashingiz mumkin."
    )
    await message.answer(text, parse_mode="HTML")

@teacher_router.callback_query(F.data.startswith("teach_rep_"))
async def cb_teacher_start_reply(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    is_teach = await db.is_teacher(user_id)
    is_adm = await db.is_admin(user_id)

    if not (is_teach or is_adm):
        await callback.answer("Sizda javob berish huquqi yo'q.", show_alert=True)
        return

    q_id = int(callback.data.replace("teach_rep_", ""))
    question = await db.get_question(q_id)

    if not question:
        await callback.answer("Savol topilmadi.", show_alert=True)
        return

    if question['status'] == 'answered':
        await callback.answer("Bu savolga allaqachon javob berilgan.", show_alert=True)
        return

    if question['status'] == 'rejected':
        await callback.answer("Bu savol rad etilgan.", show_alert=True)
        return

    await state.set_state(TeacherReplyState.waiting_for_answer)
    await state.update_data(
        question_id=q_id,
        origin_chat_id=callback.message.chat.id,
        origin_message_id=callback.message.message_id,
        origin_text=callback.message.text,
        origin_caption=callback.message.caption
    )

    role_label = "Ustoz" if is_teach else "Admin"
    text = (
        f"✍️ <b>#{q_id} raqamli savolga {role_label} sifatida javob yozish:</b>\n\n"
        f"Javobingizni <b>matn, ovozli xabar (audio/voice), rasm, video yoki hujjat</b> ko'rinishida yuboring."
    )
    await callback.message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()

@teacher_router.message(TeacherReplyState.waiting_for_answer)
async def process_teacher_answer(message: Message, state: FSMContext, bot: Bot):
    sender = message.from_user
    data = await state.get_data()
    q_id = data.get("question_id")

    question = await db.get_question(q_id)
    if not question:
        await state.clear()
        await message.answer("Savol ma'lumotlari topilmadi.")
        return

    ans_text = None
    ans_media_id = None
    ans_media_type = None

    if message.text:
        ans_text = message.text
        ans_media_type = "text"
    elif message.voice:
        ans_media_id = message.voice.file_id
        ans_media_type = "voice"
        ans_text = message.caption
    elif message.audio:
        ans_media_id = message.audio.file_id
        ans_media_type = "audio"
        ans_text = message.caption
    elif message.photo:
        ans_media_id = message.photo[-1].file_id
        ans_media_type = "photo"
        ans_text = message.caption
    elif message.video:
        ans_media_id = message.video.file_id
        ans_media_type = "video"
        ans_text = message.caption
    elif message.document:
        ans_media_id = message.document.file_id
        ans_media_type = "document"
        ans_text = message.caption
    else:
        await message.answer("Iltimos, matn, rasm, ovozli xabar, video yoki hujjat ko'rinishida javob yuboring.")
        return

    # Bazada saqlash
    await db.save_answer(
        question_id=q_id,
        answered_by=sender.id,
        answer_text=ans_text,
        answer_media_id=ans_media_id,
        answer_media_type=ans_media_type
    )

    is_admin = await db.is_admin(sender.id)
    is_teacher = await db.is_teacher(sender.id)

    sender_role = "Ustoz" if is_teacher else "Admin"
    sender_title = "USTOZDAN" if is_teacher else "ADMINDAN"

    # 1. FOYDALANUVCHIGA JAVOBNI YUBORISH
    user_id = question['user_telegram_id']
    orig_content = html.escape((question['text_content'] or question['media_caption'] or f"[{question['question_type']} savol]")[:200])
    
    header = (
        f"🎓 <b>SAVOLINGIZGA {sender_title} JAVOB KELDI!</b>\n\n"
        f"<b>Savol #{q_id}:</b> <i>{orig_content}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
    )

    try:
        if ans_media_type == "text":
            user_msg = f"{header}💬 <b>{sender_role} javobi:</b>\n\n{html.escape(ans_text)}"
            await bot.send_message(chat_id=user_id, text=user_msg, parse_mode="HTML")
        elif ans_media_type == "voice":
            caption = f"{header}💬 <b>{sender_role} ovozli javobi</b>"
            await bot.send_voice(chat_id=user_id, voice=ans_media_id, caption=caption, parse_mode="HTML")
        elif ans_media_type == "audio":
            caption = f"{header}💬 <b>{sender_role} audio javobi</b>"
            if ans_text:
                caption += f"\n\n{html.escape(ans_text)}"
            await bot.send_audio(chat_id=user_id, audio=ans_media_id, caption=caption, parse_mode="HTML")
        elif ans_media_type == "photo":
            caption = f"{header}💬 <b>{sender_role} javobi:</b>"
            if ans_text:
                caption += f"\n\n{html.escape(ans_text)}"
            await bot.send_photo(chat_id=user_id, photo=ans_media_id, caption=caption, parse_mode="HTML")
        elif ans_media_type == "video":
            caption = f"{header}💬 <b>{sender_role} video javobi:</b>"
            if ans_text:
                caption += f"\n\n{html.escape(ans_text)}"
            await bot.send_video(chat_id=user_id, video=ans_media_id, caption=caption, parse_mode="HTML")
        elif ans_media_type == "document":
            caption = f"{header}💬 <b>{sender_role} yuborgan fayl:</b>"
            if ans_text:
                caption += f"\n\n{html.escape(ans_text)}"
            await bot.send_document(chat_id=user_id, document=ans_media_id, caption=caption, parse_mode="HTML")
        
        await message.answer(
            f"✅ <b>Javobingiz muvaffaqiyatli foydalanuvchiga yetkazildi!</b> (#{q_id})",
            reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(
            f"⚠️ Javob saqlandi, lekin foydalanuvchiga yuborishda xatolik: {e}",
            reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher)
        )

    # Dastlabki xabardagi tugmalarni olib tashlab, javob berilganligini ko'rsatish
    origin_chat_id = data.get("origin_chat_id")
    origin_message_id = data.get("origin_message_id")
    origin_text = data.get("origin_text")
    origin_caption = data.get("origin_caption")

    if origin_chat_id and origin_message_id:
        try:
            responder_display = html.escape(sender.full_name)
            notice = f"\n\n<i>💬 Javob berildi ({sender_role}: {responder_display})</i>"
            if origin_text:
                await bot.edit_message_text(
                    chat_id=origin_chat_id,
                    message_id=origin_message_id,
                    text=origin_text + notice,
                    parse_mode="HTML"
                )
            elif origin_caption:
                await bot.edit_message_caption(
                    chat_id=origin_chat_id,
                    message_id=origin_message_id,
                    caption=origin_caption + notice,
                    parse_mode="HTML"
                )
        except Exception:
            pass

    await state.clear()
