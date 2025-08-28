"""
ربات رادیو اسرائیل - موزیک و اعلان‌های صوتی دولتی
Radio Israel Bot - Music and Government Voice Announcements
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

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/radio.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class RadioIsraelBot(commands.Bot):
    """ربات رادیو اسرائیل - پخش موزیک و اعلان‌های دولتی"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # راه‌اندازی کمک‌کننده‌ها
        self.embed_helper = EmbedHelper()
        
        # وضعیت رادیو
        self.radio_status = {
            "is_playing": False,           # آیا در حال پخش است
            "current_song": None,          # آهنگ فعلی
            "playlist": [],                # لیست پخش
            "volume": 50,                  # صدا (0-100)
            "auto_announcements": True,    # اعلان‌های خودکار
            "last_announcement": None,     # آخرین اعلان
            "total_songs_played": 0,       # تعداد کل آهنگ‌های پخش شده
            "listeners_count": 0           # تعداد شنوندگان
        }
        
        # لیست آهنگ‌های اسرائیلی
        self.israeli_music = [
            {
                "title": "هاتیکوا (سرود ملی اسرائیل)",
                "artist": "نفتالی هرتس ایمبر",
                "duration": "2:30",
                "category": "ملی",
                "url": "https://example.com/hatikva.mp3"
            },
            {
                "title": "یروشالیم شل زهاو",
                "artist": "نومی شمر",
                "duration": "3:45",
                "category": "ملی",
                "url": "https://example.com/jerusalem.mp3"
            },
            {
                "title": "شالوم عالخم",
                "artist": "آرتست اسرائیلی",
                "duration": "4:20",
                "category": "فولکلور",
                "url": "https://example.com/shalom.mp3"
            },
            {
                "title": "هاوا ناگیلا",
                "artist": "آرتست سنتی",
                "duration": "3:15",
                "category": "فولکلور",
                "url": "https://example.com/hava.mp3"
            },
            {
                "title": "ام یسرائل",
                "artist": "آرتست معاصر",
                "duration": "4:10",
                "category": "معاصر",
                "url": "https://example.com/am.mp3"
            }
        ]
        
        # اعلان‌های دولتی
        self.government_announcements = [
            "سلام، این رادیو اسرائیل است. اخبار مهم: انتخابات نخست‌وزیری در حال برگزاری است.",
            "اعلان دولتی: تمام شهروندان موظف به رعایت قوانین کشور هستند.",
            "خبر فوری: بودجه ملی برای پروژه‌های عمرانی افزایش یافت.",
            "هشدار امنیتی: سطح آمادگی دفاعی به DEFCON 3 ارتقا یافت.",
            "اعلان اقتصادی: نرخ مالیات برای سال جدید تنظیم شد."
        ]
        
        # اتصالات صوتی
        self.voice_connections = {}
        
        # داده‌های ذخیره‌شده
        self.data_file = "data/radio_data.json"
        self.load_data()
        
        # راه‌اندازی وظایف خودکار
        self.setup_tasks()
        
        logger.info("📻 ربات رادیو اسرائیل راه‌اندازی شد")
    
    async def setup_hook(self):
        """راه‌اندازی اولیه ربات"""
        await self.add_cog(RadioCommands(self))
        await self.add_cog(PlaylistCommands(self))
        await self.add_cog(AnnouncementCommands(self))
        
        logger.info("✅ تمام کامندها با موفقیت بارگذاری شدند")
    
    def setup_tasks(self):
        """راه‌اندازی وظایف خودکار"""
        self.auto_music_rotation.start()
        self.government_announcement_scheduler.start()
        self.listener_count_update.start()
        
        logger.info("✅ وظایف خودکار راه‌اندازی شدند")
    
    def load_data(self):
        """بارگذاری داده‌های ذخیره‌شده"""
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.radio_status.update(data.get('radio_status', {}))
                    logger.info("✅ داده‌های رادیو بارگذاری شدند")
            else:
                self.save_data()
                logger.info("✅ فایل داده‌های جدید ایجاد شد")
        except Exception as e:
            logger.error(f"❌ خطا در بارگذاری داده‌ها: {e}")
    
    def save_data(self):
        """ذخیره داده‌های رادیو"""
        try:
            data = {
                'radio_status': self.radio_status,
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("✅ داده‌های رادیو ذخیره شدند")
        except Exception as e:
            logger.error(f"❌ خطا در ذخیره داده‌ها: {e}")
    
    async def on_ready(self):
        """رویداد آماده شدن ربات"""
        logger.info(f"📻 ربات رادیو اسرائیل آماده شد: {self.user}")
        
        # تنظیم وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="رادیو اسرائیل 📻"
            )
        )
    
    @tasks.loop(minutes=30)
    async def auto_music_rotation(self):
        """چرخش خودکار موزیک"""
        try:
            if self.radio_status["is_playing"] and self.radio_status["playlist"]:
                # انتخاب آهنگ بعدی
                next_song = random.choice(self.radio_status["playlist"])
                self.radio_status["current_song"] = next_song
                self.radio_status["total_songs_played"] += 1
                
                # اعلان آهنگ جدید
                await self.broadcast_song_change(next_song)
                
                self.save_data()
                logger.info(f"✅ آهنگ جدید پخش شد: {next_song['title']}")
                
        except Exception as e:
            logger.error(f"❌ خطا در چرخش خودکار موزیک: {e}")
    
    @tasks.loop(hours=2)
    async def government_announcement_scheduler(self):
        """برنامه‌ریزی اعلان‌های دولتی"""
        try:
            if self.radio_status["auto_announcements"]:
                # انتخاب اعلان تصادفی
                announcement = random.choice(self.government_announcements)
                
                # پخش اعلان
                await self.broadcast_government_announcement(announcement)
                
                self.radio_status["last_announcement"] = datetime.datetime.now().isoformat()
                self.save_data()
                
                logger.info("✅ اعلان دولتی پخش شد")
                
        except Exception as e:
            logger.error(f"❌ خطا در برنامه‌ریزی اعلان‌ها: {e}")
    
    @tasks.loop(minutes=5)
    async def listener_count_update(self):
        """به‌روزرسانی تعداد شنوندگان"""
        try:
            total_listeners = 0
            
            for guild_id, connection in self.voice_connections.items():
                if connection and connection.is_connected():
                    guild = self.get_guild(int(guild_id))
                    if guild:
                        for channel in guild.voice_channels:
                            if channel.members:
                                total_listeners += len(channel.members)
            
            self.radio_status["listeners_count"] = total_listeners
            
        except Exception as e:
            logger.error(f"❌ خطا در به‌روزرسانی تعداد شنوندگان: {e}")
    
    async def broadcast_song_change(self, song: Dict):
        """اعلان تغییر آهنگ"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            # ارسال به چنل عمومی
            general_channel = discord.utils.get(guild.channels, name="عمومی")
            if not general_channel:
                return
            
            embed = self.embed_helper.create_info_embed(
                title="🎵 آهنگ جدید در رادیو اسرائیل",
                description=f"در حال پخش: **{song['title']}**",
                fields=[
                    {"name": "آرتست", "value": song["artist"], "inline": True},
                    {"name": "مدت", "value": song["duration"], "inline": True},
                    {"name": "دسته‌بندی", "value": song["category"], "inline": True}
                ],
                thumbnail="https://i.imgur.com/music-icon.png"
            )
            
            await general_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ خطا در اعلان تغییر آهنگ: {e}")
    
    async def broadcast_government_announcement(self, announcement: str):
        """پخش اعلان دولتی"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            # ارسال به چنل اخبار ملی
            news_channel = discord.utils.get(guild.channels, name="اخبار-ملی")
            if not news_channel:
                return
            
            embed = self.embed_helper.create_news_embed(
                title="📢 اعلان دولتی",
                description=announcement,
                author="رادیو اسرائیل",
                category="دولتی"
            )
            
            await news_channel.send(embed=embed)
            
            # پخش صوتی در چنل‌های صوتی
            await self.play_voice_announcement(announcement)
            
        except Exception as e:
            logger.error(f"❌ خطا در پخش اعلان دولتی: {e}")
    
    async def play_voice_announcement(self, announcement: str):
        """پخش صوتی اعلان"""
        try:
            # در اینجا می‌توان از Text-to-Speech استفاده کرد
            # فعلاً فقط لاگ می‌کنیم
            logger.info(f"📢 اعلان صوتی: {announcement}")
            
            # ارسال به تمام چنل‌های صوتی فعال
            for guild_id, connection in self.voice_connections.items():
                if connection and connection.is_connected():
                    # اینجا می‌توان فایل صوتی اعلان را پخش کرد
                    pass
                    
        except Exception as e:
            logger.error(f"❌ خطا در پخش صوتی اعلان: {e}")
    
    async def join_voice_channel(self, channel):
        """پیوستن به چنل صوتی"""
        try:
            if channel.guild.id in self.voice_connections:
                # اگر قبلاً متصل هستیم، ابتدا قطع کنیم
                await self.leave_voice_channel(channel.guild.id)
            
            # پیوستن به چنل جدید
            voice_client = await channel.connect()
            self.voice_connections[str(channel.guild.id)] = voice_client
            
            logger.info(f"✅ به چنل صوتی {channel.name} پیوستیم")
            return voice_client
            
        except Exception as e:
            logger.error(f"❌ خطا در پیوستن به چنل صوتی: {e}")
            return None
    
    async def leave_voice_channel(self, guild_id: int):
        """ترک چنل صوتی"""
        try:
            guild_id_str = str(guild_id)
            
            if guild_id_str in self.voice_connections:
                connection = self.voice_connections[guild_id_str]
                if connection and connection.is_connected():
                    await connection.disconnect()
                
                del self.voice_connections[guild_id_str]
                logger.info(f"✅ از چنل صوتی ترک کردیم")
                
        except Exception as e:
            logger.error(f"❌ خطا در ترک چنل صوتی: {e}")
    
    async def play_music(self, guild_id: int, song_url: str):
        """پخش موزیک"""
        try:
            guild_id_str = str(guild_id)
            
            if guild_id_str not in self.voice_connections:
                logger.warning("⚠️ ابتدا باید به چنل صوتی بپیوندیم")
                return False
            
            connection = self.voice_connections[guild_id_str]
            if not connection or not connection.is_connected():
                logger.warning("⚠️ اتصال صوتی فعال نیست")
                return False
            
            # در اینجا می‌توان از FFmpeg برای پخش موزیک استفاده کرد
            # فعلاً فقط وضعیت را تغییر می‌دهیم
            self.radio_status["is_playing"] = True
            self.radio_status["current_song"] = {
                "title": "آهنگ در حال پخش",
                "artist": "آرتست",
                "duration": "0:00",
                "url": song_url
            }
            
            logger.info(f"✅ موزیک شروع شد: {song_url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در پخش موزیک: {e}")
            return False
    
    async def stop_music(self, guild_id: int):
        """توقف موزیک"""
        try:
            guild_id_str = str(guild_id)
            
            if guild_id_str in self.voice_connections:
                connection = self.voice_connections[guild_id_str]
                if connection and connection.is_connected():
                    # توقف پخش
                    if connection.is_playing():
                        connection.stop()
                
                self.radio_status["is_playing"] = False
                self.radio_status["current_song"] = None
                
                logger.info("✅ موزیک متوقف شد")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطا در توقف موزیک: {e}")
            return False

# کلاس کامندهای رادیو
class RadioCommands(commands.Cog):
    """کامندهای مربوط به کنترل رادیو"""
    
    def __init__(self, bot: RadioIsraelBot):
        self.bot = bot
    
    @commands.command(name="join")
    async def join_voice(self, ctx):
        """پیوستن به چنل صوتی"""
        try:
            if not ctx.author.voice:
                embed = self.bot.embed_helper.create_error_embed(
                    title="خطا در پیوستن",
                    description="ابتدا باید به یک چنل صوتی بپیوندید.",
                    error_code="RADIO_001"
                )
                await ctx.send(embed=embed)
                return
            
            voice_channel = ctx.author.voice.channel
            
            embed = self.bot.embed_helper.create_info_embed(
                title="🔊 پیوستن به چنل صوتی",
                description=f"در حال پیوستن به {voice_channel.name}..."
            )
            
            message = await ctx.send(embed=embed)
            
            # پیوستن به چنل
            voice_client = await self.bot.join_voice_channel(voice_channel)
            
            if voice_client:
                embed = self.bot.embed_helper.create_success_embed(
                    title="✅ پیوستن موفق",
                    description=f"به چنل صوتی {voice_channel.name} پیوستیم.",
                    fields=[
                        {"name": "چنل", "value": voice_channel.name, "inline": True},
                        {"name": "وضعیت", "value": "متصل", "inline": True}
                    ]
                )
            else:
                embed = self.bot.embed_helper.create_error_embed(
                    title="❌ خطا در پیوستن",
                    description="خطا در پیوستن به چنل صوتی.",
                    error_code="RADIO_002"
                )
            
            await message.edit(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در پیوستن",
                description=f"خطا در پیوستن به چنل صوتی: {str(e)}",
                error_code="RADIO_003"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در پیوستن به چنل صوتی: {e}")
    
    @commands.command(name="leave")
    async def leave_voice(self, ctx):
        """ترک چنل صوتی"""
        try:
            guild_id = ctx.guild.id
            
            embed = self.bot.embed_helper.create_info_embed(
                title="🔊 ترک چنل صوتی",
                description="در حال ترک چنل صوتی..."
            )
            
            message = await ctx.send(embed=embed)
            
            # ترک چنل
            success = await self.bot.leave_voice_channel(guild_id)
            
            if success:
                embed = self.bot.embed_helper.create_success_embed(
                    title="✅ ترک موفق",
                    description="از چنل صوتی ترک کردیم."
                )
            else:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="⚠️ ترک ناموفق",
                    description="در حال حاضر به چنل صوتی متصل نیستیم."
                )
            
            await message.edit(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در ترک",
                description=f"خطا در ترک چنل صوتی: {str(e)}",
                error_code="RADIO_004"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در ترک چنل صوتی: {e}")
    
    @commands.command(name="play")
    async def play_music(self, ctx, song_name: str = None):
        """پخش موزیک"""
        try:
            guild_id = ctx.guild.id
            
            if not song_name:
                # انتخاب آهنگ تصادفی
                song = random.choice(self.bot.israeli_music)
                song_name = song["title"]
            else:
                # یافتن آهنگ
                song = None
                for s in self.bot.israeli_music:
                    if song_name.lower() in s["title"].lower():
                        song = s
                        break
                
                if not song:
                    embed = self.bot.embed_helper.create_error_embed(
                        title="آهنگ یافت نشد",
                        description=f"آهنگ '{song_name}' یافت نشد.",
                        error_code="RADIO_005"
                    )
                    await ctx.send(embed=embed)
                    return
            
            embed = self.bot.embed_helper.create_info_embed(
                title="🎵 شروع پخش",
                description=f"در حال شروع پخش {song['title']}..."
            )
            
            message = await ctx.send(embed=embed)
            
            # پخش موزیک
            success = await self.bot.play_music(guild_id, song["url"])
            
            if success:
                embed = self.bot.embed_helper.create_success_embed(
                    title="✅ موزیک شروع شد",
                    description=f"**{song['title']}** در حال پخش است.",
                    fields=[
                        {"name": "آرتست", "value": song["artist"], "inline": True},
                        {"name": "مدت", "value": song["duration"], "inline": True},
                        {"name": "دسته‌بندی", "value": song["category"], "inline": True}
                    ],
                    thumbnail="https://i.imgur.com/music-icon.png"
                )
            else:
                embed = self.bot.embed_helper.create_error_embed(
                    title="❌ خطا در پخش",
                    description="خطا در شروع پخش موزیک.",
                    error_code="RADIO_006"
                )
            
            await message.edit(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در پخش",
                description=f"خطا در پخش موزیک: {str(e)}",
                error_code="RADIO_007"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در پخش موزیک: {e}")
    
    @commands.command(name="stop")
    async def stop_music(self, ctx):
        """توقف موزیک"""
        try:
            guild_id = ctx.guild.id
            
            embed = self.bot.embed_helper.create_info_embed(
                title="⏹️ توقف موزیک",
                description="در حال توقف موزیک..."
            )
            
            message = await ctx.send(embed=embed)
            
            # توقف موزیک
            success = await self.bot.stop_music(guild_id)
            
            if success:
                embed = self.bot.embed_helper.create_success_embed(
                    title="✅ موزیک متوقف شد",
                    description="پخش موزیک متوقف شد."
                )
            else:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="⚠️ توقف ناموفق",
                    description="در حال حاضر موزیکی پخش نمی‌شود."
                )
            
            await message.edit(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در توقف",
                description=f"خطا در توقف موزیک: {str(e)}",
                error_code="RADIO_008"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در توقف موزیک: {e}")
    
    @commands.command(name="status")
    async def radio_status(self, ctx):
        """نمایش وضعیت رادیو"""
        try:
            embed = self.bot.embed_helper.create_info_embed(
                title="📻 وضعیت رادیو اسرائیل",
                description="وضعیت لحظه‌ای رادیو",
                fields=[
                    {"name": "🎵 وضعیت پخش", "value": "در حال پخش" if self.bot.radio_status["is_playing"] else "متوقف", "inline": True},
                    {"name": "🔊 صدا", "value": f"{self.bot.radio_status['volume']}%", "inline": True},
                    {"name": "📊 تعداد آهنگ‌های پخش شده", "value": f"{self.bot.radio_status['total_songs_played']}", "inline": True},
                    {"name": "👥 تعداد شنوندگان", "value": f"{self.bot.radio_status['listeners_count']}", "inline": True},
                    {"name": "📢 اعلان‌های خودکار", "value": "فعال" if self.bot.radio_status["auto_announcements"] else "غیرفعال", "inline": True}
                ]
            )
            
            if self.bot.radio_status["current_song"]:
                current_song = self.bot.radio_status["current_song"]
                embed.add_field(
                    name="🎵 آهنگ فعلی",
                    value=f"**{current_song['title']}** - {current_song['artist']}",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش وضعیت",
                description=f"خطا در نمایش وضعیت رادیو: {str(e)}",
                error_code="RADIO_009"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش وضعیت رادیو: {e}")

# کلاس کامندهای لیست پخش
class PlaylistCommands(commands.Cog):
    """کلاس مربوط به لیست پخش"""
    
    def __init__(self, bot: RadioIsraelBot):
        self.bot = bot
    
    @commands.command(name="playlist")
    async def show_playlist(self, ctx):
        """نمایش لیست پخش"""
        try:
            if not self.bot.radio_status["playlist"]:
                embed = self.bot.embed_helper.create_info_embed(
                    title="📋 لیست پخش",
                    description="لیست پخش خالی است."
                )
                await ctx.send(embed=embed)
                return
            
            playlist_text = ""
            for i, song in enumerate(self.bot.radio_status["playlist"], 1):
                playlist_text += f"**{i}.** {song['title']} - {song['artist']} ({song['duration']})\n"
            
            embed = self.bot.embed_helper.create_info_embed(
                title="📋 لیست پخش رادیو اسرائیل",
                description=f"لیست پخش فعلی ({len(self.bot.radio_status['playlist'])} آهنگ):",
                fields=[
                    {"name": "آهنگ‌ها", "value": playlist_text, "inline": False}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش لیست پخش",
                description=f"خطا در نمایش لیست پخش: {str(e)}",
                error_code="RADIO_010"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش لیست پخش: {e}")
    
    @commands.command(name="add_song")
    async def add_song_to_playlist(self, ctx, song_name: str):
        """افزودن آهنگ به لیست پخش"""
        try:
            # یافتن آهنگ
            song = None
            for s in self.bot.israeli_music:
                if song_name.lower() in s["title"].lower():
                    song = s
                    break
            
            if not song:
                embed = self.bot.embed_helper.create_error_embed(
                    title="آهنگ یافت نشد",
                    description=f"آهنگ '{song_name}' یافت نشد.",
                    error_code="RADIO_011"
                )
                await ctx.send(embed=embed)
                return
            
            # افزودن به لیست پخش
            if song not in self.bot.radio_status["playlist"]:
                self.bot.radio_status["playlist"].append(song)
                
                embed = self.bot.embed_helper.create_success_embed(
                    title="✅ آهنگ اضافه شد",
                    description=f"**{song['title']}** به لیست پخش اضافه شد.",
                    fields=[
                        {"name": "آرتست", "value": song["artist"], "inline": True},
                        {"name": "مدت", "value": song["duration"], "inline": True}
                    ]
                )
                
                self.bot.save_data()
            else:
                embed = self.bot.embed_helper.create_warning_embed(
                    title="آهنگ موجود",
                    description="این آهنگ قبلاً در لیست پخش موجود است."
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در افزودن آهنگ",
                description=f"خطا در افزودن آهنگ: {str(e)}",
                error_code="RADIO_012"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در افزودن آهنگ: {e}")

# کلاس کامندهای اعلان‌ها
class AnnouncementCommands(commands.Cog):
    """کلاس مربوط به اعلان‌های دولتی"""
    
    def __init__(self, bot: RadioIsraelBot):
        self.bot = bot
    
    @commands.command(name="announce")
    @commands.has_permissions(administrator=True)
    async def make_announcement(self, ctx, *, announcement_text: str):
        """ایجاد اعلان دولتی جدید"""
        try:
            embed = self.bot.embed_helper.create_news_embed(
                title="📢 اعلان دولتی جدید",
                description=announcement_text,
                author="ادمین",
                category="دولتی"
            )
            
            await ctx.send(embed=embed)
            
            # پخش اعلان
            await self.bot.broadcast_government_announcement(announcement_text)
            
            logger.info(f"✅ اعلان دولتی جدید ایجاد شد: {announcement_text[:50]}...")
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در ایجاد اعلان",
                description=f"خطا در ایجاد اعلان: {str(e)}",
                error_code="RADIO_013"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در ایجاد اعلان: {e}")
    
    @commands.command(name="toggle_announcements")
    @commands.has_permissions(administrator=True)
    async def toggle_auto_announcements(self, ctx):
        """تغییر وضعیت اعلان‌های خودکار"""
        try:
            current_status = self.bot.radio_status["auto_announcements"]
            self.bot.radio_status["auto_announcements"] = not current_status
            
            new_status = "فعال" if self.bot.radio_status["auto_announcements"] else "غیرفعال"
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ وضعیت اعلان‌ها تغییر یافت",
                description=f"اعلان‌های خودکار {new_status} شدند."
            )
            
            await ctx.send(embed=embed)
            self.bot.save_data()
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در تغییر وضعیت",
                description=f"خطا در تغییر وضعیت اعلان‌ها: {str(e)}",
                error_code="RADIO_014"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در تغییر وضعیت اعلان‌ها: {e}")

# راه‌اندازی ربات
async def main():
    """تابع اصلی راه‌اندازی ربات"""
    bot = RadioIsraelBot()
    
    try:
        await bot.start(BOT_TOKENS["radio"])
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # اجرای ربات
    asyncio.run(main())