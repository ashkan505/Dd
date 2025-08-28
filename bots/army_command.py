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

class ArmyCommandBot(commands.Bot):
    """ربات فرماندهی کل ارتش اسرائیل"""
    
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
        
        # وضعیت نظامی
        self.military_status = {
            "defcon_level": 5,
            "active_operations": 0,
            "total_soldiers": 0,
            "equipment_ready": 100,
            "morale": 85,
            "last_training": None,
            "deployed_units": [],
            "strategic_reserves": 1000
        }
        
        # واحدهای نظامی
        self.military_units = {
            "infantry": {"count": 500, "equipment": "rifles", "status": "ready"},
            "tanks": {"count": 100, "equipment": "Merkava", "status": "ready"},
            "artillery": {"count": 50, "equipment": "155mm", "status": "ready"},
            "air_defense": {"count": 25, "equipment": "Iron Dome", "status": "ready"},
            "special_forces": {"count": 100, "equipment": "advanced", "status": "ready"}
        }
        
        # مأموریت‌های نظامی
        self.active_missions = {}
        self.mission_types = ["گشت مرزی", "تمرین نظامی", "عملیات امنیتی", "پشتیبانی هوایی", "عملیات دریایی"]
        
        # فایل داده
        self.data_file = "data/army_command_data.json"
        self.load_data()
        
        # راه‌اندازی وظایف
        self.setup_tasks()
        
        # اضافه کردن کاگ‌ها
        self.add_cog(ArmyCommands(self))
        self.add_cog(MissionCommands(self))
        self.add_cog(EquipmentCommands(self))
        self.add_cog(TrainingCommands(self))
    
    def load_data(self):
        """بارگذاری داده‌ها از فایل"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.military_status.update(data.get("military_status", {}))
                    self.military_units.update(data.get("military_units", {}))
                    self.active_missions.update(data.get("active_missions", {}))
                logging.info("✅ داده‌های نظامی بارگذاری شد")
        except Exception as e:
            logging.error(f"❌ خطا در بارگذاری داده‌های نظامی: {e}")
    
    def save_data(self):
        """ذخیره داده‌ها در فایل"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            data = {
                "military_status": self.military_status,
                "military_units": self.military_units,
                "active_missions": self.active_missions
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"❌ خطا در ذخیره داده‌های نظامی: {e}")
    
    def setup_tasks(self):
        """راه‌اندازی وظایف خودکار"""
        self.daily_training.start()
        self.equipment_maintenance.start()
        self.mission_rotation.start()
        self.morale_update.start()
    
    @tasks.loop(hours=24)
    async def daily_training(self):
        """تمرین روزانه نظامی"""
        try:
            # انتخاب تصادفی واحد برای تمرین
            unit_type = random.choice(list(self.military_units.keys()))
            unit = self.military_units[unit_type]
            
            # بهبود مهارت واحد
            if unit["status"] == "ready":
                # شبیه‌سازی بهبود مهارت
                improvement = random.randint(1, 5)
                unit["count"] = min(unit["count"] + improvement, unit["count"] * 2)
                
                # ارسال گزارش تمرین
                embed = self.embed_helper.create_military_embed(
                    "🏋️ تمرین روزانه نظامی",
                    f"واحد {unit_type} تمرین روزانه خود را با موفقیت انجام داد\n"
                    f"تعداد: {unit['count']}\n"
                    f"وضعیت: {unit['status']}",
                    "success"
                )
                
                # ارسال به کانال نظامی
                await self.broadcast_military_update(embed)
                
                self.military_status["last_training"] = datetime.datetime.now().isoformat()
                self.save_data()
                
        except Exception as e:
            logging.error(f"❌ خطا در تمرین روزانه: {e}")
    
    @tasks.loop(hours=6)
    async def equipment_maintenance(self):
        """نگهداری تجهیزات"""
        try:
            # بررسی وضعیت تجهیزات
            total_equipment = sum(unit["count"] for unit in self.military_units.values())
            if total_equipment > 0:
                # شبیه‌سازی نگهداری
                maintenance_needed = random.randint(1, 10)
                self.military_status["equipment_ready"] = max(80, 100 - maintenance_needed)
                
                if self.military_status["equipment_ready"] < 90:
                    embed = self.embed_helper.create_military_embed(
                        "🔧 نگهداری تجهیزات",
                        f"تجهیزات نیاز به نگهداری دارند\n"
                        f"وضعیت: {self.military_status['equipment_ready']}%",
                        "warning"
                    )
                    await self.broadcast_military_update(embed)
                
                self.save_data()
                
        except Exception as e:
            logging.error(f"❌ خطا در نگهداری تجهیزات: {e}")
    
    @tasks.loop(hours=4)
    async def mission_rotation(self):
        """چرخش مأموریت‌های نظامی"""
        try:
            # ایجاد مأموریت جدید
            if len(self.active_missions) < 3:
                mission_type = random.choice(self.mission_types)
                mission_id = f"mission_{len(self.active_missions) + 1}"
                
                # تولید مأموریت با Gemini
                mission_description = await self.gemini.generate_mission(
                    mission_type, "military", "army"
                )
                
                mission = {
                    "id": mission_id,
                    "type": mission_type,
                    "description": mission_description,
                    "status": "active",
                    "created_at": datetime.datetime.now().isoformat(),
                    "duration": random.randint(2, 8),
                    "required_units": random.randint(1, 3)
                }
                
                self.active_missions[mission_id] = mission
                
                # ارسال اعلان مأموریت
                embed = self.embed_helper.create_mission_embed(
                    "🎯 مأموریت نظامی جدید",
                    f"نوع: {mission_type}\n"
                    f"توضیحات: {mission_description}\n"
                    f"واحدهای مورد نیاز: {mission['required_units']}",
                    "info"
                )
                
                await self.broadcast_military_update(embed)
                self.save_data()
                
        except Exception as e:
            logging.error(f"❌ خطا در چرخش مأموریت: {e}")
    
    @tasks.loop(hours=12)
    async def morale_update(self):
        """به‌روزرسانی روحیه نظامی"""
        try:
            # عوامل مؤثر بر روحیه
            equipment_factor = self.military_status["equipment_ready"] / 100
            training_factor = 1.0 if self.military_status["last_training"] else 0.8
            
            # محاسبه روحیه جدید
            base_morale = 85
            morale_change = random.randint(-5, 5)
            new_morale = base_morale + morale_change
            
            # اعمال عوامل
            new_morale = int(new_morale * equipment_factor * training_factor)
            new_morale = max(50, min(100, new_morale))
            
            old_morale = self.military_status["morale"]
            self.military_status["morale"] = new_morale
            
            # اعلان تغییرات مهم
            if abs(new_morale - old_morale) > 10:
                status = "success" if new_morale > old_morale else "warning"
                embed = self.embed_helper.create_military_embed(
                    "💪 تغییر روحیه نظامی",
                    f"روحیه نظامی تغییر کرد\n"
                    f"قبل: {old_morale}%\n"
                    f"حالا: {new_morale}%",
                    status
                )
                await self.broadcast_military_update(embed)
            
            self.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در به‌روزرسانی روحیه: {e}")
    
    async def broadcast_military_update(self, embed):
        """ارسال به‌روزرسانی نظامی به کانال‌های مربوطه"""
        try:
            # ارسال به کانال نظامی
            military_channel_id = SERVER_CONFIG.get("military_channel_id")
            if military_channel_id:
                channel = self.get_channel(military_channel_id)
                if channel:
                    await channel.send(embed=embed)
            
            # ارسال به کانال فرماندهی
            command_channel_id = SERVER_CONFIG.get("command_channel_id")
            if command_channel_id:
                channel = self.get_channel(command_channel_id)
                if channel:
                    await channel.send(embed=embed)
                    
        except Exception as e:
            logging.error(f"❌ خطا در ارسال به‌روزرسانی نظامی: {e}")
    
    async def on_ready(self):
        """هنگام آماده شدن ربات"""
        logging.info(f"✅ ربات فرماندهی کل ارتش آماده شد: {self.user}")
        
        # تنظیم وضعیت
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="وضعیت نظامی اسرائیل"
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


class ArmyCommands(commands.Cog):
    """دستورات فرماندهی ارتش"""
    
    def __init__(self, bot: ArmyCommandBot):
        self.bot = bot
    
    @commands.command(name="وضعیت_نظامی")
    @commands.has_permissions(manage_messages=True)
    async def military_status(self, ctx):
        """نمایش وضعیت کلی نظامی"""
        try:
            embed = self.bot.embed_helper.create_military_embed(
                "🎖️ وضعیت نظامی اسرائیل",
                f"**سطح DEFCON:** {self.bot.military_status['defcon_level']}\n"
                f"**عملیات فعال:** {self.bot.military_status['active_operations']}\n"
                f"**کل سربازان:** {self.bot.military_status['total_soldiers']}\n"
                f"**آمادگی تجهیزات:** {self.bot.military_status['equipment_ready']}%\n"
                f"**روحیه:** {self.bot.military_status['morale']}%\n"
                f"**آخرین تمرین:** {self.bot.military_status['last_training'] or 'هیچ'}\n"
                f"**واحدهای مستقر:** {len(self.bot.military_status['deployed_units'])}\n"
                f"**ذخایر استراتژیک:** {self.bot.military_status['strategic_reserves']}",
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش وضعیت نظامی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش وضعیت نظامی"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="واحدها")
    async def show_units(self, ctx):
        """نمایش واحدهای نظامی"""
        try:
            units_text = ""
            for unit_type, unit in self.bot.military_units.items():
                status_emoji = "✅" if unit["status"] == "ready" else "⚠️"
                units_text += f"{status_emoji} **{unit_type}:** {unit['count']} ({unit['equipment']})\n"
            
            embed = self.bot.embed_helper.create_military_embed(
                "🚁 واحدهای نظامی",
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
    
    @commands.command(name="تغییر_defcon")
    @commands.has_permissions(administrator=True)
    async def change_defcon(self, ctx, level: int):
        """تغییر سطح DEFCON"""
        try:
            if not 1 <= level <= 5:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ سطح نامعتبر",
                    "سطح DEFCON باید بین 1 تا 5 باشد"
                )
                await ctx.send(embed=embed)
                return
            
            old_level = self.bot.military_status["defcon_level"]
            self.bot.military_status["defcon_level"] = level
            
            embed = self.bot.embed_helper.create_military_embed(
                "🚨 تغییر سطح DEFCON",
                f"سطح DEFCON از {old_level} به {level} تغییر کرد\n"
                f"**توجه:** این تغییر بر تمام سیستم‌های دفاعی تأثیر می‌گذارد",
                "warning" if level < old_level else "success"
            )
            
            await ctx.send(embed=embed)
            self.bot.save_data()
            
        except ValueError:
            embed = self.bot.embed_helper.create_error_embed(
                "❌ ورودی نامعتبر",
                "لطفاً یک عدد وارد کنید"
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"❌ خطا در تغییر DEFCON: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در تغییر سطح DEFCON"
            )
            await ctx.send(embed=embed)


class MissionCommands(commands.Cog):
    """دستورات مأموریت‌های نظامی"""
    
    def __init__(self, bot: ArmyCommandBot):
        self.bot = bot
    
    @commands.command(name="مأموریت‌ها")
    async def show_missions(self, ctx):
        """نمایش مأموریت‌های فعال"""
        try:
            if not self.bot.active_missions:
                embed = self.bot.embed_helper.create_info_embed(
                    "📋 مأموریت‌های نظامی",
                    "هیچ مأموریت فعالی وجود ندارد"
                )
                await ctx.send(embed=embed)
                return
            
            missions_text = ""
            for mission_id, mission in self.bot.active_missions.items():
                status_emoji = "🟢" if mission["status"] == "active" else "🔴"
                missions_text += f"{status_emoji} **{mission['type']}** (ID: {mission_id})\n"
                missions_text += f"توضیحات: {mission['description'][:100]}...\n"
                missions_text += f"واحدهای مورد نیاز: {mission['required_units']}\n"
                missions_text += f"مدت: {mission['duration']} ساعت\n\n"
            
            embed = self.bot.embed_helper.create_mission_embed(
                "🎯 مأموریت‌های فعال",
                missions_text,
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش مأموریت‌ها: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش مأموریت‌ها"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="شروع_مأموریت")
    @commands.has_permissions(manage_messages=True)
    async def start_mission(self, ctx, mission_type: str, description: str):
        """شروع مأموریت جدید"""
        try:
            if mission_type not in self.bot.mission_types:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ نوع نامعتبر",
                    f"انواع مجاز: {', '.join(self.bot.mission_types)}"
                )
                await ctx.send(embed=embed)
                return
            
            mission_id = f"manual_mission_{len(self.bot.active_missions) + 1}"
            mission = {
                "id": mission_id,
                "type": mission_type,
                "description": description,
                "status": "active",
                "created_at": datetime.datetime.now().isoformat(),
                "duration": random.randint(2, 8),
                "required_units": random.randint(1, 3),
                "commander": ctx.author.id
            }
            
            self.bot.active_missions[mission_id] = mission
            self.bot.military_status["active_operations"] += 1
            
            embed = self.bot.embed_helper.create_mission_embed(
                "🚀 مأموریت جدید شروع شد",
                f"**نوع:** {mission_type}\n"
                f"**توضیحات:** {description}\n"
                f"**فرمانده:** {ctx.author.mention}\n"
                f"**واحدهای مورد نیاز:** {mission['required_units']}",
                "success"
            )
            
            await ctx.send(embed=embed)
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در شروع مأموریت: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در شروع مأموریت"
            )
            await ctx.send(embed=embed)


class EquipmentCommands(commands.Cog):
    """دستورات تجهیزات نظامی"""
    
    def __init__(self, bot: ArmyCommandBot):
        self.bot = bot
    
    @commands.command(name="تجهیزات")
    async def show_equipment(self, ctx):
        """نمایش وضعیت تجهیزات"""
        try:
            embed = self.bot.embed_helper.create_military_embed(
                "🔧 وضعیت تجهیزات",
                f"**آمادگی کلی:** {self.bot.military_status['equipment_ready']}%\n\n"
                f"**جزئیات واحدها:**\n" + 
                "\n".join([f"• {unit_type}: {unit['equipment']} ({unit['count']} عدد)" 
                           for unit_type, unit in self.bot.military_units.items()]),
                "info"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"❌ خطا در نمایش تجهیزات: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در نمایش تجهیزات"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="تعمیر_تجهیزات")
    @commands.has_permissions(manage_messages=True)
    async def repair_equipment(self, ctx):
        """تعمیر تجهیزات نظامی"""
        try:
            old_ready = self.bot.military_status["equipment_ready"]
            repair_amount = random.randint(10, 20)
            
            self.bot.military_status["equipment_ready"] = min(100, old_ready + repair_amount)
            
            embed = self.bot.embed_helper.create_military_embed(
                "🔧 تعمیر تجهیزات",
                f"تجهیزات تعمیر شد\n"
                f"قبل: {old_ready}%\n"
                f"بعد: {self.bot.military_status['equipment_ready']}%",
                "success"
            )
            
            await ctx.send(embed=embed)
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در تعمیر تجهیزات: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در تعمیر تجهیزات"
            )
            await ctx.send(embed=embed)


class TrainingCommands(commands.Cog):
    """دستورات تمرین نظامی"""
    
    def __init__(self, bot: ArmyCommandBot):
        self.bot = bot
    
    @commands.command(name="تمرین_نظامی")
    @commands.has_permissions(manage_messages=True)
    async def military_training(self, ctx, unit_type: str = None):
        """شروع تمرین نظامی"""
        try:
            if unit_type and unit_type not in self.bot.military_units:
                embed = self.bot.embed_helper.create_error_embed(
                    "❌ واحد نامعتبر",
                    f"واحدهای مجاز: {', '.join(self.bot.military_units.keys())}"
                )
                await ctx.send(embed=embed)
                return
            
            # انتخاب واحد برای تمرین
            if not unit_type:
                unit_type = random.choice(list(self.bot.military_units.keys()))
            
            unit = self.bot.military_units[unit_type]
            
            # شبیه‌سازی تمرین
            improvement = random.randint(5, 15)
            old_count = unit["count"]
            unit["count"] = min(unit["count"] + improvement, old_count * 2)
            
            # بهبود روحیه
            morale_boost = random.randint(1, 5)
            self.bot.military_status["morale"] = min(100, self.bot.military_status["morale"] + morale_boost)
            
            embed = self.bot.embed_helper.create_military_embed(
                "🏋️ تمرین نظامی",
                f"**واحد:** {unit_type}\n"
                f"**بهبود:** +{improvement} (قبل: {old_count}, بعد: {unit['count']})\n"
                f"**بهبود روحیه:** +{morale_boost}%\n"
                f"**روحیه جدید:** {self.bot.military_status['morale']}%",
                "success"
            )
            
            await ctx.send(embed=embed)
            
            # به‌روزرسانی زمان آخرین تمرین
            self.bot.military_status["last_training"] = datetime.datetime.now().isoformat()
            self.bot.save_data()
            
        except Exception as e:
            logging.error(f"❌ خطا در تمرین نظامی: {e}")
            embed = self.bot.embed_helper.create_error_embed(
                "❌ خطا",
                "خطا در شروع تمرین نظامی"
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
    
    token = BOT_TOKENS.get("army_command")
    if not token:
        print("❌ توکن ربات فرماندهی ارتش یافت نشد!")
        return
    
    print("🚀 راه‌اندازی ربات فرماندهی کل ارتش اسرائیل...")
    
    # ایجاد و راه‌اندازی ربات
    bot = ArmyCommandBot()
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())