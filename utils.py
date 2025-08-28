"""
ابزارهای کمکی و کلاس‌های پایه
Utility functions and base classes for Israel RP Bot Ecosystem
"""

import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import aiohttp
import logging
from config import BotConfig, EMBED_COLORS, SYSTEM_MESSAGES
import pytz

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تنظیم Gemini AI
genai.configure(api_key=BotConfig.GEMINI_API_KEY)

class GeminiAI:
    """کلاس مدیریت هوش مصنوعی Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
    
    async def generate_content(self, prompt: str, context: str = "") -> str:
        """تولید محتوا با استفاده از Gemini AI"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                safety_settings=self.safety_settings
            )
            return response.text
        except Exception as e:
            logger.error(f"خطا در تولید محتوا Gemini: {e}")
            return "متأسفانه در حال حاضر نمی‌توانم پاسخ مناسبی تولید کنم."
    
    async def generate_news(self) -> Dict[str, str]:
        """تولید خبر تصادفی"""
        prompt = """
        یک خبر کوتاه و جالب برای سرور رول‌پلی اسرائیل تولید کن.
        خبر باید شامل عنوان، متن کوتاه و نوع خبر (مثبت/منفی/خنثی) باشد.
        خبر باید واقع‌گرایانه و مناسب برای بازی باشد.
        پاسخ را به صورت JSON با کلیدهای title, content, type برگردان.
        """
        try:
            response = await self.generate_content(prompt)
            # تلاش برای تجزیه JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "title": "اخبار روز",
                    "content": response[:200] + "...",
                    "type": "neutral"
                }
        except Exception as e:
            logger.error(f"خطا در تولید خبر: {e}")
            return {
                "title": "اخبار سیستم",
                "content": "در حال حاضر خبری برای اعلام وجود ندارد.",
                "type": "neutral"
            }
    
    async def generate_crisis(self) -> Dict[str, str]:
        """تولید بحران تصادفی"""
        crisis_types = [
            "زلزله", "سیل", "رسوایی سیاسی", "اعتصاب", 
            "حمله سایبری", "بحران اقتصادی", "مشکل دیپلماتیک"
        ]
        crisis_type = random.choice(crisis_types)
        
        prompt = f"""
        یک بحران {crisis_type} برای سرور رول‌پلی اسرائیل تولید کن.
        بحران باید شامل عنوان، توضیحات، راه‌حل‌های پیشنهادی و تأثیرات احتمالی باشد.
        پاسخ را به صورت JSON با کلیدهای title, description, solutions, effects برگردان.
        """
        
        try:
            response = await self.generate_content(prompt)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "title": f"بحران {crisis_type}",
                    "description": "یک بحران غیرمنتظره رخ داده است.",
                    "solutions": ["تشکیل کمیته بحران", "تخصیص بودجه اضطراری"],
                    "effects": ["کاهش رضایت عمومی", "افزایش هزینه‌ها"]
                }
        except Exception as e:
            logger.error(f"خطا در تولید بحران: {e}")
            return {
                "title": "بحران سیستمی",
                "description": "یک مشکل فنی در سیستم رخ داده است.",
                "solutions": ["تماس با پشتیبانی فنی"],
                "effects": ["اختلال موقت در خدمات"]
            }
    
    async def generate_mission(self, role: str, difficulty: str = "medium") -> Dict[str, str]:
        """تولید مأموریت بر اساس نقش کاربر"""
        prompt = f"""
        یک مأموریت {difficulty} برای شخصی با نقش {role} در سرور رول‌پلی اسرائیل تولید کن.
        مأموریت باید شامل عنوان، توضیحات، اهداف و پاداش باشد.
        پاسخ را به صورت JSON با کلیدهای title, description, objectives, reward برگردان.
        """
        
        try:
            response = await self.generate_content(prompt)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "title": f"مأموریت {role}",
                    "description": "یک مأموریت جدید برای شما تعریف شده است.",
                    "objectives": ["انجام وظایف محوله"],
                    "reward": "100 XP + 500 شکل"
                }
        except Exception as e:
            logger.error(f"خطا در تولید مأموریت: {e}")
            return {
                "title": "مأموریت عمومی",
                "description": "در انتظار تعریف مأموریت جدید...",
                "objectives": ["صبر و انتظار"],
                "reward": "50 XP"
            }

class DatabaseManager:
    """مدیریت پایگاه داده"""
    
    def __init__(self):
        self.db_path = "israel_rp.json"
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """بارگذاری داده‌ها از فایل"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_default_data()
        except Exception as e:
            logger.error(f"خطا در بارگذاری داده‌ها: {e}")
            return self.create_default_data()
    
    def save_data(self):
        """ذخیره داده‌ها در فایل"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"خطا در ذخیره داده‌ها: {e}")
    
    def create_default_data(self) -> Dict:
        """ایجاد داده‌های پیش‌فرض"""
        return {
            "users": {},
            "economy": {
                "national_budget": 10000000,
                "tax_collected": 0,
                "total_transactions": 0
            },
            "government": {
                "prime_minister": None,
                "ministers": {},
                "laws": [],
                "elections": []
            },
            "military": {
                "defcon_level": 5,
                "active_missions": [],
                "equipment": {
                    "iron_dome_missiles": 1000,
                    "david_sling_missiles": 500,
                    "arrow_3_missiles": 200,
                    "arrow_4_missiles": 100
                }
            },
            "statistics": {
                "public_approval": 75,
                "national_resources": {
                    "water": 100,
                    "energy": 100
                }
            },
            "events": [],
            "properties": {},
            "companies": {},
            "political_parties": {}
        }
    
    def get_user(self, user_id: int) -> Dict:
        """دریافت اطلاعات کاربر"""
        user_id_str = str(user_id)
        if user_id_str not in self.data["users"]:
            self.data["users"][user_id_str] = self.create_default_user()
            self.save_data()
        return self.data["users"][user_id_str]
    
    def create_default_user(self) -> Dict:
        """ایجاد کاربر پیش‌فرض"""
        return {
            "balance": 1000,
            "role": "tourist",
            "xp": 0,
            "skills": {
                "leadership": 0,
                "negotiation": 0,
                "technical": 0,
                "combat": 0
            },
            "properties": [],
            "achievements": [],
            "last_daily": None,
            "missions_completed": 0,
            "votes_participated": 0,
            "join_date": datetime.now().isoformat()
        }
    
    def update_user(self, user_id: int, data: Dict):
        """به‌روزرسانی اطلاعات کاربر"""
        user_id_str = str(user_id)
        if user_id_str in self.data["users"]:
            self.data["users"][user_id_str].update(data)
            self.save_data()

class EmbedBuilder:
    """سازنده Embed های زیبا"""
    
    @staticmethod
    def create_embed(
        title: str,
        description: str = "",
        color: int = EMBED_COLORS['info'],
        thumbnail: str = None,
        image: str = None,
        fields: List[Dict] = None,
        footer: str = None,
        timestamp: bool = True
    ) -> discord.Embed:
        """ایجاد Embed با تنظیمات کامل"""
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if image:
            embed.set_image(url=image)
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
        
        if footer:
            embed.set_footer(text=footer)
        
        if timestamp:
            embed.timestamp = datetime.now(BotConfig.TIMEZONE)
        
        return embed
    
    @staticmethod
    def success_embed(title: str, description: str = "") -> discord.Embed:
        """Embed موفقیت"""
        return EmbedBuilder.create_embed(
            title=f"✅ {title}",
            description=description,
            color=EMBED_COLORS['success']
        )
    
    @staticmethod
    def error_embed(title: str, description: str = "") -> discord.Embed:
        """Embed خطا"""
        return EmbedBuilder.create_embed(
            title=f"❌ {title}",
            description=description,
            color=EMBED_COLORS['error']
        )
    
    @staticmethod
    def warning_embed(title: str, description: str = "") -> discord.Embed:
        """Embed هشدار"""
        return EmbedBuilder.create_embed(
            title=f"⚠️ {title}",
            description=description,
            color=EMBED_COLORS['warning']
        )
    
    @staticmethod
    def info_embed(title: str, description: str = "") -> discord.Embed:
        """Embed اطلاعات"""
        return EmbedBuilder.create_embed(
            title=f"ℹ️ {title}",
            description=description,
            color=EMBED_COLORS['info']
        )

class PermissionManager:
    """مدیریت مجوزها و دسترسی‌ها"""
    
    @staticmethod
    def has_role(member: discord.Member, role_name: str) -> bool:
        """بررسی داشتن نقش خاص"""
        return any(role.name == role_name for role in member.roles)
    
    @staticmethod
    def has_any_role(member: discord.Member, role_names: List[str]) -> bool:
        """بررسی داشتن یکی از نقش‌های مشخص"""
        member_roles = [role.name for role in member.roles]
        return any(role in member_roles for role in role_names)
    
    @staticmethod
    def is_admin(member: discord.Member) -> bool:
        """بررسی مدیر بودن"""
        return (member.guild_permissions.administrator or 
                member.id in BotConfig.ADMIN_USER_IDS)
    
    @staticmethod
    def is_government_member(member: discord.Member) -> bool:
        """بررسی عضو دولت بودن"""
        government_roles = ['نخست‌وزیر', 'وزیر', 'عضو کنست']
        return PermissionManager.has_any_role(member, government_roles)
    
    @staticmethod
    def is_military_member(member: discord.Member) -> bool:
        """بررسی عضو نظامی بودن"""
        military_roles = ['ژنرال', 'سرهنگ', 'سرگرد', 'سرباز', 'خلبان', 'افسر نیروی دریایی']
        return PermissionManager.has_any_role(member, military_roles)

class TimeManager:
    """مدیریت زمان و برنامه‌ریزی"""
    
    @staticmethod
    def get_current_time() -> datetime:
        """دریافت زمان فعلی با تنظیم منطقه زمانی"""
        return datetime.now(BotConfig.TIMEZONE)
    
    @staticmethod
    def format_time(dt: datetime) -> str:
        """فرمت کردن زمان"""
        return dt.strftime("%Y/%m/%d %H:%M:%S")
    
    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """بررسی یکسان بودن روز"""
        return dt1.date() == dt2.date()
    
    @staticmethod
    def get_time_until_next_event(event_time: datetime) -> timedelta:
        """محاسبه زمان باقی‌مانده تا رویداد بعدی"""
        return event_time - TimeManager.get_current_time()

class EconomyManager:
    """مدیریت اقتصاد"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_balance(self, user_id: int) -> int:
        """دریافت موجودی کاربر"""
        user = self.db.get_user(user_id)
        return user.get('balance', 0)
    
    def add_money(self, user_id: int, amount: int, reason: str = ""):
        """اضافه کردن پول به حساب کاربر"""
        user = self.db.get_user(user_id)
        user['balance'] = user.get('balance', 0) + amount
        self.db.update_user(user_id, user)
        
        # ثبت تراکنش
        self.log_transaction(user_id, amount, reason, "credit")
    
    def subtract_money(self, user_id: int, amount: int, reason: str = "") -> bool:
        """کم کردن پول از حساب کاربر"""
        user = self.db.get_user(user_id)
        current_balance = user.get('balance', 0)
        
        if current_balance >= amount:
            user['balance'] = current_balance - amount
            self.db.update_user(user_id, user)
            
            # ثبت تراکنش
            self.log_transaction(user_id, -amount, reason, "debit")
            return True
        return False
    
    def transfer_money(self, from_user: int, to_user: int, amount: int, reason: str = "") -> bool:
        """انتقال پول بین کاربران"""
        if self.subtract_money(from_user, amount, f"انتقال به کاربر {to_user}: {reason}"):
            self.add_money(to_user, amount, f"دریافت از کاربر {from_user}: {reason}")
            return True
        return False
    
    def log_transaction(self, user_id: int, amount: int, reason: str, type: str):
        """ثبت تراکنش"""
        transaction = {
            "user_id": user_id,
            "amount": amount,
            "reason": reason,
            "type": type,
            "timestamp": datetime.now().isoformat()
        }
        
        if "transactions" not in self.db.data:
            self.db.data["transactions"] = []
        
        self.db.data["transactions"].append(transaction)
        self.db.save_data()
    
    def calculate_daily_income(self, user_role: str) -> int:
        """محاسبه درآمد روزانه بر اساس نقش"""
        from config import EconomicConfig
        return EconomicConfig.DAILY_INCOME.get(user_role, 0)
    
    def collect_tax(self, amount: int, tax_type: str = "transaction") -> int:
        """جمع‌آوری مالیات"""
        from config import EconomicConfig
        tax_rate = EconomicConfig.TAX_RATES.get(f"{tax_type}_tax", 0)
        tax_amount = int(amount * tax_rate)
        
        # اضافه کردن به خزانه ملی
        self.db.data["economy"]["national_budget"] += tax_amount
        self.db.data["economy"]["tax_collected"] += tax_amount
        self.db.save_data()
        
        return tax_amount

class NotificationManager:
    """مدیریت اعلان‌ها و پیام‌ها"""
    
    @staticmethod
    async def send_dm(user: discord.User, embed: discord.Embed):
        """ارسال پیام خصوصی"""
        try:
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            logger.warning(f"نمی‌توان به کاربر {user.id} پیام خصوصی ارسال کرد")
            return False
        except Exception as e:
            logger.error(f"خطا در ارسال پیام خصوصی: {e}")
            return False
    
    @staticmethod
    async def send_channel_message(channel: discord.TextChannel, embed: discord.Embed):
        """ارسال پیام به کانال"""
        try:
            await channel.send(embed=embed)
            return True
        except Exception as e:
            logger.error(f"خطا در ارسال پیام به کانال: {e}")
            return False
    
    @staticmethod
    async def broadcast_message(guild: discord.Guild, embed: discord.Embed, channel_name: str = "general-chat"):
        """پخش پیام در کانال عمومی"""
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            await NotificationManager.send_channel_message(channel, embed)

class SecurityManager:
    """مدیریت امنیت و نظارت"""
    
    @staticmethod
    def is_spam(messages: List[discord.Message], threshold: int = 5, time_window: int = 10) -> bool:
        """تشخیص اسپم"""
        if len(messages) < threshold:
            return False
        
        recent_messages = [
            msg for msg in messages 
            if (datetime.now() - msg.created_at).seconds < time_window
        ]
        
        return len(recent_messages) >= threshold
    
    @staticmethod
    def is_raid(guild: discord.Guild, new_members_count: int, time_window: int = 60) -> bool:
        """تشخیص حمله جمعی"""
        threshold = max(5, guild.member_count // 100)  # حداقل 5 یا 1% اعضا
        return new_members_count >= threshold
    
    @staticmethod
    async def log_security_event(guild: discord.Guild, event_type: str, details: str):
        """ثبت رویداد امنیتی"""
        security_channel = discord.utils.get(guild.text_channels, name="war-room")
        if security_channel:
            embed = EmbedBuilder.create_embed(
                title=f"🚨 رویداد امنیتی: {event_type}",
                description=details,
                color=EMBED_COLORS['error']
            )
            await security_channel.send(embed=embed)

# کلاس پایه برای تمام ربات‌ها
class BaseBot(commands.Bot):
    """کلاس پایه برای تمام ربات‌ها"""
    
    def __init__(self, command_prefix: str, bot_name: str, **kwargs):
        intents = discord.Intents.all()
        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)
        
        self.bot_name = bot_name
        self.db = DatabaseManager()
        self.ai = GeminiAI()
        self.economy = EconomyManager(self.db)
        self.start_time = datetime.now()
        
        # تنظیم event handlers
        self.setup_events()
    
    def setup_events(self):
        """تنظیم event handler های پایه"""
        
        @self.event
        async def on_ready():
            logger.info(f"{self.bot_name} آماده است! ({self.user})")
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="🇮🇱 اسرائیل"
                )
            )
        
        @self.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                embed = EmbedBuilder.error_embed(
                    "دستور یافت نشد",
                    "این دستور وجود ندارد. از `!help` برای مشاهده دستورات استفاده کنید."
                )
                await ctx.send(embed=embed)
            elif isinstance(error, commands.MissingPermissions):
                embed = EmbedBuilder.error_embed(
                    "عدم دسترسی",
                    "شما مجوز استفاده از این دستور را ندارید."
                )
                await ctx.send(embed=embed)
            elif isinstance(error, commands.MissingRequiredArgument):
                embed = EmbedBuilder.error_embed(
                    "پارامتر ناقص",
                    f"پارامتر `{error.param.name}` الزامی است."
                )
                await ctx.send(embed=embed)
            else:
                logger.error(f"خطا در دستور: {error}")
                embed = EmbedBuilder.error_embed(
                    "خطای سیستم",
                    SYSTEM_MESSAGES['system_error']
                )
                await ctx.send(embed=embed)
    
    async def get_main_guild(self) -> Optional[discord.Guild]:
        """دریافت سرور اصلی"""
        return self.get_guild(BotConfig.MAIN_GUILD_ID)
    
    def get_uptime(self) -> str:
        """محاسبه مدت زمان آنلاین بودن"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{days} روز، {hours} ساعت، {minutes} دقیقه، {seconds} ثانیه"

# تابع کمکی برای اجرای چندین ربات
async def run_multiple_bots(bots: List[BaseBot]):
    """اجرای همزمان چندین ربات"""
    tasks = []
    for bot in bots:
        task = asyncio.create_task(bot.start(bot.token))
        tasks.append(task)
    
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات‌ها: {e}")
        for bot in bots:
            await bot.close()

# تابع کمکی برای فرمت کردن اعداد
def format_number(number: int) -> str:
    """فرمت کردن اعداد با جداکننده هزارگان"""
    return f"{number:,}".replace(",", "،")

# تابع کمکی برای تولید ID یکتا
def generate_unique_id() -> str:
    """تولید شناسه یکتا"""
    import uuid
    return str(uuid.uuid4())[:8]

# تابع کمکی برای محاسبه درصد
def calculate_percentage(part: int, total: int) -> float:
    """محاسبه درصد"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

# تابع کمکی برای انتخاب تصادفی با وزن
def weighted_random_choice(choices: List[Dict]) -> Dict:
    """انتخاب تصادفی با در نظر گیری وزن"""
    total_weight = sum(choice.get('weight', 1) for choice in choices)
    random_weight = random.uniform(0, total_weight)
    
    current_weight = 0
    for choice in choices:
        current_weight += choice.get('weight', 1)
        if random_weight <= current_weight:
            return choice
    
    return choices[-1] if choices else {}

# تابع کمکی برای تبدیل زمان به رشته فارسی
def time_to_persian(dt: datetime) -> str:
    """تبدیل زمان به فرمت فارسی"""
    persian_months = [
        "فروردین", "اردیبهشت", "خرداد", "تیر",
        "مرداد", "شهریور", "مهر", "آبان",
        "آذر", "دی", "بهمن", "اسفند"
    ]
    
    persian_weekdays = [
        "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه",
        "جمعه", "شنبه", "یکشنبه"
    ]
    
    # این یک تبدیل ساده است - برای تبدیل دقیق به تقویم شمسی نیاز به کتابخانه مخصوص است
    weekday = persian_weekdays[dt.weekday()]
    return f"{weekday}، {dt.day} {persian_months[dt.month-1]} {dt.year}"

# اموجی‌های مورد استفاده در سیستم
EMOJIS = {
    'israel_flag': '🇮🇱',
    'star_of_david': '✡️',
    'shield': '🛡️',
    'sword': '⚔️',
    'money': '💰',
    'government': '🏛️',
    'military': '🪖',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'fire': '🔥',
    'explosion': '💥',
    'rocket': '🚀',
    'target': '🎯',
    'medal': '🏅',
    'crown': '👑',
    'key': '🔑',
    'lock': '🔒',
    'bell': '🔔',
    'loudspeaker': '📢'
}