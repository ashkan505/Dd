"""
ربات مرکزی ستاره داوود - مغز متفکر اکوسیستم رول‌پلی اسرائیل
Magen David Bot - The Mastermind of Israel RP Ecosystem
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

from config import BOT_TOKENS, SERVER_CONFIG, ROLE_IDS, CATEGORY_IDS, CHANNEL_IDS, ECONOMY_CONFIG
from utils.gemini_helper import GeminiHelper
from utils.embed_helper import EmbedHelper

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/magen_david.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class MagenDavidBot(commands.Bot):
    """ربات مرکزی ستاره داوود - کنترل‌کننده کل اکوسیستم"""
    
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
        self.gemini = GeminiHelper()
        self.embed_helper = EmbedHelper()
        
        # وضعیت‌های سرور
        self.server_status = {
            "defcon_level": 5,
            "public_approval": 75,
            "national_budget": 1000000,
            "active_citizens": 0,
            "active_military": 0,
            "government_formed": False,
            "election_active": False,
            "crisis_active": False
        }
        
        # داده‌های ذخیره‌شده
        self.data_file = "data/magen_david_data.json"
        self.load_data()
        
        # راه‌اندازی وظایف خودکار
        self.setup_tasks()
        
        logger.info("🤖 ربات مرکزی ستاره داوود راه‌اندازی شد")
    
    async def setup_hook(self):
        """راه‌اندازی اولیه ربات"""
        await self.add_cog(GovernmentCommands(self))
        await self.add_cog(CitizenshipCommands(self))
        await self.add_cog(ElectionCommands(self))
        await self.add_cog(ControlCommands(self))
        await self.add_cog(EventCommands(self))
        
        logger.info("✅ تمام کامندها با موفقیت بارگذاری شدند")
    
    def setup_tasks(self):
        """راه‌اندازی وظایف خودکار"""
        self.daily_income.start()
        self.random_events.start()
        self.environment_simulation.start()
        self.news_broadcast.start()
        
        logger.info("✅ وظایف خودکار راه‌اندازی شدند")
    
    def load_data(self):
        """بارگذاری داده‌های ذخیره‌شده"""
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.server_status.update(data.get('server_status', {}))
                    logger.info("✅ داده‌های سرور بارگذاری شدند")
            else:
                self.save_data()
                logger.info("✅ فایل داده‌های جدید ایجاد شد")
        except Exception as e:
            logger.error(f"❌ خطا در بارگذاری داده‌ها: {e}")
    
    def save_data(self):
        """ذخیره داده‌های سرور"""
        try:
            data = {
                'server_status': self.server_status,
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("✅ داده‌های سرور ذخیره شدند")
        except Exception as e:
            logger.error(f"❌ خطا در ذخیره داده‌ها: {e}")
    
    async def on_ready(self):
        """رویداد آماده شدن ربات"""
        logger.info(f"🤖 ربات مرکزی ستاره داوود آماده شد: {self.user}")
        logger.info(f"🏠 متصل به سرور: {len(self.guilds)} سرور")
        
        # تنظیم وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="سرور رول‌پلی اسرائیل 🇮🇱"
            )
        )
    
    @tasks.loop(hours=24)
    async def daily_income(self):
        """توزیع درآمد روزانه برای شهروندان"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            citizen_role = discord.utils.get(guild.roles, name="شهروند")
            if not citizen_role:
                return
            
            for member in citizen_role.members:
                # اینجا باید با ربات اقتصادی هماهنگ شود
                logger.info(f"💰 درآمد روزانه برای {member.display_name}")
            
            logger.info("✅ درآمد روزانه توزیع شد")
        except Exception as e:
            logger.error(f"❌ خطا در توزیع درآمد روزانه: {e}")
    
    @tasks.loop(hours=6)
    async def random_events(self):
        """تولید رویدادهای تصادفی"""
        try:
            if not self.server_status["crisis_active"]:
                event = await self.gemini.generate_random_event()
                if event and "خطا" not in str(event):
                    # ارسال رویداد به چنل اخبار ملی
                    await self.broadcast_event(event)
                    logger.info(f"🎲 رویداد تصادفی تولید شد: {event.get('title', 'بدون عنوان')}")
        except Exception as e:
            logger.error(f"❌ خطا در تولید رویداد تصادفی: {e}")
    
    @tasks.loop(hours=1)
    async def environment_simulation(self):
        """شبیه‌سازی محیطی (شب و روز، آب و هوا)"""
        try:
            current_hour = datetime.datetime.now().hour
            if current_hour in [6, 12, 18, 0]:  # هر 6 ساعت
                time_status = "🌅 صبح" if 6 <= current_hour < 12 else \
                             "☀️ ظهر" if 12 <= current_hour < 18 else \
                             "🌆 عصر" if 18 <= current_hour < 24 else "🌙 شب"
                
                # ارسال وضعیت محیطی
                await self.broadcast_environment_status(time_status)
        except Exception as e:
            logger.error(f"❌ خطا در شبیه‌سازی محیطی: {e}")
    
    @tasks.loop(minutes=30)
    async def news_broadcast(self):
        """پخش اخبار مهم"""
        try:
            if self.server_status["election_active"] or self.server_status["crisis_active"]:
                # تولید و ارسال اخبار مهم
                await self.broadcast_important_news()
        except Exception as e:
            logger.error(f"❌ خطا در پخش اخبار: {e}")
    
    async def broadcast_event(self, event: Dict[str, Any]):
        """ارسال رویداد به چنل اخبار ملی"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            news_channel = discord.utils.get(guild.channels, name="اخبار-ملی")
            if not news_channel:
                return
            
            embed = self.embed_helper.create_news_embed(
                title=event.get("title", "رویداد جدید"),
                description=event.get("description", "توضیحات رویداد"),
                author="سیستم خودکار",
                category="رویداد تصادفی"
            )
            
            await news_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"❌ خطا در ارسال رویداد: {e}")
    
    async def broadcast_environment_status(self, time_status: str):
        """ارسال وضعیت محیطی"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            general_channel = discord.utils.get(guild.channels, name="عمومی")
            if not general_channel:
                return
            
            embed = self.embed_helper.create_info_embed(
                title="وضعیت محیطی",
                description=f"زمان فعلی: {time_status}\nوضعیت آب و هوا: آفتابی ☀️",
                fields=[
                    {"name": "دما", "value": "25°C", "inline": True},
                    {"name": "رطوبت", "value": "45%", "inline": True},
                    {"name": "فشار هوا", "value": "1013 hPa", "inline": True}
                ]
            )
            
            await general_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"❌ خطا در ارسال وضعیت محیطی: {e}")
    
    async def broadcast_important_news(self):
        """پخش اخبار مهم"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            news_channel = discord.utils.get(guild.channels, name="اخبار-ملی")
            if not news_channel:
                return
            
            if self.server_status["election_active"]:
                news_text = await self.gemini.generate_news("انتخابات", {"status": "فعال"})
                embed = self.embed_helper.create_news_embed(
                    title="📰 اخبار انتخابات",
                    description=news_text,
                    author="سیستم انتخابات",
                    category="سیاسی"
                )
                await news_channel.send(embed=embed)
            
            if self.server_status["crisis_active"]:
                news_text = await self.gemini.generate_news("بحران", {"status": "فعال"})
                embed = self.embed_helper.create_news_embed(
                    title="🚨 اخبار بحران",
                    description=news_text,
                    author="سیستم مدیریت بحران",
                    category="بحران"
                )
                await news_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"❌ خطا در پخش اخبار مهم: {e}")

# کلاس کامندهای دولتی
class GovernmentCommands(commands.Cog):
    """کامندهای مربوط به دولت و کنست"""
    
    def __init__(self, bot: MagenDavidBot):
        self.bot = bot
    
    @commands.command(name="initialize_israel")
    @commands.has_permissions(administrator=True)
    async def initialize_israel(self, ctx):
        """راه‌اندازی کامل سرور اسرائیل"""
        try:
            embed = self.bot.embed_helper.create_info_embed(
                title="راه‌اندازی سرور اسرائیل",
                description="در حال راه‌اندازی سرور... لطفاً صبر کنید.",
                fields=[
                    {"name": "مرحله", "value": "شروع فرآیند", "inline": False}
                ]
            )
            
            message = await ctx.send(embed=embed)
            
            # مرحله 1: ایجاد رول‌ها
            await self.create_roles(ctx.guild)
            await message.edit(embed=self.update_progress_embed("ایجاد رول‌ها", 25))
            
            # مرحله 2: ایجاد کتگوری‌ها
            await self.create_categories(ctx.guild)
            await message.edit(embed=self.update_progress_embed("ایجاد کتگوری‌ها", 50))
            
            # مرحله 3: ایجاد چنل‌ها
            await self.create_channels(ctx.guild)
            await message.edit(embed=self.update_progress_embed("ایجاد چنل‌ها", 75))
            
            # مرحله 4: تنظیم پرمیشن‌ها
            await self.setup_permissions(ctx.guild)
            await message.edit(embed=self.update_progress_embed("تنظیم پرمیشن‌ها", 100))
            
            # تکمیل
            final_embed = self.bot.embed_helper.create_success_embed(
                title="راه‌اندازی تکمیل شد",
                description="سرور اسرائیل با موفقیت راه‌اندازی شد! 🎉",
                fields=[
                    {"name": "وضعیت", "value": "✅ آماده", "inline": True},
                    {"name": "زمان", "value": datetime.datetime.now().strftime("%H:%M:%S"), "inline": True}
                ]
            )
            
            await message.edit(embed=final_embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در راه‌اندازی",
                description=f"خطا در راه‌اندازی سرور: {str(e)}",
                error_code="INIT_001"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در راه‌اندازی سرور: {e}")
    
    async def create_roles(self, guild):
        """ایجاد رول‌های مورد نیاز"""
        roles_to_create = [
            ("شهروند", discord.Colour.green(), "شهروندان عادی اسرائیل"),
            ("سرباز", discord.Colour.blue(), "سربازان ارتش"),
            ("وزیر", discord.Colour.purple(), "وزرای کابینه"),
            ("نخست_وزیر", discord.Colour.gold(), "نخست‌وزیر اسرائیل"),
            ("عضو_کنست", discord.Colour.dark_purple(), "اعضای کنست"),
            ("دانشمند", discord.Colour.orange(), "دانشمندان و محققان"),
            ("پزشک", discord.Colour.red(), "پزشکان و کادر درمان"),
            ("خلبان", discord.Colour.dark_blue(), "خلبانان نیروی هوایی"),
            ("توریست", discord.Colour.light_grey(), "توریست‌های موقت"),
            ("قاضی", discord.Colour.dark_grey(), "قضات دادگاه"),
            ("مامور_موساد", discord.Colour.dark_red(), "ماموران موساد"),
            ("خلافکار", discord.Colour.dark_green(), "خلافکاران")
        ]
        
        for role_name, colour, reason in roles_to_create:
            if not discord.utils.get(guild.roles, name=role_name):
                await guild.create_role(name=role_name, colour=colour, reason=reason)
                logger.info(f"✅ رول {role_name} ایجاد شد")
    
    async def create_categories(self, guild):
        """ایجاد کتگوری‌های مورد نیاز"""
        categories_to_create = [
            ("دولت", "امور دولتی و سیاسی"),
            ("ارتش", "امور نظامی و دفاعی"),
            ("اقتصاد", "امور اقتصادی و مالی"),
            ("مناطق_شهری", "زندگی شهری و اجتماعی"),
            ("آژانس_های_اطلاعاتی", "امور اطلاعاتی و امنیتی"),
            ("دانشگاه", "آموزش و پژوهش")
        ]
        
        for cat_name, reason in categories_to_create:
            if not discord.utils.get(guild.categories, name=cat_name):
                await guild.create_category(name=cat_name, reason=reason)
                logger.info(f"✅ کتگوری {cat_name} ایجاد شد")
    
    async def create_channels(self, guild):
        """ایجاد چنل‌های مورد نیاز"""
        channels_to_create = [
            ("اداره-مهاجرت", "text", "دولت", "درخواست شهروندی"),
            ("اخبار-ملی", "text", "دولت", "اخبار رسمی کشور"),
            ("اتاق-جنگ", "text", "ارتش", "وضعیت دفاعی"),
            ("دادگاه", "text", "دولت", "رسیدگی به شکایات"),
            ("تالار-مشاهیر", "text", "مناطق_شهری", "دستاوردهای کاربران"),
            ("اداره-کار", "text", "اقتصاد", "درخواست شغل")
        ]
        
        for channel_name, channel_type, category_name, reason in channels_to_create:
            category = discord.utils.get(guild.categories, name=category_name)
            if category and not discord.utils.get(guild.channels, name=channel_name):
                if channel_type == "text":
                    await category.create_text_channel(name=channel_name, reason=reason)
                elif channel_type == "voice":
                    await category.create_voice_channel(name=channel_name, reason=reason)
                logger.info(f"✅ چنل {channel_name} ایجاد شد")
    
    async def setup_permissions(self, guild):
        """تنظیم پرمیشن‌های رول‌ها"""
        try:
            # تنظیم پرمیشن‌های رول توریست
            tourist_role = discord.utils.get(guild.roles, name="توریست")
            if tourist_role:
                for channel in guild.channels:
                    if channel.name in ["اداره-مهاجرت", "عمومی"]:
                        await channel.set_permissions(tourist_role, read_messages=True, send_messages=True)
                    else:
                        await channel.set_permissions(tourist_role, read_messages=False, send_messages=False)
            
            # تنظیم پرمیشن‌های رول شهروند
            citizen_role = discord.utils.get(guild.roles, name="شهروند")
            if citizen_role:
                for channel in guild.channels:
                    if channel.name not in ["اتاق-جنگ", "آژانس-های-اطلاعاتی"]:
                        await channel.set_permissions(citizen_role, read_messages=True, send_messages=True)
            
            logger.info("✅ پرمیشن‌های رول‌ها تنظیم شدند")
        except Exception as e:
            logger.error(f"❌ خطا در تنظیم پرمیشن‌ها: {e}")
    
    def update_progress_embed(self, stage: str, progress: int):
        """به‌روزرسانی Embed پیشرفت"""
        return self.bot.embed_helper.create_info_embed(
            title="راه‌اندازی سرور اسرائیل",
            description=f"در حال {stage}...",
            fields=[
                {"name": "مرحله فعلی", "value": stage, "inline": True},
                {"name": "پیشرفت", "value": f"{progress}%", "inline": True}
            ]
        )

# کلاس کامندهای شهروندی
class CitizenshipCommands(commands.Cog):
    """کامندهای مربوط به شهروندی و مهاجرت"""
    
    def __init__(self, bot: MagenDavidBot):
        self.bot = bot
        self.citizenship_applications = {}  # درخواست‌های شهروندی
    
    @commands.command(name="apply_citizenship")
    async def apply_citizenship(self, ctx):
        """درخواست شهروندی اسرائیل"""
        try:
            user = ctx.author
            
            # بررسی اینکه آیا کاربر قبلاً درخواست داده یا نه
            if user.id in self.citizenship_applications:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="درخواست قبلی",
                    description="شما قبلاً درخواست شهروندی داده‌اید. لطفاً منتظر بررسی بمانید."
                )
                await ctx.send(embed=embed)
                return
            
            # تولید سوالات شهروندی
            questions = await self.bot.gemini.generate_citizenship_questions()
            
            # ذخیره درخواست
            self.citizenship_applications[user.id] = {
                "questions": questions,
                "answers": {},
                "status": "waiting_answers",
                "start_time": datetime.datetime.now()
            }
            
            # ارسال سوالات
            embed = self.bot.embed_helper.create_citizenship_embed(questions, user)
            await ctx.send(embed=embed)
            
            logger.info(f"✅ درخواست شهروندی برای {user.display_name} ثبت شد")
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در درخواست شهروندی",
                description=f"خطا در ثبت درخواست: {str(e)}",
                error_code="CIT_001"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در درخواست شهروندی: {e}")
    
    @commands.command(name="answer")
    async def answer_question(self, ctx, question_number: int, *, answer: str):
        """پاسخ به سوال شهروندی"""
        try:
            user = ctx.author
            
            # بررسی وجود درخواست
            if user.id not in self.citizenship_applications:
                embed = self.bot.embed_helper.create_error_embed(
                    title="درخواست یافت نشد",
                    description="شما درخواست شهروندی ثبت نکرده‌اید.",
                    error_code="CIT_002"
                )
                await ctx.send(embed=embed)
                return
            
            application = self.citizenship_applications[user.id]
            
            # بررسی شماره سوال
            if question_number < 1 or question_number > len(application["questions"]):
                embed = self.bot.embed_helper.create_error_embed(
                    title="شماره سوال نامعتبر",
                    description=f"شماره سوال باید بین 1 تا {len(application['questions'])} باشد.",
                    error_code="CIT_003"
                )
                await ctx.send(embed=embed)
                return
            
            # ذخیره پاسخ
            application["answers"][question_number] = answer
            
            # بررسی تکمیل پاسخ‌ها
            if len(application["answers"]) == len(application["questions"]):
                await self.process_citizenship_application(ctx, user, application)
            else:
                embed = self.bot.embed_helper.create_success_embed(
                    title="پاسخ ثبت شد",
                    description=f"پاسخ شما به سوال {question_number} ثبت شد. {len(application['questions']) - len(application['answers'])} سوال باقی مانده است."
                )
                await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در ثبت پاسخ",
                description=f"خطا در ثبت پاسخ: {str(e)}",
                error_code="CIT_004"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در ثبت پاسخ: {e}")
    
    async def process_citizenship_application(self, ctx, user, application):
        """پردازش درخواست شهروندی"""
        try:
            # بررسی پاسخ‌ها (در اینجا می‌توان از Gemini برای ارزیابی استفاده کرد)
            correct_answers = 0
            total_questions = len(application["questions"])
            
            # ارزیابی ساده (در نسخه واقعی باید از Gemini استفاده شود)
            for i, answer in application["answers"].items():
                if len(answer) > 10:  # پاسخ‌های طولانی‌تر احتمالاً بهتر هستند
                    correct_answers += 1
            
            pass_rate = (correct_answers / total_questions) * 100
            
            if pass_rate >= 60:  # حداقل 60% برای قبولی
                # اعطای رول شهروند
                citizen_role = discord.utils.get(ctx.guild.roles, name="شهروند")
                if citizen_role:
                    await user.add_roles(citizen_role)
                    
                    # حذف رول توریست
                    tourist_role = discord.utils.get(ctx.guild.roles, name="توریست")
                    if tourist_role and tourist_role in user.roles:
                        await user.remove_roles(tourist_role)
                    
                    embed = self.bot.embed_helper.create_success_embed(
                        title="تبریک! شهروندی اعطا شد",
                        description=f"کاربر گرامی {user.mention}، شما با موفقیت شهروند اسرائیل شدید! 🎉",
                        fields=[
                            {"name": "نمره", "value": f"{pass_rate:.1f}%", "inline": True},
                            {"name": "وضعیت", "value": "قبول شده", "inline": True}
                        ]
                    )
                    
                    # ارسال پیام خصوصی
                    try:
                        await user.send("🎉 تبریک! شما شهروند اسرائیل شدید!")
                    except:
                        pass
                    
                    # حذف از لیست درخواست‌ها
                    del self.citizenship_applications[user.id]
                    
                    logger.info(f"✅ شهروندی برای {user.display_name} اعطا شد")
                    
                else:
                    embed = self.bot.embed_helper.create_error_embed(
                        title="خطا در اعطای شهروندی",
                        description="رول شهروند یافت نشد. لطفاً با مدیر تماس بگیرید.",
                        error_code="CIT_005"
                    )
            else:
                embed = self.bot.embed_helper.create_error_embed(
                    title="شهروندی رد شد",
                    description=f"متأسفانه شما نمره کافی کسب نکردید. نمره شما: {pass_rate:.1f}%",
                    error_code="CIT_006"
                )
                
                # حذف از لیست درخواست‌ها
                del self.citizenship_applications[user.id]
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در پردازش درخواست",
                description=f"خطا در پردازش درخواست: {str(e)}",
                error_code="CIT_007"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در پردازش درخواست شهروندی: {e}")

# کلاس کامندهای انتخابات
class ElectionCommands(commands.Cog):
    """کامندهای مربوط به انتخابات و رأی‌گیری"""
    
    def __init__(self, bot: MagenDavidBot):
        self.bot = bot
        self.active_elections = {}
        self.votes = {}
    
    @commands.command(name="start_election")
    @commands.has_permissions(administrator=True)
    async def start_election(self, ctx, duration_hours: int = 24):
        """شروع انتخابات نخست‌وزیری"""
        try:
            if self.bot.server_status["election_active"]:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="انتخابات فعال",
                    description="انتخابات در حال برگزاری است. لطفاً منتظر پایان انتخابات فعلی بمانید."
                )
                await ctx.send(embed=embed)
                return
            
            # ایجاد کاندیداها (در نسخه واقعی باید از کاربران واقعی استفاده شود)
            candidates = [
                {"name": "بنیامین نتانیاهو", "party": "لیکود", "slogan": "امنیت و رفاه"},
                {"name": "یائیر لاپید", "party": "یش عتید", "slogan": "تغییر و نوآوری"},
                {"name": "نفتالی بنت", "party": "یمینا", "slogan": "وحدت ملی"}
            ]
            
            end_time = datetime.datetime.now() + datetime.timedelta(hours=duration_hours)
            
            # ثبت انتخابات
            election_id = f"election_{int(datetime.datetime.now().timestamp())}"
            self.active_elections[election_id] = {
                "candidates": candidates,
                "end_time": end_time,
                "votes": {},
                "status": "active"
            }
            
            self.bot.server_status["election_active"] = True
            
            # ارسال Embed انتخابات
            embed = self.bot.embed_helper.create_election_embed(candidates, end_time)
            await ctx.send(embed=embed)
            
            logger.info(f"✅ انتخابات جدید شروع شد: {election_id}")
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در شروع انتخابات",
                description=f"خطا در شروع انتخابات: {str(e)}",
                error_code="ELE_001"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در شروع انتخابات: {e}")
    
    @commands.command(name="vote")
    async def vote(self, ctx, candidate_name: str):
        """ثبت رأی در انتخابات"""
        try:
            user = ctx.author
            
            # بررسی وجود انتخابات فعال
            if not self.bot.server_status["election_active"]:
                embed = self.bot.embed_helper.create_error_embed(
                    title="انتخابات فعال نیست",
                    description="در حال حاضر انتخابات فعالی وجود ندارد.",
                    error_code="ELE_002"
                )
                await ctx.send(embed=embed)
                return
            
            # بررسی رول شهروند
            citizen_role = discord.utils.get(ctx.guild.roles, name="شهروند")
            if not citizen_role or citizen_role not in user.roles:
                embed = self.bot.embed_helper.create_error_embed(
                    title="عدم صلاحیت",
                    description="فقط شهروندان می‌توانند در انتخابات شرکت کنند.",
                    error_code="ELE_003"
                )
                await ctx.send(embed=embed)
                return
            
            # یافتن انتخابات فعال
            active_election = None
            for election_id, election in self.active_elections.items():
                if election["status"] == "active":
                    active_election = election
                    break
            
            if not active_election:
                embed = self.bot.embed_helper.create_error_embed(
                    title="انتخابات یافت نشد",
                    description="انتخابات فعالی یافت نشد.",
                    error_code="ELE_004"
                )
                await ctx.send(embed=embed)
                return
            
            # بررسی اینکه آیا کاربر قبلاً رأی داده یا نه
            if user.id in active_election["votes"]:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="رأی قبلی",
                    description="شما قبلاً در این انتخابات رأی داده‌اید."
                )
                await ctx.send(embed=embed)
                return
            
            # یافتن کاندیدا
            candidate = None
            for c in active_election["candidates"]:
                if candidate_name.lower() in c["name"].lower():
                    candidate = c
                    break
            
            if not candidate:
                embed = self.bot.embed_helper.create_error_embed(
                    title="کاندیدا یافت نشد",
                    description=f"کاندیدایی با نام '{candidate_name}' یافت نشد.",
                    error_code="ELE_005"
                )
                await ctx.send(embed=embed)
                return
            
            # ثبت رأی
            active_election["votes"][user.id] = candidate["name"]
            
            embed = self.bot.embed_helper.create_success_embed(
                title="رأی ثبت شد",
                description=f"رأی شما برای {candidate['name']} ثبت شد.",
                fields=[
                    {"name": "کاندیدا", "value": candidate["name"], "inline": True},
                    {"name": "حزب", "value": candidate["party"], "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            logger.info(f"✅ رأی {user.display_name} برای {candidate['name']} ثبت شد")
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در ثبت رأی",
                description=f"خطا در ثبت رأی: {str(e)}",
                error_code="ELE_006"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در ثبت رأی: {e}")

# کلاس کامندهای کنترل
class ControlCommands(commands.Cog):
    """کامندهای کنترل و مدیریت"""
    
    def __init__(self, bot: MagenDavidBot):
        self.bot = bot
    
    @commands.command(name="control_panel")
    @commands.has_permissions(administrator=True)
    async def control_panel(self, ctx):
        """نمایش داشبورد کنترل مرکزی"""
        try:
            embed = self.bot.embed_helper.create_government_embed(
                title="داشبورد کنترل مرکزی",
                description="وضعیت لحظه‌ای تمام سیستم‌های سرور",
                fields=[
                    {"name": "🛡️ سطح آمادگی دفاعی", "value": f"DEFCON {self.bot.server_status['defcon_level']}", "inline": True},
                    {"name": "📊 رضایت عمومی", "value": f"{self.bot.server_status['public_approval']}%", "inline": True},
                    {"name": "💰 بودجه ملی", "value": f"{self.bot.server_status['national_budget']:,} شِکِل", "inline": True},
                    {"name": "👥 شهروندان فعال", "value": f"{self.bot.server_status['active_citizens']}", "inline": True},
                    {"name": "⚔️ نیروهای نظامی", "value": f"{self.bot.server_status['active_military']}", "inline": True},
                    {"name": "🏛️ دولت تشکیل شده", "value": "✅ بله" if self.bot.server_status['government_formed'] else "❌ خیر", "inline": True},
                    {"name": "🗳️ انتخابات فعال", "value": "✅ بله" if self.bot.server_status['election_active'] else "❌ خیر", "inline": True},
                    {"name": "🚨 بحران فعال", "value": "✅ بله" if self.bot.server_status['crisis_active'] else "❌ خیر", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش داشبورد",
                description=f"خطا در نمایش داشبورد: {str(e)}",
                error_code="CTRL_001"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش داشبورد: {e}")
    
    @commands.command(name="defcon")
    @commands.has_permissions(administrator=True)
    async def set_defcon(self, ctx, level: int):
        """تنظیم سطح آمادگی دفاعی"""
        try:
            if level < 1 or level > 5:
                embed = self.bot.embed_helper.create_error_embed(
                    title="سطح نامعتبر",
                    description="سطح DEFCON باید بین 1 تا 5 باشد.",
                    error_code="CTRL_002"
                )
                await ctx.send(embed=embed)
                return
            
            old_level = self.bot.server_status["defcon_level"]
            self.bot.server_status["defcon_level"] = level
            
            embed = self.bot.embed_helper.create_military_embed(
                title="تغییر سطح آمادگی دفاعی",
                description=f"سطح آمادگی دفاعی از DEFCON {old_level} به DEFCON {level} تغییر یافت.",
                fields=[
                    {"name": "سطح قبلی", "value": f"DEFCON {old_level}", "inline": True},
                    {"name": "سطح جدید", "value": f"DEFCON {level}", "inline": True},
                    {"name": "وضعیت", "value": "تغییر یافت", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
            # ذخیره تغییرات
            self.bot.save_data()
            
            logger.info(f"✅ سطح DEFCON به {level} تغییر یافت")
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در تنظیم DEFCON",
                description=f"خطا در تنظیم سطح آمادگی: {str(e)}",
                error_code="CTRL_003"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در تنظیم DEFCON: {e}")

# کلاس کامندهای رویدادها
class EventCommands(commands.Cog):
    """کامندهای مربوط به رویدادها و بحران‌ها"""
    
    def __init__(self, bot: MagenDavidBot):
        self.bot = bot
    
    @commands.command(name="trigger_crisis")
    @commands.has_permissions(administrator=True)
    async def trigger_crisis(self, ctx, crisis_type: str):
        """راه‌اندازی بحران (برای تست)"""
        try:
            if self.bot.server_status["crisis_active"]:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="بحران فعال",
                    description="در حال حاضر بحران فعالی وجود دارد."
                )
                await ctx.send(embed=embed)
                return
            
            # تولید بحران با Gemini
            crisis_details = await self.bot.gemini.generate_random_event()
            
            if crisis_details and "خطا" not in str(crisis_details):
                self.bot.server_status["crisis_active"] = True
                
                embed = self.bot.embed_helper.create_news_embed(
                    title=f"🚨 بحران {crisis_type}",
                    description=crisis_details.get("description", "توضیحات بحران"),
                    author="سیستم مدیریت بحران",
                    category="بحران"
                )
                
                await ctx.send(embed=embed)
                
                # ذخیره تغییرات
                self.bot.save_data()
                
                logger.info(f"✅ بحران {crisis_type} راه‌اندازی شد")
            else:
                embed = self.bot.embed_helper.create_error_embed(
                    title="خطا در تولید بحران",
                    description="خطا در تولید بحران با هوش مصنوعی.",
                    error_code="EVENT_001"
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در راه‌اندازی بحران",
                description=f"خطا در راه‌اندازی بحران: {str(e)}",
                error_code="EVENT_002"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در راه‌اندازی بحران: {e}")

# راه‌اندازی ربات
async def main():
    """تابع اصلی راه‌اندازی ربات"""
    bot = MagenDavidBot()
    
    try:
        await bot.start(BOT_TOKENS["magen_david"])
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # اجرای ربات
    asyncio.run(main())