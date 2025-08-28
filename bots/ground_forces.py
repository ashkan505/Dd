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

class GroundForcesBot(commands.Bot):
    """ربات نیروی زمینی اسرائیل"""
    
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
        
        # وضعیت نیروی زمینی
        self.ground_forces_status = {
            "combat_readiness": 90,
            "active_operations": 0,
            "total_soldiers": 0,
            "supply_level": 100,
            "territory_control": 100,
            "last_exercise": None,
            "deployed_units": [],
            "strategic_positions": 15
        }
        
        # واحدهای زمینی
        self.ground_units = {
            "infantry": {
                "regular_infantry": {"count": 1000, "status": "ready", "supplies": 100, "weapons": "full"},
                "paratroopers": {"count": 500, "status": "ready", "supplies": 100, "weapons": "full"},
                "special_forces": {"count": 300, "status": "ready", "supplies": 100, "weapons": "full"}
            },
            "armor": {
                "main_battle_tanks": {"count": 200, "status": "ready", "fuel": 100, "ammunition": "full"},
                "infantry_fighting_vehicles": {"count": 150, "status": "ready", "fuel": 100, "ammunition": "full"},
                "armored_personnel_carriers": {"count": 300, "status": "ready", "fuel": 100, "ammunition": "full"}
            },
            "artillery": {
                "self_propelled_artillery": {"count": 100, "status": "ready", "ammunition": "full", "range": "long"},
                "rocket_artillery": {"count": 50, "status": "ready", "ammunition": "full", "range": "very_long"},
                "mortars": {"count": 200, "status": "ready", "ammunition": "full", "range": "medium"}
            },
            "engineering": {
                "combat_engineers": {"count": 400, "status": "ready", "equipment": "full", "specialization": "demolition"},
                "bridge_builders": {"count": 200, "status": "ready", "equipment": "full", "specialization": "construction"},
                "mine_clearers": {"count": 150, "status": "ready", "equipment": "full", "specialization": "clearance"}
            }
        }
        
        # مأموریت‌های زمینی
        self.ground_missions = {}
        self.mission_types = ["گشت مرزی", "عملیات پاکسازی", "دفاع از مواضع", "حمله زمینی", "عملیات مهندسی"]
        
        # وضعیت زمینی
        self.terrain_conditions = {
            "weather": "clear",
            "visibility": "excellent",
            "ground_conditions": "firm",
            "temperature": 25,
            "humidity": 60
        }
        
        # فایل داده
        self.data_file = "data/ground_forces_data.json"
        self.load_data()
        
        # راه‌اندازی وظایف
        self.setup_tasks()
        
        # اضافه کردن کاگ‌ها
        self.add_cog(GroundForcesCommands(self))
        self.add_cog(UnitCommands(self))
        self.add_cog(MissionCommands(self))
        self.add_cog(TerrainCommands(self))
    
    def load_data(self):
        """بارگذاری داده‌ها از فایل"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ground_forces_status.update(data.get("ground_forces_status", {}))
                    self.ground_units.update(data.get("ground_units", {}))
                    self.ground_missions.update(data.get("ground_missions", {}))
                    self.terrain_conditions.update(data.get("terrain_conditions", {}))
                logging.info("✅ داده‌های نیروی زمینی بارگذاری شد")
        except Exception as e:
            logging.error(f"❌ خطا در بارگذاری داده‌های نیروی زمینی: {e}")
    
    def save_data(self):
        """ذخیره داده‌ها در فایل"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            data = {
                "ground_forces_status": self.ground_forces_status,
                "ground_units": self.ground_units,
                "ground_missions": self.ground_missions,
                "terrain_conditions": self.terrain_conditions
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"❌ خطا در ذخیره داده‌های نیروی زمینی: {e}")
    
    def setup_tasks(self):
        """راه‌اندازی وظایف خودکار"""
        self.terrain_update.start()
        self.supply_consumption.start()
        self.combat_readiness_check.start()
        self.ground_patrol.start()
    
    @tasks.loop(hours=3)
    async def terrain_update(self):
        """به‌روزرسانی وضعیت زمینی"""
        try:
            # شبیه‌سازی تغییرات زمینی
            terrain_changes = {
                "weather": random.choice(["clear", "cloudy", "rainy", "foggy"]),
                "visibility": random.choice(["excellent", "good", "moderate", "poor"]),
                "ground_conditions": random.choice(["firm", "soft", "muddy", "frozen"]),
                "temperature": max(-5, min(40, self.terrain_conditions["temperature"] + random.randint(-3, 3))),
                "humidity": max(20, min(90, self.terrain_conditions["humidity"] + random.randint(-10, 10)))
            }
            
            # بررسی تغییرات مهم
            old_visibility = self.terrain_conditions["visibility"]
            old_ground = self.terrain_conditions["ground_conditions"]
            self.terrain_conditions.update(terrain_changes)
            
            if (old_visibility != self.terrain_conditions["visibility"] or 
                old_ground != self.terrain_conditions["ground_conditions"]):
                
                embed = self.embed_helper.create_military_embed(
                    "🌍 تغییر وضعیت زمینی",
                    f"**آب و هوا:** {self.terrain_conditions['weather']}\n"
                    f"**دید:** {self.terrain_conditions['visibility']}\n"
                    f"**وضعیت زمین:** {self.terrain_conditions['ground_conditions']}\n"
                    f"**دما:** {self.terrain_conditions['temperature']}°C\n"
                    f"**رطوبت:** {self.terrain_conditions['humidity']}%",
                    "info"
                )
                
                await self.broadcast_ground_forces_update(embed)
            
            self.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در به‌روزرسانی زمینی: {e}")
    
    @tasks.loop(hours=2)
    async def supply_consumption(self):
        """مصرف تدارکات واحدها"""
        try:
            total_supplies_consumed = 0
            
            for category, unit_list in self.ground_units.items():
                for unit_name, unit_data in unit_list.items():
                    if unit_data["status"] == "ready":
                        # مصرف تدارکات بر اساس نوع واحد
                        if category == "infantry":
                            consumption = random.randint(2, 8)
                        elif category == "armor":
                            consumption = random.randint(5, 15)
                        elif category == "artillery":
                            consumption = random.randint(3, 10)
                        elif category == "engineering":
                            consumption = random.randint(1, 5)
                        else:
                            consumption = 3
                        
                        if "supplies" in unit_data:
                            unit_data["supplies"] = max(0, unit_data["supplies"] - consumption)
                        if "fuel" in unit_data:
                            unit_data["fuel"] = max(0, unit_data["fuel"] - consumption)
                        
                        total_supplies_consumed += consumption
                        
                        # تغییر وضعیت در صورت کمبود تدارکات
                        if (unit_data.get("supplies", 100) < 20 or 
                            unit_data.get("fuel", 100) < 20):
                            unit_data["status"] = "low_supplies"
                        elif (unit_data.get("supplies", 100) == 0 or 
                              unit_data.get("fuel", 100) == 0):
                            unit_data["status"] = "depleted"
            
            # به‌روزرسانی سطح تدارکات
            self.ground_forces_status["supply_level"] = max(0, self.ground_forces_status["supply_level"] - (total_supplies_consumed / 100))
            
            # اعلان کمبود تدارکات
            if self.ground_forces_status["supply_level"] < 30:
                embed = self.embed_helper.create_military_embed(
                    "📦 هشدار کمبود تدارکات",
                    f"سطح تدارکات نیروی زمینی به {self.ground_forces_status['supply_level']:.1f}% کاهش یافته است\n"
                    f"**توصیه:** تامین تدارکات اضطراری",
                    "warning"
                )
                await self.broadcast_ground_forces_update(embed)
            
            self.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در مصرف تدارکات: {e}")
    
    @tasks.loop(hours=6)
    async def combat_readiness_check(self):
        """بررسی آمادگی رزمی"""
        try:
            readiness_issues = 0
            
            for category, unit_list in self.ground_units.items():
                for unit_name, unit_data in unit_list.items():
                    if unit_data["status"] == "ready":
                        # احتمال نیاز به نگهداری
                        if random.random() < 0.08:  # 8% احتمال
                            unit_data["status"] = "maintenance"
                            readiness_issues += 1
            
            # محاسبه آمادگی رزمی جدید
            total_units = sum(len(unit_list) for unit_list in self.ground_units.values())
            ready_units = sum(
                sum(1 for unit in unit_list.values() if unit["status"] == "ready")
                for unit_list in self.ground_units.values()
            )
            
            self.ground_forces_status["combat_readiness"] = (ready_units / total_units) * 100 if total_units > 0 else 0
            
            if readiness_issues > 0:
                embed = self.embed_helper.create_military_embed(
                    "🔧 نیاز به نگهداری",
                    f"{readiness_issues} واحد نیاز به نگهداری دارند\n"
                    f"آمادگی رزمی: {self.ground_forces_status['combat_readiness']:.1f}%",
                    "warning"
                )
                await self.broadcast_ground_forces_update(embed)
            
            self.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در بررسی آمادگی رزمی: {e}")
    
    @tasks.loop(hours=8)
    async def ground_patrol(self):
        """گشت زمینی خودکار"""
        try:
            # ایجاد مأموریت گشت زمینی
            if len(self.ground_missions) < 2:
                mission_type = "گشت مرزی"
                mission_id = f"patrol_{len(self.ground_missions) + 1}"
                
                # تولید مأموریت با Gemini
                mission_description = await self.gemini.generate_mission(
                    mission_type, "military", "ground_forces"
                )
                
                # انتخاب واحدهای مناسب
                available_units = []
                for category, unit_list in self.ground_units.items():
                    for unit_name, unit_data in unit_list.items():
                        if unit_data["status"] == "ready":
                            if "supplies" in unit_data and unit_data["supplies"] > 50:
                                available_units.append(f"{unit_name} ({category})")
                            elif "fuel" in unit_data and unit_data["fuel"] > 50:
                                available_units.append(f"{unit_name} ({category})")
                
                if available_units:
                    selected_unit = random.choice(available_units)
                    
                    # تأثیر شرایط زمینی
                    terrain_impact = (
                        self.terrain_conditions["visibility"] in ["excellent", "good"] and
                        self.terrain_conditions["ground_conditions"] in ["firm", "soft"]
                    )
                    
                    mission = {
                        "id": mission_id,
                        "type": mission_type,
                        "description": mission_description,
                        "status": "active",
                        "created_at": datetime.datetime.now().isoformat(),
                        "duration": random.randint(3, 8),
                        "unit": selected_unit,
                        "terrain_impact": terrain_impact
                    }
                    
                    self.ground_missions[mission_id] = mission
                    self.ground_forces_status["active_operations"] += 1
                    
                    # ارسال اعلان مأموریت
                    embed = self.embed_helper.create_mission_embed(
                        "🚶 گشت زمینی جدید",
                        f"**نوع:** {mission_type}\n"
                        f"**توضیحات:** {mission_description}\n"
                        f"**واحد:** {selected_unit}\n"
                        f"**مدت:** {mission['duration']} ساعت\n"
                        f"**تأثیر زمینی:** {'مطلوب' if mission['terrain_impact'] else 'متوسط'}",
                        "info"
                    )
                    
                    await self.broadcast_ground_forces_update(embed)
                    self.save_data()
                
        except Exception as e:
            logging.error(f"❌ خطا در گشت زمینی: {e}")
    
    async def broadcast_ground_forces_update(self, embed):
        """ارسال به‌روزرسانی نیروی زمینی به کانال‌های مربوطه"""
        try:
            # ارسال به کانال نظامی
            military_channel_id = SERVER_CONFIG.get("military_channel_id")
            if military_channel_id:
                channel = self.get_channel(military_channel_id)
                if channel:
                    await channel.send(embed=embed)
            
            # ارسال به کانال نیروی زمینی
            ground_forces_channel_id = SERVER_CONFIG.get("ground_forces_channel_id")
            if ground_forces_channel_id:
                channel = self.get_channel(ground_forces_channel_id)
                if channel:
                    await channel.send(embed=embed)
                    
        except Exception as e:
            logging.error(f"❌ خطا در ارسال به‌روزرسانی نیروی زمینی: {e}")
    
    async def on_ready(self):
        """هنگام آماده شدن ربات"""
        logging.info(f"✅ ربات نیروی زمینی آماده شد: {self.user}")
        
        # محاسبه تعداد کل سربازان
        total_soldiers = sum(
            sum(unit_data["count"] for unit_data in unit_list.values())
            for unit_list in self.ground_units.values()
        )
        self.ground_forces_status["total_soldiers"] = total_soldiers
        
        # تنظیم وضعیت
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="زمین اسرائیل"
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


class GroundForcesCommands(commands.Cog):
    """دستورات نیروی زمینی"""
    
    def __init__(self, bot: GroundForcesBot):
        self.bot = bot
    
    @commands.command(name="وضعیت_زمینی")
    @commands.has_permissions(manage_messages=True)
    async def ground_forces_status(self, ctx):
        """نمایش وضعیت کلی نیروی زمینی"""
        try:
            embed = self.bot.embed_helper.create_military_embed(
                "🚶 وضعیت نیروی زمینی اسرائیل",
                f"**آمادگی رزمی:** {self.bot.ground_forces_status['combat_readiness']:.1f}%\n"
                f"**عملیات فعال:** {self.bot.ground_forces_status['active_operations']}\n"
                f"**کل سربازان:** {self.bot.ground_forces_status['total_soldiers']}\n"
                f"**سطح تدارکات:** {self.bot.ground_forces_status['supply_level']:.1f}%\n"
                f"**کنترل قلمرو:** {self.bot.ground_forces_status['territory_control']}%\n"
                f"**آخرین تمرین:** {self.bot.ground_forces_status['last_exercise'] or 'هیچ'}\n"
                f"**واحدهای مستقر:** {len(self.bot.ground_forces_status['deployed_units'])}\n"
                f"**مواضع استراتژیک:** {self.bot.ground_forces_status['strategic_positions']}",
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش وضعیت زمینی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش وضعیت زمینی"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="واحدها")
    async def show_units(self, ctx):
        """نمایش واحدهای زمینی"""
        try:
            units_text = ""
            for category, unit_list in self.bot.ground_units.items():
                units_text += f"**{category.upper()}:**\n"
                for unit_name, unit_data in unit_list.items():
                    status_emoji = "✅" if unit_data["status"] == "ready" else "⚠️"
                    supply_emoji = "🟢" if unit_data.get("supplies", 100) > 50 else "🟡" if unit_data.get("supplies", 100) > 20 else "🔴"
                    fuel_emoji = "🟢" if unit_data.get("fuel", 100) > 50 else "🟡" if unit_data.get("fuel", 100) > 20 else "🔴"
                    
                    if "supplies" in unit_data:
                        units_text += f"{status_emoji} {unit_name}: {unit_data['count']} عدد {supply_emoji} {unit_data['supplies']}%\n"
                    elif "fuel" in unit_data:
                        units_text += f"{status_emoji} {unit_name}: {unit_data['count']} عدد {fuel_emoji} {unit_data['fuel']}%\n"
                    else:
                        units_text += f"{status_emoji} {unit_name}: {unit_data['count']} عدد\n"
                units_text += "\n"
            
            embed = self.bot.embed_helper.create_military_embed(
                "🛡️ واحدهای زمینی",
                units_text,
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش واحدها: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش واحدها"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="تامین_تدارکات")
    @commands.has_permissions(manage_messages=True)
    async def resupply_units(self, ctx, unit_name: str = None):
        """تامین تدارکات واحدها"""
        try:
            if unit_name:
                # تامین تدارکات واحد خاص
                found = False
                for category, unit_list in self.bot.ground_units.items():
                    if unit_name in unit_list:
                        unit = unit_list[unit_name]
                        old_supplies = unit.get("supplies", 100)
                        old_fuel = unit.get("fuel", 100)
                        
                        if "supplies" in unit:
                            unit["supplies"] = 100
                        if "fuel" in unit:
                            unit["fuel"] = 100
                        
                        unit["status"] = "ready"
                        
                        embed = self.bot.embed_helper.create_military_embed(
                            "📦 تامین تدارکات",
                            f"واحد {unit_name} تامین تدارکات شد\n"
                            f"تدارکات: {old_supplies}% → 100%\n"
                            f"سوخت: {old_fuel}% → 100%",
                            "success"
                        )
                        
                        await ctx.send(embed=embed)
                        found = True
                        break
                
                if not found:
                    embed = self.bot.embed_helper.create_error_embed(
                        "❌ واحد یافت نشد",
                        f"واحد {unit_name} یافت نشد"
                    )
                    await ctx.send(embed=embed)
                    return
            else:
                # تامین تدارکات تمام واحدها
                resupplied_count = 0
                for category, unit_list in self.bot.ground_units.items():
                    for unit_name, unit_data in unit_list.items():
                        if unit_data.get("supplies", 100) < 100 or unit_data.get("fuel", 100) < 100:
                            if "supplies" in unit_data:
                                unit_data["supplies"] = 100
                            if "fuel" in unit_data:
                                unit_data["fuel"] = 100
                            unit_data["status"] = "ready"
                            resupplied_count += 1
                
                # تامین سطح تدارکات
                self.bot.ground_forces_status["supply_level"] = 100
                
                embed = self.bot.embed_helper.create_military_embed(
                    "📦 تامین تدارکات کامل",
                    f"{resupplied_count} واحد تامین تدارکات شدند\n"
                    f"سطح تدارکات: 100%",
                    "success"
                )
                
                await ctx.send(embed=embed)
            
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در تامین تدارکات: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در تامین تدارکات"
            )
            await ctx.send(embed=embed)


class UnitCommands(commands.Cog):
    """دستورات واحدها"""
    
    def __init__(self, bot: GroundForcesBot):
        self.bot = bot
    
    @commands.command(name="تعمیر_واحد")
    @commands.has_permissions(manage_messages=True)
    async def repair_unit(self, ctx, unit_name: str):
        """تعمیر واحد خاص"""
        try:
            found = False
            for category, unit_list in self.bot.ground_units.items():
                if unit_name in unit_list:
                    unit = unit_list[unit_name]
                    old_status = unit["status"]
                    unit["status"] = "ready"
                    
                    embed = self.bot.embed_helper.create_military_embed(
                        "🔧 تعمیر واحد",
                        f"واحد {unit_name} تعمیر شد\n"
                        f"وضعیت قبلی: {old_status}\n"
                        f"وضعیت جدید: ready",
                        "success"
                    )
                    
                    await ctx.send(embed=embed)
                    found = True
                    break
            
            if not found:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ واحد یافت نشد",
                    f"واحد {unit_name} یافت نشد"
                )
                await ctx.send(embed=embed)
                return
            
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در تعمیر واحد: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در تعمیر واحد"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="تمرین_زمینی")
    @commands.has_permissions(manage_messages=True)
    async def ground_exercise(self, ctx, unit_name: str = None):
        """شروع تمرین زمینی"""
        try:
            if unit_name:
                # تمرین واحد خاص
                found = False
                for category, unit_list in self.bot.ground_units.items():
                    if unit_name in unit_list:
                        unit = unit_list[unit_name]
                        if unit["status"] == "ready":
                            # شبیه‌سازی تمرین
                            improvement = random.randint(5, 15)
                            old_count = unit["count"]
                            unit["count"] = min(unit["count"] + improvement, old_count * 2)
                            
                            embed = self.bot.embed_helper.create_military_embed(
                                "🏋️ تمرین زمینی",
                                f"**واحد:** {unit_name}\n"
                                f"**بهبود:** +{improvement} (قبل: {old_count}, بعد: {unit['count']})",
                                "success"
                            )
                            
                            await ctx.send(embed=embed)
                            found = True
                            break
                        else:
                            embed = self.bot.embed_helper.create_error_embed(
                                "❌ واحد آماده نیست",
                                f"واحد {unit_name} در وضعیت {unit['status']} است"
                            )
                            await ctx.send(embed=embed)
                            return
                
                if not found:
                    embed = self.bot.embed_helper.create_error_embed(
                        "❌ واحد یافت نشد",
                        f"واحد {unit_name} یافت نشد"
                    )
                    await ctx.send(embed=embed)
                    return
            else:
                # تمرین تصادفی
                available_units = []
                for category, unit_list in self.bot.ground_units.items():
                    for unit_name, unit_data in unit_list.items():
                        if unit_data["status"] == "ready":
                            available_units.append((unit_name, unit_data))
                
                if available_units:
                    selected_unit_name, selected_unit = random.choice(available_units)
                    improvement = random.randint(3, 10)
                    old_count = selected_unit["count"]
                    selected_unit["count"] = min(selected_unit["count"] + improvement, old_count * 2)
                    
                    embed = self.bot.embed_helper.create_military_embed(
                        "🏋️ تمرین زمینی خودکار",
                        f"**واحد:** {selected_unit_name}\n"
                        f"**بهبود:** +{improvement} (قبل: {old_count}, بعد: {selected_unit['count']})",
                        "success"
                    )
                    
                    await ctx.send(embed=embed)
                else:
                    embed = self.bot.embed_helper.create_error_embed(
                        "❌ هیچ واحد آماده‌ای وجود ندارد",
                        "لطفاً ابتدا واحدها را تعمیر کنید"
                    )
                    await ctx.send(embed=embed)
                    return
            
            # به‌روزرسانی زمان آخرین تمرین
            self.bot.ground_forces_status["last_exercise"] = datetime.datetime.now().isoformat()
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در تمرین زمینی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در شروع تمرین زمینی"
            )
            await ctx.send(embed=embed)


class MissionCommands(commands.Cog):
    """دستورات مأموریت‌های زمینی"""
    
    def __init__(self, bot: GroundForcesBot):
        self.bot = bot
    
    @commands.command(name="مأموریت‌های_زمینی")
    async def show_ground_missions(self, ctx):
        """نمایش مأموریت‌های زمینی فعال"""
        try:
            if not self.bot.ground_missions:
                embed = self.bot.embed_helper.create_info_embed(
                    "📋 مأموریت‌های زمینی",
                    "هیچ مأموریت زمینی فعالی وجود ندارد"
                )
                await ctx.send(embed=embed)
                return
            
            missions_text = ""
            for mission_id, mission in self.bot.ground_missions.items():
                status_emoji = "🟢" if mission["status"] == "active" else "🔴"
                terrain_emoji = "🌍" if mission["terrain_impact"] else "🌫️"
                missions_text += f"{status_emoji} **{mission['type']}** (ID: {mission_id})\n"
                missions_text += f"توضیحات: {mission['description'][:100]}...\n"
                missions_text += f"واحد: {mission['unit']}\n"
                missions_text += f"مدت: {mission['duration']} ساعت {terrain_emoji}\n\n"
            
            embed = self.bot.embed_helper.create_mission_embed(
                "🚶 مأموریت‌های زمینی فعال",
                missions_text,
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش مأموریت‌های زمینی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش مأموریت‌های زمینی"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="شروع_مأموریت_زمینی")
    @commands.has_permissions(manage_messages=True)
    async def start_ground_mission(self, ctx, mission_type: str, description: str, unit_name: str):
        """شروع مأموریت زمینی جدید"""
        try:
            if mission_type not in self.bot.mission_types:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ نوع نامعتبر",
                    f"انواع مجاز: {', '.join(self.bot.mission_types)}"
                )
                await ctx.send(embed=embed)
                return
            
            # بررسی موجودیت واحد
            unit_found = False
            for category, unit_list in self.bot.ground_units.items():
                if unit_name in unit_list:
                    unit_data = unit_list[unit_name]
                    if unit_data["status"] == "ready":
                        if "supplies" in unit_data and unit_data["supplies"] > 50:
                            unit_found = True
                            break
                        elif "fuel" in unit_data and unit_data["fuel"] > 50:
                            unit_found = True
                            break
            
            if not unit_found:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ واحد نامعتبر",
                    "واحد باید آماده و دارای تدارکات کافی باشد"
                )
                await ctx.send(embed=embed)
                return
            
            mission_id = f"manual_ground_mission_{len(self.bot.ground_missions) + 1}"
            mission = {
                "id": mission_id,
                "type": mission_type,
                "description": description,
                "status": "active",
                "created_at": datetime.datetime.now().isoformat(),
                "duration": random.randint(3, 10),
                "unit": unit_name,
                "terrain_impact": (
                    self.bot.terrain_conditions["visibility"] in ["excellent", "good"] and
                    self.bot.terrain_conditions["ground_conditions"] in ["firm", "soft"]
                ),
                "commander": ctx.author.id
            }
            
            self.bot.ground_missions[mission_id] = mission
            self.bot.ground_forces_status["active_operations"] += 1
            
            embed = self.bot.embed_helper.create_mission_embed(
                "🚀 مأموریت زمینی جدید",
                f"**نوع:** {mission_type}\n"
                f"**توضیحات:** {description}\n"
                f"**فرمانده:** {ctx.author.mention}\n"
                f"**واحد:** {unit_name}\n"
                f"**تأثیر زمینی:** {'مطلوب' if mission['terrain_impact'] else 'متوسط'}",
                "success"
            )
            
            await ctx.send(embed=embed)
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در شروع مأموریت زمینی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در شروع مأموریت زمینی"
            )
            await ctx.send(embed=embed)


class TerrainCommands(commands.Cog):
    """دستورات زمینی"""
    
    def __init__(self, bot: GroundForcesBot):
        self.bot = bot
    
    @commands.command(name="وضعیت_زمین")
    async def terrain_status(self, ctx):
        """نمایش وضعیت زمینی"""
        try:
            weather_emoji = {
                "clear": "☀️",
                "cloudy": "⛅",
                "rainy": "🌧️",
                "foggy": "🌫️"
            }
            
            ground_emoji = {
                "firm": "🟢",
                "soft": "🟡",
                "muddy": "🟤",
                "frozen": "❄️"
            }
            
            embed = self.bot.embed_helper.create_military_embed(
                "🌍 وضعیت زمینی",
                f"**آب و هوا:** {weather_emoji.get(self.bot.terrain_conditions['weather'], '❓')} {self.bot.terrain_conditions['weather']}\n"
                f"**دید:** 👁️ {self.bot.terrain_conditions['visibility']}\n"
                f"**وضعیت زمین:** {ground_emoji.get(self.bot.terrain_conditions['ground_conditions'], '❓')} {self.bot.terrain_conditions['ground_conditions']}\n"
                f"**دما:** 🌡️ {self.bot.terrain_conditions['temperature']}°C\n"
                f"**رطوبت:** 💧 {self.bot.terrain_conditions['humidity']}%\n\n"
                f"**تأثیر بر عملیات:** {'مطلوب' if self.bot.terrain_conditions['visibility'] in ['excellent', 'good'] and self.bot.terrain_conditions['ground_conditions'] in ['firm', 'soft'] else 'متوسط'}",
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش وضعیت زمینی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش وضعیت زمینی"
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
    
    token = BOT_TOKENS.get("ground_forces")
    if not token:
        print("❌ توکن ربات نیروی زمینی یافت نشد!")
        return
    
    print("🚀 راه‌اندازی ربات نیروی زمینی اسرائیل...")
    
    # ایجاد و راه‌اندازی ربات
    bot = GroundForcesBot()
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())