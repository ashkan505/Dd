"""
ربات گنبد آهنین - سیستم دفاعی ضد اسپم
Iron Dome Bot - Anti-Spam Defense System
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import logging
import datetime
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
        logging.FileHandler('logs/iron_dome.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class IronDomeBot(commands.Bot):
    """ربات گنبد آهنین - مقابله با اسپم پیام‌های کوتاه و سریع"""
    
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
            "missile_count": 100,  # تعداد موشک‌های موجود
            "interceptions": 0,    # تعداد رهگیری‌ها
            "spam_detected": 0,    # تعداد اسپم‌های شناسایی شده
            "last_interception": None
        }
        
        # تنظیمات تشخیص اسپم
        self.spam_settings = {
            "min_message_length": 5,      # حداقل طول پیام
            "max_messages_per_minute": 3,  # حداکثر پیام در دقیقه
            "spam_threshold": 5           # آستانه تشخیص اسپم
        }
        
        # ردیابی پیام‌های کاربران
        self.user_message_tracker = {}
        
        # داده‌های ذخیره‌شده
        self.data_file = "data/iron_dome_data.json"
        self.load_data()
        
        logger.info("🛡️ ربات گنبد آهنین راه‌اندازی شد")
    
    async def setup_hook(self):
        """راه‌اندازی اولیه ربات"""
        await self.add_cog(DefenseCommands(self))
        await self.add_cog(SpamDetection(self))
        
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
        logger.info(f"🛡️ ربات گنبد آهنین آماده شد: {self.user}")
        
        # تنظیم وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="دفاع از سرور اسرائیل 🛡️"
            )
        )
    
    async def on_message(self, message):
        """رویداد دریافت پیام"""
        if message.author.bot:
            return
        
        # بررسی اسپم
        await self.check_spam(message)
        
        # پردازش کامندها
        await self.process_commands(message)
    
    async def check_spam(self, message):
        """بررسی پیام برای تشخیص اسپم"""
        try:
            user_id = message.author.id
            current_time = datetime.datetime.now()
            
            # اضافه کردن کاربر به ردیاب
            if user_id not in self.user_message_tracker:
                self.user_message_tracker[user_id] = {
                    "messages": [],
                    "warnings": 0
                }
            
            # اضافه کردن پیام جدید
            self.user_message_tracker[user_id]["messages"].append({
                "content": message.content,
                "timestamp": current_time
            })
            
            # حذف پیام‌های قدیمی (بیش از 1 دقیقه)
            cutoff_time = current_time - datetime.timedelta(minutes=1)
            self.user_message_tracker[user_id]["messages"] = [
                msg for msg in self.user_message_tracker[user_id]["messages"]
                if msg["timestamp"] > cutoff_time
            ]
            
            # بررسی شرایط اسپم
            if self.is_spam(user_id):
                await self.intercept_spam(message, user_id)
                
        except Exception as e:
            logger.error(f"❌ خطا در بررسی اسپم: {e}")
    
    def is_spam(self, user_id: int) -> bool:
        """تشخیص اسپم بر اساس الگوهای مختلف"""
        try:
            user_data = self.user_message_tracker.get(user_id, {})
            messages = user_data.get("messages", [])
            
            if len(messages) == 0:
                return False
            
            # بررسی تعداد پیام‌ها در دقیقه
            if len(messages) > self.spam_settings["max_messages_per_minute"]:
                return True
            
            # بررسی طول پیام‌ها
            short_messages = sum(1 for msg in messages if len(msg["content"]) < self.spam_settings["min_message_length"])
            if short_messages > 2:
                return True
            
            # بررسی تکرار پیام‌ها
            content_counts = {}
            for msg in messages:
                content = msg["content"].lower().strip()
                content_counts[content] = content_counts.get(content, 0) + 1
                if content_counts[content] > 2:  # تکرار بیش از 2 بار
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطا در تشخیص اسپم: {e}")
            return False
    
    async def intercept_spam(self, message, user_id: int):
        """رهگیری و حذف اسپم"""
        try:
            # بررسی موجودی موشک
            if self.defense_status["missile_count"] <= 0:
                logger.warning("⚠️ موجودی موشک تمام شده است")
                return
            
            # کاهش موجودی موشک
            self.defense_status["missile_count"] -= 1
            self.defense_status["interceptions"] += 1
            self.defense_status["spam_detected"] += 1
            self.defense_status["last_interception"] = datetime.datetime.now().isoformat()
            
            # نمایش انیمیشن رهگیری
            embed = self.embed_helper.create_military_embed(
                title="🛡️ گنبد آهنین فعال شد",
                description="اسپم شناسایی و رهگیری شد!",
                fields=[
                    {"name": "هدف", "value": message.author.mention, "inline": True},
                    {"name": "نوع تهدید", "value": "اسپم پیام", "inline": True},
                    {"name": "موجودی موشک", "value": f"{self.defense_status['missile_count']}", "inline": True}
                ]
            )
            
            # ارسال پیام رهگیری
            await message.channel.send(embed=embed)
            
            # حذف پیام اسپم
            try:
                await message.delete()
                logger.info(f"✅ اسپم از {message.author.display_name} رهگیری و حذف شد")
            except discord.Forbidden:
                logger.warning(f"⚠️ عدم دسترسی برای حذف پیام از {message.author.display_name}")
            
            # افزایش هشدار کاربر
            self.user_message_tracker[user_id]["warnings"] += 1
            
            # ذخیره تغییرات
            self.save_data()
            
        except Exception as e:
            logger.error(f"❌ خطا در رهگیری اسپم: {e}")
    
    async def refill_missiles(self, count: int):
        """پر کردن موجودی موشک‌ها"""
        try:
            old_count = self.defense_status["missile_count"]
            self.defense_status["missile_count"] += count
            
            embed = self.embed_helper.create_success_embed(
                title="🚀 پر کردن موجودی موشک",
                description=f"موجودی موشک‌ها افزایش یافت",
                fields=[
                    {"name": "موجودی قبلی", "value": f"{old_count}", "inline": True},
                    {"name": "موجودی جدید", "value": f"{self.defense_status['missile_count']}", "inline": True},
                    {"name": "تعداد اضافه شده", "value": f"{count}", "inline": True}
                ]
            )
            
            # ارسال به چنل اتاق جنگ
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if guild:
                war_room = discord.utils.get(guild.channels, name="اتاق-جنگ")
                if war_room:
                    await war_room.send(embed=embed)
            
            self.save_data()
            logger.info(f"✅ موجودی موشک‌ها به {self.defense_status['missile_count']} افزایش یافت")
            
        except Exception as e:
            logger.error(f"❌ خطا در پر کردن موجودی موشک: {e}")

# کلاس کامندهای دفاعی
class DefenseCommands(commands.Cog):
    """کامندهای مربوط به دفاع و کنترل"""
    
    def __init__(self, bot: IronDomeBot):
        self.bot = bot
    
    @commands.command(name="status")
    @commands.has_permissions(administrator=True)
    async def defense_status(self, ctx):
        """نمایش وضعیت دفاعی گنبد آهنین"""
        try:
            embed = self.bot.embed_helper.create_military_embed(
                title="🛡️ وضعیت گنبد آهنین",
                description="وضعیت لحظه‌ای سیستم دفاعی",
                fields=[
                    {"name": "🚀 موجودی موشک", "value": f"{self.bot.defense_status['missile_count']}", "inline": True},
                    {"name": "🎯 رهگیری‌ها", "value": f"{self.bot.defense_status['interceptions']}", "inline": True},
                    {"name": "⚠️ اسپم شناسایی شده", "value": f"{self.bot.defense_status['spam_detected']}", "inline": True},
                    {"name": "⏰ آخرین رهگیری", "value": self.bot.defense_status['last_interception'] or "هیچ", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش وضعیت",
                description=f"خطا در نمایش وضعیت دفاعی: {str(e)}",
                error_code="IRON_001"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش وضعیت دفاعی: {e}")
    
    @commands.command(name="refill")
    @commands.has_permissions(administrator=True)
    async def refill_missiles(self, ctx, count: int):
        """پر کردن موجودی موشک‌ها"""
        try:
            if count <= 0:
                embed = self.bot.embed_helper.create_error_embed(
                    title="تعداد نامعتبر",
                    description="تعداد موشک باید مثبت باشد.",
                    error_code="IRON_002"
                )
                await ctx.send(embed=embed)
                return
            
            await self.bot.refill_missiles(count)
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ پر کردن موجودی",
                description=f"{count} موشک به موجودی اضافه شد."
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در پر کردن موجودی",
                description=f"خطا در پر کردن موجودی: {str(e)}",
                error_code="IRON_003"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در پر کردن موجودی: {e}")
    
    @commands.command(name="settings")
    @commands.has_permissions(administrator=True)
    async def show_settings(self, ctx):
        """نمایش تنظیمات تشخیص اسپم"""
        try:
            embed = self.bot.embed_helper.create_info_embed(
                title="⚙️ تنظیمات تشخیص اسپم",
                description="تنظیمات فعلی سیستم تشخیص اسپم",
                fields=[
                    {"name": "📏 حداقل طول پیام", "value": f"{self.bot.spam_settings['min_message_length']} کاراکتر", "inline": True},
                    {"name": "⏱️ حداکثر پیام در دقیقه", "value": f"{self.bot.spam_settings['max_messages_per_minute']}", "inline": True},
                    {"name": "🚨 آستانه تشخیص", "value": f"{self.bot.spam_settings['spam_threshold']}", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش تنظیمات",
                description=f"خطا در نمایش تنظیمات: {str(e)}",
                error_code="IRON_004"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش تنظیمات: {e}")

# کلاس تشخیص اسپم
class SpamDetection(commands.Cog):
    """کلاس تشخیص و مدیریت اسپم"""
    
    def __init__(self, bot: IronDomeBot):
        self.bot = bot
    
    @commands.command(name="warnings")
    async def check_warnings(self, ctx, user: discord.Member = None):
        """بررسی هشدارهای کاربر"""
        try:
            target_user = user or ctx.author
            user_id = target_user.id
            
            if user_id not in self.bot.user_message_tracker:
                embed = self.bot.embed_helper.create_info_embed(
                    title="📊 وضعیت هشدار",
                    description=f"{target_user.display_name} هیچ هشدار اسپمی ندارد."
                )
            else:
                warnings = self.bot.user_message_tracker[user_id]["warnings"]
                embed = self.bot.embed_helper.create_warning_embed(
                    title="📊 وضعیت هشدار",
                    description=f"{target_user.display_name} دارای {warnings} هشدار اسپم است."
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در بررسی هشدارها",
                description=f"خطا در بررسی هشدارها: {str(e)}",
                error_code="IRON_005"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در بررسی هشدارها: {e}")

# راه‌اندازی ربات
async def main():
    """تابع اصلی راه‌اندازی ربات"""
    bot = IronDomeBot()
    
    try:
        await bot.start(BOT_TOKENS["iron_dome"])
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # اجرای ربات
    asyncio.run(main())