"""
اسکریپت اصلی راه‌اندازی اکوسیستم ربات‌های هوشمند اسرائیل
Main Launcher Script for Israeli Smart Bot Ecosystem
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import bot
from magen_david_bot import bot
from config import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """تابع اصلی راه‌اندازی"""
    try:
        logger.info("🚀 راه‌اندازی اکوسیستم ربات‌های هوشمند اسرائیل...")
        logger.info("🌟 ستاره داوود در حال بیدار شدن...")
        
        # Check if bot token is available
        if not config.MAGEN_DAVID_TOKEN:
            logger.error("❌ توکن ربات ستاره داوود یافت نشد!")
            logger.error("لطفاً متغیر محیطی MAGEN_DAVID_TOKEN را تنظیم کنید.")
            return
        
        # Check if Gemini API key is available
        if not config.GEMINI_API_KEY:
            logger.warning("⚠️ کلید API جمنای یافت نشد!")
            logger.warning("ربات در حالت پیش‌فرض کار خواهد کرد.")
        
        # Check if server ID is available
        if not config.SERVER_ID:
            logger.error("❌ شناسه سرور یافت نشد!")
            logger.error("لطفاً متغیر محیطی SERVER_ID را تنظیم کنید.")
            return
        
        logger.info("✅ تمام تنظیمات اولیه بررسی شد")
        logger.info("🔗 در حال اتصال به دیسکورد...")
        
        # Start the bot
        async with bot:
            await bot.start(config.MAGEN_DAVID_TOKEN)
            
    except KeyboardInterrupt:
        logger.info("🛑 دریافت سیگنال توقف...")
        logger.info("🔄 در حال خاموش کردن ربات...")
        
    except Exception as e:
        logger.error(f"💥 خطای غیرمنتظره: {e}")
        logger.error("🔧 جزئیات خطا:", exc_info=True)
        
    finally:
        logger.info("👋 ربات ستاره داوود خاموش شد")

def check_environment():
    """بررسی محیط اجرا"""
    logger.info("🔍 بررسی محیط اجرا...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ نسخه پایتون 3.8 یا بالاتر مورد نیاز است!")
        logger.error(f"نسخه فعلی: {sys.version}")
        return False
    
    logger.info(f"✅ نسخه پایتون: {sys.version}")
    
    # Check required files
    required_files = [
        "config.py",
        "models.py", 
        "gemini_integration.py",
        "magen_david_bot.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            logger.error(f"❌ فایل مورد نیاز یافت نشد: {file}")
            return False
    
    logger.info("✅ تمام فایل‌های مورد نیاز موجود است")
    
    # Check dependencies
    try:
        import discord
        logger.info(f"✅ discord.py: {discord.__version__}")
    except ImportError:
        logger.error("❌ کتابخانه discord.py یافت نشد!")
        return False
    
    try:
        import google.generativeai
        logger.info("✅ google-generativeai موجود است")
    except ImportError:
        logger.warning("⚠️ کتابخانه google-generativeai یافت نشد!")
        logger.warning("ربات در حالت پیش‌فرض کار خواهد کرد")
    
    try:
        import dotenv
        logger.info("✅ python-dotenv موجود است")
    except ImportError:
        logger.warning("⚠️ کتابخانه python-dotenv یافت نشد!")
    
    return True

def print_banner():
    """نمایش بنر راه‌اندازی"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🌟 ستاره داوود - اکوسیستم ربات‌های هوشمند اسرائیل 🌟        ║
    ║                                                              ║
    ║                    Magen David - Israeli Smart Bot Ecosystem ║
    ║                                                              ║
    ║  🚀 راه‌اندازی سیستم...                                        ║
    ║  🔒 سیستم دفاعی چندلایه                                      ║
    ║  🏛️ شبیه‌سازی دولت و کنست                                    ║
    ║  💰 اقتصاد پویا و واقع‌گرایانه                               ║
    ║  🎭 رول‌پلی عمیق و جذاب                                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_help():
    """نمایش راهنمای استفاده"""
    help_text = """
    📖 راهنمای راه‌اندازی اکوسیستم ربات‌های هوشمند اسرائیل
    
    🔧 پیش‌نیازها:
    - پایتون 3.8 یا بالاتر
    - توکن ربات دیسکورد
    - کلید API جمنای (اختیاری)
    
    📁 ساختار فایل‌ها:
    ├── main.py                    # اسکریپت اصلی راه‌اندازی
    ├── config.py                  # تنظیمات و پیکربندی
    ├── models.py                  # مدل‌های پایگاه داده
    ├── gemini_integration.py      # یکپارچه‌سازی هوش مصنوعی
    ├── magen_david_bot.py        # ربات مرکزی ستاره داوود
    ├── cogs/                     # ماژول‌های تخصصی
    │   ├── government_cog.py     # ماژول دولت
    │   ├── military_cog.py       # ماژول نظامی
    │   ├── economy_cog.py        # ماژول اقتصاد
    │   ├── civilian_cog.py       # ماژول مدنی
    │   └── intelligence_cog.py   # ماژول اطلاعاتی
    ├── requirements.txt           # وابستگی‌ها
    └── .env                      # متغیرهای محیطی
    
    🌍 متغیرهای محیطی مورد نیاز:
    MAGEN_DAVID_TOKEN=your_bot_token_here
    GEMINI_API_KEY=your_gemini_api_key_here
    SERVER_ID=your_discord_server_id_here
    
    🚀 راه‌اندازی:
    python main.py
    
    📚 مستندات کامل:
    برای اطلاعات بیشتر، فایل README.md را مطالعه کنید.
    
    🆘 پشتیبانی:
    در صورت بروز مشکل، لاگ‌ها را بررسی کنید.
    """
    print(help_text)

if __name__ == "__main__":
    # Display banner
    print_banner()
    
    # Check if help is requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        sys.exit(0)
    
    # Check environment
    if not check_environment():
        logger.error("❌ بررسی محیط اجرا ناموفق بود!")
        logger.error("لطفاً مشکلات را برطرف کرده و دوباره تلاش کنید.")
        sys.exit(1)
    
    logger.info("✅ بررسی محیط اجرا موفقیت‌آمیز بود")
    logger.info("🚀 شروع راه‌اندازی ربات...")
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 راه‌اندازی متوقف شد")
    except Exception as e:
        logger.error(f"💥 خطا در راه‌اندازی: {e}")
        sys.exit(1)