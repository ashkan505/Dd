"""
ربات مرکزی ستاره داوود - مغز متفکر اکوسیستم اسرائیل
Magen David Bot - The Mastermind of Israeli Ecosystem
"""

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import json
import datetime
import random
from typing import Dict, List, Optional, Any, Union
from config import config
from models import db_manager, User, Government, Military, Economy
from gemini_integration import gemini_ai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MagenDavidBot(commands.Bot):
    """ربات مرکزی ستاره داوود"""
    
    def __init__(self):
        """راه‌اندازی ربات مرکزی"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.guild_reactions = True
        
        super().__init__(
            command_prefix=config.MAGEN_DAVID_PREFIX,
            intents=intents,
            help_command=None
        )
        
        # Initialize components
        self.db_manager = db_manager
        self.government = Government(db_manager)
        self.military = Military(db_manager)
        self.economy = Economy(db_manager)
        self.gemini_ai = gemini_ai
        
        # Bot state
        self.is_initialized = False
        self.server_guild = None
        self.control_channels = {}
        self.event_tasks = []
        
        # Load cogs
        self.load_extension('cogs.government_cog')
        self.load_extension('cogs.military_cog')
        self.load_extension('cogs.economy_cog')
        self.load_extension('cogs.civilian_cog')
        self.load_extension('cogs.intelligence_cog')
        
        logger.info("Magen David Bot initialized")
    
    async def setup_hook(self):
        """تنظیم اولیه ربات"""
        logger.info("Setting up Magen David Bot...")
        
        # Test Gemini AI connection
        if await self.gemini_ai.test_connection():
            logger.info("Gemini AI connection successful")
        else:
            logger.warning("Gemini AI connection failed, using fallback mode")
    
    async def on_ready(self):
        """رویداد آماده شدن ربات"""
        logger.info(f"Magen David Bot is ready! Logged in as {self.user}")
        
        # Find the target server
        for guild in self.guilds:
            if str(guild.id) == config.SERVER_ID:
                self.server_guild = guild
                logger.info(f"Found target server: {guild.name}")
                break
        
        if not self.server_guild:
            logger.error("Target server not found!")
            return
        
        # Start background tasks
        self.start_background_tasks()
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="سرور رول‌پلی اسرائیل"
            )
        )
    
    def start_background_tasks(self):
        """شروع وظایف پس‌زمینه"""
        self.daily_economy_update.start()
        self.random_events.start()
        self.crisis_generator.start()
        self.news_broadcast.start()
        self.environment_simulation.start()
        logger.info("Background tasks started")
    
    @tasks.loop(hours=24)
    async def daily_economy_update(self):
        """به‌روزرسانی روزانه اقتصاد"""
        try:
            # Update user balances
            users = self.db_manager.execute_query("SELECT user_id FROM users WHERE is_active = 1")
            
            for user_row in users:
                user_id = user_row[0]
                user = User(user_id, self.db_manager)
                
                # Add daily income based on role
                if user.role == "شهروند":
                    user.add_balance(config.DAILY_INCOME)
                elif user.role == "سرباز":
                    user.add_balance(config.DAILY_INCOME + 50)
                elif user.role == "وزیر":
                    user.add_balance(config.DAILY_INCOME + 100)
                elif user.role == "نخست‌وزیر":
                    user.add_balance(config.DAILY_INCOME + 200)
                
                # Add experience points
                user.add_experience(10)
            
            # Update national economy
            self.economy.change_gdp(random.randint(-10000, 50000))
            
            # Broadcast update
            await self.broadcast_economy_update()
            
            logger.info("Daily economy update completed")
            
        except Exception as e:
            logger.error(f"Error in daily economy update: {e}")
    
    @tasks.loop(hours=6)
    async def random_events(self):
        """تولید رویدادهای تصادفی"""
        try:
            if random.random() < 0.3:  # 30% chance every 6 hours
                event = await self.gemini_ai.generate_news_event()
                
                # Create event in database
                self.db_manager.execute_update(
                    "INSERT INTO events (event_type, event_name, event_description, event_data, severity, start_time) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        event.get("event_type", "اجتماعی"),
                        event.get("title", "رویداد جدید"),
                        event.get("description", "توضیح رویداد"),
                        json.dumps(event),
                        event.get("severity", "medium"),
                        datetime.datetime.now().isoformat()
                    )
                )
                
                # Broadcast event
                await self.broadcast_event(event)
                
                logger.info(f"Random event generated: {event.get('title', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"Error generating random event: {e}")
    
    @tasks.loop(hours=12)
    async def crisis_generator(self):
        """تولید بحران‌های تصادفی"""
        try:
            if random.random() < 0.1:  # 10% chance every 12 hours
                crisis = await self.gemini_ai.generate_crisis_scenario()
                
                # Create crisis in database
                self.db_manager.execute_update(
                    "INSERT INTO events (event_type, event_name, event_description, event_data, severity, start_time) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        "crisis",
                        crisis.get("crisis_name", "بحران جدید"),
                        f"بحران {crisis.get('crisis_type', 'نامشخص')} رخ داده است",
                        json.dumps(crisis),
                        crisis.get("severity", "medium"),
                        datetime.datetime.now().isoformat()
                    )
                )
                
                # Update public approval
                approval_impact = crisis.get("public_approval_impact", -10)
                self.government.change_public_approval(approval_impact)
                
                # Broadcast crisis
                await self.broadcast_crisis(crisis)
                
                logger.info(f"Crisis generated: {crisis.get('crisis_name', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"Error generating crisis: {e}")
    
    @tasks.loop(hours=2)
    async def news_broadcast(self):
        """پخش اخبار مهم"""
        try:
            # Get recent events
            events = self.db_manager.execute_query(
                "SELECT * FROM events WHERE is_active = 1 AND created_at > datetime('now', '-2 hours') ORDER BY created_at DESC LIMIT 5"
            )
            
            if events:
                await self.broadcast_news_summary(events)
                
        except Exception as e:
            logger.error(f"Error broadcasting news: {e}")
    
    @tasks.loop(hours=1)
    async def environment_simulation(self):
        """شبیه‌سازی محیطی"""
        try:
            current_hour = datetime.datetime.now().hour
            
            # Day/Night cycle
            if 6 <= current_hour < 18:
                time_status = "روز"
                emoji = "☀️"
            else:
                time_status = "شب"
                emoji = "🌙"
            
            # Weather simulation
            weather_conditions = ["آفتابی", "ابری", "بارانی", "طوفانی"]
            current_weather = random.choice(weather_conditions)
            
            # Update environment status
            await self.update_environment_status(time_status, current_weather, emoji)
            
        except Exception as e:
            logger.error(f"Error in environment simulation: {e}")
    
    async def broadcast_economy_update(self):
        """پخش به‌روزرسانی اقتصاد"""
        try:
            embed = discord.Embed(
                title="📊 به‌روزرسانی روزانه اقتصاد",
                description="وضعیت اقتصادی امروز سرور",
                color=config.COLORS["economy"],
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(
                name="💰 تولید ناخالص داخلی",
                value=f"{self.economy.gdp:,} شِکِل",
                inline=True
            )
            
            embed.add_field(
                name="🏦 بودجه ملی",
                value=f"{self.government.budget:,} شِکِل",
                inline=True
            )
            
            embed.add_field(
                name="📈 نرخ تورم",
                value=f"{self.economy.inflation_rate:.2%}",
                inline=True
            )
            
            embed.add_field(
                name="👥 رضایت عمومی",
                value=f"{self.government.public_approval}%",
                inline=True
            )
            
            embed.add_field(
                name="🔒 سطح دفاعی",
                value=f"DEFCON {self.military.defcon_level}",
                inline=True
            )
            
            embed.set_footer(text="ستاره داوود - سیستم اقتصادی")
            
            # Send to economy channel
            economy_channel = discord.utils.get(
                self.server_guild.channels,
                name="اقتصاد"
            )
            
            if economy_channel:
                await economy_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error broadcasting economy update: {e}")
    
    async def broadcast_event(self, event: Dict[str, Any]):
        """پخش رویداد"""
        try:
            severity_colors = {
                "low": config.COLORS["success"],
                "medium": config.COLORS["warning"],
                "high": config.COLORS["error"]
            }
            
            embed = discord.Embed(
                title=f"📰 {event.get('title', 'رویداد جدید')}",
                description=event.get("description", "توضیح رویداد"),
                color=severity_colors.get(event.get("severity", "medium"), config.COLORS["info"]),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(
                name="📋 نوع رویداد",
                value=event.get("event_type", "نامشخص"),
                inline=True
            )
            
            embed.add_field(
                name="⏱️ مدت تأثیر",
                value=f"{event.get('duration_hours', 24)} ساعت",
                inline=True
            )
            
            embed.add_field(
                name="📊 شدت",
                value=event.get("severity", "متوسط"),
                inline=True
            )
            
            if event.get("effects"):
                embed.add_field(
                    name="🎯 تأثیرات",
                    value=event.get("effects", ""),
                    inline=False
                )
            
            if event.get("rp_elements"):
                embed.add_field(
                    name="🎮 جنبه‌های رول‌پلی",
                    value=event.get("rp_elements", ""),
                    inline=False
                )
            
            embed.set_footer(text="ستاره داوود - سیستم رویدادها")
            
            # Send to national news channel
            news_channel = discord.utils.get(
                self.server_guild.channels,
                name="اخبار_ملی"
            )
            
            if news_channel:
                await news_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}")
    
    async def broadcast_crisis(self, crisis: Dict[str, Any]):
        """پخش بحران"""
        try:
            severity_colors = {
                "low": config.COLORS["warning"],
                "medium": config.COLORS["error"],
                "high": config.COLORS["war"],
                "critical": 0xFF0000
            }
            
            embed = discord.Embed(
                title=f"🚨 بحران: {crisis.get('crisis_name', 'بحران جدید')}",
                description=f"یک بحران {crisis.get('crisis_type', 'نامشخص')} رخ داده است!",
                color=severity_colors.get(crisis.get("severity", "medium"), config.COLORS["error"]),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(
                name="📋 نوع بحران",
                value=crisis.get("crisis_type", "نامشخص"),
                inline=True
            )
            
            embed.add_field(
                name="⏱️ مدت بحران",
                value=f"{crisis.get('duration_days', 7)} روز",
                inline=True
            )
            
            embed.add_field(
                name="📊 شدت",
                value=crisis.get("severity", "متوسط"),
                inline=True
            )
            
            if crisis.get("immediate_effects"):
                embed.add_field(
                    name="⚡ تأثیرات فوری",
                    value="\n".join(crisis.get("immediate_effects", [])),
                    inline=False
                )
            
            if crisis.get("long_term_effects"):
                embed.add_field(
                    name="🕐 تأثیرات بلندمدت",
                    value="\n".join(crisis.get("long_term_effects", [])),
                    inline=False
                )
            
            if crisis.get("rp_opportunities"):
                embed.add_field(
                    name="🎮 فرصت‌های رول‌پلی",
                    value="\n".join(crisis.get("rp_opportunities", [])),
                    inline=False
                )
            
            embed.set_footer(text="ستاره داوود - سیستم بحران‌ها")
            
            # Send to war room and national news
            war_room = discord.utils.get(
                self.server_guild.channels,
                name="اتاق_جنگ"
            )
            
            news_channel = discord.utils.get(
                self.server_guild.channels,
                name="اخبار_ملی"
            )
            
            if war_room:
                await war_room.send(embed=embed)
            
            if news_channel:
                await news_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error broadcasting crisis: {e}")
    
    async def broadcast_news_summary(self, events: List[tuple]):
        """پخش خلاصه اخبار"""
        try:
            if not events:
                return
            
            embed = discord.Embed(
                title="📰 خلاصه اخبار",
                description="آخرین رویدادهای سرور",
                color=config.COLORS["media"],
                timestamp=datetime.datetime.now()
            )
            
            for event in events[:3]:  # Show top 3 events
                embed.add_field(
                    name=f"📋 {event[2]}",
                    value=f"**نوع:** {event[1]}\n**وضعیت:** {event[5]}",
                    inline=False
                )
            
            embed.set_footer(text="ستاره داوود - سیستم اخبار")
            
            # Send to national news channel
            news_channel = discord.utils.get(
                self.server_guild.channels,
                name="اخبار_ملی"
            )
            
            if news_channel:
                await news_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error broadcasting news summary: {e}")
    
    async def update_environment_status(self, time_status: str, weather: str, emoji: str):
        """به‌روزرسانی وضعیت محیطی"""
        try:
            embed = discord.Embed(
                title=f"{emoji} وضعیت محیطی",
                description="وضعیت فعلی محیط سرور",
                color=config.COLORS["info"],
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(
                name="🌍 زمان",
                value=time_status,
                inline=True
            )
            
            embed.add_field(
                name="🌤️ آب و هوا",
                value=weather,
                inline=True
            )
            
            embed.add_field(
                name="📊 رضایت عمومی",
                value=f"{self.government.public_approval}%",
                inline=True
            )
            
            embed.set_footer(text="ستاره داوود - سیستم محیطی")
            
            # Send to main channel
            main_channel = discord.utils.get(
                self.server_guild.channels,
                name="شهروندان"
            )
            
            if main_channel:
                await main_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error updating environment status: {e}")
    
    async def on_command_error(self, ctx, error):
        """مدیریت خطاهای کامند"""
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="❌ خطا",
                description="کامند مورد نظر یافت نشد.",
                color=config.COLORS["error"]
            )
            embed.add_field(
                name="💡 راهنما",
                value="از کامند `!help` برای مشاهده لیست کامندها استفاده کنید.",
                inline=False
            )
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 دسترسی محدود",
                description="شما مجوز استفاده از این کامند را ندارید.",
                color=config.COLORS["warning"]
            )
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="⚠️ پارامتر ناقص",
                description=f"پارامتر `{error.param.name}` مورد نیاز است.",
                color=config.COLORS["warning"]
            )
            await ctx.send(embed=embed)
            
        else:
            embed = discord.Embed(
                title="💥 خطای سیستمی",
                description="خطایی در اجرای کامند رخ داده است.",
                color=config.COLORS["error"]
            )
            embed.add_field(
                name="🔧 جزئیات",
                value=str(error),
                inline=False
            )
            await ctx.send(embed=embed)
            
            logger.error(f"Command error: {error}")

# Create bot instance
bot = MagenDavidBot()

# Export
__all__ = ['MagenDavidBot', 'bot']