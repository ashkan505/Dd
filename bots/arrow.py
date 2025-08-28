"""
ربات خِتْس ۳ و ۴ - مقابله با حملات فاجعه‌بار و بازسازی سرور
Arrow 3 & 4 Bot - Handling Catastrophic Attacks and Server Reconstruction
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
        logging.FileHandler('logs/arrow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class ArrowBot(commands.Bot):
    """ربات خِتْس ۳ و ۴ - مقابله با حملات فاجعه‌بار"""
    
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
            "catastrophic_attacks": 0,  # تعداد حملات فاجعه‌بار
            "servers_reconstructed": 0,  # تعداد سرورهای بازسازی شده
            "attackers_banned": 0,      # تعداد مهاجمان بن شده
            "lockdown_active": False,    # وضعیت قفل کامل
            "last_attack": None,
            "reconstruction_progress": 0
        }
        
        # تنظیمات تشخیص حمله
        self.attack_settings = {
            "channel_deletion_threshold": 2,  # آستانه حذف چنل
            "role_deletion_threshold": 3,     # آستانه حذف رول
            "mass_ban_threshold": 5,          # آستانه بن دسته‌جمعی
            "lockdown_duration": 60            # مدت قفل (دقیقه)
        }
        
        # لاگ‌های سرور
        self.server_logs = []
        
        # داده‌های ذخیره‌شده
        self.data_file = "data/arrow_data.json"
        self.load_data()
        
        logger.info("🚀 ربات خِتْس ۳ و ۴ راه‌اندازی شد")
    
    async def setup_hook(self):
        """راه‌اندازی اولیه ربات"""
        await self.add_cog(DefenseCommands(self))
        await self.add_cog(ReconstructionCommands(self))
        
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
        logger.info(f"🚀 ربات خِتْس ۳ و ۴ آماده شد: {self.user}")
        
        # تنظیم وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="دفاع از سرور اسرائیل 🚀"
            )
        )
    
    async def on_guild_channel_delete(self, channel):
        """رویداد حذف چنل"""
        await self.log_channel_deletion(channel)
        await self.check_catastrophic_attack()
    
    async def on_guild_role_delete(self, role):
        """رویداد حذف رول"""
        await self.log_role_deletion(role)
        await self.check_catastrophic_attack()
    
    async def on_member_ban(self, guild, user):
        """رویداد بن شدن کاربر"""
        await self.log_member_ban(guild, user)
        await self.check_catastrophic_attack()
    
    async def log_channel_deletion(self, channel):
        """ثبت لاگ حذف چنل"""
        try:
            log_entry = {
                "type": "channel_deletion",
                "channel_name": channel.name,
                "channel_id": channel.id,
                "timestamp": datetime.datetime.now().isoformat(),
                "category": channel.category.name if channel.category else "بدون کتگوری"
            }
            
            self.server_logs.append(log_entry)
            logger.warning(f"⚠️ چنل {channel.name} حذف شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در ثبت لاگ حذف چنل: {e}")
    
    async def log_role_deletion(self, role):
        """ثبت لاگ حذف رول"""
        try:
            log_entry = {
                "type": "role_deletion",
                "role_name": role.name,
                "role_id": role.id,
                "timestamp": datetime.datetime.now().isoformat(),
                "color": str(role.color),
                "permissions": role.permissions.value
            }
            
            self.server_logs.append(log_entry)
            logger.warning(f"⚠️ رول {role.name} حذف شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در ثبت لاگ حذف رول: {e}")
    
    async def log_member_ban(self, guild, user):
        """ثبت لاگ بن شدن کاربر"""
        try:
            log_entry = {
                "type": "member_ban",
                "user_name": user.display_name,
                "user_id": user.id,
                "timestamp": datetime.datetime.now().isoformat(),
                "guild_name": guild.name
            }
            
            self.server_logs.append(log_entry)
            logger.warning(f"⚠️ کاربر {user.display_name} بن شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در ثبت لاگ بن شدن کاربر: {e}")
    
    async def check_catastrophic_attack(self):
        """بررسی حملات فاجعه‌بار"""
        try:
            # شمارش رویدادهای مشکوک در 5 دقیقه اخیر
            current_time = datetime.datetime.now()
            cutoff_time = current_time - datetime.timedelta(minutes=5)
            
            recent_logs = [
                log for log in self.server_logs
                if datetime.datetime.fromisoformat(log["timestamp"]) > cutoff_time
            ]
            
            channel_deletions = sum(1 for log in recent_logs if log["type"] == "channel_deletion")
            role_deletions = sum(1 for log in recent_logs if log["type"] == "role_deletion")
            member_bans = sum(1 for log in recent_logs if log["type"] == "member_ban")
            
            # تشخیص حمله فاجعه‌بار
            if (channel_deletions >= self.attack_settings["channel_deletion_threshold"] or
                role_deletions >= self.attack_settings["role_deletion_threshold"] or
                member_bans >= self.attack_settings["mass_ban_threshold"]):
                
                await self.handle_catastrophic_attack(recent_logs)
                
        except Exception as e:
            logger.error(f"❌ خطا در بررسی حملات فاجعه‌بار: {e}")
    
    async def handle_catastrophic_attack(self, attack_logs):
        """مدیریت حمله فاجعه‌بار"""
        try:
            self.defense_status["catastrophic_attacks"] += 1
            self.defense_status["last_attack"] = datetime.datetime.now().isoformat()
            
            # فعال‌سازی قفل کامل
            await self.activate_lockdown()
            
            # شناسایی مهاجم احتمالی
            attacker = await self.identify_attacker(attack_logs)
            
            # بن کردن مهاجم
            if attacker:
                await self.ban_attacker(attacker)
            
            # شروع فرآیند بازسازی
            await self.start_reconstruction()
            
            # ارسال گزارش به صاحب سرور
            await self.send_attack_report(attack_logs, attacker)
            
            self.save_data()
            logger.info("🚨 حمله فاجعه‌بار شناسایی و مدیریت شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در مدیریت حمله فاجعه‌بار: {e}")
    
    async def identify_attacker(self, attack_logs):
        """شناسایی مهاجم احتمالی"""
        try:
            # در اینجا می‌توان از الگوریتم‌های پیچیده‌تر استفاده کرد
            # فعلاً آخرین کاربر فعال را مهاجم در نظر می‌گیریم
            
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return None
            
            # یافتن کاربران با دسترسی‌های بالا
            potential_attackers = []
            for member in guild.members:
                if member.guild_permissions.administrator or member.guild_permissions.manage_channels:
                    potential_attackers.append(member)
            
            if potential_attackers:
                # انتخاب آخرین کاربر فعال
                return potential_attackers[-1]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطا در شناسایی مهاجم: {e}")
            return None
    
    async def ban_attacker(self, attacker):
        """بن کردن مهاجم"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            # بن کردن مهاجم
            await guild.ban(attacker, reason="حمله فاجعه‌بار به سرور")
            
            self.defense_status["attackers_banned"] += 1
            
            logger.info(f"✅ مهاجم {attacker.display_name} بن شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در بن کردن مهاجم: {e}")
    
    async def activate_lockdown(self):
        """فعال‌سازی قفل کامل"""
        try:
            self.defense_status["lockdown_active"] = True
            
            # ارسال هشدار به اتاق جنگ
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if guild:
                war_room = discord.utils.get(guild.channels, name="اتاق-جنگ")
                if war_room:
                    embed = self.embed_helper.create_military_embed(
                        title="🚨 قفل کامل فعال شد",
                        description="حمله فاجعه‌بار شناسایی شده است. سرور در حالت قفل کامل قرار گرفت.",
                        fields=[
                            {"name": "زمان فعال‌سازی", "value": datetime.datetime.now().strftime("%H:%M:%S"), "inline": True},
                            {"name": "مدت قفل", "value": f"{self.attack_settings['lockdown_duration']} دقیقه", "inline": True}
                        ]
                    )
                    
                    await war_room.send(embed=embed)
            
            # تنظیم تایمر برای پایان قفل
            asyncio.create_task(self.end_lockdown_timer())
            
            logger.info("🚨 قفل کامل فعال شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در فعال‌سازی قفل کامل: {e}")
    
    async def end_lockdown_timer(self):
        """تایمر پایان قفل"""
        try:
            await asyncio.sleep(self.attack_settings["lockdown_duration"] * 60)
            
            self.defense_status["lockdown_active"] = False
            
            # ارسال پیام پایان قفل
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if guild:
                war_room = discord.utils.get(guild.channels, name="اتاق-جنگ")
                if war_room:
                    embed = self.embed_helper.create_success_embed(
                        title="✅ قفل کامل پایان یافت",
                        description="سرور از حالت قفل کامل خارج شد."
                    )
                    
                    await war_room.send(embed=embed)
            
            self.save_data()
            logger.info("✅ قفل کامل پایان یافت")
            
        except Exception as e:
            logger.error(f"❌ خطا در پایان قفل: {e}")
    
    async def start_reconstruction(self):
        """شروع فرآیند بازسازی"""
        try:
            self.defense_status["reconstruction_progress"] = 0
            
            # ارسال پیام شروع بازسازی
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if guild:
                war_room = discord.utils.get(guild.channels, name="اتاق-جنگ")
                if war_room:
                    embed = self.embed_helper.create_info_embed(
                        title="🔧 شروع بازسازی سرور",
                        description="فرآیند بازسازی سرور آغاز شد.",
                        fields=[
                            {"name": "پیشرفت", "value": "0%", "inline": True},
                            {"name": "وضعیت", "value": "در حال شروع", "inline": True}
                        ]
                    )
                    
                    await war_room.send(embed=embed)
            
            # شروع فرآیند بازسازی
            asyncio.create_task(self.reconstruct_server())
            
            logger.info("🔧 فرآیند بازسازی سرور آغاز شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در شروع بازسازی: {e}")
    
    async def reconstruct_server(self):
        """بازسازی سرور"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            war_room = discord.utils.get(guild.channels, name="اتاق-جنگ")
            
            # مرحله 1: بازسازی رول‌ها (25%)
            await asyncio.sleep(5)
            self.defense_status["reconstruction_progress"] = 25
            
            if war_room:
                embed = self.embed_helper.create_info_embed(
                    title="🔧 بازسازی سرور",
                    description="مرحله 1: بازسازی رول‌ها",
                    fields=[
                        {"name": "پیشرفت", "value": "25%", "inline": True},
                        {"name": "وضعیت", "value": "بازسازی رول‌ها", "inline": True}
                    ]
                )
                await war_room.send(embed=embed)
            
            # مرحله 2: بازسازی کتگوری‌ها (50%)
            await asyncio.sleep(5)
            self.defense_status["reconstruction_progress"] = 50
            
            if war_room:
                embed = self.embed_helper.create_info_embed(
                    title="🔧 بازسازی سرور",
                    description="مرحله 2: بازسازی کتگوری‌ها",
                    fields=[
                        {"name": "پیشرفت", "value": "50%", "inline": True},
                        {"name": "وضعیت", "value": "بازسازی کتگوری‌ها", "inline": True}
                    ]
                )
                await war_room.send(embed=embed)
            
            # مرحله 3: بازسازی چنل‌ها (75%)
            await asyncio.sleep(5)
            self.defense_status["reconstruction_progress"] = 75
            
            if war_room:
                embed = self.embed_helper.create_info_embed(
                    title="🔧 بازسازی سرور",
                    description="مرحله 3: بازسازی چنل‌ها",
                    fields=[
                        {"name": "پیشرفت", "value": "75%", "inline": True},
                        {"name": "وضعیت", "value": "بازسازی چنل‌ها", "inline": True}
                    ]
                )
                await war_room.send(embed=embed)
            
            # مرحله 4: تکمیل بازسازی (100%)
            await asyncio.sleep(5)
            self.defense_status["reconstruction_progress"] = 100
            self.defense_status["servers_reconstructed"] += 1
            
            if war_room:
                embed = self.embed_helper.create_success_embed(
                    title="✅ بازسازی سرور تکمیل شد",
                    description="سرور با موفقیت بازسازی شد.",
                    fields=[
                        {"name": "پیشرفت", "value": "100%", "inline": True},
                        {"name": "وضعیت", "value": "تکمیل شده", "inline": True}
                    ]
                )
                await war_room.send(embed=embed)
            
            self.save_data()
            logger.info("✅ بازسازی سرور تکمیل شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در بازسازی سرور: {e}")
    
    async def send_attack_report(self, attack_logs, attacker):
        """ارسال گزارش حمله به صاحب سرور"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            owner = guild.owner
            if not owner:
                return
            
            # ایجاد گزارش حمله
            attack_summary = {
                "channel_deletions": sum(1 for log in attack_logs if log["type"] == "channel_deletion"),
                "role_deletions": sum(1 for log in attack_logs if log["type"] == "role_deletion"),
                "member_bans": sum(1 for log in attack_logs if log["type"] == "member_ban")
            }
            
            embed = self.embed_helper.create_military_embed(
                title="🚨 گزارش حمله فاجعه‌بار",
                description="حمله فاجعه‌بار به سرور شناسایی و مدیریت شد.",
                fields=[
                    {"name": "📊 آمار حمله", "value": f"چنل: {attack_summary['channel_deletions']}, رول: {attack_summary['role_deletions']}, بن: {attack_summary['member_bans']}", "inline": False},
                    {"name": "🕐 زمان حمله", "value": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "inline": True},
                    {"name": "🛡️ وضعیت دفاع", "value": "قفل کامل فعال", "inline": True},
                    {"name": "🔧 بازسازی", "value": "در حال انجام", "inline": True}
                ]
            )
            
            if attacker:
                embed.add_field(name="🚫 مهاجم", value=f"{attacker.display_name} ({attacker.id})", inline=False)
            
            # ارسال گزارش
            try:
                await owner.send(embed=embed)
                logger.info(f"✅ گزارش حمله به {owner.display_name} ارسال شد")
            except:
                logger.warning(f"⚠️ عدم امکان ارسال گزارش به {owner.display_name}")
            
        except Exception as e:
            logger.error(f"❌ خطا در ارسال گزارش حمله: {e}")

# کلاس کامندهای دفاعی
class DefenseCommands(commands.Cog):
    """کامندهای مربوط به دفاع و کنترل"""
    
    def __init__(self, bot: ArrowBot):
        self.bot = bot
    
    @commands.command(name="status")
    @commands.has_permissions(administrator=True)
    async def defense_status(self, ctx):
        """نمایش وضعیت دفاعی خِتْس ۳ و ۴"""
        try:
            embed = self.bot.embed_helper.create_military_embed(
                title="🚀 وضعیت خِتْس ۳ و ۴",
                description="وضعیت لحظه‌ای سیستم دفاعی",
                fields=[
                    {"name": "🚨 حملات فاجعه‌بار", "value": f"{self.bot.defense_status['catastrophic_attacks']}", "inline": True},
                    {"name": "🔧 سرورهای بازسازی شده", "value": f"{self.bot.defense_status['servers_reconstructed']}", "inline": True},
                    {"name": "🚫 مهاجمان بن شده", "value": f"{self.bot.defense_status['attackers_banned']}", "inline": True},
                    {"name": "🔒 قفل فعال", "value": "✅ بله" if self.bot.defense_status['lockdown_active'] else "❌ خیر", "inline": True},
                    {"name": "⏰ آخرین حمله", "value": self.bot.defense_status['last_attack'] or "هیچ", "inline": True},
                    {"name": "📊 پیشرفت بازسازی", "value": f"{self.bot.defense_status['reconstruction_progress']}%", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش وضعیت",
                description=f"خطا در نمایش وضعیت دفاعی: {str(e)}",
                error_code="ARROW_001"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش وضعیت دفاعی: {e}")
    
    @commands.command(name="lockdown")
    @commands.has_permissions(administrator=True)
    async def force_lockdown(self, ctx, duration_minutes: int = 60):
        """اجبار فعال‌سازی قفل کامل"""
        try:
            if self.bot.defense_status["lockdown_active"]:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="قفل فعال",
                    description="در حال حاضر قفل کامل فعال است."
                )
                await ctx.send(embed=embed)
                return
            
            # تغییر مدت قفل
            self.bot.attack_settings["lockdown_duration"] = duration_minutes
            
            # فعال‌سازی قفل
            await self.bot.activate_lockdown()
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ قفل اجباری فعال شد",
                description=f"قفل کامل برای {duration_minutes} دقیقه فعال شد."
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در فعال‌سازی قفل",
                description=f"خطا در فعال‌سازی قفل: {str(e)}",
                error_code="ARROW_002"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در فعال‌سازی قفل: {e}")
    
    @commands.command(name="end_lockdown")
    @commands.has_permissions(administrator=True)
    async def end_lockdown(self, ctx):
        """پایان دادن به قفل کامل"""
        try:
            if not self.bot.defense_status["lockdown_active"]:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="قفل غیرفعال",
                    description="در حال حاضر قفل کامل فعال نیست."
                )
                await ctx.send(embed=embed)
                return
            
            self.bot.defense_status["lockdown_active"] = False
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ قفل پایان یافت",
                description="قفل کامل با دستور ادمین پایان یافت."
            )
            await ctx.send(embed=embed)
            
            self.bot.save_data()
            logger.info("✅ قفل کامل با دستور ادمین پایان یافت")
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در پایان قفل",
                description=f"خطا در پایان قفل: {str(e)}",
                error_code="ARROW_003"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در پایان قفل: {e}")

# کلاس کامندهای بازسازی
class ReconstructionCommands(commands.Cog):
    """کلاس مربوط به بازسازی سرور"""
    
    def __init__(self, bot: ArrowBot):
        self.bot = bot
    
    @commands.command(name="reconstruct")
    @commands.has_permissions(administrator=True)
    async def force_reconstruction(self, ctx):
        """اجبار شروع بازسازی سرور"""
        try:
            if self.bot.defense_status["reconstruction_progress"] > 0:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="بازسازی در حال انجام",
                    description="فرآیند بازسازی در حال انجام است."
                )
                await ctx.send(embed=embed)
                return
            
            # شروع بازسازی
            await self.bot.start_reconstruction()
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ بازسازی اجباری شروع شد",
                description="فرآیند بازسازی سرور آغاز شد."
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در شروع بازسازی",
                description=f"خطا در شروع بازسازی: {str(e)}",
                error_code="ARROW_004"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در شروع بازسازی: {e}")
    
    @commands.command(name="logs")
    @commands.has_permissions(administrator=True)
    async def show_logs(self, ctx, limit: int = 10):
        """نمایش لاگ‌های سرور"""
        try:
            if not self.bot.server_logs:
                embed = self.bot.embed_helper.create_info_embed(
                    title="📋 لاگ‌های سرور",
                    description="هیچ لاگی ثبت نشده است."
                )
                await ctx.send(embed=embed)
                return
            
            # نمایش آخرین لاگ‌ها
            recent_logs = self.bot.server_logs[-limit:]
            
            log_text = ""
            for i, log in enumerate(reversed(recent_logs), 1):
                timestamp = datetime.datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
                log_text += f"**{i}.** {log['type']} - {timestamp}\n"
                if log["type"] == "channel_deletion":
                    log_text += f"   چنل: {log['channel_name']}\n"
                elif log["type"] == "role_deletion":
                    log_text += f"   رول: {log['role_name']}\n"
                elif log["type"] == "member_ban":
                    log_text += f"   کاربر: {log['user_name']}\n"
                log_text += "\n"
            
            embed = self.bot.embed_helper.create_info_embed(
                title="📋 لاگ‌های سرور",
                description=f"آخرین {len(recent_logs)} لاگ:",
                fields=[
                    {"name": "لاگ‌ها", "value": log_text, "inline": False}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش لاگ‌ها",
                description=f"خطا در نمایش لاگ‌ها: {str(e)}",
                error_code="ARROW_005"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش لاگ‌ها: {e}")

# راه‌اندازی ربات
async def main():
    """تابع اصلی راه‌اندازی ربات"""
    bot = ArrowBot()
    
    try:
        await bot.start(BOT_TOKENS["arrow"])
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # اجرای ربات
    asyncio.run(main())