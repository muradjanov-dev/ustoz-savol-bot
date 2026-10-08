# 🤖 "Ustozga Savol Yo'llash" Telegram Boti

Foydalanuvchilarga ustozga savol yo'llash, adminlarga savollarni moderatsiya qilish, ustozlarga esa qulay shaklda javob berish imkonini beruvchi to'liq asinxron Telegram bot.

---

## 🌟 Asosiy Imkoniyatlar

- **Foydalanuvchilar uchun:**
  - ✍️ Matn, rasm, ovozli xabar (voice), audio, video yoki hujjat ko'rinishida savol yo'llash.
  - 📋 O'zining barcha yuborgan savollari va ularning holatini (kutilmoqda, tasdiqlandi, javob berildi, rad etildi) ko'rish.
  - 🔔 Savol tasdiqlanganda yoki ustoz javob berganda darhol xabardor bo'lish.

- **Adminlar uchun:**
  - 🛡 Bosh adminlar: `7909561860`, `917456291`.
  - 📨 Yangi savollarni qabul qilish: yuboruvchining to'liq ma'lumotlari (Ism, Familiya, Username, Telegram ID, Profil havolasi, Sana).
  - ✅ **Tasdiqlash va Ustozga yuborish**, ✍️ **O'zim javob berish** (admin o'zi to'g'ridan-to'g'ri javob berishi mumkin) yoki ❌ **Rad etish** (foydalanuvchiga rad xabari bormaydi).
  - 👨‍🏫 **Ustozlar boshqaruvi**: Yangi ustoz Telegram ID sini qo'shish, ro'yxatni ko'rish, o'chirish.
  - 🛡 **Adminlar boshqaruvi**: Yangi admin Telegram ID sini qo'shish, ro'yxatni ko'rish, o'chirish.
  - ℹ️ **@ScanIDBot qo'llanmasi**: Ustoz yoki foydalanuvchi Telegram ID sini osonlikcha aniqlash bo'yicha to'liq instruksiya.
  - 📊 **Bot statistikasi**: Jami foydalanuvchilar, savollar soni, javob berilganlar va boshqalar.

- **Ustozlar (Teachers) uchun:**
  - 🎓 Admin tomonidan tasdiqlangan savollarni to'liq profil ma'lumotlari bilan qabul qilish.
  - 💬 «Javob berish» tugmasi orqali to'g'ridan-to'g'ri matn yoki ovozli xabar bilan javob yo'llash.
  - ⚡️ Javob avtomatik tarzda o'quvchiga yetkaziladi.

---

## 🚀 Railway.app ga Deploy Qilish Qo'llanmasi

Railway-ga joylash juda oson:

### 1-Usul: GitHub orqali (Tavsiya etiladi)
1. Ushbu loyiha fayllarini o'zingizning **GitHub** akkauntingizdagi yangi (yoki mavjud) repozitoriyga yuklang (`git push`).
2. [Railway.app](https://railway.app) saytiga kiring va akkauntingizga kiring.
3. **«New Project»** tugmasini bosing -> **«Deploy from GitHub repo»** ni tanlang.
4. Yuklagan repozitoriyangizni tanlang.
5. **Variables (Muhit o'zgaruvchilari)** bo'limiga o'ting va quyidagi o'zgaruvchilarni kiriting:
   - `BOT_TOKEN` = `<@BotFather bergan token>`
   - `SUPER_ADMINS` = `7909561860,917456291`
   - `DB_PATH` = `/data/bot_database.sqlite3`
6. Railway-da **Add Volume** qilib uni `/data` papkasiga ulang (ma'lumotlar bazasi qayta ishga tushganda saqlanib qolishi uchun). Volume'ni `/app` ga ulamang — u kod fayllarini yopib qo'yadi.
7. Deploy avtomatik amalga oshadi va bot ishga tushadi! 🚀

### 2-Usul: Railway CLI orqali
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

---

## 💻 Lokal Muhitda Ishga Tushirish

1. Python 3.10+ o'rnatilganligiga ishonch hosil qiling.
2. Kerakli paketlarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
3. `.env.example` dan nusxa olib `.env` yarating va tokenni kiriting:
   ```env
   BOT_TOKEN=<@BotFather bergan token>
   SUPER_ADMINS=7909561860,917456291
   DB_PATH=bot_database.sqlite3
   ```
4. Botni ishga tushiring:
   ```bash
   python bot.py
   ```

---

## 📖 Telegram ID ni Qanday Olish Mumkin? (@ScanIDBot)

1. Telegram orqali **@ScanIDBot** botiga kiring.
2. `/start` buyrug'ini yuboring — o'zingizning Telegram ID raqamingiz chiqadi.
3. Ustoz yoki boshqa insonning ID sini bilish uchun uning istalgan xabarini **@ScanIDBot** ga Forward (uzatish) qiling.
4. Chiqqan ID raqamni Admin panel orqali qo'shing.
