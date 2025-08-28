import discord
from discord.ext import commands, tasks
import asyncio
import json
import logging
import datetime
import random
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BOT_TOKENS, SERVER_CONFIG, MILITARY_CONFIG
from utils.embed_helper import EmbedHelper
from utils.gemini_helper import GeminiHelper

class AirForceBot(commands.Bot):
    """ربات نیروی هوایی اسرائیل"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        self.embed_helper = EmbedHelper()
        self.gemini = GeminiHelper()
        
        # وضعیت نیروی هوایی
        self.air_force_status = {
            "air_superiority": 95,
            "active_sorties": 0,
            "total_aircraft": 0,
            "fuel_reserves": 100,
            "maintenance_ready": 100,
            "last_mission": None,
            "air_defense_ready": True,
            "strategic_bombers": 0
        }
        
        # هواپیماهای نظامی
        self.aircraft = {
            "fighters": {
                "F-35I Adir": {"count": 25, "status": "ready", "fuel": 100, "weapons": "full"},
                "F-16I Sufa": {"count": 50, "status": "ready", "fuel": 100, "weapons": "full"},
                "F-15I Ra'am": {"count": 30, "status": "ready", "fuel": 100, "weapons": "full"}
            },
            "bombers": {
                "F-15I Strike Eagle": {"count": 15, "status": "ready", "fuel": 100, "weapons": "full"}
            },
            "transport": {
                "C-130J Super Hercules": {"count": 10, "status": "ready", "fuel": 100, "cargo": "empty"}
            },
            "helicopters": {
                "AH-64 Apache": {"count": 20, "status": "ready", "fuel": 100, "weapons": "full"},
                "CH-53K King Stallion": {"count": 15, "status": "ready", "fuel": 100, "cargo": "empty"}
            }
        }
        
        # مأموریت‌های هوایی
        self.air_missions = {}
        self.mission_types = ["گشت هوایی", "عملیات ضربتی", "پشتیبانی هوایی", "ترابری نظامی", "عملیات شناسایی"]
        
        # وضعیت هوایی
        self.weather_conditions = {
            "visibility": "excellent",
            "wind_speed": 5,
            "cloud_cover": "clear",
            "temperature": 25
        }
        
        # فایل داده
        self.data_file = "data/air_force_data.json"
        self.load_data()
        
        # راه‌اندازی وظایف
        self.setup_tasks()
        
        # اضافه کردن کاگ‌ها
        self.add_cog(AirForceCommands(self))
        self.add_cog(AircraftCommands(self))
        self.add_cog(MissionCommands(self))
        self.add_cog(WeatherCommands(self))
    
    def load_data(self):
        """بارگذاری داده‌ها از فایل"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.air_force_status.update(data.get("air_force_status", {}))
                    self.aircraft.update(data.get("aircraft", {}))
                    self.air_missions.update(data.get("air_missions", {}))
                    self.weather_conditions.update(data.get("weather_conditions", {}))
                logging.info("✅ داده‌های نیروی هوایی بارگذاری شد")
        except Exception as e:
            logging.error(f"❌ خطا در بارگذاری داده‌های نیروی هوایی: {e}")
    
    def save_data(self):
        """ذخیره داده‌ها در فایل"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            data = {
                "air_force_status": self.air_force_status,
                "aircraft": self.aircraft,
                "air_missions": self.air_missions,
                "weather_conditions": self.weather_conditions
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"❌ خطا در ذخیره داده‌های نیروی هوایی: {e}")
    
    def setup_tasks(self):
        """راه‌اندازی وظایف خودکار"""
        self.weather_update.start()
        self.fuel_consumption.start()
        self.maintenance_check.start()
        self.air_patrol.start()
    
    @tasks.loop(hours=2)
    async def weather_update(self):
        """به‌روزرسانی وضعیت هوایی"""
        try:
            # شبیه‌سازی تغییرات آب و هوایی
            weather_changes = {
                "visibility": random.choice(["excellent", "good", "moderate", "poor"]),
                "wind_speed": max(0, min(50, self.weather_conditions["wind_speed"] + random.randint(-3, 3))),
                "cloud_cover": random.choice(["clear", "partly_cloudy", "cloudy", "overcast"]),
                "temperature": max(-10, min(45, self.weather_conditions["temperature"] + random.randint(-2, 2)))
            }
            
            # بررسی تغییرات مهم
            old_visibility = self.weather_conditions["visibility"]
            self.weather_conditions.update(weather_changes)
            
            if old_visibility != self.weather_conditions["visibility"]:
                embed = self.embed_helper.create_military_embed(
                    "🌤️ تغییر وضعیت هوایی",
                    f"**دید:** {self.weather_conditions['visibility']}\n"
                    f"**سرعت باد:** {self.weather_conditions['wind_speed']} km/h\n"
                    f"**پوشش ابر:** {self.weather_conditions['cloud_cover']}\n"
                    f"**دما:** {self.weather_conditions['temperature']}°C",
                    "info"
                )
                
                await self.broadcast_air_force_update(embed)
            
            self.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در به‌روزرسانی هوایی: {e}")
    
    @tasks.loop(hours=1)
    async def fuel_consumption(self):
        """مصرف سوخت هواپیماها"""
        try:
            total_fuel_consumed = 0
            
            for category, aircraft_list in self.aircraft.items():
                for aircraft_name, aircraft_data in aircraft_list.items():
                    if aircraft_data["status"] == "ready":
                        # مصرف سوخت بر اساس نوع هواپیما
                        if category == "fighters":
                            consumption = random.randint(5, 15)
                        elif category == "bombers":
                            consumption = random.randint(10, 20)
                        elif category == "transport":
                            consumption = random.randint(3, 8)
                        elif category == "helicopters":
                            consumption = random.randint(2, 6)
                        else:
                            consumption = 5
                        
                        aircraft_data["fuel"] = max(0, aircraft_data["fuel"] - consumption)
                        total_fuel_consumed += consumption
                        
                        # تغییر وضعیت در صورت کمبود سوخت
                        if aircraft_data["fuel"] < 20:
                            aircraft_data["status"] = "low_fuel"
                        elif aircraft_data["fuel"] == 0:
                            aircraft_data["status"] = "grounded"
            
            # به‌روزرسانی ذخایر سوخت
            self.air_force_status["fuel_reserves"] = max(0, self.air_force_status["fuel_reserves"] - (total_fuel_consumed / 100))
            
            # اعلان کمبود سوخت
            if self.air_force_status["fuel_reserves"] < 30:
                embed = self.embed_helper.create_military_embed(
                    "⛽ هشدار کمبود سوخت",
                    f"ذخایر سوخت نیروی هوایی به {self.air_force_status['fuel_reserves']:.1f}% کاهش یافته است\n"
                    f"**توصیه:** تامین سوخت اضطراری",
                    "warning"
                )
                await self.broadcast_air_force_update(embed)
            
            self.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در مصرف سوخت: {e}")
    
    @tasks.loop(hours=4)
    async def maintenance_check(self):
        """بررسی نگهداری هواپیماها"""
        try:
            maintenance_needed = 0
            
            for category, aircraft_list in self.aircraft.items():
                for aircraft_name, aircraft_data in aircraft_list.items():
                    if aircraft_data["status"] == "ready":
                        # احتمال نیاز به نگهداری
                        if random.random() < 0.1:  # 10% احتمال
                            aircraft_data["status"] = "maintenance"
                            maintenance_needed += 1
            
            # به‌روزرسانی وضعیت آمادگی
            total_aircraft = sum(len(aircraft_list) for aircraft_list in self.aircraft.values())
            ready_aircraft = sum(
                sum(1 for aircraft in aircraft_list.values() if aircraft["status"] == "ready")
                for aircraft_list in self.aircraft.values()
            )
            
            self.air_force_status["maintenance_ready"] = (ready_aircraft / total_aircraft) * 100 if total_aircraft > 0 else 0
            
            if maintenance_needed > 0:
                embed = self.embed_helper.create_military_embed(
                    "🔧 نیاز به نگهداری",
                    f"{maintenance_needed} هواپیما نیاز به نگهداری دارند\n"
                    f"آمادگی کلی: {self.air_force_status['maintenance_ready']:.1f}%",
                    "warning"
                )
                await self.broadcast_air_force_update(embed)
            
            self.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در بررسی نگهداری: {e}")
    
    @tasks.loop(hours=6)
    async def air_patrol(self):
        """گشت هوایی خودکار"""
        try:
            # ایجاد مأموریت گشت هوایی
            if len(self.air_missions) < 2:
                mission_type = "گشت هوایی"
                mission_id = f"patrol_{len(self.air_missions) + 1}"
                
                # تولید مأموریت با Gemini
                mission_description = await self.gemini.generate_mission(
                    mission_type, "military", "air_force"
                )
                
                # انتخاب هواپیماهای مناسب
                available_aircraft = []
                for category, aircraft_list in self.aircraft.items():
                    for aircraft_name, aircraft_data in aircraft_list.items():
                        if aircraft_data["status"] == "ready" and aircraft_data["fuel"] > 50:
                            available_aircraft.append(f"{aircraft_name} ({category})")
                
                if available_aircraft:
                    selected_aircraft = random.choice(available_aircraft)
                    
                    mission = {
                        "id": mission_id,
                        "type": mission_type,
                        "description": mission_description,
                        "status": "active",
                        "created_at": datetime.datetime.now().isoformat(),
                        "duration": random.randint(2, 6),
                        "aircraft": selected_aircraft,
                        "weather_impact": self.weather_conditions["visibility"] == "excellent"
                    }
                    
                    self.air_missions[mission_id] = mission
                    self.air_force_status["active_sorties"] += 1
                    
                    # ارسال اعلان مأموریت
                    embed = self.embed_helper.create_mission_embed(
                        "✈️ گشت هوایی جدید",
                        f"**نوع:** {mission_type}\n"
                        f"**توضیحات:** {mission_description}\n"
                        f"**هواپیما:** {selected_aircraft}\n"
                        f"**مدت:** {mission['duration']} ساعت\n"
                        f"**تأثیر هوایی:** {'مطلوب' if mission['weather_impact'] else 'متوسط'}",
                        "info"
                    )
                    
                    await self.broadcast_air_force_update(embed)
                    self.save_data()
                
        except Exception as e:
            logging.error(f"❌ خطا در گشت هوایی: {e}")
    
    async def broadcast_air_force_update(self, embed):
        """ارسال به‌روزرسانی نیروی هوایی به کانال‌های مربوطه"""
        try:
            # ارسال به کانال نظامی
            military_channel_id = SERVER_CONFIG.get("military_channel_id")
            if military_channel_id:
                channel = self.get_channel(military_channel_id)
                if channel:
                    await channel.send(embed=embed)
            
            # ارسال به کانال نیروی هوایی
            air_force_channel_id = SERVER_CONFIG.get("air_force_channel_id")
            if air_force_channel_id:
                channel = self.get_channel(air_force_channel_id)
                if channel:
                    await channel.send(embed=embed)
                    
        except Exception as e:
            logging.error(f"❌ خطا در ارسال به‌روزرسانی نیروی هوایی: {e}")
    
    async def on_ready(self):
        """هنگام آماده شدن ربات"""
        logging.info(f"✅ ربات نیروی هوایی آماده شد: {self.user}")
        
        # محاسبه تعداد کل هواپیماها
        total_aircraft = sum(len(aircraft_list) for aircraft_list in self.aircraft.values())
        self.air_force_status["total_aircraft"] = total_aircraft
        
        # تنظیم وضعیت
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="آسمان اسرائیل"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """مدیریت خطاهای دستورات"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            embed = self.embed_helper.create_error_embed(
                "❌ دسترسی محدود",
                "شما مجوز استفاده از این دستور را ندارید"
            )
            await ctx.send(embed=embed)
            return
        
        # خطای عمومی
        embed = self.embed_helper.create_error_embed(
            "❌ خطا در اجرای دستور",
            f"خطا: {str(error)}"
        )
        await ctx.send(embed=embed)
        logging.error(f"خطا در دستور {ctx.command}: {error}")


class AirForceCommands(commands.Cog):
    """دستورات نیروی هوایی"""
    
    def __init__(self, bot: AirForceBot):
        self.bot = bot
    
    @commands.command(name="وضعیت_هوایی")
    @commands.has_permissions(manage_messages=True)
    async def air_force_status(self, ctx):
        """نمایش وضعیت کلی نیروی هوایی"""
        try:
            embed = self.bot.embed_helper.create_military_embed(
                "✈️ وضعیت نیروی هوایی اسرائیل",
                f"**برتری هوایی:** {self.bot.air_force_status['air_superiority']}%\n"
                f"**مأموریت‌های فعال:** {self.bot.air_force_status['active_sorties']}\n"
                f"**کل هواپیماها:** {self.bot.air_force_status['total_aircraft']}\n"
                f"**ذخایر سوخت:** {self.bot.air_force_status['fuel_reserves']:.1f}%\n"
                f"**آمادگی نگهداری:** {self.bot.air_force_status['maintenance_ready']:.1f}%\n"
                f"**آخرین مأموریت:** {self.bot.air_force_status['last_mission'] or 'هیچ'}\n"
                f"**دفاع هوایی:** {'آماده' if self.bot.air_force_status['air_defense_ready'] else 'غیرآماده'}\n"
                f"**بمب‌افکن‌های استراتژیک:** {self.bot.air_force_status['strategic_bombers']}",
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش وضعیت هوایی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش وضعیت هوایی"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="هواپیماها")
    async def show_aircraft(self, ctx):
        """نمایش هواپیماهای نظامی"""
        try:
            aircraft_text = ""
            for category, aircraft_list in self.bot.aircraft.items():
                aircraft_text += f"**{category.upper()}:**\n"
                for aircraft_name, aircraft_data in aircraft_list.items():
                    status_emoji = "✅" if aircraft_data["status"] == "ready" else "⚠️"
                    fuel_emoji = "🟢" if aircraft_data["fuel"] > 50 else "🟡" if aircraft_data["fuel"] > 20 else "🔴"
                    aircraft_text += f"{status_emoji} {aircraft_name}: {aircraft_data['count']} عدد {fuel_emoji} {aircraft_data['fuel']}%\n"
                aircraft_text += "\n"
            
            embed = self.bot.embed_helper.create_military_embed(
                "🛩️ هواپیماهای نظامی",
                aircraft_text,
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش هواپیماها: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش هواپیماها"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="تامین_سوخت")
    @commands.has_permissions(manage_messages=True)
    async def refuel_aircraft(self, ctx, aircraft_name: str = None):
        """تامین سوخت هواپیماها"""
        try:
            if aircraft_name:
                # تامین سوخت هواپیمای خاص
                found = False
                for category, aircraft_list in self.bot.aircraft.items():
                    if aircraft_name in aircraft_list:
                        aircraft = aircraft_list[aircraft_name]
                        old_fuel = aircraft["fuel"]
                        aircraft["fuel"] = 100
                        aircraft["status"] = "ready"
                        
                        embed = self.bot.embed_helper.create_military_embed(
                            "⛽ تامین سوخت",
                            f"هواپیمای {aircraft_name} تامین سوخت شد\n"
                            f"قبل: {old_fuel}%\n"
                            f"بعد: 100%",
                            "success"
                        )
                        
                        await ctx.send(embed=embed)
                        found = True
                        break
                
                if not found:
                    embed = self.bot.embed_helper.create_error_embed(
                        "❌ هواپیما یافت نشد",
                        f"هواپیمای {aircraft_name} یافت نشد"
                    )
                    await ctx.send(embed=embed)
                    return
            else:
                # تامین سوخت تمام هواپیماها
                refueled_count = 0
                for category, aircraft_list in self.bot.aircraft.items():
                    for aircraft_name, aircraft_data in aircraft_list.items():
                        if aircraft_data["fuel"] < 100:
                            aircraft_data["fuel"] = 100
                            aircraft_data["status"] = "ready"
                            refueled_count += 1
                
                # تامین ذخایر سوخت
                self.bot.air_force_status["fuel_reserves"] = 100
                
                embed = self.bot.embed_helper.create_military_embed(
                    "⛽ تامین سوخت کامل",
                    f"{refueled_count} هواپیما تامین سوخت شدند\n"
                    f"ذخایر سوخت: 100%",
                    "success"
                )
                
                await ctx.send(embed=embed)
            
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در تامین سوخت: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در تامین سوخت"
            )
            await ctx.send(embed=embed)


class AircraftCommands(commands.Cog):
    """دستورات هواپیماها"""
    
    def __init__(self, bot: AirForceBot):
        self.bot = bot
    
    @commands.command(name="تعمیر_هواپیما")
    @commands.has_permissions(manage_messages=True)
    async def repair_aircraft(self, ctx, aircraft_name: str):
        """تعمیر هواپیمای خاص"""
        try:
            found = False
            for category, aircraft_list in self.bot.aircraft.items():
                if aircraft_name in aircraft_list:
                    aircraft = aircraft_list[aircraft_name]
                    old_status = aircraft["status"]
                    aircraft["status"] = "ready"
                    
                    embed = self.bot.embed_helper.create_military_embed(
                        "🔧 تعمیر هواپیما",
                        f"هواپیمای {aircraft_name} تعمیر شد\n"
                        f"وضعیت قبلی: {old_status}\n"
                        f"وضعیت جدید: ready",
                        "success"
                    )
                    
                    await ctx.send(embed=embed)
                    found = True
                    break
            
            if not found:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ هواپیما یافت نشد",
                    f"هواپیمای {aircraft_name} یافت نشد"
                )
                await ctx.send(embed=embed)
                return
            
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در تعمیر هواپیما: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در تعمیر هواپیما"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="وضعیت_هوا")
    async def weather_status(self, ctx):
        """نمایش وضعیت هوایی"""
        try:
            weather_emoji = {
                "excellent": "☀️",
                "good": "🌤️",
                "moderate": "⛅",
                "poor": "🌫️"
            }
            
            embed = self.bot.embed_helper.create_military_embed(
                "🌤️ وضعیت هوایی",
                f"**دید:** {weather_emoji.get(self.bot.weather_conditions['visibility'], '❓')} {self.bot.weather_conditions['visibility']}\n"
                f"**سرعت باد:** 💨 {self.bot.weather_conditions['wind_speed']} km/h\n"
                f"**پوشش ابر:** ☁️ {self.bot.weather_conditions['cloud_cover']}\n"
                f"**دما:** 🌡️ {self.bot.weather_conditions['temperature']}°C\n\n"
                f"**تأثیر بر عملیات:** {'مطلوب' if self.bot.weather_conditions['visibility'] in ['excellent', 'good'] else 'متوسط'}",
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش وضعیت هوایی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش وضعیت هوایی"
            )
            await ctx.send(embed=embed)


class MissionCommands(commands.Cog):
    """دستورات مأموریت‌های هوایی"""
    
    def __init__(self, bot: AirForceBot):
        self.bot = bot
    
    @commands.command(name="مأموریت‌های_هوایی")
    async def show_air_missions(self, ctx):
        """نمایش مأموریت‌های هوایی فعال"""
        try:
            if not self.bot.air_missions:
                embed = self.bot.embed_helper.create_info_embed(
                    "📋 مأموریت‌های هوایی",
                    "هیچ مأموریت هوایی فعالی وجود ندارد"
                )
                await ctx.send(embed=embed)
                return
            
            missions_text = ""
            for mission_id, mission in self.bot.air_missions.items():
                status_emoji = "🟢" if mission["status"] == "active" else "🔴"
                weather_emoji = "☀️" if mission["weather_impact"] else "🌤️"
                missions_text += f"{status_emoji} **{mission['type']}** (ID: {mission_id})\n"
                missions_text += f"توضیحات: {mission['description'][:100]}...\n"
                missions_text += f"هواپیما: {mission['aircraft']}\n"
                missions_text += f"مدت: {mission['duration']} ساعت {weather_emoji}\n\n"
            
            embed = self.bot.embed_helper.create_mission_embed(
                "✈️ مأموریت‌های هوایی فعال",
                missions_text,
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش مأموریت‌های هوایی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش مأموریت‌های هوایی"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="شروع_مأموریت_هوایی")
    @commands.has_permissions(manage_messages=True)
    async def start_air_mission(self, ctx, mission_type: str, description: str, aircraft_name: str):
        """شروع مأموریت هوایی جدید"""
        try:
            if mission_type not in self.bot.mission_types:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ نوع نامعتبر",
                    f"انواع مجاز: {', '.join(self.bot.mission_types)}"
                )
                await ctx.send(embed=embed)
                return
            
            # بررسی موجودیت هواپیما
            aircraft_found = False
            for category, aircraft_list in self.bot.aircraft.items():
                if aircraft_name in aircraft_list:
                    aircraft_data = aircraft_list[aircraft_name]
                    if aircraft_data["status"] == "ready" and aircraft_data["fuel"] > 50:
                        aircraft_found = True
                        break
            
            if not aircraft_found:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ هواپیما نامعتبر",
                    "هواپیما باید آماده و دارای سوخت کافی باشد"
                )
                await ctx.send(embed=embed)
                return
            
            mission_id = f"manual_air_mission_{len(self.bot.air_missions) + 1}"
            mission = {
                "id": mission_id,
                "type": mission_type,
                "description": description,
                "status": "active",
                "created_at": datetime.datetime.now().isoformat(),
                "duration": random.randint(2, 8),
                "aircraft": aircraft_name,
                "weather_impact": self.bot.weather_conditions["visibility"] in ["excellent", "good"],
                "commander": ctx.author.id
            }
            
            self.bot.air_missions[mission_id] = mission
            self.bot.air_force_status["active_sorties"] += 1
            self.bot.air_force_status["last_mission"] = datetime.datetime.now().isoformat()
            
            embed = self.bot.embed_helper.create_mission_embed(
                "🚀 مأموریت هوایی جدید",
                f"**نوع:** {mission_type}\n"
                f"**توضیحات:** {description}\n"
                f"**فرمانده:** {ctx.author.mention}\n"
                f"**هواپیما:** {aircraft_name}\n"
                f"**تأثیر هوایی:** {'مطلوب' if mission['weather_impact'] else 'متوسط'}",
                "success"
            )
            
            await ctx.send(embed=embed)
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در شروع مأموریت هوایی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در شروع مأموریت هوایی"
            )
            await ctx.send(embed=embed)


class WeatherCommands(commands.Cog):
    """دستورات هواشناسی"""
    
    def __init__(self, bot: AirForceBot):
        self.bot = bot
    
    @commands.command(name="تغییر_هوا")
    @commands.has_permissions(manage_messages=True)
    async def change_weather(self, ctx, visibility: str, wind_speed: int, cloud_cover: str, temperature: int):
        """تغییر وضعیت هوایی (برای تست)"""
        try:
            if visibility not in ["excellent", "good", "moderate", "poor"]:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ دید نامعتبر",
                    "مقادیر مجاز: excellent, good, moderate, poor"
                )
                await ctx.send(embed=embed)
                return
            
            if cloud_cover not in ["clear", "partly_cloudy", "cloudy", "overcast"]:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ پوشش ابر نامعتبر",
                    "مقادیر مجاز: clear, partly_cloudy, cloudy, overcast"
                )
                await ctx.send(embed=embed)
                return
            
            if not -20 <= temperature <= 50:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ دما نامعتبر",
                    "دما باید بین -20 تا 50 درجه باشد"
                )
                await ctx.send(embed=embed)
                return
            
            if not 0 <= wind_speed <= 100:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ سرعت باد نامعتبر",
                    "سرعت باد باید بین 0 تا 100 km/h باشد"
                )
                await ctx.send(embed=embed)
                return
            
            old_weather = self.bot.weather_conditions.copy()
            
            self.bot.weather_conditions.update({
                "visibility": visibility,
                "wind_speed": wind_speed,
                "cloud_cover": cloud_cover,
                "temperature": temperature
            })
            
            embed = self.bot.embed_helper.create_military_embed(
                "🌤️ تغییر وضعیت هوایی",
                f"**دید:** {old_weather['visibility']} → {visibility}\n"
                f"**سرعت باد:** {old_weather['wind_speed']} → {wind_speed} km/h\n"
                f"**پوشش ابر:** {old_weather['cloud_cover']} → {cloud_cover}\n"
                f"**دما:** {old_weather['temperature']} → {temperature}°C",
                "success"
            )
            
            await ctx.send(embed=embed)
            self.bot.save_data()
            
        except ValueError:
            embed = self.bot.embed_helper.create_error_embed(
                "❌ ورودی نامعتبر",
                "لطفاً مقادیر صحیح وارد کنید"
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"❌ خطا در تغییر هوا: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در تغییر وضعیت هوایی"
            )
            await ctx.send(embed=embed)


async def main():
    """تابع اصلی"""
    # بررسی وجود فایل config
    if not os.path.exists('config.py'):
        print("❌ فایل config.py یافت نشد!")
        print("لطفاً ابتدا فایل .env را تنظیم کنید")
        return
    
    # بررسی وجود فایل .env
    if not os.path.exists('.env'):
        print("⚠️ فایل .env یافت نشد!")
        print("لطفاً فایل .env.example را کپی کرده و تنظیم کنید")
    
    # بارگذاری تنظیمات
    from config import BOT_TOKENS
    
    token = BOT_TOKENS.get("air_force")
    if not token:
        print("❌ توکن ربات نیروی هوایی یافت نشد!")
        return
    
    print("🚀 راه‌اندازی ربات نیروی هوایی اسرائیل...")
    
    # ایجاد و راه‌اندازی ربات
    bot = AirForceBot()
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())