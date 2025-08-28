# 🌟 ستاره داوود - اکوسیستم ربات‌های هوشمند اسرائیل
# Magen David - Israeli Smart Bot Ecosystem

## 📋 خلاصه پروژه

این پروژه یک اکوسیستم کامل و پیشرفته از ربات‌های دیسکورد برای سرور رول‌پلی اسرائیل است. سیستم شامل یک ربات مرکزی (ستاره داوود) و چندین ربات تخصصی است که همگی با استفاده از هوش مصنوعی Google Gemini کار می‌کنند.

## ✨ ویژگی‌های کلیدی

### 🏛️ سیستم دولت و کنست
- شبیه‌سازی کامل دولت پارلمانی اسرائیل
- سیستم انتخابات خودکار
- قانون‌گذاری و رأی‌گیری
- تشکیل کابینه و وزارت‌خانه‌ها

### ⚔️ سیستم دفاعی چندلایه
- **گنبد آهنین**: مقابله با اسپم و حملات کوچک
- **فلاخن داوود**: دفاع در برابر حملات منشن و Raid
- **خِتْس ۳ و ۴**: مقابله با حملات فاجعه‌بار
- **تاد**: دفاع پیشگیرانه و اسکن کاربران

### 💰 سیستم اقتصادی پیشرفته
- واحد پول شِکِل
- سیستم بانکی و مالیات
- بورس تل‌آویو
- صنایع نظامی و تولید

### 🎭 رول‌پلی عمیق
- سیستم شهروندی و مهاجرت
- مشاغل مختلف با درآمد متفاوت
- سیستم مهارت‌ها و تجربه
- دستاوردها و میراث فردی

### 🤖 هوش مصنوعی Gemini
- تولید محتوای پویا
- تحلیل زبان طبیعی
- شخصیت‌پردازی ربات‌ها
- تولید سناریوهای بحران

## 🚀 راه‌اندازی

### پیش‌نیازها
- Python 3.8 یا بالاتر
- Discord Bot Token
- Google Gemini API Key (اختیاری)
- Discord Server ID

### نصب وابستگی‌ها

```bash
# نصب وابستگی‌های اصلی
pip install -r requirements.txt

# یا نصب دستی
pip install discord.py google-generativeai python-dotenv
```

### تنظیم متغیرهای محیطی

فایل `.env` را در ریشه پروژه ایجاد کنید:

```env
# Discord Bot Tokens
MAGEN_DAVID_TOKEN=your_magen_david_bot_token_here
IRON_DOME_TOKEN=your_iron_dome_bot_token_here
DAVIDS_SLING_TOKEN=your_davids_sling_bot_token_here
ARROW_3_TOKEN=your_arrow_3_bot_token_here
ARROW_4_TOKEN=your_arrow_4_bot_token_here
THAAD_TOKEN=your_thaad_bot_token_here
IDF_COMMAND_TOKEN=your_idf_command_bot_token_here
AIR_FORCE_TOKEN=your_air_force_bot_token_here
GROUND_FORCE_TOKEN=your_ground_force_bot_token_here
NAVY_TOKEN=your_navy_bot_token_here
MOSSAD_TOKEN=your_mossad_bot_token_here
UNIT_8200_TOKEN=your_unit_8200_bot_token_here
CENTRAL_BANK_TOKEN=your_central_bank_bot_token_here
MILITARY_INDUSTRIES_TOKEN=your_military_industries_bot_token_here
ISRAEL_RADIO_TOKEN=your_israel_radio_bot_token_here
NATIONAL_NEWS_TOKEN=your_national_news_bot_token_here

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
SERVER_ID=your_discord_server_id_here
OWNER_ID=your_discord_user_id_here

# Database (اختیاری)
DATABASE_URL=sqlite:///israel_rp.db

# Logging (اختیاری)
LOG_LEVEL=INFO
LOG_FILE=israel_rp.log
```

### اجرای پروژه

```bash
# راه‌اندازی اصلی
python main.py

# نمایش راهنما
python main.py --help
```

## 📁 ساختار پروژه

```
israel_rp_bot/
├── main.py                    # اسکریپت اصلی راه‌اندازی
├── config.py                  # تنظیمات و پیکربندی
├── models.py                  # مدل‌های پایگاه داده
├── gemini_integration.py      # یکپارچه‌سازی هوش مصنوعی
├── magen_david_bot.py        # ربات مرکزی ستاره داوود
├── cogs/                     # ماژول‌های تخصصی
│   ├── government_cog.py     # ماژول دولت و کنست
│   ├── military_cog.py       # ماژول نظامی و دفاعی
│   ├── economy_cog.py        # ماژول اقتصادی
│   ├── civilian_cog.py       # ماژول مدنی
│   └── intelligence_cog.py   # ماژول اطلاعاتی
├── requirements.txt           # وابستگی‌ها
├── README.md                 # مستندات
└── .env                      # متغیرهای محیطی
```

## 🎮 کامندهای اصلی

### 🏛️ دولت
- `!initialize_israel` - راه‌اندازی کامل سرور
- `!apply_citizenship` - درخواست شهروندی
- `!control_panel` - داشبورد کنترل مرکزی
- `!propose_law` - پیشنهاد قانون
- `!vote_law` - رأی‌گیری برای قانون

### ⚔️ نظامی
- `!defcon [level]` - تغییر سطح دفاعی
- `!deploy_forces` - اعزام نیرو
- `!mission_status` - وضعیت مأموریت‌ها
- `!war_declaration` - اعلام جنگ

### 💰 اقتصاد
- `!balance` - مشاهده موجودی
- `!transfer @user amount` - انتقال پول
- `!invest` - سرمایه‌گذاری
- `!stock_market` - بازار بورس

### 👥 شهروندان
- `!profile` - پروفایل شخصی
- `!skills` - مهارت‌ها
- `!job_application` - درخواست شغل
- `!education` - سیستم آموزشی

## 🔧 تنظیمات پیشرفته

### تغییر تنظیمات اقتصادی
در فایل `config.py` می‌توانید تنظیمات زیر را تغییر دهید:

```python
# Economic Configuration
self.STARTING_BALANCE = 1000      # موجودی اولیه شهروندان
self.DAILY_INCOME = 100           # درآمد روزانه
self.TAX_RATE = 0.15              # نرخ مالیات
self.INFLATION_RATE = 0.02        # نرخ تورم ماهانه
```

### تنظیم سیستم دفاعی
```python
# Military Configuration
self.DEFCON_LEVELS = {
    5: "DEFCON 5 - Normal",
    4: "DEFCON 4 - Increased",
    3: "DEFCON 3 - Elevated",
    2: "DEFCON 2 - High",
    1: "DEFCON 1 - Maximum"
}
```

### تنظیم رویدادها
```python
# Time Configuration
self.GAME_DAYS_PER_REAL_DAY = 7      # 1 روز واقعی = 7 روز بازی
self.ELECTION_INTERVAL_DAYS = 30      # انتخابات هر 30 روز
self.CRISIS_INTERVAL_HOURS = 6        # بحران هر 6 ساعت
```

## 🚨 عیب‌یابی

### مشکلات رایج

#### خطای اتصال به Discord
```
❌ توکن ربات ستاره داوود یافت نشد!
```
**راه‌حل:** توکن ربات را در فایل `.env` بررسی کنید.

#### خطای Gemini AI
```
⚠️ کلید API جمنای یافت نشد!
```
**راه‌حل:** کلید API را تنظیم کنید یا ربات در حالت پیش‌فرض کار خواهد کرد.

#### خطای پایگاه داده
```
❌ خطا در راه‌اندازی پایگاه داده
```
**راه‌حل:** مجوزهای نوشتن در پوشه پروژه را بررسی کنید.

### لاگ‌ها
لاگ‌ها در فایل `israel_rp.log` ذخیره می‌شوند. برای بررسی مشکلات:

```bash
# مشاهده لاگ‌های زنده
tail -f israel_rp.log

# جستجو در لاگ‌ها
grep "ERROR" israel_rp.log
```

## 🔒 امنیت

### نکات مهم
- توکن‌های ربات‌ها را محرمانه نگه دارید
- فایل `.env` را در `.gitignore` قرار دهید
- مجوزهای ربات‌ها را محدود کنید
- از HTTPS برای اتصالات استفاده کنید

### تنظیمات امنیتی Discord
```python
# تنظیم مجوزهای محدود
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
```

## 📚 توسعه و سفارشی‌سازی

### افزودن ربات جدید
1. فایل جدید در پوشه `cogs/` ایجاد کنید
2. کلاس `Cog` را extend کنید
3. کامندهای مورد نظر را اضافه کنید
4. در `magen_david_bot.py` ماژول را load کنید

### تغییر شخصیت ربات‌ها
در فایل `gemini_integration.py` می‌توانید شخصیت ربات‌ها را تغییر دهید:

```python
async def generate_character_personality(self, character_type: str, user_name: str):
    # تغییر prompt برای شخصیت‌های مختلف
    prompt = f"شما ربات {character_type} هستید..."
```

### افزودن ویژگی جدید
1. مدل جدید در `models.py` ایجاد کنید
2. کامند جدید در `cogs/` اضافه کنید
3. تنظیمات مربوطه در `config.py` قرار دهید
4. تست کنید و مستندات را به‌روزرسانی کنید

## 🌟 مشارکت

### چگونه مشارکت کنیم
1. پروژه را fork کنید
2. شاخه جدید برای ویژگی ایجاد کنید
3. تغییرات را commit کنید
4. Pull Request ارسال کنید

### استانداردهای کدنویسی
- از docstring برای توضیح توابع استفاده کنید
- نام‌گذاری متغیرها به فارسی باشد
- خطاها را به درستی مدیریت کنید
- تست‌ها را بنویسید

## 📞 پشتیبانی

### کانال‌های ارتباطی
- **Discord:** سرور رسمی پروژه
- **GitHub Issues:** گزارش مشکلات
- **Wiki:** مستندات کامل

### منابع مفید
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Google Gemini API](https://ai.google.dev/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر فایل `LICENSE` را مطالعه کنید.

## 🙏 تشکر و قدردانی

- تیم Discord.py برای کتابخانه عالی
- Google برای API هوش مصنوعی Gemini
- جامعه متن‌باز برای الهام‌بخشی

---

**🌟 ستاره داوود - اکوسیستم ربات‌های هوشمند اسرائیل 🌟**

*با افتخار ساخته شده برای جامعه رول‌پلی اسرائیل*