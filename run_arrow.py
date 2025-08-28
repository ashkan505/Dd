#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی ربات خِتْس ۳ و ۴ اسرائیل
Script to run Arrow bot
"""

import asyncio
import logging
import os
import sys

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Arrow - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/arrow_standalone.log'),
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
        from bots.arrow import ArrowBot
        from config import BOT_TOKENS
        
        # بررسی توکن
        token = BOT_TOKENS.get("arrow")
        if not token:
            logger.error("❌ توکن ربات خِتْس ۳ و ۴ یافت نشد!")
            return
        
        logger.info("🚀 راه‌اندازی ربات خِتْس ۳ و ۴ اسرائیل...")
        
        # ایجاد و راه‌اندازی ربات
        bot = ArrowBot()
        await bot.start(token)
        
    except KeyboardInterrupt:
        logger.info("📡 راه‌اندازی توسط کاربر متوقف شد")
    except Exception as e:
        logger.error(f"❌ خطای غیرمنتظره: {e}")
    finally:
        logger.info("👋 خروج از برنامه")

if __name__ == "__main__":
    print("🚀 راه‌اندازی ربات خِتْس ۳ و ۴ اسرائیل...")
    print("برای توقف، Ctrl+C را فشار دهید")
    print("-" * 50)
    
    # اجرای برنامه
    asyncio.run(main())