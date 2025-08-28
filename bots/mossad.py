"""
ربات موساد - جمع‌آوری اطلاعات و عملیات‌های مخفی
Mossad Intelligence Bot - Intelligence Gathering and Secret Operations
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import logging
import datetime
import random
from typing import Dict, List, Optional, Any
import os
import sys

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BOT_TOKENS, SERVER_CONFIG
from utils.embed_helper import EmbedHelper
from utils.gemini_helper import GeminiHelper

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mossad.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class MossadBot(commands.Bot):
    """ربات موساد - عملیات اطلاعاتی و جاسوسی"""
    
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
        self.gemini = GeminiHelper()
        
        # وضعیت عملیات‌های اطلاعاتی
        self.intelligence_status = {
            "operations_completed": 0,    # تعداد عملیات‌های تکمیل شده
            "intelligence_gathered": 0,   # تعداد اطلاعات جمع‌آوری شده
            "agents_active": 0,           # تعداد مأموران فعال
            "secrets_discovered": 0,      # تعداد اسرار کشف شده
            "last_operation": None,
            "security_level": "high"      # سطح امنیتی
        }
        
        # مأموران موساد
        self.agents = {}
        
        # عملیات‌های مخفی
        self.secret_operations = {}
        
        # اطلاعات جمع‌آوری شده
        self.intelligence_database = {}
        
        # مأموریت‌های جاری
        self.active_missions = {}
        
        # داده‌های ذخیره‌شده
        self.data_file = "data/mossad_data.json"
        self.load_data()
        
        # راه‌اندازی وظایف خودکار
        self.setup_tasks()
        
        logger.info("🕵️ ربات موساد راه‌اندازی شد")
    
    async def setup_hook(self):
        """راه‌اندازی اولیه ربات"""
        await self.add_cog(IntelligenceCommands(self))
        await self.add_cog(AgentCommands(self))
        await self.add_cog(SecretOperations(self))
        await self.add_cog(CounterIntelligence(self))
        
        logger.info("✅ تمام کامندها با موفقیت بارگذاری شدند")
    
    def setup_tasks(self):
        """راه‌اندازی وظایف خودکار"""
        self.intelligence_gathering.start()
        self.security_scan.start()
        self.mission_monitoring.start()
        
        logger.info("✅ وظایف خودکار راه‌اندازی شدند")
    
    def load_data(self):
        """بارگذاری داده‌های ذخیره‌شده"""
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.intelligence_status.update(data.get('intelligence_status', {}))
                    self.agents.update(data.get('agents', {}))
                    self.secret_operations.update(data.get('secret_operations', {}))
                    self.intelligence_database.update(data.get('intelligence_database', {}))
                    logger.info("✅ داده‌های اطلاعاتی بارگذاری شدند")
            else:
                self.save_data()
                logger.info("✅ فایل داده‌های جدید ایجاد شد")
        except Exception as e:
            logger.error(f"❌ خطا در بارگذاری داده‌ها: {e}")
    
    def save_data(self):
        """ذخیره داده‌های اطلاعاتی"""
        try:
            data = {
                'intelligence_status': self.intelligence_status,
                'agents': self.agents,
                'secret_operations': self.secret_operations,
                'intelligence_database': self.intelligence_database,
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("✅ داده‌های اطلاعاتی ذخیره شدند")
        except Exception as e:
            logger.error(f"❌ خطا در ذخیره داده‌ها: {e}")
    
    async def on_ready(self):
        """رویداد آماده شدن ربات"""
        logger.info(f"🕵️ ربات موساد آماده شد: {self.user}")
        
        # تنظیم وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="عملیات اطلاعاتی اسرائیل 🕵️"
            )
        )
    
    @tasks.loop(hours=4)
    async def intelligence_gathering(self):
        """جمع‌آوری خودکار اطلاعات"""
        try:
            # تولید اطلاعات تصادفی با Gemini
            intel_data = await self.generate_random_intelligence()
            
            if intel_data and "خطا" not in str(intel_data):
                intel_id = f"intel_{int(datetime.datetime.now().timestamp())}"
                self.intelligence_database[intel_id] = intel_data
                
                self.intelligence_status["intelligence_gathered"] += 1
                self.intelligence_status["last_operation"] = datetime.datetime.now().isoformat()
                
                # ارسال به چنل اطلاعاتی
                await self.broadcast_intelligence(intel_data)
                
                self.save_data()
                logger.info(f"✅ اطلاعات جدید جمع‌آوری شد: {intel_id}")
                
        except Exception as e:
            logger.error(f"❌ خطا در جمع‌آوری اطلاعات: {e}")
    
    @tasks.loop(hours=2)
    async def security_scan(self):
        """اسکن امنیتی سرور"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            # بررسی کاربران مشکوک
            suspicious_users = await self.scan_for_suspicious_users(guild)
            
            if suspicious_users:
                await self.report_suspicious_activity(suspicious_users)
                
        except Exception as e:
            logger.error(f"❌ خطا در اسکن امنیتی: {e}")
    
    @tasks.loop(minutes=30)
    async def mission_monitoring(self):
        """نظارت بر مأموریت‌های جاری"""
        try:
            current_time = datetime.datetime.now()
            completed_missions = []
            
            for mission_id, mission in self.active_missions.items():
                if mission["status"] == "active":
                    # بررسی زمان مأموریت
                    mission_start = datetime.datetime.fromisoformat(mission["start_time"])
                    mission_duration = mission.get("duration", 60)  # دقیقه
                    
                    if (current_time - mission_start).total_seconds() > mission_duration * 60:
                        # مأموریت تمام شده
                        await self.complete_mission(mission_id, mission)
                        completed_missions.append(mission_id)
            
            # حذف مأموریت‌های تکمیل شده
            for mission_id in completed_missions:
                del self.active_missions[mission_id]
                
        except Exception as e:
            logger.error(f"❌ خطا در نظارت بر مأموریت‌ها: {e}")
    
    async def generate_random_intelligence(self):
        """تولید اطلاعات تصادفی با Gemini"""
        try:
            intel_types = [
                "تحرکات نظامی",
                "فعالیت‌های اقتصادی",
                "تغییرات سیاسی",
                "فعالیت‌های اطلاعاتی",
                "تحرکات دیپلماتیک"
            ]
            
            intel_type = random.choice(intel_types)
            
            intel_data = await self.gemini.generate_content(
                f"یک گزارش اطلاعاتی کوتاه درباره {intel_type} در منطقه خاورمیانه تولید کن. این گزارش باید واقع‌گرایانه و حرفه‌ای باشد."
            )
            
            if intel_data and "خطا" not in intel_data:
                return {
                    "type": intel_type,
                    "content": intel_data,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "reliability": random.randint(70, 95),
                    "source": "مأموران مخفی"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطا در تولید اطلاعات تصادفی: {e}")
            return None
    
    async def scan_for_suspicious_users(self, guild):
        """اسکن کاربران مشکوک"""
        try:
            suspicious_users = []
            
            for member in guild.members:
                # بررسی معیارهای مشکوک
                if await self.is_user_suspicious(member):
                    suspicious_users.append(member)
            
            return suspicious_users
            
        except Exception as e:
            logger.error(f"❌ خطا در اسکن کاربران مشکوک: {e}")
            return []
    
    async def is_user_suspicious(self, member):
        """بررسی مشکوک بودن کاربر"""
        try:
            # معیارهای مشکوک
            account_age = (datetime.datetime.now() - member.created_at).days
            
            # حساب بسیار جدید
            if account_age < 7:
                return True
            
            # بدون آواتار
            if member.avatar is None:
                return True
            
            # نام مشکوک
            username = member.display_name.lower()
            suspicious_keywords = ["hack", "spam", "bot", "fake", "test"]
            if any(keyword in username for keyword in suspicious_keywords):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطا در بررسی مشکوک بودن کاربر: {e}")
            return False
    
    async def report_suspicious_activity(self, suspicious_users):
        """گزارش فعالیت مشکوک"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            # ارسال به چنل امنیتی
            security_channel = discord.utils.get(guild.channels, name="آژانس-های-اطلاعاتی")
            if not security_channel:
                return
            
            users_text = "\n".join([f"• {user.display_name} ({user.id})" for user in suspicious_users])
            
            embed = self.embed_helper.create_warning_embed(
                title="🚨 فعالیت مشکوک شناسایی شد",
                description=f"{len(suspicious_users)} کاربر مشکوک شناسایی شدند:",
                fields=[
                    {"name": "کاربران مشکوک", "value": users_text, "inline": False}
                ]
            )
            
            await security_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ خطا در گزارش فعالیت مشکوک: {e}")
    
    async def broadcast_intelligence(self, intel_data):
        """اعلان اطلاعات جدید"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            intel_channel = discord.utils.get(guild.channels, name="آژانس-های-اطلاعاتی")
            if not intel_channel:
                return
            
            embed = self.embed_helper.create_news_embed(
                title=f"🕵️ اطلاعات جدید: {intel_data['type']}",
                description=intel_data["content"],
                author="موساد",
                category="اطلاعاتی"
            )
            
            embed.add_field(name="🔒 قابلیت اطمینان", value=f"{intel_data['reliability']}%", inline=True)
            embed.add_field(name="📡 منبع", value=intel_data["source"], inline=True)
            
            await intel_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ خطا در اعلان اطلاعات: {e}")
    
    async def create_mission(self, agent_id: str, mission_type: str, target: str, duration: int):
        """ایجاد مأموریت جدید"""
        try:
            mission_id = f"mission_{int(datetime.datetime.now().timestamp())}"
            
            mission = {
                "id": mission_id,
                "agent_id": agent_id,
                "type": mission_type,
                "target": target,
                "duration": duration,
                "status": "active",
                "start_time": datetime.datetime.now().isoformat(),
                "progress": 0,
                "risks": random.randint(20, 80)
            }
            
            self.active_missions[mission_id] = mission
            
            # ارسال مأموریت به مأمور
            await self.send_mission_to_agent(agent_id, mission)
            
            self.save_data()
            logger.info(f"✅ مأموریت جدید ایجاد شد: {mission_id}")
            
            return mission_id
            
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد مأموریت: {e}")
            return None
    
    async def send_mission_to_agent(self, agent_id: str, mission: Dict):
        """ارسال مأموریت به مأمور"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            agent_member = guild.get_member(int(agent_id))
            if not agent_member:
                return
            
            # ارسال پیام خصوصی
            embed = self.embed_helper.create_military_embed(
                title="🎯 مأموریت جدید",
                description="یک مأموریت جدید برای شما تعیین شده است.",
                fields=[
                    {"name": "نوع مأموریت", "value": mission["type"], "inline": True},
                    {"name": "هدف", "value": mission["target"], "inline": True},
                    {"name": "مدت", "value": f"{mission['duration']} دقیقه", "inline": True},
                    {"name": "سطح ریسک", "value": f"{mission['risks']}%", "inline": True}
                ]
            )
            
            try:
                await agent_member.send(embed=embed)
                logger.info(f"✅ مأموریت به {agent_member.display_name} ارسال شد")
            except:
                logger.warning(f"⚠️ عدم امکان ارسال مأموریت به {agent_member.display_name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در ارسال مأموریت: {e}")
    
    async def complete_mission(self, mission_id: str, mission: Dict):
        """تکمیل مأموریت"""
        try:
            # محاسبه نتیجه مأموریت
            success_rate = random.randint(60, 95)
            mission["status"] = "completed"
            mission["success_rate"] = success_rate
            mission["completion_time"] = datetime.datetime.now().isoformat()
            
            # به‌روزرسانی آمار
            self.intelligence_status["operations_completed"] += 1
            
            # پاداش مأمور
            if success_rate >= 80:
                await self.reward_agent(mission["agent_id"], "success")
            else:
                await self.reward_agent(mission["agent_id"], "partial")
            
            # ارسال گزارش تکمیل
            await self.broadcast_mission_completion(mission)
            
            self.save_data()
            logger.info(f"✅ مأموریت {mission_id} تکمیل شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در تکمیل مأموریت: {e}")
    
    async def reward_agent(self, agent_id: str, result: str):
        """پاداش مأمور"""
        try:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                
                if result == "success":
                    agent["experience"] = agent.get("experience", 0) + 100
                    agent["successful_missions"] = agent.get("successful_missions", 0) + 1
                else:
                    agent["experience"] = agent.get("experience", 0) + 50
                    agent["failed_missions"] = agent.get("failed_missions", 0) + 1
                
                # ارتقای سطح
                if agent["experience"] >= 1000 and agent.get("level", 1) == 1:
                    agent["level"] = 2
                    await self.announce_agent_promotion(agent_id)
                elif agent["experience"] >= 2500 and agent.get("level", 1) < 3:
                    agent["level"] = 3
                    await self.announce_agent_promotion(agent_id)
                
        except Exception as e:
            logger.error(f"❌ خطا در پاداش مأمور: {e}")
    
    async def announce_agent_promotion(self, agent_id: str):
        """اعلان ارتقای مأمور"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            agent_member = guild.get_member(int(agent_id))
            if not agent_member:
                return
            
            intel_channel = discord.utils.get(guild.channels, name="آژانس-های-اطلاعاتی")
            if not intel_channel:
                return
            
            embed = self.embed_helper.create_success_embed(
                title="🎖️ ارتقای مأمور",
                description=f"مأمور {agent_member.mention} ارتقا یافت!",
                fields=[
                    {"name": "مأمور", "value": agent_member.display_name, "inline": True},
                    {"name": "سطح جدید", "value": f"سطح {self.agents[agent_id]['level']}", "inline": True}
                ]
            )
            
            await intel_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ خطا در اعلان ارتقا: {e}")
    
    async def broadcast_mission_completion(self, mission: Dict):
        """اعلان تکمیل مأموریت"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            intel_channel = discord.utils.get(guild.channels, name="آژانس-های-اطلاعاتی")
            if not intel_channel:
                return
            
            agent_member = guild.get_member(int(mission["agent_id"]))
            agent_name = agent_member.display_name if agent_member else "مأمور ناشناس"
            
            embed = self.embed_helper.create_military_embed(
                title="✅ مأموریت تکمیل شد",
                description=f"مأموریت {mission['type']} تکمیل شد.",
                fields=[
                    {"name": "مأمور", "value": agent_name, "inline": True},
                    {"name": "نوع مأموریت", "value": mission["type"], "inline": True},
                    {"name": "هدف", "value": mission["target"], "inline": True},
                    {"name": "نرخ موفقیت", "value": f"{mission['success_rate']}%", "inline": True}
                ]
            )
            
            await intel_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ خطا در اعلان تکمیل مأموریت: {e}")

# کلاس کامندهای اطلاعاتی
class IntelligenceCommands(commands.Cog):
    """کامندهای مربوط به اطلاعات و عملیات"""
    
    def __init__(self, bot: MossadBot):
        self.bot = bot
    
    @commands.command(name="status")
    @commands.has_permissions(administrator=True)
    async def intelligence_status(self, ctx):
        """نمایش وضعیت عملیات‌های اطلاعاتی"""
        try:
            embed = self.bot.embed_helper.create_military_embed(
                title="🕵️ وضعیت موساد",
                description="وضعیت لحظه‌ای عملیات‌های اطلاعاتی",
                fields=[
                    {"name": "✅ عملیات‌های تکمیل شده", "value": f"{self.bot.intelligence_status['operations_completed']}", "inline": True},
                    {"name": "📊 اطلاعات جمع‌آوری شده", "value": f"{self.bot.intelligence_status['intelligence_gathered']}", "inline": True},
                    {"name": "🕵️ مأموران فعال", "value": f"{self.bot.intelligence_status['agents_active']}", "inline": True},
                    {"name": "🔐 اسرار کشف شده", "value": f"{self.bot.intelligence_status['secrets_discovered']}", "inline": True},
                    {"name": "🛡️ سطح امنیتی", "value": self.bot.intelligence_status["security_level"], "inline": True},
                    {"name": "⏰ آخرین عملیات", "value": self.bot.intelligence_status["last_operation"] or "هیچ", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش وضعیت",
                description=f"خطا در نمایش وضعیت اطلاعاتی: {str(e)}",
                error_code="MOSSAD_001"
            )
            await ctx.send(embed=embed)
            logger.error(f"❌ خطا در نمایش وضعیت اطلاعاتی: {e}")
    
    @commands.command(name="gather_intel")
    async def gather_intelligence(self, ctx, target: str):
        """جمع‌آوری اطلاعات درباره هدف مشخص"""
        try:
            user = ctx.author
            
            # بررسی رول مأمور موساد
            mossad_role = discord.utils.get(ctx.guild.roles, name="مامور_موساد")
            if not mossad_role or mossad_role not in user.roles:
                embed = self.bot.embed_helper.create_error_embed(
                    title="عدم صلاحیت",
                    description="فقط مأموران موساد می‌توانند از این کامند استفاده کنند.",
                    error_code="MOSSAD_002"
                )
                await ctx.send(embed=embed)
                return
            
            # تولید اطلاعات با Gemini
            intel_data = await self.bot.gemini.generate_content(
                f"یک گزارش اطلاعاتی کوتاه و حرفه‌ای درباره {target} تولید کن. این گزارش باید شامل جزئیات مهم و تحلیل باشد."
            )
            
            if intel_data and "خطا" not in intel_data:
                intel_id = f"intel_{int(datetime.datetime.now().timestamp())}"
                self.bot.intelligence_database[intel_id] = {
                    "type": "جمع‌آوری هدفمند",
                    "target": target,
                    "content": intel_data,
                    "agent": user.display_name,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "reliability": 85,
                    "source": "مأمور موساد"
                }
                
                self.bot.intelligence_status["intelligence_gathered"] += 1
                self.bot.save_data()
                
                embed = self.bot.embed_helper.create_success_embed(
                    title="✅ اطلاعات جمع‌آوری شد",
                    description=f"اطلاعات درباره {target} با موفقیت جمع‌آوری شد.",
                    fields=[
                        {"name": "هدف", "value": target, "inline": True},
                        {"name": "مأمور", "value": user.display_name, "inline": True},
                        {"name": "قابلیت اطمینان", "value": "85%", "inline": True}
                    ]
                )
                
                await ctx.send(embed=embed)
                
                # ارسال اطلاعات به چنل اطلاعاتی
                await self.bot.broadcast_intelligence(self.bot.intelligence_database[intel_id])
                
            else:
                embed = self.bot.embed_helper.create_error_embed(
                    title="خطا در جمع‌آوری اطلاعات",
                    description="خطا در تولید اطلاعات با هوش مصنوعی.",
                    error_code="MOSSAD_003"
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در جمع‌آوری اطلاعات",
                description=f"خطا در جمع‌آوری اطلاعات: {str(e)}",
                error_code="MOSSAD_004"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در جمع‌آوری اطلاعات: {e}")

# کلاس کامندهای مأموران
class AgentCommands(commands.Cog):
    """کامندهای مربوط به مأموران موساد"""
    
    def __init__(self, bot: MossadBot):
        self.bot = bot
    
    @commands.command(name="register_agent")
    @commands.has_permissions(administrator=True)
    async def register_agent(self, ctx, user: discord.Member):
        """ثبت‌نام مأمور جدید"""
        try:
            user_id = str(user.id)
            
            if user_id in self.bot.agents:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="مأمور قبلی",
                    description="این کاربر قبلاً به عنوان مأمور ثبت شده است."
                )
                await ctx.send(embed=embed)
                return
            
            # ایجاد مأمور جدید
            self.bot.agents[user_id] = {
                "user_id": user_id,
                "username": user.display_name,
                "level": 1,
                "experience": 0,
                "join_date": datetime.datetime.now().isoformat(),
                "successful_missions": 0,
                "failed_missions": 0,
                "specializations": [],
                "status": "active"
            }
            
            # اعطای رول مأمور موساد
            mossad_role = discord.utils.get(ctx.guild.roles, name="مامور_موساد")
            if mossad_role:
                await user.add_roles(mossad_role)
            
            self.bot.intelligence_status["agents_active"] += 1
            self.bot.save_data()
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ مأمور جدید ثبت شد",
                description=f"{user.display_name} به عنوان مأمور موساد ثبت شد.",
                fields=[
                    {"name": "مأمور", "value": user.display_name, "inline": True},
                    {"name": "سطح", "value": "سطح 1", "inline": True},
                    {"name": "وضعیت", "value": "فعال", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
            # ارسال پیام خصوصی
            try:
                welcome_embed = self.bot.embed_helper.create_info_embed(
                    title="🕵️ خوش آمدید به موساد",
                    description="شما به عنوان مأمور موساد ثبت شده‌اید.",
                    fields=[
                        {"name": "سطح اولیه", "value": "سطح 1", "inline": True},
                        {"name": "وظایف", "value": "جمع‌آوری اطلاعات و عملیات مخفی", "inline": True}
                    ]
                )
                await user.send(embed=welcome_embed)
            except:
                pass
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در ثبت‌نام مأمور",
                description=f"خطا در ثبت‌نام مأمور: {str(e)}",
                error_code="MOSSAD_005"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در ثبت‌نام مأمور: {e}")

# کلاس کامندهای عملیات مخفی
class SecretOperations(commands.Cog):
    """کلاس مربوط به عملیات‌های مخفی"""
    
    def __init__(self, bot: MossadBot):
        self.bot = bot
    
    @commands.command(name="create_mission")
    @commands.has_permissions(administrator=True)
    async def create_secret_mission(self, ctx, agent: discord.Member, mission_type: str, target: str, duration: int):
        """ایجاد مأموریت مخفی جدید"""
        try:
            agent_id = str(agent.id)
            
            if agent_id not in self.bot.agents:
                embed = self.bot.embed_helper.create_error_embed(
                    title="مأمور یافت نشد",
                    description="این کاربر مأمور موساد نیست.",
                    error_code="MOSSAD_006"
                )
                await ctx.send(embed=embed)
                return
            
            # ایجاد مأموریت
            mission_id = await self.bot.create_mission(agent_id, mission_type, target, duration)
            
            if mission_id:
                embed = self.bot.embed_helper.create_success_embed(
                    title="✅ مأموریت ایجاد شد",
                    description=f"مأموریت {mission_type} برای {agent.display_name} ایجاد شد.",
                    fields=[
                        {"name": "نوع مأموریت", "value": mission_type, "inline": True},
                        {"name": "هدف", "value": target, "inline": True},
                        {"name": "مدت", "value": f"{duration} دقیقه", "inline": True}
                    ]
                )
                
                await ctx.send(embed=embed)
            else:
                embed = self.bot.embed_helper.create_error_embed(
                    title="خطا در ایجاد مأموریت",
                    description="خطا در ایجاد مأموریت.",
                    error_code="MOSSAD_007"
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در ایجاد مأموریت",
                description=f"خطا در ایجاد مأموریت: {str(e)}",
                error_code="MOSSAD_008"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در ایجاد مأموریت: {e}")

# کلاس ضدجاسوسی
class CounterIntelligence(commands.Cog):
    """کلاس مربوط به ضدجاسوسی"""
    
    def __init__(self, bot: MossadBot):
        self.bot = bot
    
    @commands.command(name="scan")
    @commands.has_permissions(administrator=True)
    async def security_scan(self, ctx):
        """اجرای اسکن امنیتی دستی"""
        try:
            guild = ctx.guild
            
            embed = self.bot.embed_helper.create_info_embed(
                title="🔍 شروع اسکن امنیتی",
                description="اسکن امنیتی سرور آغاز شد..."
            )
            
            message = await ctx.send(embed=embed)
            
            # اجرای اسکن
            suspicious_users = await self.bot.scan_for_suspicious_users(guild)
            
            if suspicious_users:
                users_text = "\n".join([f"• {user.display_name} ({user.id})" for user in suspicious_users])
                
                result_embed = self.bot.embed_helper.create_warning_embed(
                    title="🚨 اسکن امنیتی تکمیل شد",
                    description=f"{len(suspicious_users)} کاربر مشکوک شناسایی شدند:",
                    fields=[
                        {"name": "کاربران مشکوک", "value": users_text, "inline": False}
                    ]
                )
            else:
                result_embed = self.bot.embed_helper.create_success_embed(
                    title="✅ اسکن امنیتی تکمیل شد",
                    description="هیچ کاربر مشکوکی شناسایی نشد."
                )
            
            await message.edit(embed=result_embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در اسکن امنیتی",
                description=f"خطا در اسکن امنیتی: {str(e)}",
                error_code="MOSSAD_009"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در اسکن امنیتی: {e}")

# راه‌اندازی ربات
async def main():
    """تابع اصلی راه‌اندازی ربات"""
    bot = MossadBot()
    
    try:
        await bot.start(BOT_TOKENS["mossad"])
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # اجرای ربات
    asyncio.run(main())