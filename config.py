import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylidan o'qish
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Bosh adminlar ID ro'yxati (vergul bilan ajratilgan yoki standart qiymat)
raw_admins = os.getenv("SUPER_ADMINS", "7909561860,917456291")
SUPER_ADMINS = [int(admin_id.strip()) for admin_id in raw_admins.split(",") if admin_id.strip().isdigit()]

# Ma'lumotlar bazasi fayli
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "bot_database.sqlite3"))
