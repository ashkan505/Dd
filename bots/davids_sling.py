"""
ربات فلاخن داوود - مقابله با منشن، لینک‌های مخرب و حملات
David's Sling Bot - Handling Mentions, Malicious Links and Raids
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import logging
import datetime
import re
from typing import Dict, List, Optional, Any
import os
import sys

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BOT_TOKENS, SERVER_CONFIG, MILITARY_CONFIG
from utils.embed_helper import EmbedHelper

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/davids_sling.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class DavidsSlingBot(commands.Bot):
    """ربات فلاخن داوود - مقابله با منشن، لینک‌های مخرب و حملات"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # راه‌اندازی کمک‌کننده‌ها
        self.embed_helper = EmbedHelper()
        
        # وضعیت‌های دفاعی
        self.defense_status = {
            "mentions_blocked": 0,     # تعداد منشن‌های مسدود شده
            "links_blocked": 0,        # تعداد لینک‌های مسدود شده
            "raids_prevented": 0,      # تعداد حملات جلوگیری شده
            "quarantine_active": False, # وضعیت قرنطینه
            "last_attack": None
        }
        
        # تنظیمات تشخیص تهدید
        self.threat_settings = {
            "max_mentions_per_message": 3,  # حداکثر منشن در پیام
            "suspicious_link_patterns": [    # الگوهای لینک مشکوک
                r"discord\.gg/[a-zA-Z0-9]+",
                r"bit\.ly/[a-zA-Z0-9]+",
                r"tinyurl\.com/[a-zA-Z0-9]+",
                r"goo\.gl/[a-zA-Z0-9]+"
            ],
            "raid_threshold": 5,            # آستانه تشخیص حمله
            "quarantine_duration": 30       # مدت قرنطینه (دقیقه)
        }
        
        # ردیابی فعالیت‌های مشکوک
        self.suspicious_activity = {}
        
        # داده‌های ذخیره‌شده
        self.data_file = "data/davids_sling_data.json"
        self.load_data()
        
        logger.info("🏹 ربات فلاخن داوود راه‌اندازی شد")
    
    async def setup_hook(self):
        """راه‌اندازی اولیه ربات"""
        await self.add_cog(DefenseCommands(self))
        await self.add_cog(ThreatDetection(self))
        
        logger.info("✅ تمام کامندها با موفقیت بارگذاری شدند")
    
    def load_data(self):
        """بارگذاری داده‌های ذخیره‌شده"""
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.defense_status.update(data.get('defense_status', {}))
                    logger.info("✅ داده‌های دفاعی بارگذاری شدند")
            else:
                self.save_data()
                logger.info("✅ فایل داده‌های جدید ایجاد شد")
        except Exception as e:
            logger.error(f"❌ خطا در بارگذاری داده‌ها: {e}")
    
    def save_data(self):
        """ذخیره داده‌های دفاعی"""
        try:
            data = {
                'defense_status': self.defense_status,
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("✅ داده‌های دفاعی ذخیره شدند")
        except Exception as e:
            logger.error(f"❌ خطا در ذخیره داده‌ها: {e}")
    
    async def on_ready(self):
        """رویداد آماده شدن ربات"""
        logger.info(f"🏹 ربات فلاخن داوود آماده شد: {self.user}")
        
        # تنظیم وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="حفاظت از سرور اسرائیل 🏹"
            )
        )
    
    async def on_message(self, message):
        """رویداد دریافت پیام"""
        if message.author.bot:
            return
        
        # بررسی تهدیدات
        await self.check_threats(message)
        
        # پردازش کامندها
        await self.process_commands(message)
    
    async def check_threats(self, message):
        """بررسی پیام برای تشخیص تهدیدات"""
        try:
            # بررسی منشن‌های مشکوک
            if await self.check_mentions(message):
                await self.handle_mention_threat(message)
            
            # بررسی لینک‌های مشکوک
            if await self.check_suspicious_links(message):
                await self.handle_link_threat(message)
            
            # بررسی حملات
            if await self.check_raid_activity(message):
                await self.handle_raid_threat(message)
                
        except Exception as e:
            logger.error(f"❌ خطا در بررسی تهدیدات: {e}")
    
    async def check_mentions(self, message) -> bool:
        """بررسی منشن‌های مشکوک"""
        try:
            mentions = message.mentions
            if len(mentions) > self.threat_settings["max_mentions_per_message"]:
                return True
            
            # بررسی منشن‌های متوالی
            content = message.content.lower()
            mention_count = content.count('@')
            if mention_count > self.threat_settings["max_mentions_per_message"]:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطا در بررسی منشن‌ها: {e}")
            return False
    
    async def check_suspicious_links(self, message) -> bool:
        """بررسی لینک‌های مشکوک"""
        try:
            content = message.content.lower()
            
            for pattern in self.threat_settings["suspicious_link_patterns"]:
                if re.search(pattern, content):
                    return True
            
            # بررسی لینک‌های بدون پروتکل
            if re.search(r'[a-zA-Z0-9]+\.[a-zA-Z]{2,}', content):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطا در بررسی لینک‌ها: {e}")
            return False
    
    async def check_raid_activity(self, message) -> bool:
        """بررسی فعالیت‌های حمله"""
        try:
            user_id = message.author.id
            current_time = datetime.datetime.now()
            
            # اضافه کردن کاربر به ردیاب
            if user_id not in self.suspicious_activity:
                self.suspicious_activity[user_id] = {
                    "messages": [],
                    "warnings": 0,
                    "first_seen": current_time
                }
            
            # اضافه کردن پیام جدید
            self.suspicious_activity[user_id]["messages"].append({
                "content": message.content,
                "timestamp": current_time
            })
            
            # حذف پیام‌های قدیمی (بیش از 5 دقیقه)
            cutoff_time = current_time - datetime.timedelta(minutes=5)
            self.suspicious_activity[user_id]["messages"] = [
                msg for msg in self.suspicious_activity[user_id]["messages"]
                if msg["timestamp"] > cutoff_time
            ]
            
            # بررسی تعداد پیام‌ها
            if len(self.suspicious_activity[user_id]["messages"]) > self.threat_settings["raid_threshold"]:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطا در بررسی فعالیت‌های حمله: {e}")
            return False
    
    async def handle_mention_threat(self, message):
        """مدیریت تهدید منشن"""
        try:
            self.defense_status["mentions_blocked"] += 1
            self.defense_status["last_attack"] = datetime.datetime.now().isoformat()
            
            # نمایش پیام دفاعی
            embed = self.embed_helper.create_warning_embed(
                title="🏹 فلاخن داوود فعال شد",
                description="منشن مشکوک شناسایی شد!"
            )
            
            await message.channel.send(embed=embed)
            
            # حذف پیام
            try:
                await message.delete()
                logger.info(f"✅ پیام منشن مشکوک از {message.author.display_name} حذف شد")
            except discord.Forbidden:
                logger.warning(f"⚠️ عدم دسترسی برای حذف پیام از {message.author.display_name}")
            
            # افزایش هشدار کاربر
            user_id = message.author.id
            if user_id in self.suspicious_activity:
                self.suspicious_activity[user_id]["warnings"] += 1
            
            self.save_data()
            
        except Exception as e:
            logger.error(f"❌ خطا در مدیریت تهدید منشن: {e}")
    
    async def handle_link_threat(self, message):
        """مدیریت تهدید لینک"""
        try:
            self.defense_status["links_blocked"] += 1
            self.defense_status["last_attack"] = datetime.datetime.now().isoformat()
            
            # نمایش پیام دفاعی
            embed = self.embed_helper.create_warning_embed(
                title="🏹 فلاخن داوود فعال شد",
                description="لینک مشکوک شناسایی شد!"
            )
            
            await message.channel.send(embed=embed)
            
            # حذف پیام
            try:
                await message.delete()
                logger.info(f"✅ پیام لینک مشکوک از {message.author.display_name} حذف شد")
            except discord.Forbidden:
                logger.warning(f"⚠️ عدم دسترسی برای حذف پیام از {message.author.display_name}")
            
            # افزایش هشدار کاربر
            user_id = message.author.id
            if user_id in self.suspicious_activity:
                self.suspicious_activity[user_id]["warnings"] += 1
            
            self.save_data()
            
        except Exception as e:
            logger.error(f"❌ خطا در مدیریت تهدید لینک: {e}")
    
    async def handle_raid_threat(self, message):
        """مدیریت تهدید حمله"""
        try:
            self.defense_status["raids_prevented"] += 1
            self.defense_status["last_attack"] = datetime.datetime.now().isoformat()
            
            # فعال‌سازی قرنطینه
            if not self.defense_status["quarantine_active"]:
                await self.activate_quarantine()
            
            # نمایش پیام دفاعی
            embed = self.embed_helper.create_military_embed(
                title="🚨 حمله شناسایی شد",
                description="سیستم قرنطینه فعال شد!",
                fields=[
                    {"name": "مهاجم", "value": message.author.mention, "inline": True},
                    {"name": "نوع تهدید", "value": "حمله", "inline": True},
                    {"name": "وضعیت", "value": "قرنطینه فعال", "inline": True}
                ]
            )
            
            await message.channel.send(embed=embed)
            
            # حذف پیام
            try:
                await message.delete()
                logger.info(f"✅ پیام حمله از {message.author.display_name} حذف شد")
            except discord.Forbidden:
                logger.warning(f"⚠️ عدم دسترسی برای حذف پیام از {message.author.display_name}")
            
            # افزایش هشدار کاربر
            user_id = message.author.id
            if user_id in self.suspicious_activity:
                self.suspicious_activity[user_id]["warnings"] += 1
            
            self.save_data()
            
        except Exception as e:
            logger.error(f"❌ خطا در مدیریت تهدید حمله: {e}")
    
    async def activate_quarantine(self):
        """فعال‌سازی حالت قرنطینه"""
        try:
            self.defense_status["quarantine_active"] = True
            
            # ارسال هشدار به اتاق جنگ
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if guild:
                war_room = discord.utils.get(guild.channels, name="اتاق-جنگ")
                if war_room:
                    embed = self.embed_helper.create_military_embed(
                        title="🚨 حالت قرنطینه فعال شد",
                        description="حمله شناسایی شده است. سرور در حالت قرنطینه قرار گرفت.",
                        fields=[
                            {"name": "زمان فعال‌سازی", "value": datetime.datetime.now().strftime("%H:%M:%S"), "inline": True},
                            {"name": "مدت قرنطینه", "value": f"{self.threat_settings['quarantine_duration']} دقیقه", "inline": True}
                        ]
                    )
                    
                    await war_room.send(embed=embed)
            
            # تنظیم تایمر برای پایان قرنطینه
            asyncio.create_task(self.end_quarantine_timer())
            
            logger.info("🚨 حالت قرنطینه فعال شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در فعال‌سازی قرنطینه: {e}")
    
    async def end_quarantine_timer(self):
        """تایمر پایان قرنطینه"""
        try:
            await asyncio.sleep(self.threat_settings["quarantine_duration"] * 60)
            
            self.defense_status["quarantine_active"] = False
            
            # ارسال پیام پایان قرنطینه
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if guild:
                war_room = discord.utils.get(guild.channels, name="اتاق-جنگ")
                if war_room:
                    embed = self.embed_helper.create_success_embed(
                        title="✅ حالت قرنطینه پایان یافت",
                        description="سرور از حالت قرنطینه خارج شد."
                    )
                    
                    await war_room.send(embed=embed)
            
            self.save_data()
            logger.info("✅ حالت قرنطینه پایان یافت")
            
        except Exception as e:
            logger.error(f"❌ خطا در پایان قرنطینه: {e}")

# کلاس کامندهای دفاعی
class DefenseCommands(commands.Cog):
    """کامندهای مربوط به دفاع و کنترل"""
    
    def __init__(self, bot: DavidsSlingBot):
        self.bot = bot
    
    @commands.command(name="status")
    @commands.has_permissions(administrator=True)
    async def defense_status(self, ctx):
        """نمایش وضعیت دفاعی فلاخن داوود"""
        try:
            embed = self.bot.embed_helper.create_military_embed(
                title="🏹 وضعیت فلاخن داوود",
                description="وضعیت لحظه‌ای سیستم دفاعی",
                fields=[
                    {"name": "🚫 منشن‌های مسدود شده", "value": f"{self.bot.defense_status['mentions_blocked']}", "inline": True},
                    {"name": "🔗 لینک‌های مسدود شده", "value": f"{self.bot.defense_status['links_blocked']}", "inline": True},
                    {"name": "🛡️ حملات جلوگیری شده", "value": f"{self.bot.defense_status['raids_prevented']}", "inline": True},
                    {"name": "🚨 قرنطینه فعال", "value": "✅ بله" if self.bot.defense_status['quarantine_active'] else "❌ خیر", "inline": True},
                    {"name": "⏰ آخرین حمله", "value": self.bot.defense_status['last_attack'] or "هیچ", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش وضعیت",
                description=f"خطا در نمایش وضعیت دفاعی: {str(e)}",
                error_code="SLING_001"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش وضعیت دفاعی: {e}")
    
    @commands.command(name="quarantine")
    @commands.has_permissions(administrator=True)
    async def force_quarantine(self, ctx, duration_minutes: int = 30):
        """اجبار فعال‌سازی قرنطینه"""
        try:
            if self.bot.defense_status["quarantine_active"]:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="قرنطینه فعال",
                    description="در حال حاضر قرنطینه فعال است."
                )
                await ctx.send(embed=embed)
                return
            
            # تغییر مدت قرنطینه
            self.bot.threat_settings["quarantine_duration"] = duration_minutes
            
            # فعال‌سازی قرنطینه
            await self.bot.activate_quarantine()
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ قرنطینه اجباری فعال شد",
                description=f"قرنطینه برای {duration_minutes} دقیقه فعال شد."
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در فعال‌سازی قرنطینه",
                description=f"خطا در فعال‌سازی قرنطینه: {str(e)}",
                error_code="SLING_002"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در فعال‌سازی قرنطینه: {e}")
    
    @commands.command(name="end_quarantine")
    @commands.has_permissions(administrator=True)
    async def end_quarantine(self, ctx):
        """پایان دادن به قرنطینه"""
        try:
            if not self.bot.defense_status["quarantine_active"]:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="قرنطینه غیرفعال",
                    description="در حال حاضر قرنطینه فعال نیست."
                )
                await ctx.send(embed=embed)
                return
            
            self.bot.defense_status["quarantine_active"] = False
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ قرنطینه پایان یافت",
                description="قرنطینه با دستور ادمین پایان یافت."
            )
            await ctx.send(embed=embed)
            
            self.bot.save_data()
            logger.info("✅ قرنطینه با دستور ادمین پایان یافت")
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در پایان قرنطینه",
                description=f"خطا در پایان قرنطینه: {str(e)}",
                error_code="SLING_003"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در پایان قرنطینه: {e}")

# کلاس تشخیص تهدید
class ThreatDetection(commands.Cog):
    """کلاس تشخیص و مدیریت تهدیدات"""
    
    def __init__(self, bot: DavidsSlingBot):
        self.bot = bot
    
    @commands.command(name="activity")
    async def check_activity(self, ctx, user: discord.Member = None):
        """بررسی فعالیت‌های مشکوک کاربر"""
        try:
            target_user = user or ctx.author
            user_id = target_user.id
            
            if user_id not in self.bot.suspicious_activity:
                embed = self.bot.embed_helper.create_info_embed(
                    title="📊 وضعیت فعالیت",
                    description=f"{target_user.display_name} هیچ فعالیت مشکوکی ندارد."
                )
            else:
                activity = self.bot.suspicious_activity[user_id]
                embed = self.bot.embed_helper.create_warning_embed(
                    title="📊 وضعیت فعالیت",
                    description=f"{target_user.display_name} دارای فعالیت مشکوک است.",
                    fields=[
                        {"name": "⚠️ هشدارها", "value": f"{activity['warnings']}", "inline": True},
                        {"name": "📝 پیام‌های اخیر", "value": f"{len(activity['messages'])}", "inline": True},
                        {"name": "🕐 اولین مشاهده", "value": activity['first_seen'].strftime("%H:%M:%S"), "inline": True}
                    ]
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در بررسی فعالیت",
                description=f"خطا در بررسی فعالیت: {str(e)}",
                error_code="SLING_004"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در بررسی فعالیت: {e}")

# راه‌اندازی ربات
async def main():
    """تابع اصلی راه‌اندازی ربات"""
    bot = DavidsSlingBot()
    
    try:
        await bot.start(BOT_TOKENS["davids_sling"])
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # اجرای ربات
    asyncio.run(main())