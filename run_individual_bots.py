#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی ربات‌های جداگانه اسرائیل
Script to run individual Israel bots based on user choice
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
    format='%(asctime)s - Individual Bot - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/individual_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class IndividualBotRunner:
    """اجرای ربات‌های جداگانه"""
    
    def __init__(self):
        self.running = False
        self.current_bot = None
        
        # تنظیم سیگنال‌ها برای خروج ایمن
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # لیست ربات‌های موجود
        self.available_bots = {
            "1": ("Magen David", "bots.magen_david", "MagenDavidBot", "magen_david"),
            "2": ("Iron Dome", "bots.iron_dome", "IronDomeBot", "iron_dome"),
            "3": ("David's Sling", "bots.davids_sling", "DavidsSlingBot", "davids_sling"),
            "4": ("Arrow", "bots.arrow", "ArrowBot", "arrow"),
            "5": ("Army Command", "bots.army_command", "ArmyCommandBot", "army_command"),
            "6": ("Air Force", "bots.air_force", "AirForceBot", "air_force"),
            "7": ("Ground Forces", "bots.ground_forces", "GroundForcesBot", "ground_forces"),
            "8": ("Economy", "bots.economy", "EconomyBot", "economy"),
            "9": ("Mossad", "bots.mossad", "MossadBot", "mossad"),
            "10": ("Radio Israel", "bots.radio", "RadioIsraelBot", "radio")
        }
        
        logger.info("🚀 اجراکننده ربات‌های جداگانه راه‌اندازی شد")
    
    def signal_handler(self, signum, frame):
        """مدیریت سیگنال‌های خروج"""
        logger.info(f"📡 سیگنال {signum} دریافت شد. در حال خروج ایمن...")
        self.running = False
    
    def show_menu(self):
        """نمایش منوی انتخاب ربات"""
        print("\n" + "="*60)
        print("🎯 انتخاب ربات برای راه‌اندازی")
        print("="*60)
        
        for key, (name, module, class_name, token_key) in self.available_bots.items():
            print(f"{key}. {name}")
        
        print("0. خروج")
        print("="*60)
    
    def get_user_choice(self) -> str:
        """دریافت انتخاب کاربر"""
        while True:
            try:
                choice = input("\n🔍 شماره ربات مورد نظر را وارد کنید: ").strip()
                if choice == "0":
                    return "0"
                elif choice in self.available_bots:
                    return choice
                else:
                    print("❌ انتخاب نامعتبر! لطفاً شماره صحیح وارد کنید.")
            except KeyboardInterrupt:
                return "0"
            except Exception:
                print("❌ خطا در دریافت ورودی!")
    
    async def start_bot(self, bot_name: str, module_path: str, class_name: str, token_key: str):
        """راه‌اندازی ربات انتخاب شده"""
        try:
            logger.info(f"🔄 راه‌اندازی {bot_name}...")
            
            # بررسی وجود فایل config
            if not os.path.exists('config.py'):
                logger.error("❌ فایل config.py یافت نشد!")
                return False
            
            # import کردن ماژول ربات
            try:
                module = __import__(module_path, fromlist=[class_name])
                bot_class = getattr(module, class_name)
            except ImportError as e:
                logger.error(f"❌ خطا در import کردن ماژول {module_path}: {e}")
                return False
            except AttributeError as e:
                logger.error(f"❌ خطا در یافتن کلاس {class_name}: {e}")
                return False
            
            # دریافت توکن
            try:
                from config import BOT_TOKENS
                token = BOT_TOKENS.get(token_key)
                if not token:
                    logger.error(f"❌ توکن برای {bot_name} یافت نشد!")
                    return False
            except Exception as e:
                logger.error(f"❌ خطا در دریافت توکن: {e}")
                return False
            
            # ایجاد ربات
            bot = bot_class()
            self.current_bot = bot
            
            logger.info(f"✅ {bot_name} راه‌اندازی شد")
            
            # شروع ربات
            await bot.start(token)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی {bot_name}: {e}")
            return False
    
    async def run(self):
        """اجرای اصلی"""
        try:
            self.running = True
            
            while self.running:
                # نمایش منو
                self.show_menu()
                
                # دریافت انتخاب کاربر
                choice = self.get_user_choice()
                
                if choice == "0":
                    print("👋 خروج از برنامه...")
                    break
                
                # راه‌اندازی ربات انتخاب شده
                bot_name, module_path, class_name, token_key = self.available_bots[choice]
                
                print(f"\n🚀 راه‌اندازی {bot_name}...")
                print("برای توقف، Ctrl+C را فشار دهید")
                print("-" * 50)
                
                success = await self.start_bot(bot_name, module_path, class_name, token_key)
                
                if success:
                    logger.info(f"✅ {bot_name} با موفقیت اجرا شد")
                else:
                    logger.error(f"❌ {bot_name} با خطا مواجه شد")
                    print(f"\n❌ خطا در راه‌اندازی {bot_name}")
                
                # پاک کردن ربات فعلی
                self.current_bot = None
                
                # انتظار برای انتخاب بعدی
                if self.running:
                    input("\n⏸️ برای ادامه، Enter را فشار دهید...")
                
        except KeyboardInterrupt:
            logger.info("📡 راه‌اندازی توسط کاربر متوقف شد")
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره: {e}")
        finally:
            self.running = False
            await self.cleanup()
    
    async def cleanup(self):
        """پاکسازی منابع"""
        try:
            if self.current_bot:
                await self.current_bot.close()
                logger.info("✅ ربات فعلی متوقف شد")
        except Exception as e:
            logger.error(f"❌ خطا در پاکسازی: {e}")

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
        
        # راه‌اندازی اجراکننده ربات‌های جداگانه
        runner = IndividualBotRunner()
        await runner.run()
        
    except KeyboardInterrupt:
        print("\n📡 راه‌اندازی توسط کاربر متوقف شد")
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
    finally:
        print("👋 خروج از برنامه")

if __name__ == "__main__":
    print("🚀 راه‌اندازی اجراکننده ربات‌های جداگانه اسرائیل...")
    print("این اسکریپت به شما امکان انتخاب و راه‌اندازی ربات‌های مختلف را می‌دهد")
    print("-" * 60)
    
    # اجرای برنامه
    asyncio.run(main())