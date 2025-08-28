#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی ربات‌های اقتصادی و اطلاعاتی اسرائیل
Script to run Israel economy and intelligence bots
"""

import asyncio
import logging
import os
import sys
from typing import List, Dict, Any
import signal
import time

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Economy & Intel Bots - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/economy_intel_bots.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class EconomyIntelBotManager:
    """مدیریت‌کننده ربات‌های اقتصادی و اطلاعاتی"""
    
    def __init__(self):
        self.bots = {}
        self.running = False
        self.startup_time = None
        
        # تنظیم سیگنال‌ها برای خروج ایمن
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("💰🕵️ مدیر ربات‌های اقتصادی و اطلاعاتی راه‌اندازی شد")
    
    def signal_handler(self, signum, frame):
        """مدیریت سیگنال‌های خروج"""
        logger.info(f"📡 سیگنال {signum} دریافت شد. در حال خروج ایمن...")
        self.running = False
    
    async def start_bot(self, bot_name: str, bot_module: str, token: str):
        """راه‌اندازی یک ربات اقتصادی یا اطلاعاتی"""
        try:
            logger.info(f"🔄 راه‌اندازی {bot_name}...")
            
            # import کردن ماژول ربات
            module = __import__(bot_module, fromlist=['main'])
            
            # ایجاد ربات بر اساس نام
            if bot_name == "Economy":
                bot = module.EconomyBot()
            elif bot_name == "Mossad":
                bot = module.MossadBot()
            elif bot_name == "Radio Israel":
                bot = module.RadioIsraelBot()
            else:
                logger.error(f"❌ نام ربات نامعتبر: {bot_name}")
                return
            
            # ذخیره ربات
            self.bots[bot_name] = {
                'bot': bot,
                'module': bot_module,
                'status': 'starting'
            }
            
            # راه‌اندازی ربات در پس‌زمینه
            task = asyncio.create_task(self.run_bot(bot_name, bot, token))
            self.bots[bot_name]['task'] = task
            
            logger.info(f"✅ {bot_name} راه‌اندازی شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی {bot_name}: {e}")
            if bot_name in self.bots:
                self.bots[bot_name]['status'] = 'error'
    
    async def run_bot(self, bot_name: str, bot, token: str):
        """اجرای ربات"""
        try:
            self.bots[bot_name]['status'] = 'running'
            await bot.start(token)
        except Exception as e:
            logger.error(f"❌ خطا در اجرای {bot_name}: {e}")
            self.bots[bot_name]['status'] = 'error'
        finally:
            self.bots[bot_name]['status'] = 'stopped'
    
    async def start_all_bots(self):
        """راه‌اندازی تمام ربات‌های اقتصادی و اطلاعاتی"""
        try:
            from config import BOT_TOKENS
            
            # لیست ربات‌ها و ماژول‌های مربوطه
            bot_configs = [
                ("Economy", "bots.economy", BOT_TOKENS.get("economy")),
                ("Mossad", "bots.mossad", BOT_TOKENS.get("mossad")),
                ("Radio Israel", "bots.radio", BOT_TOKENS.get("radio"))
            ]
            
            # راه‌اندازی تمام ربات‌ها
            startup_tasks = []
            for bot_name, module, token in bot_configs:
                if token:
                    task = self.start_bot(bot_name, module, token)
                    startup_tasks.append(task)
                else:
                    logger.warning(f"⚠️ توکن برای {bot_name} یافت نشد")
            
            # انتظار برای راه‌اندازی تمام ربات‌ها
            await asyncio.gather(*startup_tasks, return_exceptions=True)
            
            self.startup_time = time.time()
            logger.info("🎉 تمام ربات‌های اقتصادی و اطلاعاتی راه‌اندازی شدند")
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی ربات‌ها: {e}")
    
    async def monitor_bots(self):
        """نظارت بر وضعیت ربات‌ها"""
        try:
            while self.running:
                # نمایش وضعیت ربات‌ها
                status_report = self.get_status_report()
                logger.info(f"📊 گزارش وضعیت ربات‌های اقتصادی و اطلاعاتی:\n{status_report}")
                
                # بررسی ربات‌های متوقف شده
                for bot_name, bot_info in self.bots.items():
                    if bot_info['status'] == 'error':
                        logger.warning(f"⚠️ {bot_name} با خطا مواجه شده است")
                    elif bot_info['status'] == 'stopped':
                        logger.warning(f"⚠️ {bot_name} متوقف شده است")
                
                # انتظار 4 دقیقه
                await asyncio.sleep(240)
                
        except Exception as e:
            logger.error(f"❌ خطا در نظارت بر ربات‌ها: {e}")
    
    def get_status_report(self) -> str:
        """دریافت گزارش وضعیت"""
        if not self.bots:
            return "هیچ ربات اقتصادی یا اطلاعاتی راه‌اندازی نشده است"
        
        report = []
        for bot_name, bot_info in self.bots.items():
            status_emoji = {
                'starting': '🔄',
                'running': '✅',
                'error': '❌',
                'stopped': '⏹️'
            }.get(bot_info['status'], '❓')
            
            report.append(f"{status_emoji} {bot_name}: {bot_info['status']}")
        
        return "\n".join(report)
    
    async def stop_all_bots(self):
        """توقف تمام ربات‌ها"""
        try:
            logger.info("🛑 توقف تمام ربات‌های اقتصادی و اطلاعاتی...")
            
            # توقف تمام ربات‌ها
            stop_tasks = []
            for bot_name, bot_info in self.bots.items():
                if bot_info['status'] == 'running':
                    try:
                        await bot_info['bot'].close()
                        logger.info(f"✅ {bot_name} متوقف شد")
                    except Exception as e:
                        logger.error(f"❌ خطا در توقف {bot_name}: {e}")
            
            # انتظار برای توقف کامل
            await asyncio.sleep(2)
            
            logger.info("🎯 تمام ربات‌های اقتصادی و اطلاعاتی متوقف شدند")
            
        except Exception as e:
            logger.error(f"❌ خطا در توقف ربات‌ها: {e}")
    
    async def run(self):
        """اجرای اصلی مدیر ربات‌های اقتصادی و اطلاعاتی"""
        try:
            self.running = True
            
            # راه‌اندازی تمام ربات‌ها
            await self.start_all_bots()
            
            # شروع نظارت
            monitor_task = asyncio.create_task(self.monitor_bots())
            
            # انتظار برای سیگنال خروج
            while self.running:
                await asyncio.sleep(1)
            
            # توقف نظارت
            monitor_task.cancel()
            
            # توقف تمام ربات‌ها
            await self.stop_all_bots()
            
        except Exception as e:
            logger.error(f"❌ خطا در اجرای مدیر ربات‌ها: {e}")
        finally:
            self.running = False

async def main():
    """تابع اصلی"""
    try:
        # بررسی وجود فایل config
        if not os.path.exists('config.py'):
            logger.error("❌ فایل config.py یافت نشد!")
            logger.error("لطفاً ابتدا فایل .env را تنظیم کنید")
            return
        
        # بررسی وجود فایل .env
        if not os.path.exists('.env'):
            logger.warning("⚠️ فایل .env یافت نشد!")
            logger.warning("لطفاً فایل .env.example را کپی کرده و تنظیم کنید")
        
        # راه‌اندازی مدیر ربات‌های اقتصادی و اطلاعاتی
        manager = EconomyIntelBotManager()
        await manager.run()
        
    except KeyboardInterrupt:
        logger.info("📡 راه‌اندازی توسط کاربر متوقف شد")
    except Exception as e:
        logger.error(f"❌ خطای غیرمنتظره: {e}")
    finally:
        logger.info("👋 خروج از برنامه")

if __name__ == "__main__":
    print("💰🕵️ راه‌اندازی ربات‌های اقتصادی و اطلاعاتی اسرائیل...")
    print("برای توقف، Ctrl+C را فشار دهید")
    print("-" * 50)
    
    # اجرای برنامه
    asyncio.run(main())