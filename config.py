"""
پیکربندی اصلی اکوسیستم ربات‌های هوشمند اسرائیل
Israel Smart Bot Ecosystem Configuration
"""

import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# توکن‌های ربات‌ها
BOT_TOKENS = {
    "magen_david": os.getenv("MAGEN_DAVID_TOKEN"),
    "iron_dome": os.getenv("IRON_DOME_TOKEN"),
    "davids_sling": os.getenv("DAVIDS_SLING_TOKEN"),
    "arrow": os.getenv("ARROW_TOKEN"),
    "thaad": os.getenv("THAAD_TOKEN"),
    "military": os.getenv("MILITARY_TOKEN"),
    "economy": os.getenv("ECONOMY_TOKEN"),
    "mossad": os.getenv("MOSSAD_TOKEN"),
    "unit8200": os.getenv("UNIT8200_TOKEN"),
    "radio": os.getenv("RADIO_TOKEN")
}

# کلید API گوگل Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# تنظیمات سرور
SERVER_CONFIG = {
    "guild_id": int(os.getenv("GUILD_ID", "0")),
    "admin_role_id": int(os.getenv("ADMIN_ROLE_ID", "0")),
    "owner_id": int(os.getenv("OWNER_ID", "0"))
}

# تنظیمات رول‌ها
ROLE_IDS = {
    "شهروند": "citizen_role_id",
    "سرباز": "soldier_role_id", 
    "وزیر": "minister_role_id",
    "نخست_وزیر": "prime_minister_role_id",
    "عضو_کنست": "knesset_member_role_id",
    "دانشمند": "scientist_role_id",
    "پزشک": "doctor_role_id",
    "خلبان": "pilot_role_id",
    "توریست": "tourist_role_id",
    "قاضی": "judge_role_id",
    "مامور_موساد": "mossad_agent_role_id",
    "خلافکار": "criminal_role_id"
}

# تنظیمات کتگوری‌ها
CATEGORY_IDS = {
    "دولت": "government_category_id",
    "ارتش": "military_category_id",
    "اقتصاد": "economy_category_id",
    "مناطق_شهری": "urban_areas_category_id",
    "آژانس_های_اطلاعاتی": "intelligence_agencies_category_id",
    "دانشگاه": "university_category_id"
}

# تنظیمات چنل‌ها
CHANNEL_IDS = {
    "immigration_office": "immigration_office_channel_id",
    "national_news": "national_news_channel_id",
    "war_room": "war_room_channel_id",
    "court": "court_channel_id",
    "hall_of_fame": "hall_of_fame_channel_id",
    "work_office": "work_office_channel_id"
}

# تنظیمات اقتصادی
ECONOMY_CONFIG = {
    "initial_balance": 1000,  # موجودی اولیه شهروندان
    "daily_income": 100,      # درآمد روزانه
    "tax_rate": 0.1,          # نرخ مالیات (10%)
    "currency_name": "شِکِل"
}

# تنظیمات نظامی
MILITARY_CONFIG = {
    "defcon_levels": {
        5: "آماده‌گی عادی",
        4: "آماده‌گی بالا", 
        3: "آماده‌گی شدید",
        2: "آماده‌گی بحرانی",
        1: "آماده‌گی جنگی"
    },
    "base_defcon": 5
}

# تنظیمات Gemini AI
GEMINI_CONFIG = {
    "model": "gemini-pro",
    "temperature": 0.8,
    "max_tokens": 1000
}

# رنگ‌های Embed
EMBED_COLORS = {
    "success": 0x00FF00,      # سبز
    "error": 0xFF0000,        # قرمز
    "warning": 0xFFFF00,      # زرد
    "info": 0x0099FF,         # آبی
    "government": 0x800080,   # بنفش
    "military": 0x8B4513,     # قهوه‌ای
    "economy": 0xFFD700,      # طلایی
    "news": 0x00CED1          # فیروزه‌ای
}