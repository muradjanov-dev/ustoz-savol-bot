import aiosqlite
from datetime import datetime
from typing import List, Optional, Dict, Any
from config import DB_PATH, SUPER_ADMINS

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Ma'lumotlar bazasi jadvallarini yaratish va bosh adminlarni kiritish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users jadvali
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Admins jadvali
            await db.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    telegram_id INTEGER PRIMARY KEY,
                    name TEXT,
                    added_by INTEGER,
                    is_super INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Teachers jadvali (Ustozlar)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    telegram_id INTEGER PRIMARY KEY,
                    name TEXT,
                    added_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Questions jadvali (Savollar)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_telegram_id INTEGER,
                    user_full_name TEXT,
                    username TEXT,
                    question_type TEXT,
                    text_content TEXT,
                    media_file_id TEXT,
                    media_caption TEXT,
                    status TEXT DEFAULT 'pending',
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    rejected_by INTEGER,
                    rejected_at TIMESTAMP,
                    answer_text TEXT,
                    answer_media_id TEXT,
                    answer_media_type TEXT,
                    answered_by INTEGER,
                    answered_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Bosh adminlarni avtomatik ro'yxatga kiritish
            for admin_id in SUPER_ADMINS:
                await db.execute("""
                    INSERT INTO admins (telegram_id, name, is_super, added_by)
                    VALUES (?, ?, 1, 0)
                    ON CONFLICT(telegram_id) DO UPDATE SET is_super = 1
                """, (admin_id, f"Bosh Admin ({admin_id})"))

            await db.commit()

    # --- USER OPERATIONS ---
    async def add_or_update_user(self, telegram_id: int, username: Optional[str], first_name: str, last_name: Optional[str]):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name
            """, (telegram_id, username, first_name, last_name))
            await db.commit()

    async def get_user_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    # --- ADMIN OPERATIONS ---
    async def is_admin(self, telegram_id: int) -> bool:
        if telegram_id in SUPER_ADMINS:
            return True
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,)) as cursor:
                return await cursor.fetchone() is not None

    async def is_super_admin(self, telegram_id: int) -> bool:
        if telegram_id in SUPER_ADMINS:
            return True
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT is_super FROM admins WHERE telegram_id = ?", (telegram_id,)) as cursor:
                row = await cursor.fetchone()
                return bool(row and row[0] == 1)

    async def add_admin(self, telegram_id: int, name: str, added_by: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO admins (telegram_id, name, added_by, is_super)
                    VALUES (?, ?, ?, 0)
                    ON CONFLICT(telegram_id) DO UPDATE SET name = excluded.name
                """, (telegram_id, name, added_by))
                await db.commit()
                return True
            except Exception:
                return False

    async def remove_admin(self, telegram_id: int) -> bool:
        if telegram_id in SUPER_ADMINS:
            return False # Bosh adminni o'chirib bo'lmaydi
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM admins WHERE telegram_id = ? AND is_super = 0", (telegram_id,))
            await db.commit()
            return True

    async def get_all_admins(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM admins ORDER BY is_super DESC, created_at ASC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # --- TEACHER (USTOZ) OPERATIONS ---
    async def is_teacher(self, telegram_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT 1 FROM teachers WHERE telegram_id = ?", (telegram_id,)) as cursor:
                return await cursor.fetchone() is not None

    async def add_teacher(self, telegram_id: int, name: str, added_by: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO teachers (telegram_id, name, added_by)
                    VALUES (?, ?, ?)
                    ON CONFLICT(telegram_id) DO UPDATE SET name = excluded.name
                """, (telegram_id, name, added_by))
                await db.commit()
                return True
            except Exception:
                return False

    async def remove_teacher(self, telegram_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM teachers WHERE telegram_id = ?", (telegram_id,))
            await db.commit()
            return True

    async def get_all_teachers(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM teachers ORDER BY created_at ASC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # --- QUESTION OPERATIONS ---
    async def create_question(
        self,
        user_telegram_id: int,
        user_full_name: str,
        username: Optional[str],
        question_type: str,
        text_content: Optional[str] = None,
        media_file_id: Optional[str] = None,
        media_caption: Optional[str] = None
    ) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO questions (
                    user_telegram_id, user_full_name, username,
                    question_type, text_content, media_file_id, media_caption, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (user_telegram_id, user_full_name, username, question_type, text_content, media_file_id, media_caption))
            await db.commit()
            return cursor.lastrowid

    async def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM questions WHERE id = ?", (question_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def approve_question(self, question_id: int, admin_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE questions
                SET status = 'approved', approved_by = ?, approved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (admin_id, question_id))
            await db.commit()
            return True

    async def reject_question(self, question_id: int, admin_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE questions
                SET status = 'rejected', rejected_by = ?, rejected_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (admin_id, question_id))
            await db.commit()
            return True

    async def save_answer(
        self,
        question_id: int,
        answered_by: int,
        answer_text: Optional[str] = None,
        answer_media_id: Optional[str] = None,
        answer_media_type: Optional[str] = None
    ) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE questions
                SET status = 'answered',
                    answered_by = ?,
                    answer_text = ?,
                    answer_media_id = ?,
                    answer_media_type = ?,
                    answered_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (answered_by, answer_text, answer_media_id, answer_media_type, question_id))
            await db.commit()
            return True

    async def get_user_questions(self, user_telegram_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM questions
                WHERE user_telegram_id = ?
                ORDER BY id DESC LIMIT ?
            """, (user_telegram_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_stats(self) -> Dict[str, int]:
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                stats['total_users'] = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM admins") as cursor:
                stats['total_admins'] = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM teachers") as cursor:
                stats['total_teachers'] = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM questions") as cursor:
                stats['total_questions'] = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM questions WHERE status = 'pending'") as cursor:
                stats['pending_questions'] = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM questions WHERE status = 'approved'") as cursor:
                stats['approved_questions'] = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM questions WHERE status = 'answered'") as cursor:
                stats['answered_questions'] = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM questions WHERE status = 'rejected'") as cursor:
                stats['rejected_questions'] = (await cursor.fetchone())[0]

            return stats

# Global database instance
db = Database()
