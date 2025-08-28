"""
پیکربندی اصلی اکوسیستم ربات‌های هوشمند اسرائیل
Main Configuration for Israeli Smart Bot Ecosystem
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Load environment variables
load_dotenv()

class BotType(Enum):
    """انواع ربات‌های موجود در سیستم"""
    MAGEN_DAVID = "magen_david"  # ستاره داوود - ربات مرکزی
    IRON_DOME = "iron_dome"      # گنبد آهنین
    DAVIDS_SLING = "davids_sling" # فلاخن داوود
    ARROW_3 = "arrow_3"          # خِتْس ۳
    ARROW_4 = "arrow_4"          # خِتْس ۴
    THAAD = "thaad"              # تاد
    IDF_COMMAND = "idf_command"  # فرماندهی کل ارتش
    AIR_FORCE = "air_force"      # نیروی هوایی
    GROUND_FORCE = "ground_force" # نیروی زمینی
    NAVY = "navy"                # نیروی دریایی
    MOSSAD = "mossad"            # موساد
    UNIT_8200 = "unit_8200"      # واحد ۸۲۰۰
    CENTRAL_BANK = "central_bank" # بانک مرکزی
    MILITARY_INDUSTRIES = "military_industries" # صنایع نظامی
    ISRAEL_RADIO = "israel_radio" # رادیو اسرائیل
    NATIONAL_NEWS = "national_news" # خبرگزاری ملی

class RoleType(Enum):
    """انواع رول‌های موجود در سرور"""
    TOURIST = "توریست"
    CITIZEN = "شهروند"
    SOLDIER = "سرباز"
    MINISTER = "وزیر"
    PRIME_MINISTER = "نخست‌وزیر"
    KNESSET_MEMBER = "عضو کنست"
    SCIENTIST = "دانشمند"
    DOCTOR = "پزشک"
    PILOT = "خلبان"
    JUDGE = "قاضی"
    CRIMINAL = "خلافکار"
    MOSSAD_AGENT = "مامور موساد"
    UNIT_8200_AGENT = "مامور واحد ۸۲۰۰"
    BANKER = "بانکدار"
    INDUSTRIALIST = "صنعتگر"
    JOURNALIST = "روزنامه‌نگار"
    TEACHER = "معلم"
    ENGINEER = "مهندس"

class CategoryType(Enum):
    """کتگوری‌های اصلی سرور"""
    GOVERNMENT = "دولت"
    MILITARY = "ارتش"
    ECONOMY = "اقتصاد"
    URBAN_AREAS = "مناطق شهری"
    INTELLIGENCE = "آژانس‌های اطلاعاتی"
    EDUCATION = "آموزش"
    HEALTHCARE = "بهداشت"
    MEDIA = "رسانه"
    CULTURE = "فرهنگ"
    RELIGION = "مذهب"
    TOURISM = "گردشگری"
    TRANSPORTATION = "حمل و نقل"
    ENVIRONMENT = "محیط زیست"
    SCIENCE = "علم و فناوری"
    SPORTS = "ورزش"
    ENTERTAINMENT = "سرگرمی"

@dataclass
class BotConfig:
    """پیکربندی هر ربات"""
    name: str
    token: str
    prefix: str
    description: str
    color: int
    permissions: List[str]
    channels: List[str]
    roles: List[str]
    features: List[str]

@dataclass
class ServerConfig:
    """پیکربندی سرور"""
    name: str
    id: str
    owner_id: str
    language: str
    timezone: str
    currency: str
    government_type: str
    military_strength: int
    economic_rating: int
    public_approval: int
    resources: Dict[str, int]

class Config:
    """کلاس اصلی پیکربندی"""
    
    def __init__(self):
        # Discord Bot Tokens
        self.MAGEN_DAVID_TOKEN = os.getenv('MAGEN_DAVID_TOKEN')
        self.IRON_DOME_TOKEN = os.getenv('IRON_DOME_TOKEN')
        self.DAVIDS_SLING_TOKEN = os.getenv('DAVIDS_SLING_TOKEN')
        self.ARROW_3_TOKEN = os.getenv('ARROW_3_TOKEN')
        self.ARROW_4_TOKEN = os.getenv('ARROW_4_TOKEN')
        self.THAAD_TOKEN = os.getenv('THAAD_TOKEN')
        self.IDF_COMMAND_TOKEN = os.getenv('IDF_COMMAND_TOKEN')
        self.AIR_FORCE_TOKEN = os.getenv('AIR_FORCE_TOKEN')
        self.GROUND_FORCE_TOKEN = os.getenv('GROUND_FORCE_TOKEN')
        self.NAVY_TOKEN = os.getenv('NAVY_TOKEN')
        self.MOSSAD_TOKEN = os.getenv('MOSSAD_TOKEN')
        self.UNIT_8200_TOKEN = os.getenv('UNIT_8200_TOKEN')
        self.CENTRAL_BANK_TOKEN = os.getenv('CENTRAL_BANK_TOKEN')
        self.MILITARY_INDUSTRIES_TOKEN = os.getenv('MILITARY_INDUSTRIES_TOKEN')
        self.ISRAEL_RADIO_TOKEN = os.getenv('ISRAEL_RADIO_TOKEN')
        self.NATIONAL_NEWS_TOKEN = os.getenv('NATIONAL_NEWS_TOKEN')
        
        # Google Gemini API
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        self.GEMINI_MODEL = "gemini-1.5-pro"
        
        # Server Configuration
        self.SERVER_ID = os.getenv('SERVER_ID')
        self.OWNER_ID = os.getenv('OWNER_ID')
        
        # Database Configuration
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///israel_rp.db')
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'israel_rp.log')
        
        # Economic Configuration
        self.STARTING_BALANCE = 1000  # Starting balance for new citizens
        self.DAILY_INCOME = 100       # Daily income for citizens
        self.TAX_RATE = 0.15          # 15% tax rate
        self.INFLATION_RATE = 0.02    # 2% monthly inflation
        
        # Military Configuration
        self.DEFCON_LEVELS = {
            5: "DEFCON 5 - Normal",
            4: "DEFCON 4 - Increased",
            3: "DEFCON 3 - Elevated",
            2: "DEFCON 2 - High",
            1: "DEFCON 1 - Maximum"
        }
        
        # Resource Configuration
        self.RESOURCES = {
            "water": 1000,
            "energy": 1000,
            "food": 1000,
            "materials": 1000,
            "technology": 100
        }
        
        # Role Permissions
        self.ROLE_PERMISSIONS = {
            RoleType.TOURIST: ["view_channel", "send_messages"],
            RoleType.CITIZEN: ["view_channel", "send_messages", "use_external_emojis"],
            RoleType.SOLDIER: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.MINISTER: ["view_channel", "send_messages", "use_external_emojis", "attach_files", "manage_messages"],
            RoleType.PRIME_MINISTER: ["view_channel", "send_messages", "use_external_emojis", "attach_files", "manage_messages", "manage_channels"],
            RoleType.KNESSET_MEMBER: ["view_channel", "send_messages", "use_external_emojis", "attach_files", "manage_messages"],
            RoleType.SCIENTIST: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.DOCTOR: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.PILOT: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.JUDGE: ["view_channel", "send_messages", "use_external_emojis", "attach_files", "manage_messages"],
            RoleType.CRIMINAL: ["view_channel", "send_messages", "use_external_emojis"],
            RoleType.MOSSAD_AGENT: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.UNIT_8200_AGENT: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.BANKER: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.INDUSTRIALIST: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.JOURNALIST: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.TEACHER: ["view_channel", "send_messages", "use_external_emojis", "attach_files"],
            RoleType.ENGINEER: ["view_channel", "send_messages", "use_external_emojis", "attach_files"]
        }
        
        # Channel Configuration
        self.CHANNELS = {
            "government": ["#دولت", "#کنست", "#کابینه", "#وزارت‌خانه‌ها"],
            "military": ["#ارتش", "#نیروی_هوایی", "#نیروی_زمینی", "#نیروی_دریایی", "#دفاع_هوایی"],
            "economy": ["#اقتصاد", "#بانک_مرکزی", "#بورس", "#صنایع_نظامی"],
            "intelligence": ["#موساد", "#واحد_۸۲۰۰", "#اطلاعات_نظامی"],
            "civilian": ["#شهروندان", "#مهاجرت", "#کار", "#آموزش", "#بهداشت"],
            "media": ["#اخبار_ملی", "#رادیو_اسرائیل", "#فرهنگ", "#ورزش"],
            "war_room": ["#اتاق_جنگ", "#گزارشات_دفاعی", "#وضعیت_امنیتی"],
            "private": ["#خانه_خصوصی", "#دفتر_خصوصی", "#اتاق_جلسات"]
        }
        
        # Color Configuration
        self.COLORS = {
            "success": 0x00FF00,      # Green
            "error": 0xFF0000,        # Red
            "warning": 0xFFFF00,      # Yellow
            "info": 0x0099FF,         # Blue
            "government": 0x9932CC,   # Purple
            "military": 0x8B0000,     # Dark Red
            "economy": 0xFFD700,      # Gold
            "intelligence": 0x000080,  # Navy Blue
            "civilian": 0x32CD32,     # Lime Green
            "media": 0xFF69B4,        # Hot Pink
            "war": 0x800000,          # Maroon
            "private": 0x696969       # Dim Gray
        }
        
        # Time Configuration
        self.GAME_DAYS_PER_REAL_DAY = 7  # 1 real day = 7 game days
        self.ELECTION_INTERVAL_DAYS = 30  # Elections every 30 game days
        self.CRISIS_INTERVAL_HOURS = 6    # Random crisis every 6 hours
        
        # Skill Configuration
        self.SKILLS = {
            "leadership": {"max_level": 10, "xp_per_level": 1000},
            "negotiation": {"max_level": 10, "xp_per_level": 800},
            "technical": {"max_level": 10, "xp_per_level": 1200},
            "combat": {"max_level": 10, "xp_per_level": 1500},
            "intelligence": {"max_level": 10, "xp_per_level": 2000},
            "economics": {"max_level": 10, "xp_per_level": 900},
            "diplomacy": {"max_level": 10, "xp_per_level": 1100},
            "science": {"max_level": 10, "xp_per_level": 1300}
        }
        
        # Achievement Configuration
        self.ACHIEVEMENTS = {
            "first_prime_minister": {"name": "نخستین نخست‌وزیر", "description": "اولین نخست‌وزیر سرور", "reward": 10000},
            "first_billionaire": {"name": "اولین میلیاردر", "description": "رسیدن به یک میلیارد شِکِل", "reward": 50000},
            "war_hero": {"name": "قهرمان جنگ", "description": "کسب ۱۰ پیروزی نظامی", "reward": 25000},
            "scientist": {"name": "دانشمند برجسته", "description": "رسیدن به سطح ۱۰ مهارت علمی", "reward": 15000},
            "diplomat": {"name": "دیپلمات ماهر", "description": "انعقاد ۵ اتحاد", "reward": 20000}
        }

# Global configuration instance
config = Config()

# Export configuration
__all__ = ['config', 'BotType', 'RoleType', 'CategoryType', 'BotConfig', 'ServerConfig']