#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی ربات فلاخن داوود اسرائیل
Script to run David's Sling bot
"""

import asyncio
import logging
import os
import sys

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Davids Sling - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/davids_sling_standalone.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

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
        
        # import کردن ربات
        from bots.davids_sling import DavidsSlingBot
        from config import BOT_TOKENS
        
        # بررسی توکن
        token = BOT_TOKENS.get("davids_sling")
        if not token:
            logger.error("❌ توکن ربات فلاخن داوود یافت نشد!")
            return
        
        logger.info("🏹 راه‌اندازی ربات فلاخن داوود اسرائیل...")
        
        # ایجاد و راه‌اندازی ربات
        bot = DavidsSlingBot()
        await bot.start(token)
        
    except KeyboardInterrupt:
        logger.info("📡 راه‌اندازی توسط کاربر متوقف شد")
    except Exception as e:
        logger.error(f"❌ خطای غیرمنتظره: {e}")
    finally:
        logger.info("👋 خروج از برنامه")

if __name__ == "__main__":
    print("🏹 راه‌اندازی ربات فلاخن داوود اسرائیل...")
    print("برای توقف، Ctrl+C را فشار دهید")
    print("-" * 50)
    
    # اجرای برنامه
    asyncio.run(main())