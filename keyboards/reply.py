from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(is_admin: bool = False, is_teacher: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="✍️ Ustozga savol yo'llash")],
        [KeyboardButton(text="📋 Mening savollarim"), KeyboardButton(text="ℹ️ Bot haqida")]
    ]
    
    extra_row = []
    if is_admin:
        extra_row.append(KeyboardButton(text="⚙️ Admin Panel"))
    if is_teacher and not is_admin:
        extra_row.append(KeyboardButton(text="👨‍🏫 Ustoz Paneli"))
        
    if extra_row:
        keyboard.append(extra_row)

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Jarayonni bekor qilish klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
