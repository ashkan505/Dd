#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات نیروی هوایی اسرائیل (IAF)
Israeli Air Force Bot

این ربات مسئول مدیریت کامل نیروی هوایی اسرائیل است:
- مدیریت ناوگان هوایی (F-35, F-16, F-15, Apache, UAVs)
- عملیات هوایی و ماموریت‌های رزمی
- پایگاه‌های هوایی و زیرساخت‌ها
- آموزش خلبانان و نگهداری هواپیماها
- دفاع هوایی و کنترل آسمان

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

class IsraeliAirForceBot(commands.Bot):
    """
    ربات نیروی هوایی اسرائیل (IAF)
    "חיל האוויר הישראלי"
    
    مأموریت: حاکمیت کامل بر آسمان اسرائیل و منطقه
    شعار: "אל על כנפי נשרים" (بر بال‌های عقاب‌ها)
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!هوایی_',
            intents=intents,
            help_command=None,
            description="🛩️ نیروی هوایی اسرائیل - حاکمان آسمان"
        )
        
        self.db = DatabaseManager()
        
        # ناوگان هوایی کامل
        self.aircraft_fleet = {
            # جنگنده‌های نسل 5
            'F-35I_Adir': {
                'name': 'F-35I آدیر (אדיר)',
                'type': 'جنگنده نسل پنجم',
                'manufacturer': 'Lockheed Martin',
                'total_count': 50,
                'operational': 45,
                'maintenance': 3,
                'training': 2,
                'max_speed': 1900,  # km/h
                'range': 2220,  # km
                'ceiling': 15240,  # m
                'crew': 1,
                'cost_per_hour': 42000,
                'capabilities': [
                    'نامرئی راداری', 'چندمنظوره', 'حمله دقیق',
                    'جنگ الکترونیک', 'شناسایی پیشرفته', 'عملیات شبانه'
                ],
                'weapons': [
                    'موشک هوا-هوا Python 5', 'موشک هوا-زمین JDAM',
                    'موشک کروز SDB', 'توپ 25mm GAU-22'
                ],
                'squadrons': ['116 سرب الجنوب', '140 الذهبي'],
                'bases': ['Nevatim', 'Tel Nof']
            },
            
            # جنگنده‌های چندمنظوره
            'F-16I_Sufa': {
                'name': 'F-16I سوفا (סופה)',
                'type': 'جنگنده چندمنظوره',
                'manufacturer': 'General Dynamics',
                'total_count': 175,
                'operational': 160,
                'maintenance': 12,
                'training': 3,
                'max_speed': 2120,
                'range': 4220,
                'ceiling': 15240,
                'crew': 1,
                'cost_per_hour': 22000,
                'capabilities': [
                    'حمله زمینی', 'هوا به هوا', 'اسکورت',
                    'گشت‌زنی', 'پشتیبانی نزدیک', 'جنگ الکترونیک'
                ],
                'weapons': [
                    'موشک Python 4/5', 'موشک Derby', 'بمب Paveway',
                    'موشک Hellfire', 'توپ M61 Vulcan'
                ],
                'squadrons': ['101 اول', '105 الصقر', '107 الفهد', '110 الليل', '115 الطائر الطنان'],
                'bases': ['Ramon', 'Hatzerim', 'Ovda']
            },
            
            # جنگنده‌های سنگین
            'F-15I_RaAm': {
                'name': 'F-15I رعم (רעם)',
                'type': 'جنگنده سنگین',
                'manufacturer': 'McDonnell Douglas',
                'total_count': 25,
                'operational': 23,
                'maintenance': 2,
                'training': 0,
                'max_speed': 2650,
                'range': 4815,
                'ceiling': 20000,
                'crew': 2,
                'cost_per_hour': 41000,
                'capabilities': [
                    'برد بلند', 'حمله عمقی', 'برتری هوایی',
                    'نفوذ عمیق', 'حمل محموله سنگین'
                ],
                'weapons': [
                    'موشک AIM-120 AMRAAM', 'موشک AIM-9 Sidewinder',
                    'بمب‌های سنگین GBU', 'موشک کروز Popeye'
                ],
                'squadrons': ['133 الاسود'],
                'bases': ['Tel Nof']
            },
            
            # بالگردهای تهاجمی
            'AH-64_Apache': {
                'name': 'AH-64 آپاچی پرناز (פרנז)',
                'type': 'بالگرد تهاجمی',
                'manufacturer': 'Boeing',
                'total_count': 48,
                'operational': 42,
                'maintenance': 4,
                'training': 2,
                'max_speed': 365,
                'range': 476,
                'ceiling': 6400,
                'crew': 2,
                'cost_per_hour': 17000,
                'capabilities': [
                    'پشتیبانی زمینی', 'ضدتانک', 'عملیات شبانه',
                    'جستجو و نابودی', 'اسکورت کاروان'
                ],
                'weapons': [
                    'موشک Hellfire', 'راکت Hydra 70',
                    'توپ M230 Chain Gun', 'موشک Spike'
                ],
                'squadrons': ['113 الدبور'],
                'bases': ['Palmachim', 'Ramon']
            },
            
            # پهپادهای پیشرفته
            'Eitan_UAV': {
                'name': 'پهپاد ایتان (איתן)',
                'type': 'پهپاد MALE',
                'manufacturer': 'IAI',
                'total_count': 12,
                'operational': 10,
                'maintenance': 2,
                'training': 0,
                'max_speed': 370,
                'range': 7000,
                'ceiling': 13700,
                'crew': 0,
                'cost_per_hour': 3500,
                'capabilities': [
                    'نظارت استراتژیک', 'جاسوسی', 'حمله دقیق',
                    'پرواز طولانی', 'جمع‌آوری اطلاعات'
                ],
                'weapons': [
                    'موشک Hellfire', 'موشک Spike',
                    'سنسورهای پیشرفته', 'دوربین‌های حرارتی'
                ],
                'squadrons': ['210 الباز'],
                'bases': ['Palmachim']
            },
            
            # پهپادهای تاکتیکی
            'Hermes_450': {
                'name': 'پهپاد هرمس 450',
                'type': 'پهپاد تاکتیکی',
                'manufacturer': 'Elbit Systems',
                'total_count': 30,
                'operational': 26,
                'maintenance': 3,
                'training': 1,
                'max_speed': 220,
                'range': 300,
                'ceiling': 5500,
                'crew': 0,
                'cost_per_hour': 1200,
                'capabilities': [
                    'شناسایی تاکتیکی', 'نظارت مرزی', 'هدایت آتش',
                    'مراقبت شهری', 'پشتیبانی زمینی'
                ],
                'weapons': [
                    'موشک‌های کوچک', 'سنسورهای الکترواپتیک',
                    'سیستم ارتباطات', 'دوربین‌های دید در شب'
                ],
                'squadrons': ['200 الصقر الاحمر'],
                'bases': ['Palmachim', 'Tel Nof']
            }
        }
        
        # پایگاه‌های هوایی
        self.air_bases = {
            'Nevatim': {
                'name': 'پایگاه هوایی نواتیم',
                'location': 'صحرای نگب',
                'coordinates': (31.208, 35.012),
                'elevation': 400,
                'runways': 2,
                'runway_length': 3600,
                'aircraft_types': ['F-35I_Adir', 'F-16I_Sufa'],
                'squadrons': ['116', '140'],
                'personnel': 2500,
                'status': 'عملیاتی کامل',
                'security_level': 'بالا',
                'facilities': [
                    'هنگرهای محافظت شده', 'سیستم دفاع هوایی',
                    'مرکز فرماندهی', 'تأسیسات نگهداری پیشرفته'
                ]
            },
            
            'Ramon': {
                'name': 'پایگاه هوایی رامون',
                'location': 'میتزپه رامون',
                'coordinates': (30.776, 34.667),
                'elevation': 650,
                'runways': 2,
                'runway_length': 3000,
                'aircraft_types': ['F-16I_Sufa', 'AH-64_Apache'],
                'squadrons': ['101', '107', '113'],
                'personnel': 1800,
                'status': 'عملیاتی کامل',
                'security_level': 'بالا',
                'facilities': [
                    'مرکز آموزش خلبانی', 'شبیه‌ساز پرواز',
                    'انبار مهمات', 'بیمارستان صحرایی'
                ]
            },
            
            'Tel_Nof': {
                'name': 'پایگاه هوایی تل نوف',
                'location': 'مرکز اسرائیل',
                'coordinates': (31.838, 34.821),
                'elevation': 75,
                'runways': 2,
                'runway_length': 2600,
                'aircraft_types': ['F-15I_RaAm', 'Hermes_450'],
                'squadrons': ['133', '200'],
                'personnel': 1200,
                'status': 'عملیاتی کامل',
                'security_level': 'متوسط',
                'facilities': [
                    'مرکز فرماندهی مرکزی', 'تأسیسات تحقیق و توسعه',
                    'آکادمی نیروی هوایی', 'موزه نیروی هوایی'
                ]
            },
            
            'Palmachim': {
                'name': 'پایگاه هوایی پالماخیم',
                'location': 'ساحل مدیترانه',
                'coordinates': (31.897, 34.690),
                'elevation': 45,
                'runways': 1,
                'runway_length': 2400,
                'aircraft_types': ['Eitan_UAV', 'Hermes_450', 'AH-64_Apache'],
                'squadrons': ['210'],
                'personnel': 800,
                'status': 'عملیاتی کامل',
                'security_level': 'بالا',
                'facilities': [
                    'مرکز کنترل پهپادها', 'ایستگاه ماهواره‌ای',
                    'آزمایشگاه فناوری', 'مرکز جنگ الکترونیک'
                ]
            }
        }
        
        # عملیات هوایی فعال
        self.active_missions = {}
        self.mission_counter = 1000
        
        # آمار عملیاتی
        self.operational_stats = {
            'total_sorties': 2847,
            'combat_missions': 234,
            'reconnaissance_missions': 456,
            'training_flights': 2157,
            'air_to_air_victories': 12,
            'ground_targets_destroyed': 89,
            'successful_interceptions': 45,
            'pilot_training_hours': 12450,
            'maintenance_hours': 35600,
            'fuel_consumed': 2840000  # لیتر
        }
        
        # وضعیت آمادگی
        self.readiness_level = 'DEFCON 3'
        self.alert_status = 'آمادگی عادی'
        
        # خلبانان و پرسنل
        self.personnel = {
            'pilots': 450,
            'navigators': 120,
            'ground_crew': 2800,
            'engineers': 340,
            'commanders': 85,
            'trainees': 95
        }
        
    async def on_ready(self):
        """آماده‌سازی ربات نیروی هوایی"""
        print(f'🛩️ {self.user} - נכון לשירות! (آماده خدمت!)')
        
        # شروع وظایف دوره‌ای
        if not self.daily_operations.is_running():
            self.daily_operations.start()
        if not self.maintenance_cycle.is_running():
            self.maintenance_cycle.start()
        if not self.training_flights.is_running():
            self.training_flights.start()
        if not self.weather_monitoring.is_running():
            self.weather_monitoring.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"آسمان اسرائیل | {self.alert_status} ✈️"
            )
        )
        
        # ایجاد کانال‌های اختصاصی در صورت عدم وجود
        guild = self.guilds[0] if self.guilds else None
        if guild:
            await self._setup_channels(guild)

    async def _setup_channels(self, guild):
        """ایجاد کانال‌های اختصاصی نیروی هوایی"""
        channels_to_create = [
            ('🛩️│فرماندهی-هوایی', 'مرکز فرماندهی نیروی هوایی'),
            ('✈️│عملیات-هوایی', 'عملیات و ماموریت‌های جاری'),
            ('🎯│ماموریت‌های-رزمی', 'ماموریت‌های رزمی و تهاجمی'),
            ('📡│کنترل-ترافیک', 'کنترل ترافیک هوایی'),
            ('🔧│نگهداری-هواپیما', 'تعمیر و نگهداری ناوگان'),
            ('🎓│آموزش-خلبانی', 'آموزش و تربیت خلبان'),
            ('📊│گزارشات-هوایی', 'گزارشات و آمار عملیاتی')
        ]
        
        air_force_category = await get_or_create_category(guild, "🛩️ نیروی هوایی اسرائیل")
        
        for channel_name, description in channels_to_create:
            await get_or_create_channel(guild, channel_name, category=air_force_category)

    @commands.command(name='وضعیت_ناوگان')
    async def fleet_status(self, ctx):
        """نمایش وضعیت کامل ناوگان هوایی"""
        embed = create_embed(
            "🛩️ وضعیت ناوگان نیروی هوایی اسرائیل",
            f"**سطح آمادگی:** {self.readiness_level}\n**وضعیت هشدار:** {self.alert_status}",
            EMBED_COLORS['primary']
        )
        
        total_aircraft = 0
        total_operational = 0
        
        for aircraft_id, aircraft in self.aircraft_fleet.items():
            total_aircraft += aircraft['total_count']
            total_operational += aircraft['operational']
            
            # محاسبه درصد آمادگی
            readiness_percent = (aircraft['operational'] / aircraft['total_count']) * 100
            
            # تعیین وضعیت بر اساس آمادگی
            if readiness_percent >= 90:
                status_emoji = "🟢"
                status_text = "عالی"
            elif readiness_percent >= 75:
                status_emoji = "🟡"
                status_text = "مطلوب"
            else:
                status_emoji = "🔴"
                status_text = "نیاز به توجه"
            
            embed.add_field(
                name=f"{status_emoji} {aircraft['name']}",
                value=f"**نوع:** {aircraft['type']}\n"
                      f"**مجموع:** {aircraft['total_count']}\n"
                      f"**عملیاتی:** {aircraft['operational']}\n"
                      f"**تعمیرات:** {aircraft['maintenance']}\n"
                      f"**آموزش:** {aircraft['training']}\n"
                      f"**آمادگی:** {readiness_percent:.1f}% ({status_text})\n"
                      f"**هزینه/ساعت:** ${aircraft['cost_per_hour']:,}",
                inline=True
            )
        
        # آمار کلی
        overall_readiness = (total_operational / total_aircraft) * 100
        embed.add_field(
            name="📊 خلاصه کلی ناوگان",
            value=f"**مجموع هواپیماها:** {total_aircraft}\n"
                  f"**آماده عملیات:** {total_operational}\n"
                  f"**آمادگی کلی:** {overall_readiness:.1f}%\n"
                  f"**وضعیت کلی:** {'🟢 عالی' if overall_readiness >= 85 else '🟡 مطلوب' if overall_readiness >= 70 else '🔴 نگران‌کننده'}",
            inline=False
        )
        
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Emblem_of_the_Israeli_Air_Force.svg/200px-Emblem_of_the_Israeli_Air_Force.svg.png")
        embed.set_footer(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
        
        await ctx.send(embed=embed)

    @commands.command(name='پایگاه‌ها')
    async def air_bases_status(self, ctx):
        """نمایش وضعیت پایگاه‌های هوایی"""
        embed = create_embed(
            "🏭 پایگاه‌های نیروی هوایی اسرائیل",
            "وضعیت فعلی پایگاه‌های هوایی:",
            EMBED_COLORS['primary']
        )
        
        for base_id, base in self.air_bases.items():
            # محاسبه هواپیماهای مستقر
            stationed_aircraft = []
            for aircraft_type in base['aircraft_types']:
                if aircraft_type in self.aircraft_fleet:
                    aircraft_name = self.aircraft_fleet[aircraft_type]['name']
                    stationed_aircraft.append(aircraft_name)
            
            # تعیین وضعیت امنیتی
            security_emoji = {
                'بالا': '🔴',
                'متوسط': '🟡',
                'پایین': '🟢'
            }.get(base['security_level'], '⚪')
            
            embed.add_field(
                name=f"🛩️ {base['name']}",
                value=f"**موقعیت:** {base['location']}\n"
                      f"**ارتفاع:** {base['elevation']} متر\n"
                      f"**باند فرود:** {base['runways']} باند ({base['runway_length']}م)\n"
                      f"**پرسنل:** {base['personnel']:,} نفر\n"
                      f"**امنیت:** {security_emoji} {base['security_level']}\n"
                      f"**وضعیت:** {base['status']}\n"
                      f"**هواپیماهای مستقر:**\n" + 
                      "\n".join([f"• {aircraft}" for aircraft in stationed_aircraft]),
                inline=True
            )
        
        embed.set_footer(text="تمام پایگاه‌ها در حالت آمادگی کامل")
        await ctx.send(embed=embed)

    @commands.command(name='ماموریت')
    @has_role(['فرمانده هوایی', 'خلبان', 'افسر عملیات', 'مدیر'])
    async def launch_mission(self, ctx, mission_type: str, aircraft_type: str, target_area: str = "نامشخص"):
        """راه‌اندازی ماموریت هوایی جدید"""
        
        # انواع ماموریت‌های مجاز
        valid_missions = {
            'حمله': 'ماموریت تهاجمی',
            'شناسایی': 'ماموریت اطلاعاتی',
            'گشت': 'گشت‌زنی هوایی',
            'اسکورت': 'اسکورت و حمایت',
            'تمرین': 'تمرین و آموزش',
            'امداد': 'عملیات امداد و نجات',
            'نظارت': 'نظارت و کنترل'
        }
        
        if mission_type not in valid_missions:
            embed = create_embed(
                "❌ نوع ماموریت نامعتبر",
                f"**انواع ماموریت مجاز:**\n" + 
                "\n".join([f"• `{k}`: {v}" for k, v in valid_missions.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی وجود هواپیما
        if aircraft_type not in self.aircraft_fleet:
            available_aircraft = "\n".join([f"• `{k}`: {v['name']}" for k, v in self.aircraft_fleet.items()])
            embed = create_embed(
                "❌ هواپیمای نامعتبر",
                f"**هواپیماهای موجود:**\n{available_aircraft}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        aircraft = self.aircraft_fleet[aircraft_type]
        
        # بررسی در دسترس بودن
        if aircraft['operational'] < 1:
            embed = create_embed(
                "❌ هواپیما در دسترس نیست",
                f"**هواپیما:** {aircraft['name']}\n"
                f"**عملیاتی:** {aircraft['operational']}\n"
                f"**تعمیرات:** {aircraft['maintenance']}\n"
                f"**آموزش:** {aircraft['training']}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی مناسب بودن هواپیما برای ماموریت
        mission_requirements = {
            'حمله': ['حمله زمینی', 'حمله دقیق', 'چندمنظوره'],
            'شناسایی': ['جاسوسی', 'شناسایی پیشرفته', 'نظارت استراتژیک'],
            'گشت': ['گشت‌زنی', 'هوا به هوا', 'برتری هوایی'],
            'اسکورت': ['اسکورت', 'حمایت', 'پشتیبانی'],
            'نظارت': ['نظارت', 'شناسایی', 'جمع‌آوری اطلاعات']
        }
        
        required_capabilities = mission_requirements.get(mission_type, [])
        if required_capabilities:
            has_capability = any(cap in aircraft['capabilities'] for cap in required_capabilities)
            if not has_capability:
                embed = create_embed(
                    "⚠️ هواپیمای نامناسب",
                    f"**هواپیما:** {aircraft['name']}\n"
                    f"**ماموریت:** {mission_type}\n"
                    f"**قابلیت‌های مورد نیاز:** {', '.join(required_capabilities)}\n"
                    f"**قابلیت‌های موجود:** {', '.join(aircraft['capabilities'])}",
                    EMBED_COLORS['warning']
                )
                await ctx.send(embed=embed)
                # ادامه می‌دهیم اما با هشدار
        
        # ایجاد ماموریت
        mission_id = f"IAF-{self.mission_counter}"
        self.mission_counter += 1
        
        # محاسبه مدت ماموریت بر اساس نوع و هواپیما
        base_duration = {
            'حمله': 180,
            'شناسایی': 240,
            'گشت': 120,
            'اسکورت': 90,
            'تمرین': 60,
            'امداد': 150,
            'نظارت': 300
        }
        
        duration = base_duration.get(mission_type, 120)
        # اضافه کردن تصادفی ±30 دقیقه
        duration += random.randint(-30, 30)
        duration = max(30, duration)  # حداقل 30 دقیقه
        
        mission_data = {
            'id': mission_id,
            'type': mission_type,
            'aircraft_type': aircraft_type,
            'aircraft_name': aircraft['name'],
            'target_area': target_area,
            'pilot': ctx.author.display_name,
            'start_time': datetime.now(),
            'duration_minutes': duration,
            'status': 'در حال انجام',
            'cost': aircraft['cost_per_hour'] * (duration / 60),
            'fuel_consumed': random.randint(1000, 5000),
            'success_probability': random.randint(85, 98)
        }
        
        # ذخیره ماموریت
        self.active_missions[mission_id] = mission_data
        
        # کاهش هواپیمای موجود
        aircraft['operational'] -= 1
        
        # تولید توضیحات ماموریت با هوش مصنوعی
        mission_prompt = f"""
        یک ماموریت {mission_type} هوایی با هواپیمای {aircraft['name']} آغاز شده است.
        منطقه هدف: {target_area}
        خلبان: {ctx.author.display_name}
        مدت ماموریت: {duration} دقیقه
        
        یک توضیح جذاب و نظامی از این ماموریت بنویس (80-120 کلمه).
        از اصطلاحات نظامی و هوایی استفاده کن.
        """
        
        try:
            mission_description = await generate_text_with_gemini(mission_prompt)
        except Exception as e:
            logger.error(f"خطا در تولید توضیحات ماموریت: {e}")
            mission_description = f"ماموریت {mission_type} با {aircraft['name']} در منطقه {target_area} با موفقیت آغاز شد."
        
        # ارسال پیام تأیید
        embed = create_embed(
            f"🚁 ماموریت {mission_type.upper()} آغاز شد",
            f"**شماره ماموریت:** `{mission_id}`\n"
            f"**نوع:** {valid_missions[mission_type]}\n"
            f"**هواپیما:** {aircraft['name']}\n"
            f"**خلبان:** {ctx.author.mention}\n"
            f"**منطقه هدف:** {target_area}\n"
            f"**مدت تخمینی:** {duration} دقیقه\n"
            f"**هزینه عملیاتی:** ${mission_data['cost']:,.0f}\n"
            f"**احتمال موفقیت:** {mission_data['success_probability']}%\n\n"
            f"**جزئیات ماموریت:**\n{mission_description}",
            EMBED_COLORS['success']
        )
        
        embed.set_footer(text=f"شروع: {datetime.now().strftime('%H:%M')} | زمان تکمیل تقریبی: {(datetime.now() + timedelta(minutes=duration)).strftime('%H:%M')}")
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830411.png")
        
        await ctx.send(embed=embed)
        
        # اطلاع‌رسانی به کانال عملیات
        ops_channel = discord.utils.get(ctx.guild.channels, name='✈️│عملیات-هوایی')
        if ops_channel:
            ops_embed = create_embed(
                "🛩️ ماموریت جدید در حال انجام",
                f"**{mission_id}** - {mission_type} توسط {ctx.author.mention}",
                EMBED_COLORS['primary']
            )
            await ops_channel.send(embed=ops_embed)

    @commands.command(name='ماموریت‌های_فعال')
    async def active_missions_status(self, ctx):
        """نمایش ماموریت‌های در حال انجام"""
        
        if not self.active_missions:
            embed = create_embed(
                "📋 ماموریت‌های فعال",
                "در حال حاضر هیچ ماموریت هوایی در جریان نیست.\n\n"
                "✈️ آسمان اسرائیل آرام است",
                EMBED_COLORS['primary']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            "🚁 ماموریت‌های هوایی فعال",
            f"تعداد ماموریت‌های در حال انجام: **{len(self.active_missions)}**",
            EMBED_COLORS['primary']
        )
        
        for mission_id, mission in list(self.active_missions.items())[:6]:  # نمایش حداکثر 6 ماموریت
            elapsed_time = datetime.now() - mission['start_time']
            elapsed_minutes = int(elapsed_time.total_seconds() / 60)
            remaining_minutes = mission['duration_minutes'] - elapsed_minutes
            
            if remaining_minutes > 0:
                status_text = f"⏳ {remaining_minutes} دقیقه باقیمانده"
                status_emoji = "🟡"
            else:
                status_text = "✅ آماده بازگشت"
                status_emoji = "🟢"
            
            # محاسبه پیشرفت
            progress = min(100, (elapsed_minutes / mission['duration_minutes']) * 100)
            progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
            
            embed.add_field(
                name=f"{status_emoji} {mission['id']}",
                value=f"**نوع:** {mission['type']}\n"
                      f"**هواپیما:** {mission['aircraft_name']}\n"
                      f"**خلبان:** {mission['pilot']}\n"
                      f"**منطقه:** {mission['target_area']}\n"
                      f"**پیشرفت:** {progress:.1f}%\n"
                      f"`{progress_bar}`\n"
                      f"**وضعیت:** {status_text}",
                inline=True
            )
        
        if len(self.active_missions) > 6:
            embed.add_field(
                name="📊 سایر ماموریت‌ها",
                value=f"و {len(self.active_missions) - 6} ماموریت دیگر...",
                inline=False
            )
        
        embed.set_footer(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        await ctx.send(embed=embed)

    @commands.command(name='آمار_عملیاتی')
    @has_role(['فرمانده هوایی', 'افسر عملیات', 'مدیر'])
    async def operational_statistics(self, ctx):
        """نمایش آمار کامل عملیاتی نیروی هوایی"""
        
        embed = create_embed(
            "📊 آمار عملیاتی نیروی هوایی اسرائیل",
            f"**دوره گزارش:** سال جاری\n**آخرین به‌روزرسانی:** {datetime.now().strftime('%Y/%m/%d')}",
            EMBED_COLORS['primary']
        )
        
        # آمار پرواز
        embed.add_field(
            name="✈️ آمار پرواز",
            value=f"**کل پروازها:** {self.operational_stats['total_sorties']:,}\n"
                  f"**ماموریت‌های رزمی:** {self.operational_stats['combat_missions']:,}\n"
                  f"**ماموریت‌های شناسایی:** {self.operational_stats['reconnaissance_missions']:,}\n"
                  f"**پروازهای تمرینی:** {self.operational_stats['training_flights']:,}\n"
                  f"**ساعات پرواز کل:** {self.operational_stats['total_sorties'] * 2:.0f}",
            inline=True
        )
        
        # آمار رزمی
        embed.add_field(
            name="🎯 آمار رزمی",
            value=f"**پیروزی‌های هوا-هوا:** {self.operational_stats['air_to_air_victories']}\n"
                  f"**اهداف زمینی منهدم:** {self.operational_stats['ground_targets_destroyed']}\n"
                  f"**رهگیری‌های موفق:** {self.operational_stats['successful_interceptions']}\n"
                  f"**نرخ موفقیت:** 96.8%\n"
                  f"**تلفات:** 0",
            inline=True
        )
        
        # آمار آموزشی و نگهداری
        embed.add_field(
            name="🎓 آموزش و نگهداری",
            value=f"**ساعات آموزش خلبانی:** {self.operational_stats['pilot_training_hours']:,}\n"
                  f"**ساعات نگهداری:** {self.operational_stats['maintenance_hours']:,}\n"
                  f"**سوخت مصرفی:** {self.operational_stats['fuel_consumed']:,} لیتر\n"
                  f"**خلبانان فعال:** {self.personnel['pilots']}\n"
                  f"**متخصصان فنی:** {self.personnel['ground_crew']:,}",
            inline=True
        )
        
        # محاسبه هزینه‌های عملیاتی
        total_operational_cost = sum([
            aircraft['cost_per_hour'] * aircraft['operational'] * 2  # فرض 2 ساعت پرواز روزانه
            for aircraft in self.aircraft_fleet.values()
        ]) * 30  # ماهانه
        
        embed.add_field(
            name="💰 اقتصادی",
            value=f"**هزینه عملیاتی ماهانه:** ${total_operational_cost:,.0f}\n"
                  f"**متوسط هزینه ماموریت:** ${total_operational_cost / max(1, self.operational_stats['combat_missions'] + self.operational_stats['reconnaissance_missions']):,.0f}\n"
                  f"**بازده عملیاتی:** عالی\n"
                  f"**صرفه‌جویی سوخت:** 12%",
            inline=True
        )
        
        # آمار آمادگی
        total_aircraft = sum([aircraft['total_count'] for aircraft in self.aircraft_fleet.values()])
        total_operational = sum([aircraft['operational'] for aircraft in self.aircraft_fleet.values()])
        readiness_percentage = (total_operational / total_aircraft) * 100
        
        embed.add_field(
            name="⚡ آمادگی",
            value=f"**سطح آمادگی کلی:** {readiness_percentage:.1f}%\n"
                  f"**وضعیت فعلی:** {self.alert_status}\n"
                  f"**DEFCON:** {self.readiness_level}\n"
                  f"**زمان پاسخ:** <5 دقیقه\n"
                  f"**دسترسی 24/7:** ✅",
            inline=True
        )
        
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Emblem_of_the_Israeli_Air_Force.svg/200px-Emblem_of_the_Israeli_Air_Force.svg.png")
        embed.set_footer(text="נכון למועד | به‌روز تا این لحظه")
        
        await ctx.send(embed=embed)

    @commands.command(name='تغییر_آمادگی')
    @has_role(['فرمانده کل', 'فرمانده هوایی', 'مدیر'])
    async def change_readiness_level(self, ctx, new_level: str):
        """تغییر سطح آمادگی نیروی هوایی"""
        
        valid_levels = {
            'DEFCON_1': 'حداکثر آمادگی - جنگ فعال',
            'DEFCON_2': 'آمادگی کامل - تهدید فوری',
            'DEFCON_3': 'آمادگی افزایش یافته',
            'DEFCON_4': 'آمادگی عادی',
            'DEFCON_5': 'آمادگی کم - صلح'
        }
        
        if new_level not in valid_levels:
            embed = create_embed(
                "❌ سطح آمادگی نامعتبر",
                "**سطوح آمادگی موجود:**\n" + 
                "\n".join([f"• `{k}`: {v}" for k, v in valid_levels.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        old_level = self.readiness_level
        self.readiness_level = new_level
        
        # تعیین وضعیت هشدار
        alert_statuses = {
            'DEFCON_1': 'هشدار قرمز - جنگ',
            'DEFCON_2': 'هشدار نارنجی - آمادگی کامل',
            'DEFCON_3': 'هشدار زرد - آمادگی افزایش یافته',
            'DEFCON_4': 'آمادگی عادی',
            'DEFCON_5': 'آمادگی کم'
        }
        
        self.alert_status = alert_statuses[new_level]
        
        # رنگ embed بر اساس سطح
        level_colors = {
            'DEFCON_1': 0xFF0000,  # قرمز
            'DEFCON_2': 0xFF8800,  # نارنجی
            'DEFCON_3': 0xFFFF00,  # زرد
            'DEFCON_4': 0x00FF00,  # سبز
            'DEFCON_5': 0x0088FF   # آبی
        }
        
        embed = create_embed(
            f"⚡ تغییر سطح آمادگی نیروی هوایی",
            f"**سطح قبلی:** {old_level}\n"
            f"**سطح جدید:** {new_level}\n"
            f"**وضعیت:** {self.alert_status}\n"
            f"**تغییر توسط:** {ctx.author.mention}\n"
            f"**زمان:** {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            level_colors[new_level]
        )
        
        # اقدامات خودکار بر اساس سطح آمادگی
        if new_level in ['DEFCON_1', 'DEFCON_2']:
            embed.add_field(
                name="🚨 اقدامات خودکار",
                value="• تمام خلبانان در حالت آماده‌باش\n"
                      "• افزایش گشت‌های هوایی\n"
                      "• فعال‌سازی سیستم‌های دفاعی\n"
                      "• محدودیت پروازهای غیرضروری",
                inline=False
            )
        
        embed.set_footer(text="تمام واحدها مطلع شدند")
        await ctx.send(embed=embed)
        
        # به‌روزرسانی وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"آسمان اسرائیل | {self.alert_status} ✈️"
            )
        )
        
        # اطلاع‌رسانی به کانال فرماندهی
        command_channel = discord.utils.get(ctx.guild.channels, name='🛩️│فرماندهی-هوایی')
        if command_channel and command_channel != ctx.channel:
            await command_channel.send(embed=embed)

    @commands.command(name='گزارش_خلبان')
    @has_role(['خلبان', 'فرمانده هوایی', 'افسر عملیات'])
    async def pilot_report(self, ctx, mission_id: str, status: str, *, details: str = ""):
        """گزارش خلبان از ماموریت"""
        
        if mission_id not in self.active_missions:
            embed = create_embed(
                "❌ ماموریت یافت نشد",
                f"ماموریت با شماره `{mission_id}` یافت نشد یا تکمیل شده است.",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        mission = self.active_missions[mission_id]
        
        # بررسی اینکه گزارش‌دهنده خلبان ماموریت است
        if mission['pilot'] != ctx.author.display_name and not any(role.name in ['فرمانده هوایی', 'مدیر'] for role in ctx.author.roles):
            embed = create_embed(
                "❌ عدم دسترسی",
                "فقط خلبان ماموریت یا فرماندهان می‌توانند گزارش ارسال کنند.",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        valid_statuses = ['موفق', 'ناموفق', 'در_حال_انجام', 'نیاز_به_پشتیبانی', 'اورژانسی']
        
        if status not in valid_statuses:
            embed = create_embed(
                "❌ وضعیت نامعتبر",
                f"**وضعیت‌های مجاز:** {', '.join(valid_statuses)}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # ثبت گزارش
        if 'reports' not in mission:
            mission['reports'] = []
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'pilot': ctx.author.display_name,
            'status': status,
            'details': details,
            'location': 'در پرواز'
        }
        
        mission['reports'].append(report)
        
        # تعیین رنگ و ایموجی بر اساس وضعیت
        status_info = {
            'موفق': ('🟢', 'ماموریت با موفقیت انجام شد'),
            'ناموفق': ('🔴', 'ماموریت ناموفق بود'),
            'در_حال_انجام': ('🟡', 'ماموریت در حال انجام'),
            'نیاز_به_پشتیبانی': ('🟠', 'نیاز به پشتیبانی فوری'),
            'اورژانسی': ('🚨', 'وضعیت اورژانسی!')
        }
        
        emoji, description = status_info[status]
        
        embed = create_embed(
            f"{emoji} گزارش خلبان - {mission_id}",
            f"**وضعیت:** {description}\n"
            f"**خلبان:** {ctx.author.mention}\n"
            f"**هواپیما:** {mission['aircraft_name']}\n"
            f"**زمان گزارش:** {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"**جزئیات:**\n{details if details else 'بدون جزئیات اضافی'}",
            EMBED_COLORS['success'] if status == 'موفق' else EMBED_COLORS['error'] if status in ['ناموفق', 'اورژانسی'] else EMBED_COLORS['warning']
        )
        
        await ctx.send(embed=embed)
        
        # اطلاع‌رسانی به کانال عملیات
        ops_channel = discord.utils.get(ctx.guild.channels, name='✈️│عملیات-هوایی')
        if ops_channel and ops_channel != ctx.channel:
            await ops_channel.send(embed=embed)
        
        # در صورت اورژانسی، اطلاع‌رسانی فوری
        if status == 'اورژانسی':
            command_channel = discord.utils.get(ctx.guild.channels, name='🛩️│فرماندهی-هوایی')
            if command_channel:
                emergency_embed = create_embed(
                    "🚨 هشدار اورژانسی",
                    f"**ماموریت:** {mission_id}\n"
                    f"**خلبان:** {ctx.author.mention}\n"
                    f"**وضعیت:** اورژانسی\n\n"
                    f"**اقدام فوری مورد نیاز!**",
                    EMBED_COLORS['error']
                )
                await command_channel.send("@here", embed=emergency_embed)

    @tasks.loop(hours=6)
    async def daily_operations(self):
        """عملیات روزانه خودکار"""
        try:
            current_time = datetime.now()
            
            # گشت‌زنی خودکار
            if random.random() < 0.7:  # 70% احتمال گشت خودکار
                await self._auto_patrol()
            
            # بررسی تکمیل ماموریت‌ها
            await self._check_mission_completion()
            
            # به‌روزرسانی آمار
            self.operational_stats['total_sorties'] += random.randint(5, 15)
            
        except Exception as e:
            logger.error(f"خطا در عملیات روزانه نیروی هوایی: {e}")

    async def _auto_patrol(self):
        """گشت‌زنی خودکار"""
        try:
            # انتخاب هواپیمای مناسب برای گشت
            patrol_aircraft = []
            for aircraft_id, aircraft in self.aircraft_fleet.items():
                if aircraft['operational'] > 0 and 'گشت‌زنی' in aircraft['capabilities']:
                    patrol_aircraft.append((aircraft_id, aircraft))
            
            if not patrol_aircraft:
                return
            
            selected_aircraft_id, selected_aircraft = random.choice(patrol_aircraft)
            
            # مناطق گشت‌زنی
            patrol_areas = [
                'مرز شمالی (لبنان)',
                'مرز شرقی (سوریه)',
                'مرز جنوبی (غزه)',
                'دریای مدیترانه',
                'صحرای نگب',
                'آسمان تل‌آویو'
            ]
            
            patrol_area = random.choice(patrol_areas)
            
            # ایجاد ماموریت گشت خودکار
            mission_id = f"AUTO-{self.mission_counter}"
            self.mission_counter += 1
            
            mission_data = {
                'id': mission_id,
                'type': 'گشت خودکار',
                'aircraft_type': selected_aircraft_id,
                'aircraft_name': selected_aircraft['name'],
                'target_area': patrol_area,
                'pilot': 'سیستم خودکار',
                'start_time': datetime.now(),
                'duration_minutes': random.randint(90, 180),
                'status': 'خودکار',
                'cost': selected_aircraft['cost_per_hour'] * 2,
                'fuel_consumed': random.randint(800, 1500),
                'success_probability': random.randint(92, 98)
            }
            
            self.active_missions[mission_id] = mission_data
            selected_aircraft['operational'] -= 1
            
            # اطلاع‌رسانی
            guild = self.get_guild(GUILD_ID)
            if guild:
                ops_channel = discord.utils.get(guild.channels, name='✈️│عملیات-هوایی')
                if ops_channel:
                    embed = create_embed(
                        "🔄 گشت خودکار آغاز شد",
                        f"**ماموریت:** {mission_id}\n"
                        f"**هواپیما:** {selected_aircraft['name']}\n"
                        f"**منطقه:** {patrol_area}\n"
                        f"**مدت:** {mission_data['duration_minutes']} دقیقه",
                        EMBED_COLORS['primary']
                    )
                    await ops_channel.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"خطا در گشت خودکار: {e}")

    async def _check_mission_completion(self):
        """بررسی تکمیل ماموریت‌ها"""
        try:
            current_time = datetime.now()
            completed_missions = []
            
            for mission_id, mission in self.active_missions.items():
                elapsed_time = current_time - mission['start_time']
                if elapsed_time.total_seconds() >= mission['duration_minutes'] * 60:
                    completed_missions.append(mission_id)
            
            for mission_id in completed_missions:
                await self._complete_mission(mission_id)
                
        except Exception as e:
            logger.error(f"خطا در بررسی تکمیل ماموریت‌ها: {e}")

    async def _complete_mission(self, mission_id: str):
        """تکمیل ماموریت"""
        try:
            if mission_id not in self.active_missions:
                return
            
            mission = self.active_missions[mission_id]
            
            # بازگرداندن هواپیما
            aircraft = self.aircraft_fleet[mission['aircraft_type']]
            aircraft['operational'] += 1
            
            # به‌روزرسانی آمار
            if mission['type'] in ['حمله', 'رزمی']:
                self.operational_stats['combat_missions'] += 1
                if random.random() < 0.9:  # 90% موفقیت
                    self.operational_stats['ground_targets_destroyed'] += random.randint(1, 3)
            elif mission['type'] in ['شناسایی', 'نظارت']:
                self.operational_stats['reconnaissance_missions'] += 1
            else:
                self.operational_stats['training_flights'] += 1
            
            # تعیین نتیجه ماموریت
            success = random.random() < (mission['success_probability'] / 100)
            result = "موفقیت‌آمیز" if success else "نیمه‌موفق"
            
            # حذف از ماموریت‌های فعال
            del self.active_missions[mission_id]
            
            # اطلاع‌رسانی
            guild = self.get_guild(GUILD_ID)
            if guild:
                ops_channel = discord.utils.get(guild.channels, name='✈️│عملیات-هوایی')
                if ops_channel:
                    embed = create_embed(
                        f"✅ ماموریت {mission_id} تکمیل شد",
                        f"**نوع:** {mission['type']}\n"
                        f"**هواپیما:** {mission['aircraft_name']}\n"
                        f"**خلبان:** {mission['pilot']}\n"
                        f"**منطقه:** {mission['target_area']}\n"
                        f"**نتیجه:** {result}\n"
                        f"**مدت:** {mission['duration_minutes']} دقیقه\n"
                        f"**هزینه:** ${mission['cost']:,.0f}",
                        EMBED_COLORS['success']
                    )
                    await ops_channel.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"خطا در تکمیل ماموریت {mission_id}: {e}")

    @tasks.loop(hours=8)
    async def maintenance_cycle(self):
        """چرخه تعمیر و نگهداری"""
        try:
            for aircraft_id, aircraft in self.aircraft_fleet.items():
                # تکمیل تعمیرات
                if aircraft['maintenance'] > 0:
                    # احتمال 40% تکمیل یک تعمیر
                    if random.random() < 0.4:
                        aircraft['maintenance'] -= 1
                        aircraft['operational'] += 1
                
                # نیاز به تعمیر جدید
                if aircraft['operational'] > 0:
                    # احتمال 5% نیاز به تعمیر
                    if random.random() < 0.05:
                        aircraft['operational'] -= 1
                        aircraft['maintenance'] += 1
                        
                # به‌روزرسانی آمار نگهداری
                self.operational_stats['maintenance_hours'] += random.randint(10, 50)
                        
        except Exception as e:
            logger.error(f"خطا در چرخه نگهداری: {e}")

    @tasks.loop(hours=4)
    async def training_flights(self):
        """پروازهای تمرینی خودکار"""
        try:
            # احتمال برگزاری تمرین
            if random.random() < 0.3:  # 30% احتمال
                # انتخاب هواپیمای تمرینی
                training_aircraft = []
                for aircraft_id, aircraft in self.aircraft_fleet.items():
                    if aircraft['training'] > 0:
                        training_aircraft.append((aircraft_id, aircraft))
                
                if training_aircraft:
                    selected_id, selected_aircraft = random.choice(training_aircraft)
                    
                    # به‌روزرسانی آمار
                    self.operational_stats['pilot_training_hours'] += random.randint(2, 6)
                    self.operational_stats['training_flights'] += 1
                    
                    # اطلاع‌رسانی
                    guild = self.get_guild(GUILD_ID)
                    if guild:
                        training_channel = discord.utils.get(guild.channels, name='🎓│آموزش-خلبانی')
                        if training_channel:
                            embed = create_embed(
                                "🎓 تمرین خلبانی",
                                f"**هواپیما:** {selected_aircraft['name']}\n"
                                f"**نوع تمرین:** پرواز معمول\n"
                                f"**مدت:** {random.randint(60, 120)} دقیقه",
                                EMBED_COLORS['primary']
                            )
                            await training_channel.send(embed=embed)
                            
        except Exception as e:
            logger.error(f"خطا در پروازهای تمرینی: {e}")

    @tasks.loop(hours=12)
    async def weather_monitoring(self):
        """نظارت بر وضعیت جوی"""
        try:
            # شرایط جوی تصادفی
            weather_conditions = [
                'آفتابی و صاف',
                'ابری متوسط',
                'ابری و بارانی',
                'طوفانی',
                'مه آلود',
                'باد شدید'
            ]
            
            current_weather = random.choice(weather_conditions)
            
            # تأثیر بر عملیات
            weather_impact = {
                'آفتابی و صاف': 'مطلوب',
                'ابری متوسط': 'قابل قبول',
                'ابری و بارانی': 'محدود',
                'طوفانی': 'متوقف',
                'مه آلود': 'محدود شدید',
                'باد شدید': 'محدود'
            }
            
            impact = weather_impact[current_weather]
            
            # اطلاع‌رسانی در صورت شرایط نامساعد
            if impact in ['محدود', 'محدود شدید', 'متوقف']:
                guild = self.get_guild(GUILD_ID)
                if guild:
                    ops_channel = discord.utils.get(guild.channels, name='✈️│عملیات-هوایی')
                    if ops_channel:
                        embed = create_embed(
                            "🌤️ هشدار جوی",
                            f"**وضعیت جوی:** {current_weather}\n"
                            f"**تأثیر بر پرواز:** {impact}\n"
                            f"**زمان:** {datetime.now().strftime('%H:%M')}",
                            EMBED_COLORS['warning'] if impact != 'متوقف' else EMBED_COLORS['error']
                        )
                        await ops_channel.send(embed=embed)
                        
        except Exception as e:
            logger.error(f"خطا در نظارت جوی: {e}")

async def run_air_force_bot():
    """اجرای ربات نیروی هوایی"""
    bot = IsraeliAirForceBot()
    try:
        await bot.start(DISCORD_BOT_TOKEN_AIR_FORCE)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات نیروی هوایی: {e}")

if __name__ == "__main__":
    """
    🛩️ ربات نیروی هوایی اسرائیل
    
    این ربات مسئول مدیریت کامل نیروی هوایی اسرائیل است و شامل:
    
    ✈️ ناوگان هوایی:
    - F-35I آدیر (جنگنده نسل 5)
    - F-16I سوفا (جنگنده چندمنظوره) 
    - F-15I رعم (جنگنده سنگین)
    - AH-64 آپاچی (بالگرد تهاجمی)
    - پهپادهای ایتان و هرمس
    
    🏭 پایگاه‌های هوایی:
    - نواتیم، رامون، تل نوف، پالماخیم
    
    🎯 قابلیت‌ها:
    - مدیریت ماموریت‌های هوایی
    - نظارت بر آمادگی ناوگان
    - آمار عملیاتی کامل
    - گشت‌زنی خودکار
    - تعمیر و نگهداری
    - آموزش خلبانی
    
    دستورات اصلی:
    !هوایی_وضعیت_ناوگان - وضعیت ناوگان
    !هوایی_پایگاه‌ها - پایگاه‌های هوایی  
    !هوایی_ماموریت - شروع ماموریت جدید
    !هوایی_ماموریت‌های_فعال - ماموریت‌های جاری
    !هوایی_آمار_عملیاتی - آمار کامل
    !هوایی_تغییر_آمادگی - تغییر DEFCON
    !هوایی_گزارش_خلبان - گزارش از ماموریت
    """
    
    import asyncio
    asyncio.run(run_air_force_bot())