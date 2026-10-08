import html
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards import (
    get_admin_main_inline,
    get_teachers_manage_inline,
    get_admins_manage_inline,
    get_delete_teacher_inline,
    get_delete_admin_inline,
    get_back_to_admin_main,
    get_teacher_question_inline,
    get_main_keyboard,
    get_cancel_keyboard
)
from utils import format_user_profile, get_id_instruction_text

admin_router = Router()

class AdminAddTeacherState(StatesGroup):
    waiting_for_id = State()
    waiting_for_name = State()

class AdminAddAdminState(StatesGroup):
    waiting_for_id = State()
    waiting_for_name = State()

# --- ADMIN PANEL ENTRY ---
@admin_router.message(F.text == "⚙️ Admin Panel")
@admin_router.message(Command("admin"))
async def open_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if not await db.is_admin(user_id):
        await message.answer("Sizda admin huquqlari mavjud emas.")
        return

    text = (
        "⚙️ <b>Admin Boshqaruv Paneli</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_admin_main_inline(), parse_mode="HTML")

@admin_router.callback_query(F.data == "adm_back_main")
async def cb_admin_back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
    text = (
        "⚙️ <b>Admin Boshqaruv Paneli</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_main_inline(), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "adm_close")
async def cb_admin_close(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer("Admin panel yopildi.")

# --- STATISTIKA ---
@admin_router.callback_query(F.data == "adm_stats")
async def cb_admin_stats(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
    
    stats = await db.get_stats()
    text = (
        "📊 <b>Bot Statistikasi:</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b> {stats.get('total_users', 0)} ta\n"
        f"👨‍🏫 <b>Ustozlar soni:</b> {stats.get('total_teachers', 0)} ta\n"
        f"🛡 <b>Adminlar soni:</b> {stats.get('total_admins', 0)} ta\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"❓ <b>Jami savollar:</b> {stats.get('total_questions', 0)} ta\n"
        f"⏳ <b>Kutilayotgan:</b> {stats.get('pending_questions', 0)} ta\n"
        f"✅ <b>Tasdiqlangan (Ustozda):</b> {stats.get('approved_questions', 0)} ta\n"
        f"🎓 <b>Javob berilgan:</b> {stats.get('answered_questions', 0)} ta\n"
        f"❌ <b>Rad etilgan:</b> {stats.get('rejected_questions', 0)} ta\n"
    )
    await callback.message.edit_text(text, reply_markup=get_back_to_admin_main(), parse_mode="HTML")
    await callback.answer()

# --- ID QO'LLANMASI ---
@admin_router.callback_query(F.data == "adm_id_guide")
async def cb_admin_id_guide(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
    
    guide_text = get_id_instruction_text()
    await callback.message.edit_text(guide_text, reply_markup=get_back_to_admin_main(), parse_mode="HTML")
    await callback.answer()

# --- USTOZLAR BOSHQARUVI ---
@admin_router.callback_query(F.data == "adm_manage_teachers")
async def cb_manage_teachers(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
    
    text = (
        "👨‍🏫 <b>Ustozlar boshqaruvi bo'limi</b>\n\n"
        "Siz yangi ustoz Telegram ID sini qo'shishingiz yoki mavjudlarini o'chirishingiz mumkin."
    )
    await callback.message.edit_text(text, reply_markup=get_teachers_manage_inline(), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "adm_list_teachers")
async def cb_list_teachers(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    teachers = await db.get_all_teachers()
    if not teachers:
        text = "👨‍🏫 Hozircha birorta ham Ustoz qo'shilmagan."
    else:
        text = "📋 <b>Ro'yxatdan o'tgan Ustozlar:</b>\n\n"
        for idx, t in enumerate(teachers, 1):
            name = html.escape(t['name'] or 'Noma\'lum')
            t_id = t['telegram_id']
            text += f"{idx}. <b>{name}</b> — ID: <code>{t_id}</code> (<a href=\"tg://user?id={t_id}\">Profil</a>)\n"

    await callback.message.edit_text(text, reply_markup=get_teachers_manage_inline(), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "adm_add_teacher")
async def cb_add_teacher_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    await state.set_state(AdminAddTeacherState.waiting_for_id)
    text = (
        "➕ <b>Yangi Ustoz qo'shish</b>\n\n"
        "Iltimos, ustozning <b>Telegram ID</b> raqamini yuboring.\n\n"
        "<i>(ID raqamni bilmasangiz, <b>@ScanIDBot</b> orqali bilib olishingiz mumkin)</i>"
    )
    await callback.message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()

@admin_router.message(AdminAddTeacherState.waiting_for_id)
async def process_teacher_id(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if not text.isdigit():
        await message.answer("⚠️ Iltimos, faqat sonlardan iborat to'g'ri Telegram ID kiriting:")
        return

    teacher_id = int(text)
    await state.update_data(teacher_id=teacher_id)
    await state.set_state(AdminAddTeacherState.waiting_for_name)
    await message.answer(
        "Endi ustozning <b>Ism va Familiyasi</b> (yoki laqabi)ni kiriting:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AdminAddTeacherState.waiting_for_name)
async def process_teacher_name(message: Message, state: FSMContext):
    teacher_name = message.text.strip() if message.text else "Ustoz"
    data = await state.get_data()
    teacher_id = data['teacher_id']

    success = await db.add_teacher(
        telegram_id=teacher_id,
        name=teacher_name,
        added_by=message.from_user.id
    )

    await state.clear()
    is_admin = await db.is_admin(message.from_user.id)
    is_teacher = await db.is_teacher(message.from_user.id)

    if success:
        await message.answer(
            f"✅ <b>Ustoz muvaffaqiyatli qo'shildi!</b>\n\n"
            f"👤 <b>Ism:</b> {html.escape(teacher_name)}\n"
            f"🆔 <b>ID:</b> <code>{teacher_id}</code>",
            reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ustozni saqlashda xatolik yuz berdi.",
            reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher)
        )

@admin_router.callback_query(F.data == "adm_del_teacher_list")
async def cb_del_teacher_list(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    teachers = await db.get_all_teachers()
    if not teachers:
        await callback.answer("O'chirish uchun ustozlar mavjud emas.", show_alert=True)
        return

    text = "🗑 <b>O'chirmoqchi bo'lgan Ustozni tanlang:</b>"
    await callback.message.edit_text(text, reply_markup=get_delete_teacher_inline(teachers), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("adm_del_teach_id_"))
async def cb_del_teacher_confirm(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    teacher_id = int(callback.data.replace("adm_del_teach_id_", ""))
    await db.remove_teacher(teacher_id)
    await callback.answer("✅ Ustoz ro'yxatdan o'chirildi!", show_alert=True)
    
    # Ro'yxatni yangilash
    teachers = await db.get_all_teachers()
    if teachers:
        await callback.message.edit_text("🗑 <b>O'chirmoqchi bo'lgan Ustozni tanlang:</b>", reply_markup=get_delete_teacher_inline(teachers), parse_mode="HTML")
    else:
        await callback.message.edit_text("👨‍🏫 Ustozlar qolmadi.", reply_markup=get_teachers_manage_inline())

# --- ADMINLAR BOSHQARUVI ---
@admin_router.callback_query(F.data == "adm_manage_admins")
async def cb_manage_admins(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
    
    text = (
        "🛡 <b>Adminlar boshqaruvi bo'limi</b>\n\n"
        "Siz yangi admin Telegram ID sini qo'shishingiz yoki mavjudlarini o'chirishingiz mumkin."
    )
    await callback.message.edit_text(text, reply_markup=get_admins_manage_inline(), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "adm_list_admins")
async def cb_list_admins(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    admins = await db.get_all_admins()
    text = "📋 <b>Ro'yxatdan o'tgan Adminlar:</b>\n\n"
    for idx, a in enumerate(admins, 1):
        name = html.escape(a['name'] or 'Noma\'lum')
        a_id = a['telegram_id']
        badge = "⭐ <b>BOSH ADMIN</b>" if a.get('is_super') == 1 else "🔹 Admin"
        text += f"{idx}. {badge}: <b>{name}</b> — ID: <code>{a_id}</code> (<a href=\"tg://user?id={a_id}\">Profil</a>)\n"

    await callback.message.edit_text(text, reply_markup=get_admins_manage_inline(), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "adm_add_admin")
async def cb_add_admin_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    await state.set_state(AdminAddAdminState.waiting_for_id)
    text = (
        "➕ <b>Yangi Admin qo'shish</b>\n\n"
        "Iltimos, yangi adminning <b>Telegram ID</b> raqamini yuboring.\n\n"
        "<i>(ID raqamni bilmasangiz, <b>@ScanIDBot</b> orqali bilib olishingiz mumkin)</i>"
    )
    await callback.message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()

@admin_router.message(AdminAddAdminState.waiting_for_id)
async def process_admin_id(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if not text.isdigit():
        await message.answer("⚠️ Iltimos, faqat sonlardan iborat to'g'ri Telegram ID kiriting:")
        return

    admin_id = int(text)
    await state.update_data(admin_id=admin_id)
    await state.set_state(AdminAddAdminState.waiting_for_name)
    await message.answer(
        "Endi adminning <b>Ism va Familiyasi</b>ni kiriting:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AdminAddAdminState.waiting_for_name)
async def process_admin_name(message: Message, state: FSMContext):
    admin_name = message.text.strip() if message.text else "Admin"
    data = await state.get_data()
    admin_id = data['admin_id']

    success = await db.add_admin(
        telegram_id=admin_id,
        name=admin_name,
        added_by=message.from_user.id
    )

    await state.clear()
    is_admin = await db.is_admin(message.from_user.id)
    is_teacher = await db.is_teacher(message.from_user.id)

    if success:
        await message.answer(
            f"✅ <b>Admin muvaffaqiyatli qo'shildi!</b>\n\n"
            f"👤 <b>Ism:</b> {html.escape(admin_name)}\n"
            f"🆔 <b>ID:</b> <code>{admin_id}</code>",
            reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Adminni saqlashda xatolik yuz berdi.",
            reply_markup=get_main_keyboard(is_admin=is_admin, is_teacher=is_teacher)
        )

@admin_router.callback_query(F.data == "adm_del_admin_list")
async def cb_del_admin_list(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    admins = await db.get_all_admins()
    deletable_admins = [a for a in admins if a.get('is_super') != 1]
    if not deletable_admins:
        await callback.answer("O'chirish mumkin bo'lgan qo'shimcha adminlar mavjud emas (Bosh adminlar o'chirilmaydi).", show_alert=True)
        return

    text = "🗑 <b>O'chirmoqchi bo'lgan Adminni tanlang:</b>"
    await callback.message.edit_text(text, reply_markup=get_delete_admin_inline(admins), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("adm_del_adm_id_"))
async def cb_del_admin_confirm(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    admin_id = int(callback.data.replace("adm_del_adm_id_", ""))
    removed = await db.remove_admin(admin_id)
    if removed:
        await callback.answer("✅ Admin o'chirildi!", show_alert=True)
    else:
        await callback.answer("❌ Ushbu adminni o'chirib bo'lmaydi (Bosh admin).", show_alert=True)
        return

    admins = await db.get_all_admins()
    deletable = [a for a in admins if a.get('is_super') != 1]
    if deletable:
        await callback.message.edit_text("🗑 <b>O'chirmoqchi bo'lgan Adminni tanlang:</b>", reply_markup=get_delete_admin_inline(admins), parse_mode="HTML")
    else:
        await callback.message.edit_text("🛡 Boshqa o'chiriladigan adminlar qolmadi.", reply_markup=get_admins_manage_inline())

# --- SAVOLLAR MODERATSIYASI (TASDIQLASH / RAD ETISH) ---
@admin_router.callback_query(F.data.startswith("mod_app_"))
async def cb_approve_question(callback: CallbackQuery, bot: Bot):
    admin_user = callback.from_user
    if not await db.is_admin(admin_user.id):
        await callback.answer("Siz admin emassiz.", show_alert=True)
        return

    q_id = int(callback.data.replace("mod_app_", ""))
    question = await db.get_question(q_id)

    if not question:
        await callback.answer("Savol topilmadi.", show_alert=True)
        return

    if question['status'] != 'pending':
        await callback.answer(f"Bu savol allaqachon ko'rib chiqilgan (Holat: {question['status']}).", show_alert=True)
        return

    # Bazada statusni 'approved' qilish
    await db.approve_question(q_id, admin_user.id)

    # 1. Foydalanuvchini xabardor qilish
    try:
        await bot.send_message(
            chat_id=question['user_telegram_id'],
            text=(
                f"✅ <b>Savolingiz admin tomonidan tasdiqlandi! (#{q_id})</b>\n\n"
                f"Savol Ustoz(lar)ga yetkazildi. Ustoz javob bergach, shu yerda sizga xabar qilinadi."
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error notifying user about approved question #{q_id}: {e}")

    # 2. Savolni barcha USTOZLARGA yuborish
    teachers = await db.get_all_teachers()
    teacher_keyboard = get_teacher_question_inline(q_id)
    user_card = format_user_profile(
        user_id=question['user_telegram_id'],
        full_name=question['user_full_name'],
        username=question['username'],
        question_id=q_id,
        created_at=question['created_at']
    )

    q_type = question['question_type']
    text_content = question['text_content']
    media_file_id = question['media_file_id']
    media_caption = question['media_caption']

    teachers_sent_count = 0
    for teacher in teachers:
        t_id = teacher['telegram_id']
        try:
            if q_type == "text":
                t_msg = (
                    f"🎓 <b>USTOZ, SIZGA YANGI SAVOL KELDI (#{q_id})</b>\n\n"
                    f"{user_card}\n"
                    f"📝 <b>Savol mazmuni:</b>\n"
                    f"{html.escape(text_content)}"
                )
                await bot.send_message(
                    chat_id=t_id,
                    text=t_msg,
                    reply_markup=teacher_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "photo":
                cap = f"🎓 <b>USTOZ, SIZGA YANGI SAVOL KELDI (#{q_id})</b>\n\n{user_card}"
                if media_caption:
                    cap += f"\n📝 <b>Izoh:</b> {html.escape(media_caption)}"
                await bot.send_photo(
                    chat_id=t_id,
                    photo=media_file_id,
                    caption=cap,
                    reply_markup=teacher_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "voice":
                cap = f"🎓 <b>USTOZ, SIZGA YANGI SAVOL (OVOZLI) (#{q_id})</b>\n\n{user_card}"
                await bot.send_voice(
                    chat_id=t_id,
                    voice=media_file_id,
                    caption=cap,
                    reply_markup=teacher_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "audio":
                cap = f"🎓 <b>USTOZ, SIZGA YANGI SAVOL (AUDIO) (#{q_id})</b>\n\n{user_card}"
                await bot.send_audio(
                    chat_id=t_id,
                    audio=media_file_id,
                    caption=cap,
                    reply_markup=teacher_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "video":
                cap = f"🎓 <b>USTOZ, SIZGA YANGI SAVOL (VIDEO) (#{q_id})</b>\n\n{user_card}"
                if media_caption:
                    cap += f"\n📝 <b>Izoh:</b> {html.escape(media_caption)}"
                await bot.send_video(
                    chat_id=t_id,
                    video=media_file_id,
                    caption=cap,
                    reply_markup=teacher_keyboard,
                    parse_mode="HTML"
                )
            elif q_type == "document":
                cap = f"🎓 <b>USTOZ, SIZGA YANGI SAVOL (HUJJAT) (#{q_id})</b>\n\n{user_card}"
                if media_caption:
                    cap += f"\n📝 <b>Izoh:</b> {html.escape(media_caption)}"
                await bot.send_document(
                    chat_id=t_id,
                    document=media_file_id,
                    caption=cap,
                    reply_markup=teacher_keyboard,
                    parse_mode="HTML"
                )
            teachers_sent_count += 1
        except Exception as e:
            print(f"Error sending question #{q_id} to teacher {t_id}: {e}")

    admin_name = html.escape(admin_user.full_name)
    notice = f"\n\n<i>✅ Tasdiqladi va Ustozlarga yubordi: {admin_name}</i>"
    if not teachers:
        notice += "\n⚠️ <b>Diqqat: Hozircha botda birorta ham Ustoz ro'yxatdan o'tmagan! Iltimos, admin panel orqali Ustoz qo'shing.</b>"

    # Xabarni tahrirlash (tugmalarni olib tashlab holatni ko'rsatish)
    if callback.message.text:
        await callback.message.edit_text(callback.message.text + notice, parse_mode="HTML")
    elif callback.message.caption:
        await callback.message.edit_caption(caption=callback.message.caption + notice, parse_mode="HTML")

    await callback.answer(f"✅ Savol tasdiqlandi va {teachers_sent_count} ta ustozga yuborildi!", show_alert=True)

@admin_router.callback_query(F.data.startswith("mod_rej_"))
async def cb_reject_question(callback: CallbackQuery, bot: Bot):
    admin_user = callback.from_user
    if not await db.is_admin(admin_user.id):
        await callback.answer("Siz admin emassiz.", show_alert=True)
        return

    q_id = int(callback.data.replace("mod_rej_", ""))
    question = await db.get_question(q_id)

    if not question:
        await callback.answer("Savol topilmadi.", show_alert=True)
        return

    if question['status'] != 'pending':
        await callback.answer(f"Bu savol allaqachon ko'rib chiqilgan (Holat: {question['status']}).", show_alert=True)
        return

    # Bazada statusni 'rejected' qilish
    await db.reject_question(q_id, admin_user.id)

    # Rad etilganda foydalanuvchiga bildirishnoma yuborilmaydi (talabga muvofiq)

    admin_name = html.escape(admin_user.full_name)
    notice = f"\n\n<i>❌ Rad etdi: {admin_name}</i>"

    if callback.message.text:
        await callback.message.edit_text(callback.message.text + notice, parse_mode="HTML")
    elif callback.message.caption:
        await callback.message.edit_caption(caption=callback.message.caption + notice, parse_mode="HTML")

    await callback.answer("❌ Savol rad etildi (foydalanuvchiga xabar yuborilmadi).", show_alert=True)
