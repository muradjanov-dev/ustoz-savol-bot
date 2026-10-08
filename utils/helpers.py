from datetime import datetime
from typing import Optional, Dict, Any

def format_user_profile(
    user_id: int,
    full_name: str,
    username: Optional[str] = None,
    question_id: Optional[int] = None,
    created_at: Optional[str] = None
) -> str:
    """Foydalanuvchi va savol haqida maksimal ma'lumotni chiroyli formatda shakllantirish"""
    uname_text = f"@{username}" if username else "<i>Mavjud emas</i>"
    profile_link = f"<a href=\"tg://user?id={user_id}\">🔗 Profilga to'g'ridan-to'g'ri o'tish</a>"
    
    q_id_str = f"<b>🆔 Savol raqami:</b> #{question_id}\n" if question_id else ""
    time_str = f"<b>📅 Yuborilgan vaqt:</b> {created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    info_card = (
        f"👤 <b>YUBORUVCHI PROFILI:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"<b>📛 F.I.Sh:</b> {full_name}\n"
        f"<b>🌐 Username:</b> {uname_text}\n"
        f"<b>🆔 Telegram ID:</b> <code>{user_id}</code>\n"
        f"{profile_link}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{q_id_str}"
        f"{time_str}"
    )
    return info_card

def get_id_instruction_text() -> str:
    """Telegram ID ni @ScanIDBot orqali olish bo'yicha qisqa va tushunarli qo'llanma"""
    guide = (
        "📖 <b>Telegram ID olish bo'yicha qo'llanma:</b>\n\n"
        "1️⃣ Telegram qidiruvidan <b>@ScanIDBot</b> botiga kiring.\n"
        "2️⃣ Botga <code>/start</code> yuboring — bot sizga <b>o'zingizning ID</b> raqamingizni chiqarib beradi.\n"
        "3️⃣ <b>Ustoz yoki boshqa admin ID sini olish uchun:</b>\n"
        "   • O'sha inson yozgan biror xabarni <b>@ScanIDBot</b> botiga Forward (Uzatish) qiling.\n"
        "   • Bot xabar egasining aniq sonli Telegram ID sini ko'rsatadi.\n"
        "4️⃣ Olingan ID raqamni (masalan: <code>7909561860</code>) ushbu botga kiritasiz."
    )
    return guide
