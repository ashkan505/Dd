"""
ماژول یکپارچه‌سازی هوش مصنوعی Google Gemini
Google Gemini AI Integration Module
"""

import google.generativeai as genai
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from config import config
import json
import random
import datetime

logger = logging.getLogger(__name__)

class GeminiAI:
    """کلاس اصلی یکپارچه‌سازی با Google Gemini AI"""
    
    def __init__(self):
        """راه‌اندازی کلاس Gemini AI"""
        try:
            # تنظیم کلید API
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # انتخاب مدل
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            # تنظیمات پیش‌فرض
            self.generation_config = genai.types.GenerationConfig(
                temperature=0.8,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,
            )
            
            # تنظیمات ایمنی
            self.safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            logger.info("Gemini AI initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini AI: {e}")
            raise
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """تولید پاسخ با استفاده از Gemini AI"""
        try:
            # ترکیب prompt و context
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # تنظیم مدل
            model = genai.GenerativeModel(
                model_name=config.GEMINI_MODEL,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # تولید پاسخ
            response = await asyncio.to_thread(
                model.generate_content,
                full_prompt
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "متأسفانه نتوانستم پاسخ مناسبی تولید کنم."
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"خطا در تولید پاسخ: {str(e)}"
    
    async def generate_news_event(self) -> Dict[str, Any]:
        """تولید رویداد خبری تصادفی"""
        try:
            prompt = """
            شما یک خبرنگار حرفه‌ای اسرائیلی هستید. یک رویداد خبری واقع‌گرایانه و جذاب برای سرور رول‌پلی اسرائیل تولید کنید.
            
            لطفاً یک رویداد با مشخصات زیر تولید کنید:
            - نوع رویداد: سیاسی، اقتصادی، نظامی، اجتماعی، فرهنگی، علمی، یا محیط زیستی
            - عنوان کوتاه و جذاب
            - توضیح کامل رویداد (حداقل 3 پاراگراف)
            - تأثیرات احتمالی بر جامعه
            - واکنش‌های مختلف مردم
            - جنبه‌های رول‌پلی برای کاربران
            
            پاسخ را به صورت JSON با کلیدهای زیر ارائه دهید:
            {
                "event_type": "نوع رویداد",
                "title": "عنوان رویداد",
                "description": "توضیح کامل",
                "effects": "تأثیرات",
                "public_reactions": "واکنش‌های مردم",
                "rp_elements": "جنبه‌های رول‌پلی",
                "severity": "شدت رویداد (low/medium/high)",
                "duration_hours": "مدت زمان تأثیر (ساعت)"
            }
            """
            
            response = await self.generate_response(prompt)
            
            # تلاش برای پارس کردن JSON
            try:
                # حذف کدهای markdown احتمالی
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1]
                
                event_data = json.loads(response.strip())
                return event_data
                
            except json.JSONDecodeError:
                # اگر JSON نبود، ساختار دستی ایجاد کنیم
                return {
                    "event_type": "اجتماعی",
                    "title": "رویداد پیش‌فرض",
                    "description": response,
                    "effects": "تأثیرات مختلف بر جامعه",
                    "public_reactions": "واکنش‌های متنوع مردم",
                    "rp_elements": "فرصت‌های رول‌پلی برای کاربران",
                    "severity": "medium",
                    "duration_hours": 24
                }
                
        except Exception as e:
            logger.error(f"Error generating news event: {e}")
            return self._generate_fallback_event()
    
    async def generate_law_proposal(self, proposer_name: str, law_type: str) -> Dict[str, Any]:
        """تولید پیشنهاد قانون"""
        try:
            prompt = f"""
            شما یک قانون‌گذار حرفه‌ای در کنست اسرائیل هستید. {proposer_name} می‌خواهد یک قانون {law_type} پیشنهاد دهد.
            
            لطفاً یک پیشنهاد قانون کامل و واقع‌گرایانه تولید کنید که شامل:
            - عنوان قانون
            - خلاصه اجرایی
            - مواد قانون (حداقل 5 ماده)
            - دلایل پیشنهاد
            - تأثیرات احتمالی
            - گروه‌های ذینفع و مخالف
            - هزینه‌های اجرایی
            - جدول زمانی اجرا
            
            پاسخ را به صورت JSON با کلیدهای زیر ارائه دهید:
            {{
                "law_title": "عنوان قانون",
                "summary": "خلاصه اجرایی",
                "articles": ["ماده 1", "ماده 2", ...],
                "rationale": "دلایل پیشنهاد",
                "effects": "تأثیرات احتمالی",
                "stakeholders": "گروه‌های ذینفع",
                "opponents": "گروه‌های مخالف",
                "implementation_cost": "هزینه اجرا",
                "timeline": "جدول زمانی اجرا",
                "controversy_level": "سطح مناقشه (low/medium/high)"
            }}
            """
            
            response = await self.generate_response(prompt)
            
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1]
                
                law_data = json.loads(response.strip())
                return law_data
                
            except json.JSONDecodeError:
                return self._generate_fallback_law(proposer_name, law_type)
                
        except Exception as e:
            logger.error(f"Error generating law proposal: {e}")
            return self._generate_fallback_law(proposer_name, law_type)
    
    async def generate_diplomatic_message(self, sender: str, receiver: str, message_type: str) -> Dict[str, Any]:
        """تولید پیام دیپلماتیک"""
        try:
            prompt = f"""
            شما یک دیپلمات حرفه‌ای اسرائیلی هستید. {sender} می‌خواهد پیام {message_type} به {receiver} ارسال کند.
            
            لطفاً یک پیام دیپلماتیک رسمی و حرفه‌ای تولید کنید که شامل:
            - عنوان رسمی
            - متن اصلی پیام
            - درخواست‌های مشخص
            - پیشنهادات همکاری
            - لحن مناسب (دوستانه، رسمی، یا تهدیدآمیز)
            - امضای رسمی
            
            پاسخ را به صورت JSON با کلیدهای زیر ارائه دهید:
            {{
                "title": "عنوان رسمی",
                "content": "متن اصلی پیام",
                "requests": ["درخواست 1", "درخواست 2", ...],
                "proposals": ["پیشنهاد 1", "پیشنهاد 2", ...],
                "tone": "لحن پیام",
                "signature": "امضای رسمی",
                "urgency": "سطح فوریت (low/medium/high)",
                "expected_response_time": "زمان انتظار پاسخ (ساعت)"
            }}
            """
            
            response = await self.generate_response(prompt)
            
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1]
                
                diplomatic_data = json.loads(response.strip())
                return diplomatic_data
                
            except json.JSONDecodeError:
                return self._generate_fallback_diplomatic_message(sender, receiver, message_type)
                
        except Exception as e:
            logger.error(f"Error generating diplomatic message: {e}")
            return self._generate_fallback_diplomatic_message(sender, receiver, message_type)
    
    async def generate_mission_briefing(self, mission_type: str, difficulty: str) -> Dict[str, Any]:
        """تولید خلاصه مأموریت"""
        try:
            prompt = f"""
            شما یک افسر ستاد ارتش اسرائیل هستید. یک مأموریت {mission_type} با سطح دشواری {difficulty} طراحی کنید.
            
            لطفاً یک خلاصه مأموریت کامل تولید کنید که شامل:
            - نام و کد مأموریت
            - اهداف اصلی و فرعی
            - موقعیت جغرافیایی
            - نیروهای مورد نیاز
            - تجهیزات مورد نیاز
            - مراحل اجرا
            - خطرات احتمالی
            - پاداش‌های موفقیت
            - محدودیت‌های زمانی
            
            پاسخ را به صورت JSON با کلیدهای زیر ارائه دهید:
            {{
                "mission_name": "نام مأموریت",
                "mission_code": "کد مأموریت",
                "objectives": {{"primary": "هدف اصلی", "secondary": ["هدف فرعی 1", "هدف فرعی 2"]}},
                "location": "موقعیت جغرافیایی",
                "required_forces": {{"air": 0, "ground": 0, "navy": 0, "intelligence": 0}},
                "required_equipment": ["تجهیزات 1", "تجهیزات 2", ...],
                "execution_steps": ["مرحله 1", "مرحله 2", ...],
                "risks": ["خطر 1", "خطر 2", ...],
                "rewards": {{"experience": 0, "money": 0, "items": ["آیتم 1", "آیتم 2"]}},
                "time_limit_hours": "محدودیت زمانی (ساعت)",
                "success_rate": "احتمال موفقیت (درصد)"
            }}
            """
            
            response = await self.generate_response(prompt)
            
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1]
                
                mission_data = json.loads(response.strip())
                return mission_data
                
            except json.JSONDecodeError:
                return self._generate_fallback_mission(mission_type, difficulty)
                
        except Exception as e:
            logger.error(f"Error generating mission briefing: {e}")
            return self._generate_fallback_mission(mission_type, difficulty)
    
    async def generate_crisis_scenario(self) -> Dict[str, Any]:
        """تولید سناریوی بحران"""
        try:
            prompt = """
            شما یک تحلیلگر امنیتی ارشد اسرائیلی هستید. یک سناریوی بحران واقع‌گرایانه و پیچیده برای سرور رول‌پلی تولید کنید.
            
            لطفاً یک بحران کامل تولید کنید که شامل:
            - نوع بحران (طبیعی، سیاسی، امنیتی، اقتصادی، اجتماعی)
            - علل و زمینه‌های بحران
            - تأثیرات فوری و بلندمدت
            - گروه‌های درگیر
            - راه‌حل‌های ممکن
            - چالش‌های اجرایی
            - فرصت‌های رول‌پلی
            
            پاسخ را به صورت JSON با کلیدهای زیر ارائه دهید:
            {
                "crisis_type": "نوع بحران",
                "crisis_name": "نام بحران",
                "causes": ["علت 1", "علت 2", ...],
                "immediate_effects": ["تأثیر فوری 1", "تأثیر فوری 2", ...],
                "long_term_effects": ["تأثیر بلندمدت 1", "تأثیر بلندمدت 2", ...],
                "involved_parties": ["گروه 1", "گروه 2", ...],
                "possible_solutions": ["راه‌حل 1", "راه‌حل 2", ...],
                "implementation_challenges": ["چالش 1", "چالش 2", ...],
                "rp_opportunities": ["فرصت رول‌پلی 1", "فرصت رول‌پلی 2", ...],
                "severity": "شدت بحران (low/medium/high/critical)",
                "duration_days": "مدت زمان بحران (روز)",
                "public_approval_impact": "تأثیر بر رضایت عمومی (عدد منفی)"
            }
            """
            
            response = await self.generate_response(prompt)
            
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1]
                
                crisis_data = json.loads(response.strip())
                return crisis_data
                
            except json.JSONDecodeError:
                return self._generate_fallback_crisis()
                
        except Exception as e:
            logger.error(f"Error generating crisis scenario: {e}")
            return self._generate_fallback_crisis()
    
    async def generate_character_personality(self, character_type: str, user_name: str) -> Dict[str, Any]:
        """تولید شخصیت برای ربات‌ها"""
        try:
            prompt = f"""
            شما یک نویسنده خلاق هستید. برای ربات {character_type} که در سرور رول‌پلی اسرائیل فعالیت می‌کند، شخصیت منحصربه‌فردی طراحی کنید.
            
            لطفاً شخصیتی تولید کنید که شامل:
            - نام و لقب
            - ویژگی‌های شخصیتی اصلی
            - لحن صحبت و سبک ارتباطی
            - علایق و تخصص‌ها
            - نقاط ضعف و محدودیت‌ها
            - روابط با دیگر ربات‌ها
            - جملات و اصطلاحات مخصوص
            - واکنش‌های عاطفی
            
            پاسخ را به صورت JSON با کلیدهای زیر ارائه دهید:
            {{
                "name": "نام ربات",
                "title": "لقب یا عنوان",
                "personality_traits": ["ویژگی 1", "ویژگی 2", ...],
                "speech_style": "سبک صحبت",
                "interests": ["علاقه 1", "علاقه 2", ...],
                "expertise": ["تخصص 1", "تخصص 2", ...],
                "weaknesses": ["نقطه ضعف 1", "نقطه ضعف 2", ...],
                "relationships": {{"ربات 1": "نوع رابطه", "ربات 2": "نوع رابطه"}},
                "catchphrases": ["جمله مخصوص 1", "جمله مخصوص 2", ...],
                "emotional_responses": {{"خوشحالی": "واکنش", "ناراحتی": "واکنش", "خشم": "واکنش"}},
                "motivation": "انگیزه اصلی",
                "background_story": "داستان پس‌زمینه"
            }}
            """
            
            response = await self.generate_response(prompt)
            
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1]
                
                personality_data = json.loads(response.strip())
                return personality_data
                
            except json.JSONDecodeError:
                return self._generate_fallback_personality(character_type, user_name)
                
        except Exception as e:
            logger.error(f"Error generating character personality: {e}")
            return self._generate_fallback_personality(character_type, user_name)
    
    async def generate_quiz_question(self, subject: str, difficulty: str) -> Dict[str, Any]:
        """تولید سوال کوئیز"""
        try:
            prompt = f"""
            شما یک معلم حرفه‌ای در زمینه {subject} هستید. یک سوال کوئیز با سطح دشواری {difficulty} تولید کنید.
            
            لطفاً یک سوال کامل تولید کنید که شامل:
            - متن سوال
            - گزینه‌های پاسخ (4 گزینه)
            - پاسخ صحیح
            - توضیح کامل پاسخ
            - نکات آموزشی مرتبط
            - سطح دشواری دقیق
            
            پاسخ را به صورت JSON با کلیدهای زیر ارائه دهید:
            {{
                "question": "متن سوال",
                "options": {{"A": "گزینه A", "B": "گزینه B", "C": "گزینه C", "D": "گزینه D"}},
                "correct_answer": "حرف گزینه صحیح",
                "explanation": "توضیح کامل پاسخ",
                "educational_notes": ["نکته 1", "نکته 2", ...],
                "difficulty_score": "امتیاز دشواری (1-10)",
                "subject_area": "زمینه موضوعی",
                "estimated_time": "زمان تخمینی پاسخ (دقیقه)"
            }}
            """
            
            response = await self.generate_response(prompt)
            
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1]
                
                quiz_data = json.loads(response.strip())
                return quiz_data
                
            except json.JSONDecodeError:
                return self._generate_fallback_quiz(subject, difficulty)
                
        except Exception as e:
            logger.error(f"Error generating quiz question: {e}")
            return self._generate_fallback_quiz(subject, difficulty)
    
    def _generate_fallback_event(self) -> Dict[str, Any]:
        """تولید رویداد پیش‌فرض در صورت خطا"""
        events = [
            {
                "event_type": "اجتماعی",
                "title": "جشنواره فرهنگ‌های مختلف در تل‌آویو",
                "description": "جشنواره سالانه فرهنگ‌های مختلف در مرکز تل‌آویو برگزار شد. این رویداد که با حضور هزاران نفر همراه بود، تنوع فرهنگی اسرائیل را به نمایش گذاشت.",
                "effects": "افزایش رضایت عمومی و تقویت روابط بین فرهنگی",
                "public_reactions": "واکنش مثبت اکثریت مردم",
                "rp_elements": "فرصت برای کاربران برای شرکت در جشنواره و کسب تجربه",
                "severity": "low",
                "duration_hours": 24
            },
            {
                "event_type": "اقتصادی",
                "title": "رونق بازار بورس تل‌آویو",
                "description": "شاخص بورس تل‌آویو با رشد قابل توجهی مواجه شد. این رشد که ناشی از بهبود روابط تجاری و سرمایه‌گذاری‌های جدید است، امیدواری سرمایه‌گذاران را افزایش داده است.",
                "effects": "افزایش سرمایه‌گذاری و بهبود وضعیت اقتصادی",
                "public_reactions": "خوشحالی سرمایه‌گذاران و نگرانی از حباب احتمالی",
                "rp_elements": "فرصت برای کاربران برای سرمایه‌گذاری و کسب سود",
                "severity": "medium",
                "duration_hours": 48
            }
        ]
        return random.choice(events)
    
    def _generate_fallback_law(self, proposer_name: str, law_type: str) -> Dict[str, Any]:
        """تولید قانون پیش‌فرض در صورت خطا"""
        return {
            "law_title": f"قانون {law_type} پیشنهادی توسط {proposer_name}",
            "summary": f"این قانون به منظور بهبود وضعیت {law_type} در کشور پیشنهاد شده است.",
            "articles": [
                "ماده 1: تعاریف و مفاهیم",
                "ماده 2: اهداف و مقاصد",
                "ماده 3: مسئولیت‌ها و وظایف",
                "ماده 4: نظارت و کنترل",
                "ماده 5: ضمانت‌های اجرایی"
            ],
            "rationale": "نیاز به بهبود وضعیت موجود و ارتقای کیفیت خدمات",
            "effects": "بهبود کیفیت زندگی شهروندان و افزایش کارایی سیستم",
            "stakeholders": "شهروندان، دولت، بخش خصوصی",
            "opponents": "گروه‌های ذینفع در وضعیت موجود",
            "implementation_cost": 100000,
            "timeline": "6 ماه",
            "controversy_level": "medium"
        }
    
    def _generate_fallback_diplomatic_message(self, sender: str, receiver: str, message_type: str) -> Dict[str, Any]:
        """تولید پیام دیپلماتیک پیش‌فرض در صورت خطا"""
        return {
            "title": f"پیام {message_type} از {sender} به {receiver}",
            "content": f"با سلام و احترام، {sender} پیام {message_type} خود را به {receiver} ارسال می‌کند.",
            "requests": ["برقراری روابط دوستانه", "همکاری در زمینه‌های مشترک"],
            "proposals": ["انعقاد پیمان همکاری", "تبادل تجربیات"],
            "tone": "دوستانه و رسمی",
            "signature": f"با احترام، {sender}",
            "urgency": "medium",
            "expected_response_time": 48
        }
    
    def _generate_fallback_mission(self, mission_type: str, difficulty: str) -> Dict[str, Any]:
        """تولید مأموریت پیش‌فرض در صورت خطا"""
        return {
            "mission_name": f"مأموریت {mission_type}",
            "mission_code": f"{mission_type.upper()}-{random.randint(1000, 9999)}",
            "objectives": {
                "primary": f"تکمیل موفقیت‌آمیز مأموریت {mission_type}",
                "secondary": ["جمع‌آوری اطلاعات", "تأمین امنیت منطقه"]
            },
            "location": "منطقه عملیاتی مشخص نشده",
            "required_forces": {"air": 2, "ground": 5, "navy": 1, "intelligence": 2},
            "required_equipment": ["تجهیزات ارتباطی", "وسایل حفاظتی"],
            "execution_steps": ["آماده‌سازی", "اجرا", "تکمیل"],
            "risks": ["مقاومت دشمن", "شرایط آب و هوایی"],
            "rewards": {"experience": 500, "money": 1000, "items": ["مدال افتخار"]},
            "time_limit_hours": 12,
            "success_rate": 75
        }
    
    def _generate_fallback_crisis(self) -> Dict[str, Any]:
        """تولید بحران پیش‌فرض در صورت خطا"""
        crises = [
            {
                "crisis_type": "طبیعی",
                "crisis_name": "زلزله متوسط در شمال کشور",
                "causes": ["فعالیت تکتونیکی طبیعی"],
                "immediate_effects": ["آسیب به ساختمان‌ها", "قطع برق در برخی مناطق"],
                "long_term_effects": ["نیاز به بازسازی", "تغییر در برنامه‌های عمرانی"],
                "involved_parties": ["سازمان امداد", "دولت محلی", "سازمان‌های مردمی"],
                "possible_solutions": ["ارسال کمک‌های اضطراری", "برنامه بازسازی"],
                "implementation_challenges": ["محدودیت منابع", "هماهنگی بین سازمانی"],
                "rp_opportunities": ["مشارکت در امدادرسانی", "کمک به بازسازی"],
                "severity": "medium",
                "duration_days": 7,
                "public_approval_impact": -10
            }
        ]
        return random.choice(crises)
    
    def _generate_fallback_personality(self, character_type: str, user_name: str) -> Dict[str, Any]:
        """تولید شخصیت پیش‌فرض در صورت خطا"""
        return {
            "name": f"{character_type}",
            "title": "ربات هوشمند",
            "personality_traits": ["دقیق", "مفید", "دوستانه"],
            "speech_style": "رسمی و محترمانه",
            "interests": ["کمک به کاربران", "بهبود سیستم"],
            "expertise": ["مدیریت اطلاعات", "پاسخگویی"],
            "weaknesses": ["محدودیت در خلاقیت", "وابستگی به داده‌ها"],
            "relationships": {"دیگر ربات‌ها": "همکاری"},
            "catchphrases": ["چطور می‌تونم کمکتون کنم؟", "در خدمت شما هستم"],
            "emotional_responses": {
                "خوشحالی": "خوشحالم که تونستم کمکتون کنم",
                "ناراحتی": "متأسفم که نتوانستم کمک کافی کنم",
                "خشم": "لطفاً آرام باشید تا بتونم کمکتون کنم"
            },
            "motivation": "کمک به کاربران و بهبود تجربه آنها",
            "background_story": "ربات هوشمندی که برای خدمت به کاربران طراحی شده است"
        }
    
    def _generate_fallback_quiz(self, subject: str, difficulty: str) -> Dict[str, Any]:
        """تولید کوئیز پیش‌فرض در صورت خطا"""
        return {
            "question": f"سوال نمونه در زمینه {subject}",
            "options": {
                "A": "گزینه اول",
                "B": "گزینه دوم", 
                "C": "گزینه سوم",
                "D": "گزینه چهارم"
            },
            "correct_answer": "A",
            "explanation": "توضیح کامل پاسخ صحیح",
            "educational_notes": ["نکته آموزشی مهم", "مفهوم کلیدی"],
            "difficulty_score": 5,
            "subject_area": subject,
            "estimated_time": 2
        }
    
    async def test_connection(self) -> bool:
        """تست اتصال به Gemini AI"""
        try:
            test_prompt = "سلام، لطفاً پاسخ کوتاهی بدهید."
            response = await self.generate_response(test_prompt)
            return len(response) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# Global Gemini AI instance
gemini_ai = GeminiAI()

# Export
__all__ = ['GeminiAI', 'gemini_ai']