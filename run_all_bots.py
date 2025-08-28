#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اجرای کامل اکوسیستم ربات‌های اسرائیل
Complete Israeli RP Server Bot Ecosystem Runner

این فایل تمام ربات‌های اکوسیستم را به صورت همزمان اجرا می‌کند.
نسخه 2.0 - شامل تمام ربات‌های جدید

تاریخ: ۲۵ آگوست ۲۰۲۵
"""

import asyncio
import logging
import signal
import sys
import os
from typing import List, Dict, Any
import multiprocessing as mp
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# Import all bot classes
from magen_david_bot import MagenDavidBot
from iron_dome_bot import IronDomeBot
from david_sling_bot import DavidSlingBot
from arrow_defense_bots import Arrow3Bot, Arrow4Bot
from thaad_bot import THAADBot
from army_command_bot import ArmyCommandBot
from economic_bots import CentralBankBot, MilitaryIndustriesBot, TelAvivStockExchangeBot
from civil_systems import JobsAndEducationBot, RealEstateBot, PoliticalPartiesBot, RadioIsraelBot
from crisis_management import CrisisManagementBot, PersonalProgressBot, UndergroundEconomyBot

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('israel_rp_ecosystem.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class BotEcosystemManager:
    """مدیریت کامل اکوسیستم ربات‌ها"""
    
    def __init__(self):
        self.bots = []
        self.running = False
        self.processes = []
        self.failed_bots = []
    
    def add_bot(self, bot_class, bot_name: str, token_env_var: str):
        """اضافه کردن ربات به اکوسیستم"""
        self.bots.append({
            'class': bot_class,
            'name': bot_name,
            'token_env': token_env_var,
            'process': None,
            'restart_count': 0
        })
    
    async def run_bot(self, bot_class, bot_name: str, token_env_var: str):
        """اجرای یک ربات"""
        try:
            token = os.getenv(token_env_var)
            if not token:
                logger.error(f"توکن برای {bot_name} یافت نشد: {token_env_var}")
                return
            
            logger.info(f"🚀 شروع {bot_name}...")
            bot = bot_class()
            await bot.start(token)
            
        except Exception as e:
            logger.error(f"❌ خطا در اجرای {bot_name}: {e}")
            raise
    
    def run_bot_process(self, bot_class, bot_name: str, token_env_var: str):
        """اجرای ربات در پروسه جداگانه"""
        try:
            # ایجاد event loop جدید برای پروسه
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # اجرای ربات
            loop.run_until_complete(self.run_bot(bot_class, bot_name, token_env_var))
            
        except KeyboardInterrupt:
            logger.info(f"⏹️ ربات {bot_name} متوقف شد.")
        except Exception as e:
            logger.error(f"💥 خطای غیرمنتظره در {bot_name}: {e}")
        finally:
            loop.close()
    
    def start_all_bots(self):
        """شروع تمام ربات‌های اکوسیستم"""
        logger.info("=" * 80)
        logger.info("🇮🇱 شروع اکوسیستم کامل ربات‌های اسرائیل 🇮🇱")
        logger.info("=" * 80)
        
        self.running = True
        
        # بررسی توکن‌ها
        missing_tokens = []
        for bot_info in self.bots:
            token = os.getenv(bot_info['token_env'])
            if not token:
                missing_tokens.append((bot_info['name'], bot_info['token_env']))
        
        if missing_tokens:
            logger.warning("⚠️ توکن‌های زیر یافت نشد:")
            for bot_name, token_env in missing_tokens:
                logger.warning(f"   - {bot_name}: {token_env}")
            logger.warning("این ربات‌ها اجرا نخواهند شد.")
        
        # شروع ربات‌ها
        started_count = 0
        for bot_info in self.bots:
            token = os.getenv(bot_info['token_env'])
            if not token:
                continue
                
            try:
                process = mp.Process(
                    target=self.run_bot_process,
                    args=(bot_info['class'], bot_info['name'], bot_info['token_env']),
                    name=f"Bot-{bot_info['name']}"
                )
                process.start()
                self.processes.append(process)
                bot_info['process'] = process
                started_count += 1
                
                logger.info(f"✅ {bot_info['name']} شروع شد (PID: {process.pid})")
                
            except Exception as e:
                logger.error(f"❌ خطا در شروع {bot_info['name']}: {e}")
                self.failed_bots.append(bot_info['name'])
        
        logger.info("-" * 50)
        logger.info(f"📊 خلاصه: {started_count} ربات شروع شد، {len(self.failed_bots)} ربات ناموفق")
        if self.failed_bots:
            logger.info(f"❌ ربات‌های ناموفق: {', '.join(self.failed_bots)}")
        logger.info("-" * 50)
    
    def stop_all_bots(self):
        """متوقف کردن تمام ربات‌ها"""
        logger.info("🛑 متوقف کردن اکوسیستم...")
        
        self.running = False
        
        for i, process in enumerate(self.processes):
            if process.is_alive():
                bot_name = self.bots[i]['name'] if i < len(self.bots) else f"Process-{i}"
                logger.info(f"⏹️ متوقف کردن {bot_name} (PID: {process.pid})...")
                
                process.terminate()
                
                # انتظار برای بسته شدن نرمال
                try:
                    process.join(timeout=10)
                    logger.info(f"✅ {bot_name} متوقف شد")
                except:
                    # اگر نرمال بسته نشد، force kill
                    logger.warning(f"⚡ Force killing {bot_name}...")
                    process.kill()
                    process.join()
        
        self.processes.clear()
        logger.info("✅ تمام ربات‌ها متوقف شدند")
    
    def monitor_bots(self):
        """نظارت بر وضعیت ربات‌ها"""
        logger.info("👁️ شروع نظارت بر اکوسیستم...")
        
        while self.running:
            try:
                # بررسی وضعیت پروسه‌ها
                for i, process in enumerate(self.processes):
                    if not process.is_alive() and i < len(self.bots):
                        bot_info = self.bots[i]
                        bot_name = bot_info['name']
                        
                        logger.warning(f"💀 {bot_name} متوقف شده است!")
                        
                        # محدودیت restart
                        if bot_info['restart_count'] < 3 and self.running:
                            bot_info['restart_count'] += 1
                            logger.info(f"🔄 تلاش {bot_info['restart_count']} برای راه‌اندازی مجدد {bot_name}...")
                            
                            try:
                                new_process = mp.Process(
                                    target=self.run_bot_process,
                                    args=(bot_info['class'], bot_name, bot_info['token_env']),
                                    name=f"Bot-{bot_name}"
                                )
                                new_process.start()
                                self.processes[i] = new_process
                                bot_info['process'] = new_process
                                
                                logger.info(f"✅ {bot_name} مجدداً شروع شد (PID: {new_process.pid})")
                                
                            except Exception as e:
                                logger.error(f"❌ خطا در راه‌اندازی مجدد {bot_name}: {e}")
                        else:
                            logger.error(f"❌ {bot_name} بیش از حد مجاز restart شده. متوقف می‌شود.")
                
                # نمایش آمار دوره‌ای
                alive_count = sum(1 for p in self.processes if p.is_alive())
                logger.info(f"📊 وضعیت: {alive_count}/{len(self.processes)} ربات فعال")
                
                # انتظار قبل از بررسی بعدی
                import time
                time.sleep(60)  # بررسی هر دقیقه
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ خطا در نظارت: {e}")
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """دریافت وضعیت تفصیلی اکوسیستم"""
        status = {
            'ecosystem_status': 'running' if self.running else 'stopped',
            'total_bots': len(self.bots),
            'running_bots': 0,
            'stopped_bots': 0,
            'failed_bots': len(self.failed_bots),
            'categories': {
                'central': {'total': 0, 'running': 0},
                'defense': {'total': 0, 'running': 0},
                'military': {'total': 0, 'running': 0},
                'economic': {'total': 0, 'running': 0},
                'civil': {'total': 0, 'running': 0},
                'crisis': {'total': 0, 'running': 0}
            },
            'bot_details': []
        }
        
        # تعیین کتگوری هر ربات
        category_mapping = {
            'ستاره داوود': 'central',
            'گنبد آهنین': 'defense',
            'فلاخن داوود': 'defense',
            'خِتْس ۳': 'defense',
            'خِتْس ۴': 'defense',
            'تاد': 'defense',
            'فرماندهی کل ارتش': 'military',
            'بانک مرکزی': 'economic',
            'صنایع نظامی': 'economic',
            'بورس تل‌آویو': 'economic',
            'مشاغل و آموزش': 'civil',
            'املاک و مستغلات': 'civil',
            'احزاب سیاسی': 'civil',
            'رادیو اسرائیل': 'civil',
            'مدیریت بحران': 'crisis',
            'پیشرفت فردی': 'crisis',
            'اقتصاد سیاه': 'crisis'
        }
        
        for i, bot_info in enumerate(self.bots):
            process = self.processes[i] if i < len(self.processes) else None
            is_running = process and process.is_alive()
            
            # آمار کلی
            if is_running:
                status['running_bots'] += 1
            else:
                status['stopped_bots'] += 1
            
            # آمار کتگوری
            category = category_mapping.get(bot_info['name'], 'other')
            if category in status['categories']:
                status['categories'][category]['total'] += 1
                if is_running:
                    status['categories'][category]['running'] += 1
            
            # جزئیات ربات
            status['bot_details'].append({
                'name': bot_info['name'],
                'category': category,
                'running': is_running,
                'pid': process.pid if process else None,
                'restart_count': bot_info.get('restart_count', 0)
            })
        
        return status

def setup_signal_handlers(ecosystem_manager: BotEcosystemManager):
    """تنظیم signal handler ها"""
    
    def signal_handler(signum, frame):
        logger.info(f"📡 سیگنال {signum} دریافت شد")
        ecosystem_manager.stop_all_bots()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """تابع اصلی اکوسیستم"""
    
    print("🇮🇱" + "=" * 76 + "🇮🇱")
    print("   اکوسیستم کامل ربات‌های رول‌پلی اسرائیل - نسخه 2.0")
    print("   Israeli RP Server Complete Bot Ecosystem v2.0")
    print("🇮🇱" + "=" * 76 + "🇮🇱")
    
    # بررسی پشتیبانی multiprocessing
    if mp.get_start_method() != 'spawn':
        try:
            mp.set_start_method('spawn')
        except RuntimeError:
            pass
    
    # ایجاد مدیریت اکوسیستم
    ecosystem = BotEcosystemManager()
    
    # تنظیم کامل ربات‌ها
    bots_config = [
        # ربات مرکزی
        (MagenDavidBot, "ستاره داوود", "DISCORD_BOT_TOKEN_MAGEN_DAVID"),
        
        # سیستم دفاعی
        (IronDomeBot, "گنبد آهنین", "DISCORD_BOT_TOKEN_IRON_DOME"),
        (DavidSlingBot, "فلاخن داوود", "DISCORD_BOT_TOKEN_DAVID_SLING"),
        (Arrow3Bot, "خِتْس ۳", "DISCORD_BOT_TOKEN_ARROW_DEFENSE"),
        (Arrow4Bot, "خِتْس ۴", "DISCORD_BOT_TOKEN_ARROW_DEFENSE"),
        (THAADBot, "تاد", "DISCORD_BOT_TOKEN_THAAD"),
        
        # سیستم نظامی
        (ArmyCommandBot, "فرماندهی کل ارتش", "DISCORD_BOT_TOKEN_ARMY_COMMAND"),
        
        # سیستم اقتصادی
        (CentralBankBot, "بانک مرکزی", "DISCORD_BOT_TOKEN_CENTRAL_BANK"),
        (MilitaryIndustriesBot, "صنایع نظامی", "DISCORD_BOT_TOKEN_MILITARY_INDUSTRIES"),
        (TelAvivStockExchangeBot, "بورس تل‌آویو", "DISCORD_BOT_TOKEN_STOCK_EXCHANGE"),
        
        # سیستم‌های مدنی
        (JobsAndEducationBot, "مشاغل و آموزش", "DISCORD_BOT_TOKEN_JOBS_EDUCATION"),
        (RealEstateBot, "املاک و مستغلات", "DISCORD_BOT_TOKEN_REAL_ESTATE"),
        (PoliticalPartiesBot, "احزاب سیاسی", "DISCORD_BOT_TOKEN_POLITICAL_PARTIES"),
        (RadioIsraelBot, "رادیو اسرائیل", "DISCORD_BOT_TOKEN_RADIO_ISRAEL"),
        
        # مدیریت بحران و سیستم‌های پیشرفته
        (CrisisManagementBot, "مدیریت بحران", "DISCORD_BOT_TOKEN_CRISIS_MANAGEMENT"),
        (PersonalProgressBot, "پیشرفت فردی", "DISCORD_BOT_TOKEN_PERSONAL_PROGRESS"),
        (UndergroundEconomyBot, "اقتصاد سیاه", "DISCORD_BOT_TOKEN_UNDERGROUND"),
    ]
    
    # اضافه کردن ربات‌ها به اکوسیستم
    for bot_class, bot_name, token_env in bots_config:
        ecosystem.add_bot(bot_class, bot_name, token_env)
    
    # تنظیم signal handlers
    setup_signal_handlers(ecosystem)
    
    try:
        # شروع اکوسیستم
        ecosystem.start_all_bots()
        
        # نمایش آمار اولیه
        status = ecosystem.get_detailed_status()
        logger.info("📊 آمار اکوسیستم:")
        logger.info(f"   • مرکزی: {status['categories']['central']['running']}/{status['categories']['central']['total']}")
        logger.info(f"   • دفاعی: {status['categories']['defense']['running']}/{status['categories']['defense']['total']}")
        logger.info(f"   • نظامی: {status['categories']['military']['running']}/{status['categories']['military']['total']}")
        logger.info(f"   • اقتصادی: {status['categories']['economic']['running']}/{status['categories']['economic']['total']}")
        logger.info(f"   • مدنی: {status['categories']['civil']['running']}/{status['categories']['civil']['total']}")
        logger.info(f"   • بحران: {status['categories']['crisis']['running']}/{status['categories']['crisis']['total']}")
        logger.info(f"📈 مجموع: {status['running_bots']}/{status['total_bots']} ربات فعال")
        
        # شروع نظارت
        ecosystem.monitor_bots()
        
    except KeyboardInterrupt:
        logger.info("⌨️ دریافت سیگنال توقف از کاربر")
    except Exception as e:
        logger.error(f"💥 خطای غیرمنتظره: {e}")
    finally:
        ecosystem.stop_all_bots()
        logger.info("🏁 اکوسیستم ربات‌های اسرائیل متوقف شد")
        print("\n👋 خداحافظ!")

if __name__ == "__main__":
    """
    🇮🇱 راهنمای اجرای اکوسیستم کامل ربات‌های اسرائیل 🇮🇱
    
    📋 مراحل راه‌اندازی:
    
    1️⃣ نصب وابستگی‌ها:
       pip install -r requirements.txt
    
    2️⃣ تنظیم فایل محیطی:
       cp .env.example .env
       # ویرایش .env و تنظیم تمام توکن‌ها
    
    3️⃣ اجرای اکوسیستم:
       python run_all_bots.py
    
    4️⃣ مدیریت:
       - برای توقف: Ctrl+C
       - لاگ‌ها در: israel_rp_ecosystem.log
       - restart خودکار ربات‌های متوقف شده
    
    🏗️ معماری اکوسیستم:
    • 1 ربات مرکزی (ستاره داوود)
    • 5 ربات دفاعی (گنبد آهنین، فلاخن، خِتس، تاد)
    • 1 ربات نظامی (فرماندهی ارتش)
    • 3 ربات اقتصادی (بانک، صنایع، بورس)
    • 4 ربات مدنی (مشاغل، املاک، احزاب، رادیو)
    • 3 ربات مدیریت (بحران، پیشرفت، اقتصاد سیاه)
    
    📊 مجموع: 17 ربات تخصصی
    """
    main()