"""
کمک‌کننده هوش مصنوعی Gemini برای تولید محتوای پویا
Gemini AI Helper for Dynamic Content Generation
"""

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_CONFIG
import logging
import asyncio
from typing import Optional, List, Dict, Any

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiHelper:
    """کلاس کمکی برای تعامل با هوش مصنوعی Gemini"""
    
    def __init__(self):
        """راه‌اندازی کلاینت Gemini"""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_CONFIG["model"])
            self.is_available = True
            logger.info("✅ Gemini AI با موفقیت راه‌اندازی شد")
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی Gemini AI: {e}")
            self.is_available = False
    
    async def generate_content(self, prompt: str, context: str = "") -> Optional[str]:
        """
        تولید محتوا با استفاده از Gemini AI
        
        Args:
            prompt: دستور تولید محتوا
            context: زمینه و اطلاعات اضافی
            
        Returns:
            محتوای تولید شده یا None در صورت خطا
        """
        if not self.is_available:
            return "هوش مصنوعی در دسترس نیست"
        
        try:
            full_prompt = f"""
            {context}
            
            {prompt}
            
            لطفاً پاسخ خود را به زبان فارسی ارائه دهید و از لحن رسمی و مناسب استفاده کنید.
            """
            
            # اجرای همزمان برای جلوگیری از مسدود شدن
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(full_prompt)
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"خطا در تولید محتوا: {e}")
            return f"خطا در تولید محتوا: {str(e)}"
    
    async def generate_news(self, event_type: str, details: Dict[str, Any] = None) -> str:
        """
        تولید اخبار با استفاده از Gemini
        
        Args:
            event_type: نوع رویداد (انتخابات، جنگ، بحران و...)
            details: جزئیات رویداد
            
        Returns:
            متن خبر تولید شده
        """
        context = f"""
        شما خبرنگار رسمی رادیو اسرائیل هستید. 
        نوع رویداد: {event_type}
        جزئیات: {details or 'بدون جزئیات خاص'}
        """
        
        prompt = f"""
        یک خبر رسمی و حرفه‌ای درباره {event_type} بنویسید که:
        1. لحن رسمی و خبری داشته باشد
        2. جزئیات مهم را پوشش دهد
        3. برای خوانندگان سرور رول‌پلی اسرائیل جذاب باشد
        4. حداکثر 200 کلمه باشد
        """
        
        return await self.generate_content(prompt, context)
    
    async def generate_law_proposal(self, topic: str, proposer: str) -> str:
        """
        تولید پیشنهاد قانون با استفاده از Gemini
        
        Args:
            topic: موضوع قانون
            proposer: پیشنهاددهنده
            
        Returns:
            متن پیشنهاد قانون
        """
        context = f"""
        شما عضو کنست اسرائیل هستید که پیشنهاد قانون می‌دهید.
        موضوع: {topic}
        پیشنهاددهنده: {proposer}
        """
        
        prompt = """
        یک پیشنهاد قانون رسمی و واقع‌گرایانه بنویسید که:
        1. ساختار قانونی مناسب داشته باشد
        2. شامل مواد و تبصره‌های مشخص باشد
        3. برای جامعه اسرائیل مفید باشد
        4. حداکثر 300 کلمه باشد
        """
        
        return await self.generate_content(prompt, context)
    
    async def generate_citizenship_questions(self) -> List[str]:
        """
        تولید سوالات شهروندی با استفاده از Gemini
        
        Returns:
            لیست سوالات شهروندی
        """
        context = """
        شما مسئول اداره مهاجرت اسرائیل هستید و باید سوالات شهروندی بپرسید.
        """
        
        prompt = """
        5 سوال مهم برای درخواست شهروندی اسرائیل بنویسید که:
        1. درباره تاریخ، فرهنگ و ارزش‌های اسرائیل باشد
        2. سطح متوسط دشواری داشته باشد
        3. هر سوال در یک خط جداگانه باشد
        4. با شماره شروع شود (مثال: 1. سوال اول)
        """
        
        response = await self.generate_content(prompt, context)
        if response and "خطا" not in response:
            # تقسیم پاسخ به سوالات جداگانه
            questions = [q.strip() for q in response.split('\n') if q.strip() and q[0].isdigit()]
            return questions
        else:
            # سوالات پیش‌فرض در صورت خطا
            return [
                "1. پایتخت اسرائیل کجاست؟",
                "2. نام اولین نخست‌وزیر اسرائیل چه بود؟",
                "3. نماد ملی اسرائیل چیست؟",
                "4. زبان رسمی اسرائیل چیست؟",
                "5. سال تأسیس کشور اسرائیل چه سالی بود؟"
            ]
    
    async def generate_random_event(self) -> Dict[str, Any]:
        """
        تولید رویداد تصادفی با استفاده از Gemini
        
        Returns:
            دیکشنری شامل جزئیات رویداد
        """
        context = """
        شما مسئول تولید رویدادهای تصادفی برای سرور رول‌پلی اسرائیل هستید.
        """
        
        prompt = """
        یک رویداد تصادفی جذاب برای سرور رول‌پلی اسرائیل تولید کنید.
        پاسخ را به این فرمت JSON ارائه دهید:
        {
            "title": "عنوان رویداد",
            "description": "توضیح رویداد",
            "type": "نوع رویداد (مثبت/منفی/خنثی)",
            "effects": {
                "economy": "تأثیر بر اقتصاد (-10 تا +10)",
                "military": "تأثیر بر ارتش (-10 تا +10)",
                "public_approval": "تأثیر بر رضایت عمومی (-10 تا +10)"
            },
            "duration": "مدت تأثیر (به ساعت)"
        }
        """
        
        response = await self.generate_content(prompt, context)
        try:
            # تلاش برای تجزیه JSON
            import json
            event_data = json.loads(response)
            return event_data
        except:
            # رویداد پیش‌فرض در صورت خطا
            return {
                "title": "رویداد پیش‌فرض",
                "description": "یک رویداد معمولی در سرور",
                "type": "خنثی",
                "effects": {
                    "economy": 0,
                    "military": 0,
                    "public_approval": 0
                },
                "duration": 24
            }
    
    async def generate_dialogue(self, character1: str, character2: str, context: str) -> str:
        """
        تولید دیالوگ بین شخصیت‌ها با استفاده از Gemini
        
        Args:
            character1: شخصیت اول
            character2: شخصیت دوم
            context: زمینه دیالوگ
            
        Returns:
            متن دیالوگ تولید شده
        """
        prompt = f"""
        یک دیالوگ طبیعی و جذاب بین {character1} و {character2} بنویسید.
        زمینه: {context}
        
        دیالوگ باید:
        1. طبیعی و واقع‌گرایانه باشد
        2. شخصیت هر فرد را نشان دهد
        3. حداکثر 150 کلمه باشد
        4. با فرمت مناسب نمایش داده شود
        """
        
        return await self.generate_content(prompt)
    
    async def generate_mission(self, mission_type: str, difficulty: str) -> Dict[str, Any]:
        """
        تولید مأموریت با استفاده از Gemini
        
        Args:
            mission_type: نوع مأموریت
            difficulty: سطح دشواری
            
        Returns:
            دیکشنری شامل جزئیات مأموریت
        """
        context = f"""
        شما مسئول تولید مأموریت‌های {mission_type} برای سرور رول‌پلی اسرائیل هستید.
        سطح دشواری: {difficulty}
        """
        
        prompt = f"""
        یک مأموریت {mission_type} با سطح دشواری {difficulty} تولید کنید.
        پاسخ را به این فرمت JSON ارائه دهید:
        {{
            "title": "عنوان مأموریت",
            "description": "توضیح مأموریت",
            "objectives": ["هدف 1", "هدف 2", "هدف 3"],
            "reward": "پاداش مأموریت",
            "time_limit": "محدودیت زمانی (به دقیقه)",
            "requirements": "نیازمندی‌های مأموریت"
        }}
        """
        
        response = await self.generate_content(prompt, context)
        try:
            import json
            mission_data = json.loads(response)
            return mission_data
        except:
            return {
                "title": "مأموریت پیش‌فرض",
                "description": "یک مأموریت معمولی",
                "objectives": ["هدف 1", "هدف 2"],
                "reward": "100 شِکِل",
                "time_limit": "60 دقیقه",
                "requirements": "سطح شهروند"
            }