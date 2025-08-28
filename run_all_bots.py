"""
اجرای همزمان تمام ربات‌های اکوسیستم اسرائیل
Run All Israel RP Bots Simultaneously

این فایل تمام ربات‌های اکوسیستم را به صورت همزمان اجرا می‌کند.
"""

import asyncio
import logging
import signal
import sys
from typing import List
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

# Import all bot classes
from magen_david_bot import MagenDavidBot
from iron_dome_bot import IronDomeBot
from david_sling_bot import DavidSlingBot
from arrow_defense_bots import Arrow3Bot, Arrow4Bot
from thaad_bot import THAADBot
from army_command_bot import ArmyCommandBot

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('israel_rp_bots.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class BotManager:
    """مدیریت اجرای همزمان ربات‌ها"""
    
    def __init__(self):
        self.bots = []
        self.running = False
        self.processes = []
    
    def add_bot(self, bot_class, bot_name: str):
        """اضافه کردن ربات به لیست"""
        self.bots.append({
            'class': bot_class,
            'name': bot_name,
            'process': None
        })
    
    async def run_bot(self, bot_class, bot_name: str):
        """اجرای یک ربات"""
        try:
            logger.info(f"شروع ربات {bot_name}...")
            bot = bot_class()
            await bot.start(bot.token)
        except Exception as e:
            logger.error(f"خطا در اجرای ربات {bot_name}: {e}")
            raise
    
    def run_bot_process(self, bot_class, bot_name: str):
        """اجرای ربات در پروسه جداگانه"""
        try:
            # ایجاد event loop جدید برای پروسه
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # اجرای ربات
            loop.run_until_complete(self.run_bot(bot_class, bot_name))
        except KeyboardInterrupt:
            logger.info(f"ربات {bot_name} متوقف شد.")
        except Exception as e:
            logger.error(f"خطای غیرمنتظره در ربات {bot_name}: {e}")
        finally:
            loop.close()
    
    def start_all_bots(self):
        """شروع همه ربات‌ها"""
        logger.info("شروع اجرای همزمان تمام ربات‌ها...")
        
        self.running = True
        
        # شروع هر ربات در پروسه جداگانه
        for bot_info in self.bots:
            try:
                process = mp.Process(
                    target=self.run_bot_process,
                    args=(bot_info['class'], bot_info['name']),
                    name=f"Bot-{bot_info['name']}"
                )
                process.start()
                self.processes.append(process)
                bot_info['process'] = process
                
                logger.info(f"ربات {bot_info['name']} در پروسه {process.pid} شروع شد.")
                
            except Exception as e:
                logger.error(f"خطا در شروع ربات {bot_info['name']}: {e}")
        
        logger.info(f"تمام {len(self.processes)} ربات شروع شدند.")
    
    def stop_all_bots(self):
        """متوقف کردن همه ربات‌ها"""
        logger.info("متوقف کردن تمام ربات‌ها...")
        
        self.running = False
        
        for process in self.processes:
            if process.is_alive():
                logger.info(f"متوقف کردن پروسه {process.pid}...")
                process.terminate()
                
                # انتظار برای بسته شدن نرمال
                try:
                    process.join(timeout=5)
                except:
                    # اگر نرمال بسته نشد، force kill
                    process.kill()
                    process.join()
                
                logger.info(f"پروسه {process.pid} متوقف شد.")
        
        self.processes.clear()
        logger.info("تمام ربات‌ها متوقف شدند.")
    
    def monitor_bots(self):
        """نظارت بر وضعیت ربات‌ها"""
        while self.running:
            try:
                # بررسی وضعیت پروسه‌ها
                for i, process in enumerate(self.processes):
                    if not process.is_alive():
                        bot_name = self.bots[i]['name']
                        logger.warning(f"ربات {bot_name} (PID: {process.pid}) متوقف شده است!")
                        
                        # تلاش برای راه‌اندازی مجدد
                        if self.running:
                            logger.info(f"راه‌اندازی مجدد ربات {bot_name}...")
                            try:
                                new_process = mp.Process(
                                    target=self.run_bot_process,
                                    args=(self.bots[i]['class'], bot_name),
                                    name=f"Bot-{bot_name}"
                                )
                                new_process.start()
                                self.processes[i] = new_process
                                self.bots[i]['process'] = new_process
                                logger.info(f"ربات {bot_name} مجدداً شروع شد (PID: {new_process.pid})")
                            except Exception as e:
                                logger.error(f"خطا در راه‌اندازی مجدد ربات {bot_name}: {e}")
                
                # انتظار قبل از بررسی بعدی
                import time
                time.sleep(30)  # بررسی هر 30 ثانیه
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"خطا در نظارت بر ربات‌ها: {e}")
    
    def get_status(self) -> dict:
        """دریافت وضعیت ربات‌ها"""
        status = {
            'total_bots': len(self.bots),
            'running_bots': 0,
            'stopped_bots': 0,
            'bot_details': []
        }
        
        for i, bot_info in enumerate(self.bots):
            process = self.processes[i] if i < len(self.processes) else None
            
            is_running = process and process.is_alive()
            
            if is_running:
                status['running_bots'] += 1
            else:
                status['stopped_bots'] += 1
            
            status['bot_details'].append({
                'name': bot_info['name'],
                'running': is_running,
                'pid': process.pid if process else None
            })
        
        return status

def setup_signal_handlers(bot_manager: BotManager):
    """تنظیم signal handler ها"""
    
    def signal_handler(signum, frame):
        logger.info(f"سیگنال {signum} دریافت شد. متوقف کردن ربات‌ها...")
        bot_manager.stop_all_bots()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """تابع اصلی"""
    
    # بررسی پشتیبانی multiprocessing
    if mp.get_start_method() != 'spawn':
        try:
            mp.set_start_method('spawn')
        except RuntimeError:
            pass  # در صورتی که قبلاً تنظیم شده باشد
    
    # ایجاد مدیریت ربات‌ها
    bot_manager = BotManager()
    
    # اضافه کردن ربات‌ها
    bots_config = [
        (MagenDavidBot, "ستاره داوود"),
        (IronDomeBot, "گنبد آهنین"),
        (DavidSlingBot, "فلاخن داوود"),
        (Arrow3Bot, "خِتْس ۳"),
        (Arrow4Bot, "خِتْس ۴"),
        (THAADBot, "تاد"),
        (ArmyCommandBot, "فرماندهی کل ارتش"),
        # اضافه کردن ربات‌های دیگر در صورت وجود
    ]
    
    for bot_class, bot_name in bots_config:
        bot_manager.add_bot(bot_class, bot_name)
    
    # تنظیم signal handlers
    setup_signal_handlers(bot_manager)
    
    try:
        logger.info("=== شروع اکوسیستم ربات‌های رول‌پلی اسرائیل ===")
        
        # شروع همه ربات‌ها
        bot_manager.start_all_bots()
        
        # نمایش وضعیت اولیه
        status = bot_manager.get_status()
        logger.info(f"وضعیت: {status['running_bots']} ربات فعال از {status['total_bots']} ربات")
        
        # شروع نظارت
        logger.info("شروع نظارت بر ربات‌ها...")
        bot_manager.monitor_bots()
        
    except KeyboardInterrupt:
        logger.info("دریافت سیگنال توقف از کاربر...")
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {e}")
    finally:
        bot_manager.stop_all_bots()
        logger.info("=== پایان اکوسیستم ربات‌های رول‌پلی اسرائیل ===")

if __name__ == "__main__":
    main()