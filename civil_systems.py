#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سیستم‌های مدنی و اجتماعی اسرائیل
Civil and Social Systems for Israeli RP Server

این فایل شامل پیاده‌سازی سیستم‌های مدنی و اجتماعی است:
- سیستم مشاغل و آموزش عالی
- سیستم املاک و مستغلات  
- سیستم احزاب سیاسی
- سیستم قضایی
- رویدادهای فرهنگی و ملی
- سیستم پیشرفت فردی
- رادیو اسرائیل

تاریخ: ۲۵ آگوست ۲۰۲۵
نسخه: 1.0.0
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import random
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Tuple
import logging

# وارد کردن ماژول‌های مشترک
from config import *
from utils import *

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================= ربات سیستم مشاغل و آموزش =======================

class JobsAndEducationBot(commands.Bot):
    """
    ربات مشاغل و آموزش عالی
    مسئول مدیریت مشاغل مدنی، دانشگاه‌ها و سیستم آموزشی
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!شغل_',
            intents=intents,
            help_command=None,
            description="سیستم مشاغل و آموزش عالی اسرائیل"
        )
        
        self.db = DatabaseManager()
        
        # لیست مشاغل موجود
        self.available_jobs = {
            'پزشک': {
                'salary': 3000,
                'requirements': ['پزشکی'],
                'description': 'درمان بیماران و مراقبت از سلامت شهروندان',
                'channels': ['بیمارستان', 'اورژانس'],
                'max_positions': 10
            },
            'مهندس': {
                'salary': 2800,
                'requirements': ['مهندسی'],
                'description': 'طراحی و ساخت زیرساخت‌های شهری',
                'channels': ['مهندسی', 'پروژه‌ها'],
                'max_positions': 15
            },
            'دانشمند': {
                'salary': 3500,
                'requirements': ['علوم', 'فیزیک'],
                'description': 'تحقیق و توسعه فناوری‌های نوین',
                'channels': ['آزمایشگاه', 'تحقیقات'],
                'max_positions': 8
            },
            'معلم': {
                'salary': 2200,
                'requirements': ['آموزش'],
                'description': 'آموزش نسل آینده اسرائیل',
                'channels': ['مدرسه', 'کلاس‌ها'],
                'max_positions': 20
            },
            'روزنامه‌نگار': {
                'salary': 2000,
                'requirements': ['ارتباطات'],
                'description': 'گزارش اخبار و رویدادهای مهم',
                'channels': ['رسانه', 'خبرگزاری'],
                'max_positions': 12
            },
            'وکیل': {
                'salary': 2700,
                'requirements': ['حقوق'],
                'description': 'دفاع از حقوق شهروندان در دادگاه',
                'channels': ['دادگاه', 'دفتر-وکلا'],
                'max_positions': 10
            },
            'بازرگان': {
                'salary': 2500,
                'requirements': ['اقتصاد'],
                'description': 'مدیریت کسب و کار و تجارت',
                'channels': ['بازار', 'تجارت'],
                'max_positions': 25
            },
            'هنرمند': {
                'salary': 1800,
                'requirements': ['هنر'],
                'description': 'خلق آثار هنری و فرهنگی',
                'channels': ['گالری', 'استودیو'],
                'max_positions': 15
            }
        }
        
        # رشته‌های دانشگاهی
        self.university_majors = {
            'پزشکی': {
                'duration': 6,  # سمستر
                'difficulty': 'سخت',
                'description': 'آموزش علوم پزشکی و درمان',
                'career_paths': ['پزشک', 'پرستار']
            },
            'مهندسی': {
                'duration': 4,
                'difficulty': 'متوسط',
                'description': 'آموزش علوم فنی و مهندسی',
                'career_paths': ['مهندس', 'معمار']
            },
            'علوم': {
                'duration': 4,
                'difficulty': 'سخت',
                'description': 'تحقیق در علوم طبیعی',
                'career_paths': ['دانشمند', 'محقق']
            },
            'حقوق': {
                'duration': 4,
                'difficulty': 'متوسط',
                'description': 'آموزش قوانین و حقوق',
                'career_paths': ['وکیل', 'قاضی']
            },
            'اقتصاد': {
                'duration': 4,
                'difficulty': 'متوسط',
                'description': 'آموزش اصول اقتصادی و مالی',
                'career_paths': ['بازرگان', 'تحلیلگر مالی']
            },
            'آموزش': {
                'duration': 4,
                'difficulty': 'آسان',
                'description': 'آموزش روش‌های تدریس',
                'career_paths': ['معلم', 'مدیر مدرسه']
            },
            'ارتباطات': {
                'duration': 3,
                'difficulty': 'آسان',
                'description': 'آموزش رسانه و ارتباطات',
                'career_paths': ['روزنامه‌نگار', 'مجری']
            },
            'هنر': {
                'duration': 4,
                'difficulty': 'متوسط',
                'description': 'آموزش هنرهای تجسمی و نمایشی',
                'career_paths': ['هنرمند', 'طراح']
            }
        }
        
        # آمار اشتغال
        self.employment_stats = {}
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - سیستم مشاغل و آموزش آماده است!')
        
        if not self.weekly_quiz.is_running():
            self.weekly_quiz.start()
        if not self.job_market_update.is_running():
            self.job_market_update.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="بازار کار اسرائیل 💼"
            )
        )

    @commands.command(name='لیست_مشاغل')
    async def list_jobs(self, ctx):
        """نمایش لیست مشاغل موجود"""
        embed = create_embed(
            "💼 مشاغل موجود در اسرائیل",
            "لیست مشاغل قابل درخواست:",
            EMBED_COLORS['primary']
        )
        
        for job_name, job_info in self.available_jobs.items():
            # بررسی ظرفیت
            current_workers = len([user for user in self.db.users.values() 
                                 if user.get('job') == job_name])
            capacity_status = f"({current_workers}/{job_info['max_positions']})"
            
            # وضعیت استخدام
            if current_workers >= job_info['max_positions']:
                status = "🔴 تکمیل"
            elif current_workers >= job_info['max_positions'] * 0.8:
                status = "🟡 محدود"
            else:
                status = "🟢 آزاد"
            
            embed.add_field(
                name=f"{job_name} {status}",
                value=f"**حقوق:** {job_info['salary']:,} شکل/روز\n"
                      f"**نیازمندی:** {', '.join(job_info['requirements'])}\n"
                      f"**ظرفیت:** {capacity_status}\n"
                      f"**توضیحات:** {job_info['description']}",
                inline=True
            )
        
        embed.set_footer(text="برای درخواست شغل: !شغل_درخواست [نام شغل]")
        await ctx.send(embed=embed)

    @commands.command(name='درخواست')
    async def apply_job(self, ctx, *, job_name: str):
        """درخواست شغل"""
        user_id = str(ctx.author.id)
        
        # بررسی وجود شغل
        if job_name not in self.available_jobs:
            embed = create_embed(
                "خطا ❌",
                f"شغل '{job_name}' یافت نشد!\nبرای مشاهده لیست: `!شغل_لیست_مشاغل`",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        job_info = self.available_jobs[job_name]
        
        # بررسی شغل فعلی
        current_job = self.db.get_user_data(user_id, 'job')
        if current_job:
            embed = create_embed(
                "خطا ❌",
                f"شما در حال حاضر شغل '{current_job}' دارید!\n"
                "ابتدا با `!شغل_استعفا` از شغل فعلی استعفا دهید.",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی ظرفیت
        current_workers = len([user for user in self.db.users.values() 
                             if user.get('job') == job_name])
        if current_workers >= job_info['max_positions']:
            embed = create_embed(
                "ظرفیت تکمیل ❌",
                f"متأسفانه ظرفیت شغل '{job_name}' تکمیل است!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی مدارک تحصیلی
        user_education = self.db.get_user_data(user_id, 'education') or []
        has_required_education = any(req in user_education for req in job_info['requirements'])
        
        if not has_required_education:
            embed = create_embed(
                "مدرک ناکافی ❌",
                f"برای شغل '{job_name}' نیاز به یکی از این مدارک دارید:\n"
                f"{', '.join(job_info['requirements'])}\n\n"
                "ابتدا در دانشگاه ثبت‌نام کنید: `!شغل_ثبت‌نام_دانشگاه`",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # تصویب درخواست
        self.db.set_user_data(user_id, 'job', job_name)
        self.db.set_user_data(user_id, 'job_start_date', datetime.now().isoformat())
        
        # اضافه کردن رول شغلی
        guild = ctx.guild
        job_role = await get_or_create_role(guild, job_name, color=discord.Color.blue())
        await ctx.author.add_roles(job_role)
        
        # دسترسی به کانال‌های شغلی
        for channel_name in job_info['channels']:
            channel = await get_or_create_channel(guild, channel_name, overwrites={
                job_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            })
        
        embed = create_embed(
            "استخدام موفق ✅",
            f"**شغل:** {job_name}\n"
            f"**حقوق روزانه:** {job_info['salary']:,} شکل\n"
            f"**تاریخ شروع:** {datetime.now().strftime('%Y/%m/%d')}\n"
            f"**دسترسی‌های جدید:** {', '.join(job_info['channels'])}\n\n"
            f"🎉 تبریک! شما اکنون {job_name} هستید!",
            EMBED_COLORS['success']
        )
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='استعفا')
    async def resign_job(self, ctx):
        """استعفا از شغل فعلی"""
        user_id = str(ctx.author.id)
        current_job = self.db.get_user_data(user_id, 'job')
        
        if not current_job:
            embed = create_embed(
                "خطا ❌",
                "شما هیچ شغلی ندارید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # حذف اطلاعات شغل
        self.db.set_user_data(user_id, 'job', None)
        self.db.set_user_data(user_id, 'job_start_date', None)
        
        # حذف رول شغلی
        guild = ctx.guild
        job_role = discord.utils.get(guild.roles, name=current_job)
        if job_role and job_role in ctx.author.roles:
            await ctx.author.remove_roles(job_role)
        
        embed = create_embed(
            "استعفا ثبت شد ✅",
            f"شما از شغل '{current_job}' استعفا دادید.\n"
            "می‌توانید برای شغل جدید درخواست دهید.",
            EMBED_COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name='ثبت‌نام_دانشگاه')
    async def university_enrollment(self, ctx, *, major: str):
        """ثبت‌نام در دانشگاه"""
        user_id = str(ctx.author.id)
        
        if major not in self.university_majors:
            embed = create_embed(
                "خطا ❌",
                f"رشته '{major}' یافت نشد!\nرشته‌های موجود:\n" + 
                "\n".join(self.university_majors.keys()),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی تحصیل فعلی
        current_studies = self.db.get_user_data(user_id, 'current_studies')
        if current_studies:
            embed = create_embed(
                "خطا ❌",
                f"شما در حال حاضر در رشته '{current_studies['major']}' تحصیل می‌کنید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        major_info = self.university_majors[major]
        
        # ثبت‌نام
        studies_data = {
            'major': major,
            'semester': 1,
            'total_semesters': major_info['duration'],
            'gpa': 0,
            'start_date': datetime.now().isoformat(),
            'completed_quizzes': 0
        }
        
        self.db.set_user_data(user_id, 'current_studies', studies_data)
        
        # اضافه کردن رول دانشجو
        guild = ctx.guild
        student_role = await get_or_create_role(guild, 'دانشجو', color=discord.Color.green())
        await ctx.author.add_roles(student_role)
        
        embed = create_embed(
            "ثبت‌نام موفق ✅",
            f"**رشته:** {major}\n"
            f"**مدت تحصیل:** {major_info['duration']} سمستر\n"
            f"**سطح دشواری:** {major_info['difficulty']}\n"
            f"**توضیحات:** {major_info['description']}\n\n"
            "هر هفته کوئیز دریافت خواهید کرد!",
            EMBED_COLORS['success']
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830284.png")
        await ctx.send(embed=embed)

    @commands.command(name='وضعیت_تحصیل')
    async def education_status(self, ctx, member: discord.Member = None):
        """نمایش وضعیت تحصیلی"""
        if member is None:
            member = ctx.author
            
        user_id = str(member.id)
        current_studies = self.db.get_user_data(user_id, 'current_studies')
        completed_education = self.db.get_user_data(user_id, 'education') or []
        
        embed = create_embed(
            f"🎓 وضعیت تحصیلی {member.display_name}",
            "",
            EMBED_COLORS['primary']
        )
        
        if current_studies:
            progress = (current_studies['semester'] / current_studies['total_semesters']) * 100
            
            embed.add_field(
                name="تحصیل فعلی",
                value=f"**رشته:** {current_studies['major']}\n"
                      f"**سمستر:** {current_studies['semester']}/{current_studies['total_semesters']}\n"
                      f"**پیشرفت:** {progress:.1f}%\n"
                      f"**معدل:** {current_studies['gpa']:.2f}\n"
                      f"**کوئیزهای تکمیل شده:** {current_studies['completed_quizzes']}",
                inline=False
            )
        else:
            embed.add_field(
                name="تحصیل فعلی",
                value="در حال حاضر در دانشگاه تحصیل نمی‌کند",
                inline=False
            )
        
        if completed_education:
            embed.add_field(
                name="مدارک تحصیلی",
                value="\n".join([f"• {degree}" for degree in completed_education]),
                inline=False
            )
        
        await ctx.send(embed=embed)

    @tasks.loop(hours=168)  # هفتگی
    async def weekly_quiz(self):
        """ارسال کوئیز هفتگی برای دانشجویان"""
        try:
            guild = self.get_guild(GUILD_ID)
            if not guild:
                return
            
            for user_id, user_data in self.db.users.items():
                current_studies = user_data.get('current_studies')
                if not current_studies:
                    continue
                
                try:
                    member = guild.get_member(int(user_id))
                    if not member:
                        continue
                    
                    major = current_studies['major']
                    
                    # تولید سوال با Gemini AI
                    quiz_prompt = f"""
                    یک سوال چهارگزینه‌ای برای رشته {major} بساز.
                    سطح سوال متناسب با سمستر {current_studies['semester']} باشد.
                    
                    فرمت پاسخ:
                    سوال: [متن سوال]
                    الف) [گزینه 1]
                    ب) [گزینه 2]  
                    ج) [گزینه 3]
                    د) [گزینه 4]
                    پاسخ صحیح: [حرف گزینه صحیح]
                    """
                    
                    quiz_content = await generate_text_with_gemini(quiz_prompt)
                    
                    embed = create_embed(
                        f"📝 کوئیز هفتگی - {major}",
                        quiz_content,
                        EMBED_COLORS['primary']
                    )
                    embed.set_footer(text="برای پاسخ دادن از ایموجی‌های 🇦 🇧 🇨 🇩 استفاده کنید")
                    
                    # ارسال پیام خصوصی
                    quiz_msg = await member.send(embed=embed)
                    
                    # اضافه کردن ری‌اکشن‌ها
                    reactions = ['🇦', '🇧', '🇨', '🇩']
                    for reaction in reactions:
                        await quiz_msg.add_reaction(reaction)
                    
                except Exception as e:
                    logger.error(f"خطا در ارسال کوئیز به {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"خطا در کوئیز هفتگی: {e}")

    @tasks.loop(hours=24)
    async def job_market_update(self):
        """به‌روزرسانی بازار کار"""
        try:
            # محاسبه آمار اشتغال
            total_workers = 0
            job_distribution = {}
            
            for user_data in self.db.users.values():
                job = user_data.get('job')
                if job:
                    total_workers += 1
                    job_distribution[job] = job_distribution.get(job, 0) + 1
            
            self.employment_stats = {
                'total_workers': total_workers,
                'job_distribution': job_distribution,
                'unemployment_rate': 0  # محاسبه بر اساس کل جمعیت
            }
            
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی بازار کار: {e}")

# ======================= ربات املاک و مستغلات =======================

class RealEstateBot(commands.Bot):
    """
    ربات املاک و مستغلات
    مسئول مدیریت خرید و فروش املاک، اجاره و مدیریت ملک‌ها
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!ملک_',
            intents=intents,
            help_command=None,
            description="سیستم املاک و مستغلات اسرائیل"
        )
        
        self.db = DatabaseManager()
        
        # انواع املاک
        self.property_types = {
            'آپارتمان_کوچک': {
                'price': 500000,
                'monthly_cost': 2000,
                'description': 'آپارتمان یک خوابه مناسب برای مجردها',
                'capacity': 2
            },
            'آپارتمان_متوسط': {
                'price': 800000,
                'monthly_cost': 3500,
                'description': 'آپارتمان دو خوابه مناسب برای خانواده کوچک',
                'capacity': 4
            },
            'آپارتمان_بزرگ': {
                'price': 1200000,
                'monthly_cost': 5000,
                'description': 'آپارتمان سه خوابه مناسب برای خانواده بزرگ',
                'capacity': 6
            },
            'ویلا': {
                'price': 2500000,
                'monthly_cost': 8000,
                'description': 'ویلا مجلل با حیاط و استخر',
                'capacity': 10
            },
            'دفتر_کار': {
                'price': 600000,
                'monthly_cost': 4000,
                'description': 'فضای اداری برای کسب و کار',
                'capacity': 8
            },
            'مغازه': {
                'price': 400000,
                'monthly_cost': 3000,
                'description': 'مغازه تجاری در مرکز شهر',
                'capacity': 5
            }
        }
        
        # شهرهای موجود
        self.cities = {
            'تل‌آویو': {'multiplier': 1.5, 'description': 'پایتخت اقتصادی'},
            'اورشلیم': {'multiplier': 1.3, 'description': 'پایتخت سیاسی'},
            'حیفا': {'multiplier': 1.1, 'description': 'شهر صنعتی'},
            'بئرشبع': {'multiplier': 0.8, 'description': 'شهر جنوبی'},
            'نتانیا': {'multiplier': 1.0, 'description': 'شهر ساحلی'}
        }
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - سیستم املاک و مستغلات آماده است!')
        
        if not self.monthly_costs.is_running():
            self.monthly_costs.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="بازار املاک 🏠"
            )
        )

    @commands.command(name='بازار')
    async def property_market(self, ctx):
        """نمایش بازار املاک"""
        embed = create_embed(
            "🏠 بازار املاک اسرائیل",
            "انواع املاک موجود برای خرید:",
            EMBED_COLORS['primary']
        )
        
        for prop_type, prop_info in self.property_types.items():
            embed.add_field(
                name=prop_type.replace('_', ' '),
                value=f"**قیمت:** {prop_info['price']:,} شکل\n"
                      f"**هزینه ماهانه:** {prop_info['monthly_cost']:,} شکل\n"
                      f"**ظرفیت:** {prop_info['capacity']} نفر\n"
                      f"**توضیحات:** {prop_info['description']}",
                inline=True
            )
        
        embed.add_field(
            name="🌆 شهرهای موجود",
            value="\n".join([f"• {city}: ضریب {info['multiplier']}x ({info['description']})" 
                           for city, info in self.cities.items()]),
            inline=False
        )
        
        embed.set_footer(text="برای خرید: !ملک_خرید [نوع ملک] [شهر]")
        await ctx.send(embed=embed)

    @commands.command(name='خرید')
    async def buy_property(self, ctx, property_type: str, city: str):
        """خرید ملک"""
        user_id = str(ctx.author.id)
        
        # تبدیل نام ملک
        property_type = property_type.replace(' ', '_')
        
        if property_type not in self.property_types:
            embed = create_embed(
                "خطا ❌",
                f"نوع ملک '{property_type}' یافت نشد!\nبرای مشاهده لیست: `!ملک_بازار`",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if city not in self.cities:
            embed = create_embed(
                "خطا ❌",
                f"شهر '{city}' یافت نشد!\nشهرهای موجود: {', '.join(self.cities.keys())}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # محاسبه قیمت نهایی
        base_price = self.property_types[property_type]['price']
        city_multiplier = self.cities[city]['multiplier']
        final_price = int(base_price * city_multiplier)
        
        # بررسی املاک فعلی کاربر
        user_properties = self.db.get_user_data(user_id, 'properties') or []
        
        # محدودیت تعداد املاک (حداکثر 3 ملک)
        if len(user_properties) >= 3:
            embed = create_embed(
                "محدودیت املاک ❌",
                "شما نمی‌توانید بیش از 3 ملک داشته باشید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # شبیه‌سازی پرداخت (باید با ربات بانک ارتباط برقرار کنیم)
        
        # ایجاد کانال خصوصی
        guild = ctx.guild
        property_name = f"{property_type.replace('_', '-')}-{ctx.author.display_name}-{city}"
        
        # تنظیم دسترسی‌ها
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(
                read_messages=True, 
                send_messages=True, 
                manage_messages=True,
                manage_channels=True
            )
        }
        
        # ایجاد کتگوری املاک
        properties_category = await get_or_create_category(guild, "املاک شخصی")
        
        # ایجاد کانال متنی
        text_channel = await guild.create_text_channel(
            property_name,
            category=properties_category,
            overwrites=overwrites
        )
        
        # ایجاد کانال صوتی
        voice_channel = await guild.create_voice_channel(
            f"🏠 {property_name}",
            category=properties_category,
            overwrites=overwrites
        )
        
        # ثبت ملک در دیتابیس
        property_data = {
            'type': property_type,
            'city': city,
            'price': final_price,
            'monthly_cost': int(self.property_types[property_type]['monthly_cost'] * city_multiplier),
            'purchase_date': datetime.now().isoformat(),
            'text_channel_id': text_channel.id,
            'voice_channel_id': voice_channel.id,
            'residents': [user_id],
            'rent_income': 0
        }
        
        user_properties.append(property_data)
        self.db.set_user_data(user_id, 'properties', user_properties)
        
        embed = create_embed(
            "خرید ملک موفق ✅",
            f"**نوع ملک:** {property_type.replace('_', ' ')}\n"
            f"**شهر:** {city}\n"
            f"**قیمت نهایی:** {final_price:,} شکل\n"
            f"**هزینه ماهانه:** {property_data['monthly_cost']:,} شکل\n"
            f"**کانال متنی:** {text_channel.mention}\n"
            f"**کانال صوتی:** {voice_channel.mention}",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"تاریخ خرید: {datetime.now().strftime('%Y/%m/%d')}")
        await ctx.send(embed=embed)
        
        # پیام خوش‌آمدگویی در کانال جدید
        welcome_embed = create_embed(
            f"🏠 خوش آمدید به {property_type.replace('_', ' ')} شما!",
            f"**مالک:** {ctx.author.mention}\n"
            f"**آدرس:** {city}, اسرائیل\n"
            f"**ظرفیت:** {self.property_types[property_type]['capacity']} نفر\n\n"
            "می‌توانید دوستان خود را به اینجا دعوت کنید!",
            EMBED_COLORS['primary']
        )
        await text_channel.send(embed=welcome_embed)

    @commands.command(name='املاک_من')
    async def my_properties(self, ctx):
        """نمایش املاک کاربر"""
        user_id = str(ctx.author.id)
        user_properties = self.db.get_user_data(user_id, 'properties') or []
        
        if not user_properties:
            embed = create_embed(
                "املاک خالی",
                "شما هیچ ملکی ندارید!\nبرای خرید: `!ملک_بازار`",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            f"🏠 املاک {ctx.author.display_name}",
            f"تعداد املاک: {len(user_properties)}",
            EMBED_COLORS['primary']
        )
        
        total_value = 0
        total_monthly_cost = 0
        
        for i, prop in enumerate(user_properties, 1):
            total_value += prop['price']
            total_monthly_cost += prop['monthly_cost']
            
            text_channel = ctx.guild.get_channel(prop['text_channel_id'])
            voice_channel = ctx.guild.get_channel(prop['voice_channel_id'])
            
            embed.add_field(
                name=f"{i}. {prop['type'].replace('_', ' ')} - {prop['city']}",
                value=f"**ارزش:** {prop['price']:,} شکل\n"
                      f"**هزینه ماهانه:** {prop['monthly_cost']:,} شکل\n"
                      f"**ساکنین:** {len(prop['residents'])} نفر\n"
                      f"**کانال:** {text_channel.mention if text_channel else 'حذف شده'}",
                inline=True
            )
        
        embed.add_field(
            name="📊 خلاصه مالی",
            value=f"**کل ارزش املاک:** {total_value:,} شکل\n"
                  f"**هزینه‌های ماهانه:** {total_monthly_cost:,} شکل",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='دعوت')
    async def invite_to_property(self, ctx, member: discord.Member, property_index: int = 1):
        """دعوت کاربر به ملک"""
        user_id = str(ctx.author.id)
        user_properties = self.db.get_user_data(user_id, 'properties') or []
        
        if not user_properties or property_index > len(user_properties):
            embed = create_embed(
                "خطا ❌",
                "ملک مورد نظر یافت نشد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        prop = user_properties[property_index - 1]
        
        # بررسی ظرفیت
        max_capacity = self.property_types[prop['type']]['capacity']
        if len(prop['residents']) >= max_capacity:
            embed = create_embed(
                "ظرفیت تکمیل ❌",
                f"این ملک ظرفیت حداکثر {max_capacity} نفر را دارد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # اضافه کردن دسترسی
        text_channel = ctx.guild.get_channel(prop['text_channel_id'])
        voice_channel = ctx.guild.get_channel(prop['voice_channel_id'])
        
        if text_channel:
            await text_channel.set_permissions(
                member, 
                read_messages=True, 
                send_messages=True
            )
        
        if voice_channel:
            await voice_channel.set_permissions(
                member,
                view_channel=True,
                connect=True,
                speak=True
            )
        
        # اضافه کردن به لیست ساکنین
        prop['residents'].append(str(member.id))
        self.db.set_user_data(user_id, 'properties', user_properties)
        
        embed = create_embed(
            "دعوت موفق ✅",
            f"{member.mention} به ملک شما در {prop['city']} دعوت شد!",
            EMBED_COLORS['success']
        )
        await ctx.send(embed=embed)
        
        # اطلاع به مدعو
        if text_channel:
            welcome_msg = create_embed(
                "🎉 دعوت جدید!",
                f"{member.mention} توسط {ctx.author.mention} به این ملک دعوت شد!",
                EMBED_COLORS['primary']
            )
            await text_channel.send(embed=welcome_msg)

    @tasks.loop(hours=24 * 30)  # ماهانه
    async def monthly_costs(self):
        """کسر هزینه‌های ماهانه املاک"""
        try:
            for user_id, user_data in self.db.users.items():
                user_properties = user_data.get('properties', [])
                if not user_properties:
                    continue
                
                total_monthly_cost = sum([prop['monthly_cost'] for prop in user_properties])
                
                # کسر از حساب بانکی (باید با ربات بانک ارتباط برقرار کنیم)
                # در اینجا فقط لاگ می‌کنیم
                logger.info(f"هزینه ماهانه کاربر {user_id}: {total_monthly_cost:,} شکل")
                
        except Exception as e:
            logger.error(f"خطا در کسر هزینه‌های ماهانه: {e}")

# ======================= ربات احزاب سیاسی =======================

class PoliticalPartiesBot(commands.Bot):
    """
    ربات احزاب سیاسی
    مسئول مدیریت احزاب، انتخابات و فعالیت‌های سیاسی
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!حزب_',
            intents=intents,
            help_command=None,
            description="سیستم احزاب سیاسی اسرائیل"
        )
        
        self.db = DatabaseManager()
        
        # احزاب موجود
        self.parties = {}
        
        # انتخابات فعلی
        self.current_election = None
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - سیستم احزاب سیاسی آماده است!')
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="سیاست اسرائیل 🗳️"
            )
        )

    @commands.command(name='تأسیس')
    async def create_party(self, ctx, *, party_name: str):
        """تأسیس حزب جدید"""
        user_id = str(ctx.author.id)
        
        # بررسی وجود حزب با همین نام
        if party_name in self.parties:
            embed = create_embed(
                "خطا ❌",
                f"حزب '{party_name}' قبلاً وجود دارد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی عضویت در حزب دیگر
        user_party = self.db.get_user_data(user_id, 'political_party')
        if user_party:
            embed = create_embed(
                "خطا ❌",
                f"شما عضو حزب '{user_party}' هستید!\nابتدا از حزب خارج شوید: `!حزب_خروج`",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # تأسیس حزب
        party_data = {
            'name': party_name,
            'founder': ctx.author.display_name,
            'leader': ctx.author.display_name,
            'members': [user_id],
            'ideology': '',
            'manifesto': '',
            'votes': 0,
            'founded_date': datetime.now().isoformat()
        }
        
        self.parties[party_name] = party_data
        self.db.set_user_data(user_id, 'political_party', party_name)
        self.db.set_user_data(user_id, 'party_role', 'رهبر')
        
        # ایجاد رول حزب
        guild = ctx.guild
        party_role = await get_or_create_role(guild, f"حزب {party_name}", color=discord.Color.purple())
        await ctx.author.add_roles(party_role)
        
        # ایجاد کانال حزب
        party_category = await get_or_create_category(guild, "احزاب سیاسی")
        party_channel = await guild.create_text_channel(
            f"حزب-{party_name.replace(' ', '-')}",
            category=party_category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                party_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )
        
        embed = create_embed(
            "حزب تأسیس شد ✅",
            f"**نام حزب:** {party_name}\n"
            f"**بنیان‌گذار:** {ctx.author.mention}\n"
            f"**تاریخ تأسیس:** {datetime.now().strftime('%Y/%m/%d')}\n"
            f"**کانال حزب:** {party_channel.mention}",
            EMBED_COLORS['success']
        )
        embed.set_footer(text="حالا می‌توانید ایدئولوژی و برنامه حزب را تنظیم کنید!")
        await ctx.send(embed=embed)

    @commands.command(name='عضویت')
    async def join_party(self, ctx, *, party_name: str):
        """عضویت در حزب"""
        user_id = str(ctx.author.id)
        
        if party_name not in self.parties:
            embed = create_embed(
                "خطا ❌",
                f"حزب '{party_name}' یافت نشد!\nبرای مشاهده لیست: `!حزب_لیست`",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی عضویت فعلی
        user_party = self.db.get_user_data(user_id, 'political_party')
        if user_party:
            embed = create_embed(
                "خطا ❌",
                f"شما عضو حزب '{user_party}' هستید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # عضویت در حزب
        self.parties[party_name]['members'].append(user_id)
        self.db.set_user_data(user_id, 'political_party', party_name)
        self.db.set_user_data(user_id, 'party_role', 'عضو')
        
        # اضافه کردن رول
        guild = ctx.guild
        party_role = discord.utils.get(guild.roles, name=f"حزب {party_name}")
        if party_role:
            await ctx.author.add_roles(party_role)
        
        embed = create_embed(
            "عضویت موفق ✅",
            f"شما به حزب '{party_name}' پیوستید!\n"
            f"تعداد اعضا: {len(self.parties[party_name]['members'])} نفر",
            EMBED_COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name='لیست')
    async def list_parties(self, ctx):
        """لیست احزاب موجود"""
        if not self.parties:
            embed = create_embed(
                "هیچ حزبی موجود نیست",
                "برای تأسیس حزب جدید: `!حزب_تأسیس [نام حزب]`",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            "🗳️ احزاب سیاسی اسرائیل",
            f"تعداد احزاب: {len(self.parties)}",
            EMBED_COLORS['primary']
        )
        
        for party_name, party_data in self.parties.items():
            embed.add_field(
                name=party_name,
                value=f"**رهبر:** {party_data['leader']}\n"
                      f"**اعضا:** {len(party_data['members'])} نفر\n"
                      f"**آرا:** {party_data['votes']} رأی\n"
                      f"**تأسیس:** {party_data['founded_date'][:10]}",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='برنامه')
    @has_role(['رهبر حزب'])
    async def set_manifesto(self, ctx, *, manifesto: str):
        """تنظیم برنامه حزب"""
        user_id = str(ctx.author.id)
        user_party = self.db.get_user_data(user_id, 'political_party')
        
        if not user_party or user_party not in self.parties:
            embed = create_embed(
                "خطا ❌",
                "شما رهبر هیچ حزبی نیستید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        self.parties[user_party]['manifesto'] = manifesto
        
        embed = create_embed(
            "برنامه حزب تنظیم شد ✅",
            f"**حزب:** {user_party}\n"
            f"**برنامه جدید:**\n{manifesto}",
            EMBED_COLORS['success']
        )
        await ctx.send(embed=embed)

# ======================= ربات رادیو اسرائیل =======================

class RadioIsraelBot(commands.Bot):
    """
    ربات رادیو اسرائیل
    مسئول پخش موزیک و اعلان‌های صوتی دولتی
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!رادیو_',
            intents=intents,
            help_command=None,
            description="رادیو اسرائیل - صدای ملت"
        )
        
        self.db = DatabaseManager()
        self.current_track = None
        self.playlist = []
        self.is_playing = False
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - رادیو اسرائیل آماده است!')
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="رادیو اسرائیل 📻"
            )
        )

    @commands.command(name='اعلان')
    @has_role(['وزیر', 'نخست‌وزیر', 'مدیر'])
    async def government_announcement(self, ctx, *, message: str):
        """پخش اعلان دولتی"""
        # شبیه‌سازی تبدیل متن به گفتار
        embed = create_embed(
            "📢 اعلان رسمی دولت اسرائیل",
            f"**پیام:**\n{message}\n\n"
            f"**اعلام‌کننده:** {ctx.author.mention}\n"
            f"**زمان:** {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            EMBED_COLORS['warning']
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830411.png")
        
        # ارسال به کانال اصلی
        guild = ctx.guild
        general_channel = discord.utils.get(guild.channels, name='عمومی')
        if general_channel:
            await general_channel.send("@everyone", embed=embed)
        
        await ctx.send("✅ اعلان با موفقیت پخش شد!")

# ======================= اجرای سیستم‌های مدنی =======================

async def run_jobs_education():
    """اجرای ربات مشاغل و آموزش"""
    bot = JobsAndEducationBot()
    await bot.start(DISCORD_BOT_TOKEN_JOBS_EDUCATION)

async def run_real_estate():
    """اجرای ربات املاک"""
    bot = RealEstateBot()
    await bot.start(DISCORD_BOT_TOKEN_REAL_ESTATE)

async def run_political_parties():
    """اجرای ربات احزاب سیاسی"""
    bot = PoliticalPartiesBot()
    await bot.start(DISCORD_BOT_TOKEN_POLITICAL_PARTIES)

async def run_radio_israel():
    """اجرای ربات رادیو اسرائیل"""
    bot = RadioIsraelBot()
    await bot.start(DISCORD_BOT_TOKEN_RADIO_ISRAEL)

if __name__ == "__main__":
    """
    راهنمای اجرا:
    
    1. نصب وابستگی‌ها:
       pip install -r requirements.txt
    
    2. تنظیم متغیرهای محیطی در فایل .env:
       DISCORD_BOT_TOKEN_JOBS_EDUCATION=توکن_ربات_مشاغل_آموزش
       DISCORD_BOT_TOKEN_REAL_ESTATE=توکن_ربات_املاک
       DISCORD_BOT_TOKEN_POLITICAL_PARTIES=توکن_ربات_احزاب
       DISCORD_BOT_TOKEN_RADIO_ISRAEL=توکن_ربات_رادیو
       GEMINI_API_KEY=کلید_API_جمنای
    
    3. اجرای ربات‌ها:
       python civil_systems.py
    
    دستورات اصلی:
    
    مشاغل و آموزش:
    - !شغل_لیست_مشاغل : لیست مشاغل موجود
    - !شغل_درخواست [نام شغل] : درخواست شغل
    - !شغل_ثبت‌نام_دانشگاه [رشته] : ثبت‌نام دانشگاه
    - !شغل_وضعیت_تحصیل : وضعیت تحصیلی
    
    املاک و مستغلات:
    - !ملک_بازار : مشاهده بازار املاک
    - !ملک_خرید [نوع ملک] [شهر] : خرید ملک
    - !ملک_املاک_من : املاک شخصی
    - !ملک_دعوت @کاربر [شماره ملک] : دعوت به ملک
    
    احزاب سیاسی:
    - !حزب_تأسیس [نام حزب] : تأسیس حزب جدید
    - !حزب_عضویت [نام حزب] : عضویت در حزب
    - !حزب_لیست : لیست احزاب
    - !حزب_برنامه [متن برنامه] : تنظیم برنامه حزب
    
    رادیو اسرائیل:
    - !رادیو_اعلان [پیام] : پخش اعلان دولتی
    """
    
    import asyncio
    
    async def main():
        # اجرای همزمان تمام سیستم‌های مدنی
        await asyncio.gather(
            run_jobs_education(),
            run_real_estate(),
            run_political_parties(),
            run_radio_israel()
        )
    
    asyncio.run(main())