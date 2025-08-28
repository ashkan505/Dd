#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی ربات‌های نظامی اسرائیل
Script to run all military bots simultaneously
"""

import asyncio
import logging
import os
import sys
import signal
import time

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Military Manager - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/military_bots.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class MilitaryBotManager:
    """مدیر ربات‌های نظامی"""
    
    def __init__(self):
        self.running = False
        self.bots = {}
        self.bot_status = {}
        
        # تنظیم signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # تعریف ربات‌های نظامی
        self.military_bots = {
            "army_command": {
                "name": "فرماندهی کل ارتش",
                "module": "bots.army_command",
                "class": "ArmyCommandBot",
                "token_key": "army_command"
            },
            "air_force": {
                "name": "نیروی هوایی",
                "module": "bots.air_force",
                "class": "AirForceBot",
                "token_key": "air_force"
            },
            "ground_forces": {
                "name": "نیروی زمینی",
                "module": "bots.ground_forces",
                "class": "GroundForcesBot",
                "token_key": "ground_forces"
            }
        }
    
    def signal_handler(self, signum, frame):
        """مدیریت signal های سیستم"""
        logger.info(f"📡 دریافت signal {signum}، در حال توقف...")
        self.running = False
    
    async def start_bot(self, bot_name: str, bot_info: dict, token: str):
        """شروع یک ربات نظامی"""
        try:
            logger.info(f"🚀 راه‌اندازی {bot_info['name']}...")
            
            # import کردن ماژول ربات
            module = __import__(bot_info['module'], fromlist=[bot_info['class']])
            bot_class = getattr(module, bot_info['class'])
            
            # ایجاد نمونه ربات
            bot = bot_class()
            
            # ذخیره ربات
            self.bots[bot_name] = bot
            self.bot_status[bot_name] = "starting"
            
            # شروع ربات در background
            asyncio.create_task(self.run_bot(bot_name, bot, token))
            
            logger.info(f"✅ {bot_info['name']} شروع شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی {bot_info['name']}: {e}")
            self.bot_status[bot_name] = "error"
    
    async def run_bot(self, bot_name: str, bot, token: str):
        """اجرای ربات"""
        try:
            self.bot_status[bot_name] = "running"
            await bot.start(token)
        except Exception as e:
            logger.error(f"❌ خطا در اجرای {bot_name}: {e}")
            self.bot_status[bot_name] = "error"
        finally:
            if bot_name in self.bot_status:
                self.bot_status[bot_name] = "stopped"
    
    async def start_all_military_bots(self):
        """شروع تمام ربات‌های نظامی"""
        try:
            # بارگذاری تنظیمات
            from config import BOT_TOKENS
            
            logger.info("🎖️ راه‌اندازی ربات‌های نظامی اسرائیل...")
            
            # شروع هر ربات
            for bot_name, bot_info in self.military_bots.items():
                token = BOT_TOKENS.get(bot_info['token_key'])
                if not token:
                    logger.error(f"❌ توکن {bot_info['name']} یافت نشد!")
                    continue
                
                await self.start_bot(bot_name, bot_info, token)
                await asyncio.sleep(2)  # تاخیر بین راه‌اندازی ربات‌ها
            
            logger.info("✅ تمام ربات‌های نظامی شروع شدند")
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی ربات‌های نظامی: {e}")
    
    async def monitor_bots(self):
        """نظارت بر وضعیت ربات‌ها"""
        while self.running:
            try:
                # نمایش وضعیت
                status_report = self.get_status_report()
                logger.info(f"📊 گزارش وضعیت:\n{status_report}")
                
                # بررسی ربات‌های متوقف شده
                for bot_name, status in self.bot_status.items():
                    if status == "error":
                        logger.warning(f"⚠️ {bot_name} با خطا مواجه شده است")
                    elif status == "stopped":
                        logger.warning(f"⚠️ {bot_name} متوقف شده است")
                
                await asyncio.sleep(30)  # بررسی هر 30 ثانیه
                
            except Exception as e:
                logger.error(f"❌ خطا در نظارت: {e}")
                await asyncio.sleep(10)
    
    def get_status_report(self) -> str:
        """تولید گزارش وضعیت"""
        report = "🎖️ وضعیت ربات‌های نظامی:\n"
        report += "-" * 50 + "\n"
        
        for bot_name, bot_info in self.military_bots.items():
            status = self.bot_status.get(bot_name, "unknown")
            status_emoji = {
                "running": "🟢",
                "starting": "🟡",
                "stopped": "🔴",
                "error": "❌",
                "unknown": "❓"
            }.get(status, "❓")
            
            report += f"{status_emoji} {bot_info['name']}: {status}\n"
        
        return report
    
    async def stop_all_bots(self):
        """توقف تمام ربات‌ها"""
        try:
            logger.info("🛑 توقف ربات‌های نظامی...")
            
            for bot_name, bot in self.bots.items():
                try:
                    if bot and not bot.is_closed():
                        await bot.close()
                        logger.info(f"✅ {bot_name} متوقف شد")
                except Exception as e:
                    logger.error(f"❌ خطا در توقف {bot_name}: {e}")
            
            self.bots.clear()
            self.bot_status.clear()
            
            logger.info("✅ تمام ربات‌های نظامی متوقف شدند")
            
        except Exception as e:
            logger.error(f"❌ خطا در توقف ربات‌ها: {e}")
    
    async def run(self):
        """اجرای اصلی مدیر"""
        try:
            self.running = True
            
            # شروع ربات‌ها
            await self.start_all_military_bots()
            
            # شروع نظارت
            monitor_task = asyncio.create_task(self.monitor_bots())
            
            # انتظار برای توقف
            while self.running:
                await asyncio.sleep(1)
            
            # توقف نظارت
            monitor_task.cancel()
            
            # توقف ربات‌ها
            await self.stop_all_bots()
            
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره: {e}")
        finally:
            self.running = False


async def main():
    """تابع اصلی"""
    try:
        # بررسی وجود فایل config
        if not os.path.exists('config.py'):
            print("❌ فایل config.py یافت نشد!")
            print("لطفاً ابتدا فایل .env را تنظیم کنید")
            return
        
        # بررسی وجود فایل .env
        if not os.path.exists('.env'):
            print("⚠️ فایل .env یافت نشد!")
            print("لطفاً فایل .env.example را کپی کرده و تنظیم کنید")
        
        print("🎖️ راه‌اندازی ربات‌های نظامی اسرائیل...")
        print("برای توقف، Ctrl+C را فشار دهید")
        print("-" * 50)
        
        # ایجاد و اجرای مدیر
        manager = MilitaryBotManager()
        await manager.run()
        
    except KeyboardInterrupt:
        print("\n📡 راه‌اندازی توسط کاربر متوقف شد")
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
    finally:
        print("👋 خروج از برنامه")


if __name__ == "__main__":
    asyncio.run(main())