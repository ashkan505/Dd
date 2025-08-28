"""
پیکربندی اصلی اکوسیستم ربات‌های اسرائیل
Configuration file for Israel RP Bot Ecosystem
"""

import os
from dotenv import load_dotenv
from typing import Dict, List
import pytz

# بارگذاری متغیرهای محیطی
load_dotenv()

class BotConfig:
    """کلاس پیکربندی اصلی"""
    
    # Discord Bot Tokens
    MAGEN_DAVID_TOKEN = os.getenv('MAGEN_DAVID_TOKEN')
    IRON_DOME_TOKEN = os.getenv('IRON_DOME_TOKEN')
    DAVID_SLING_TOKEN = os.getenv('DAVID_SLING_TOKEN')
    ARROW_3_TOKEN = os.getenv('ARROW_3_TOKEN')
    ARROW_4_TOKEN = os.getenv('ARROW_4_TOKEN')
    THAAD_TOKEN = os.getenv('THAAD_TOKEN')
    ARMY_COMMAND_TOKEN = os.getenv('ARMY_COMMAND_TOKEN')
    AIR_FORCE_TOKEN = os.getenv('AIR_FORCE_TOKEN')
    NAVY_TOKEN = os.getenv('NAVY_TOKEN')
    GROUND_FORCES_TOKEN = os.getenv('GROUND_FORCES_TOKEN')
    MOSSAD_TOKEN = os.getenv('MOSSAD_TOKEN')
    UNIT_8200_TOKEN = os.getenv('UNIT_8200_TOKEN')
    CENTRAL_BANK_TOKEN = os.getenv('CENTRAL_BANK_TOKEN')
    MILITARY_INDUSTRIES_TOKEN = os.getenv('MILITARY_INDUSTRIES_TOKEN')
    RADIO_ISRAEL_TOKEN = os.getenv('RADIO_ISRAEL_TOKEN')
    UNDERWORLD_TOKEN = os.getenv('UNDERWORLD_TOKEN')
    
    # Google Gemini AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Server Configuration
    MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID', 0))
    ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]
    
    # Bot Settings
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    LANGUAGE = os.getenv('LANGUAGE', 'fa')
    TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Jerusalem'))

class ServerStructure:
    """ساختار سرور دیسکورد"""
    
    CATEGORIES = {
        'government': 'دولت اسرائیل 🏛️',
        'knesset': 'کنست اسرائیل 📜',
        'military': 'نیروهای مسلح 🪖',
        'defense': 'سامانه‌های دفاعی 🛡️',
        'intelligence': 'سازمان‌های اطلاعاتی 🕵️',
        'economy': 'اقتصاد و بانکداری 💰',
        'industry': 'صنایع و تولید 🏭',
        'cities': 'شهرها و مناطق 🏙️',
        'education': 'آموزش و دانشگاه 🎓',
        'culture': 'فرهنگ و هنر 🎭',
        'media': 'رسانه‌های ملی 📺',
        'immigration': 'مهاجرت و شهروندی 🛂',
        'justice': 'دستگاه قضایی ⚖️',
        'emergency': 'مدیریت بحران 🚨'
    }
    
    ROLES = {
        # رول‌های حکومتی
        'prime_minister': {'name': 'نخست‌وزیر', 'color': 0x1f8b4c, 'permissions': ['administrator']},
        'minister': {'name': 'وزیر', 'color': 0x3498db, 'permissions': ['manage_channels', 'manage_roles']},
        'knesset_member': {'name': 'عضو کنست', 'color': 0x9b59b6, 'permissions': ['manage_messages']},
        
        # رول‌های نظامی
        'general': {'name': 'ژنرال', 'color': 0xe74c3c, 'permissions': ['manage_channels']},
        'colonel': {'name': 'سرهنگ', 'color': 0xf39c12, 'permissions': ['manage_messages']},
        'major': {'name': 'سرگرد', 'color': 0xf1c40f, 'permissions': []},
        'soldier': {'name': 'سرباز', 'color': 0x95a5a6, 'permissions': []},
        'pilot': {'name': 'خلبان', 'color': 0x00a8ff, 'permissions': []},
        'naval_officer': {'name': 'افسر نیروی دریایی', 'color': 0x0097e6, 'permissions': []},
        
        # رول‌های اطلاعاتی
        'mossad_agent': {'name': 'مامور موساد', 'color': 0x2c2c54, 'permissions': []},
        'unit_8200_member': {'name': 'عضو واحد ۸۲۰۰', 'color': 0x40407a, 'permissions': []},
        
        # رول‌های مدنی
        'citizen': {'name': 'شهروند', 'color': 0x2ecc71, 'permissions': []},
        'tourist': {'name': 'توریست', 'color': 0xecf0f1, 'permissions': []},
        'doctor': {'name': 'پزشک', 'color': 0xe55039, 'permissions': []},
        'engineer': {'name': 'مهندس', 'color': 0x3c6382, 'permissions': []},
        'scientist': {'name': 'دانشمند', 'color': 0x8854d0, 'permissions': []},
        'teacher': {'name': 'معلم', 'color': 0xa55eea, 'permissions': []},
        'journalist': {'name': 'روزنامه‌نگار', 'color': 0x26de81, 'permissions': []},
        
        # رول‌های اقتصادی
        'banker': {'name': 'بانکدار', 'color': 0xf7b731, 'permissions': []},
        'businessman': {'name': 'تاجر', 'color': 0x5f27cd, 'permissions': []},
        'industrialist': {'name': 'صنعتگر', 'color': 0x00d2d3, 'permissions': []},
        
        # رول‌های خاص
        'judge': {'name': 'قاضی', 'color': 0x2d3436, 'permissions': ['manage_messages']},
        'criminal': {'name': 'خلافکار', 'color': 0x636e72, 'permissions': []},
        'great_person': {'name': 'شخصیت بزرگ', 'color': 0xfdcb6e, 'permissions': []}
    }
    
    CHANNELS = {
        # کانال‌های حکومتی
        'government': [
            {'name': 'cabinet-meetings', 'type': 'text', 'description': 'جلسات هیئت وزیران'},
            {'name': 'prime-minister-office', 'type': 'text', 'description': 'دفتر نخست‌وزیر'},
            {'name': 'government-announcements', 'type': 'text', 'description': 'اعلامیه‌های دولتی'}
        ],
        'knesset': [
            {'name': 'knesset-hall', 'type': 'text', 'description': 'تالار کنست'},
            {'name': 'legislation', 'type': 'text', 'description': 'قانون‌گذاری'},
            {'name': 'voting', 'type': 'text', 'description': 'رأی‌گیری'},
            {'name': 'law-archive', 'type': 'text', 'description': 'آرشیو قوانین'}
        ],
        'military': [
            {'name': 'high-command', 'type': 'text', 'description': 'فرماندهی کل'},
            {'name': 'air-force', 'type': 'text', 'description': 'نیروی هوایی'},
            {'name': 'ground-forces', 'type': 'text', 'description': 'نیروی زمینی'},
            {'name': 'navy', 'type': 'text', 'description': 'نیروی دریایی'},
            {'name': 'military-operations', 'type': 'text', 'description': 'عملیات نظامی'}
        ],
        'defense': [
            {'name': 'war-room', 'type': 'text', 'description': 'اتاق جنگ'},
            {'name': 'iron-dome-status', 'type': 'text', 'description': 'وضعیت گنبد آهنین'},
            {'name': 'defense-alerts', 'type': 'text', 'description': 'هشدارهای دفاعی'}
        ],
        'intelligence': [
            {'name': 'mossad-hq', 'type': 'text', 'description': 'مقر موساد'},
            {'name': 'unit-8200', 'type': 'text', 'description': 'واحد ۸۲۰۰'},
            {'name': 'intelligence-reports', 'type': 'text', 'description': 'گزارش‌های اطلاعاتی'}
        ],
        'economy': [
            {'name': 'central-bank', 'type': 'text', 'description': 'بانک مرکزی'},
            {'name': 'stock-exchange', 'type': 'text', 'description': 'بورس تل‌آویو'},
            {'name': 'economic-reports', 'type': 'text', 'description': 'گزارش‌های اقتصادی'}
        ],
        'cities': [
            {'name': 'jerusalem', 'type': 'text', 'description': 'اورشلیم'},
            {'name': 'tel-aviv', 'type': 'text', 'description': 'تل‌آویو'},
            {'name': 'haifa', 'type': 'text', 'description': 'حیفا'},
            {'name': 'beer-sheva', 'type': 'text', 'description': 'بئرشبع'}
        ],
        'general': [
            {'name': 'national-news', 'type': 'text', 'description': 'اخبار ملی'},
            {'name': 'immigration-office', 'type': 'text', 'description': 'اداره مهاجرت'},
            {'name': 'general-chat', 'type': 'text', 'description': 'گفتگوی عمومی'},
            {'name': 'radio-israel', 'type': 'voice', 'description': 'رادیو اسرائیل'}
        ]
    }

class EconomicConfig:
    """پیکربندی سیستم اقتصادی"""
    
    CURRENCY_NAME = "شکل"
    CURRENCY_SYMBOL = "₪"
    
    DAILY_INCOME = {
        'tourist': 0,
        'citizen': 100,
        'soldier': 150,
        'doctor': 300,
        'engineer': 250,
        'scientist': 280,
        'teacher': 200,
        'journalist': 180,
        'banker': 400,
        'businessman': 350,
        'minister': 500,
        'prime_minister': 1000
    }
    
    TAX_RATES = {
        'income_tax': 0.15,
        'transaction_tax': 0.05,
        'property_tax': 0.02
    }
    
    PROPERTY_PRICES = {
        'jerusalem': 1000000,
        'tel_aviv': 800000,
        'haifa': 600000,
        'beer_sheva': 400000
    }

class DefenseConfig:
    """پیکربندی سیستم‌های دفاعی"""
    
    DEFCON_LEVELS = {
        1: {'name': 'حداکثر آمادگی', 'color': 0xff0000, 'sensitivity': 1.0},
        2: {'name': 'آمادگی بالا', 'color': 0xff6600, 'sensitivity': 0.8},
        3: {'name': 'آمادگی متوسط', 'color': 0xffff00, 'sensitivity': 0.6},
        4: {'name': 'آمادگی پایین', 'color': 0x00ff00, 'sensitivity': 0.4},
        5: {'name': 'حالت عادی', 'color': 0x0000ff, 'sensitivity': 0.2}
    }
    
    MISSILE_INVENTORY = {
        'iron_dome': {'max': 1000, 'cost': 50000, 'effectiveness': 0.9},
        'david_sling': {'max': 500, 'cost': 100000, 'effectiveness': 0.95},
        'arrow_3': {'max': 200, 'cost': 200000, 'effectiveness': 0.98},
        'arrow_4': {'max': 100, 'cost': 300000, 'effectiveness': 0.99}
    }

class GameplayConfig:
    """پیکربندی گیم‌پلی"""
    
    XP_REWARDS = {
        'daily_login': 10,
        'complete_mission': 50,
        'participate_vote': 25,
        'pass_quiz': 30,
        'win_election': 200
    }
    
    SKILL_TREES = {
        'leadership': {'max_level': 10, 'cost_per_level': 100},
        'negotiation': {'max_level': 10, 'cost_per_level': 80},
        'technical': {'max_level': 10, 'cost_per_level': 90},
        'combat': {'max_level': 10, 'cost_per_level': 70}
    }
    
    CRISIS_TYPES = [
        {'type': 'natural_disaster', 'probability': 0.1, 'impact': 'negative'},
        {'type': 'political_scandal', 'probability': 0.08, 'impact': 'negative'},
        {'type': 'economic_boom', 'probability': 0.05, 'impact': 'positive'},
        {'type': 'scientific_breakthrough', 'probability': 0.03, 'impact': 'positive'},
        {'type': 'terrorist_attack', 'probability': 0.02, 'impact': 'very_negative'},
        {'type': 'diplomatic_success', 'probability': 0.04, 'impact': 'positive'}
    ]

# متغیرهای سراسری
CURRENT_DEFCON = 5
PUBLIC_APPROVAL = 75
NATIONAL_RESOURCES = {
    'water': 100,
    'energy': 100,
    'budget': 10000000
}

# پیام‌های سیستم
SYSTEM_MESSAGES = {
    'welcome_tourist': "🇮🇱 به اسرائیل خوش آمدید! برای دریافت شهروندی از دستور `!apply_citizenship` استفاده کنید.",
    'citizenship_granted': "🎉 تبریک! شما اکنون شهروند اسرائیل هستید.",
    'insufficient_funds': "❌ موجودی حساب شما کافی نیست.",
    'permission_denied': "🚫 شما مجوز انجام این عمل را ندارید.",
    'system_error': "⚠️ خطایی در سیستم رخ داده است. لطفاً با مدیریت تماس بگیرید."
}

# رنگ‌های Discord Embed
EMBED_COLORS = {
    'success': 0x2ecc71,
    'error': 0xe74c3c,
    'warning': 0xf39c12,
    'info': 0x3498db,
    'government': 0x1f8b4c,
    'military': 0xe74c3c,
    'economy': 0xf1c40f,
    'defense': 0x95a5a6
}