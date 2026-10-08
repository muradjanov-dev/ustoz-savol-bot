from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def get_moderation_keyboard(question_id: int) -> InlineKeyboardMarkup:
    """Adminlar uchun savolni tekshirish va javob berish tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash va Ustozga yuborish",
                    callback_data=f"mod_app_{question_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✍️ O'zim javob berish",
                    callback_data=f"teach_rep_{question_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"mod_rej_{question_id}"
                )
            ]
        ]
    )

def get_teacher_question_inline(question_id: int) -> InlineKeyboardMarkup:
    """Ustoz uchun savolga javob berish tugmasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Javob berish",
                    callback_data=f"teach_rep_{question_id}"
                )
            ]
        ]
    )

def get_admin_main_inline() -> InlineKeyboardMarkup:
    """Admin panel bosh menyusi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨‍🏫 Ustozlar boshqaruvi", callback_data="adm_manage_teachers"),
                InlineKeyboardButton(text="🛡 Adminlar boshqaruvi", callback_data="adm_manage_admins")
            ],
            [
                InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stats"),
                InlineKeyboardButton(text="ℹ️ ID olish qo'llanmasi", callback_data="adm_id_guide")
            ],
            [
                InlineKeyboardButton(text="❌ Menyu yopish", callback_data="adm_close")
            ]
        ]
    )

def get_teachers_manage_inline() -> InlineKeyboardMarkup:
    """Ustozlar boshqaruvi menyusi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Yangi Ustoz qo'shish", callback_data="adm_add_teacher"),
                InlineKeyboardButton(text="➖ Ustozni o'chirish", callback_data="adm_del_teacher_list")
            ],
            [
                InlineKeyboardButton(text="📋 Barcha Ustozlar ro'yxati", callback_data="adm_list_teachers")
            ],
            [
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_back_main")
            ]
        ]
    )

def get_admins_manage_inline() -> InlineKeyboardMarkup:
    """Adminlar boshqaruvi menyusi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Yangi Admin qo'shish", callback_data="adm_add_admin"),
                InlineKeyboardButton(text="➖ Adminni o'chirish", callback_data="adm_del_admin_list")
            ],
            [
                InlineKeyboardButton(text="📋 Barcha Adminlar ro'yxati", callback_data="adm_list_admins")
            ],
            [
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_back_main")
            ]
        ]
    )

def get_delete_teacher_inline(teachers: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """O'chirish uchun ustozlar ro'yxati"""
    buttons = []
    for t in teachers:
        name = t.get("name") or str(t.get("telegram_id"))
        t_id = t.get("telegram_id")
        buttons.append([
            InlineKeyboardButton(text=f"🗑 {name} ({t_id})", callback_data=f"adm_del_teach_id_{t_id}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_manage_teachers")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_delete_admin_inline(admins: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """O'chirish uchun adminlar ro'yxati (bosh adminlardan tashqari)"""
    buttons = []
    for a in admins:
        if a.get("is_super") == 1:
            continue
        name = a.get("name") or str(a.get("telegram_id"))
        a_id = a.get("telegram_id")
        buttons.append([
            InlineKeyboardButton(text=f"🗑 {name} ({a_id})", callback_data=f"adm_del_adm_id_{a_id}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_manage_admins")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_admin_main() -> InlineKeyboardMarkup:
    """Bosh admin menyuga qaytish"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Boshqaruv menyusi", callback_data="adm_back_main")]
        ]
    )
