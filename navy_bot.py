#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات نیروی دریایی اسرائیل (Israeli Navy)
Israeli Navy Bot

این ربات مسئول مدیریت کامل نیروی دریایی اسرائیل است:
- مدیریت ناوگان دریایی (زیردریایی‌ها، کشتی‌ها، قایق‌ها)
- عملیات دریایی و محاصره
- حفاظت سواحل و بنادر
- مبارزه با قاچاق و تهدیدات دریایی
- یگان شایطت 13 (کماندوهای دریایی)

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

class IsraeliNavyBot(commands.Bot):
    """
    ربات نیروی دریایی اسرائیل (Israeli Navy)
    "חיל הים הישראלי"
    
    مأموریت: حاکمیت بر آب‌های اسرائیل و حفاظت از سواحل
    شعار: "חיל הים - שולט בים" (نیروی دریایی - حاکم بر دریا)
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!دریایی_',
            intents=intents,
            help_command=None,
            description="⚓ نیروی دریایی اسرائیل - نگهبان دریاها"
        )
        
        self.db = DatabaseManager()
        
        # ناوگان زیردریایی
        self.submarine_fleet = {
            'INS_Tanin': {
                'name': 'زیردریایی تانین (תנין)',
                'class': 'Dolphin-2',
                'type': 'زیردریایی دیزل-الکتریک',
                'commissioned': 2014,
                'length': 68.8,  # متر
                'displacement': 2050,  # تن
                'max_depth': 350,  # متر
                'crew': 35,
                'max_speed_surface': 11,  # گره
                'max_speed_submerged': 20,  # گره
                'range': 4500,  # مایل دریایی
                'status': 'عملیاتی',
                'location': 'دریای مدیترانه',
                'mission': 'گشت‌زنی',
                'capabilities': [
                    'جاسوسی استراتژیک', 'حمله زیردریایی',
                    'عملیات مخفی', 'جمع‌آوری اطلاعات'
                ],
                'weapons': [
                    'اژدر DM2A4', 'موشک کروز Popeye Turbo',
                    'مین‌های دریایی', 'سیستم‌های جنگ الکترونیک'
                ]
            },
            
            'INS_Rahav': {
                'name': 'زیردریایی رهب (רהב)',
                'class': 'Dolphin-2',
                'type': 'زیردریایی دیزل-الکتریک',
                'commissioned': 2016,
                'length': 68.8,
                'displacement': 2050,
                'max_depth': 350,
                'crew': 35,
                'max_speed_surface': 11,
                'max_speed_submerged': 20,
                'range': 4500,
                'status': 'عملیاتی',
                'location': 'دریای سرخ',
                'mission': 'ماموریت ویژه',
                'capabilities': [
                    'حمله دوربرد', 'نظارت دریایی',
                    'عملیات ضدکشتی', 'پشتیبانی کماندو'
                ],
                'weapons': [
                    'اژدر DM2A4', 'موشک کروز',
                    'سیستم‌های پیشرفته ناوبری'
                ]
            },
            
            'INS_Dakar': {
                'name': 'زیردریایی دکار (דקר)',
                'class': 'Dolphin-1',
                'type': 'زیردریایی دیزل-الکتریک',
                'commissioned': 2000,
                'length': 57.3,
                'displacement': 1640,
                'max_depth': 300,
                'crew': 30,
                'max_speed_surface': 10,
                'max_speed_submerged': 17,
                'range': 4200,
                'status': 'عملیاتی',
                'location': 'بندر حیفا',
                'mission': 'آموزش',
                'capabilities': [
                    'گشت‌زنی ساحلی', 'آموزش خدمه',
                    'عملیات دفاعی', 'نظارت بندری'
                ],
                'weapons': [
                    'اژدر معمولی', 'سیستم سونار پیشرفته'
                ]
            }
        }
        
        # ناوگان سطحی
        self.surface_fleet = {
            'INS_Magen': {
                'name': 'ناوشکن مگن (מגן)',
                'class': 'Sa\'ar 6',
                'type': 'کورت موشک‌انداز',
                'commissioned': 2021,
                'length': 90,
                'displacement': 1900,
                'crew': 25,
                'max_speed': 26,  # گره
                'range': 2500,  # مایل دریایی
                'status': 'عملیاتی',
                'location': 'دریای مدیترانه',
                'mission': 'دفاع ساحلی',
                'capabilities': [
                    'دفاع هوایی', 'ضدکشتی', 'حمایت آتش',
                    'عملیات الکترونیک', 'نظارت راداری'
                ],
                'weapons': [
                    'سیستم Iron Dome دریایی', 'موشک Gabriel V',
                    'توپ 76mm', 'سیستم Phalanx CIWS'
                ]
            },
            
            'INS_Oz': {
                'name': 'ناوشکن عوز (עוז)',
                'class': 'Sa\'ar 6',
                'type': 'کورت موشک‌انداز',
                'commissioned': 2022,
                'length': 90,
                'displacement': 1900,
                'crew': 25,
                'max_speed': 26,
                'range': 2500,
                'status': 'عملیاتی',
                'location': 'دریای مدیترانه',
                'mission': 'گشت‌زنی',
                'capabilities': [
                    'شکار زیردریایی', 'دفاع منطقه‌ای',
                    'عملیات مشترک', 'پشتیبانی زمینی'
                ],
                'weapons': [
                    'سیستم C-Dome', 'موشک Harpoon',
                    'توپ اتوماتیک', 'اژدر سبک'
                ]
            },
            
            'INS_Atzmaut': {
                'name': 'ناوشکن عتزماعوت (עצמאות)',
                'class': 'Sa\'ar 5',
                'type': 'کورت موشک‌انداز',
                'commissioned': 1994,
                'length': 85.6,
                'displacement': 1275,
                'crew': 74,
                'max_speed': 33,
                'range': 3500,
                'status': 'عملیاتی',
                'location': 'بندر اشدود',
                'mission': 'آمادگی',
                'capabilities': [
                    'عملیات دوربرد', 'حمله ساحلی',
                    'اسکورت کاروان', 'عملیات امداد'
                ],
                'weapons': [
                    'موشک Harpoon', 'توپ 76mm Oto Melara',
                    'سیستم Phalanx', 'راکت انداز'
                ]
            }
        }
        
        # قایق‌های گشتی و سریع
        self.patrol_boats = {
            'Dvora_Class': {
                'name': 'کلاس دبورا (דבורה)',
                'type': 'قایق گشتی سریع',
                'count': 30,
                'operational': 28,
                'maintenance': 2,
                'length': 21.6,
                'crew': 9,
                'max_speed': 45,  # گره
                'range': 700,  # مایل دریایی
                'primary_role': 'گشت ساحلی',
                'capabilities': [
                    'گشت‌زنی سریع', 'مقابله با قاچاق',
                    'امداد و نجات', 'اسکورت'
                ],
                'weapons': [
                    'مسلسل سنگین 12.7mm', 'مسلسل 7.62mm',
                    'نارنجک دودزا', 'تجهیزات بازداشت'
                ],
                'bases': ['Haifa', 'Ashdod', 'Eilat']
            },
            
            'Shaldag_Class': {
                'name': 'کلاس شلدگ (שלדג)',
                'type': 'قایق تهاجمی سریع',
                'count': 12,
                'operational': 11,
                'maintenance': 1,
                'length': 25,
                'crew': 10,
                'max_speed': 50,
                'range': 500,
                'primary_role': 'عملیات ویژه',
                'capabilities': [
                    'حمله سریع', 'پشتیبانی کماندو',
                    'نفوذ ساحلی', 'عملیات شبانه'
                ],
                'weapons': [
                    'موشک Spike-ER', 'توپ 25mm',
                    'مسلسل‌های چندگانه', 'سیستم جنگ الکترونیک'
                ],
                'bases': ['Haifa', 'Eilat']
            }
        }
        
        # یگان شایطت 13 (کماندوهای دریایی)
        self.shayetet_13 = {
            'name': 'یگان شایطت 13 (שייטת 13)',
            'type': 'نیروی ویژه دریایی',
            'established': 1949,
            'total_personnel': 200,
            'operational': 180,
            'training': 15,
            'reserves': 5,
            'specializations': [
                'عملیات زیردریایی', 'شنا تاکتیکی',
                'تخریب زیردریایی', 'نجات گروگان',
                'نفوذ ساحلی', 'جاسوسی دریایی'
            ],
            'equipment': [
                'لباس‌های غواصی پیشرفته', 'تجهیزات تخریب',
                'قایق‌های نفوذی', 'سلاح‌های ضدآب'
            ],
            'recent_missions': [
                'نابودی تونل‌های دریایی غزه',
                'عملیات نجات در دریای سرخ',
                'مأموریت اطلاعاتی در لبنان'
            ],
            'bases': ['Atlit', 'Eilat'],
            'motto': 'במים, ביבשה, באוויר (در آب، خشکی، هوا)'
        }
        
        # مناطق دریایی تحت کنترل
        self.naval_zones = {
            'Mediterranean_North': {
                'name': 'شمال دریای مدیترانه',
                'coordinates': (33.0, 35.1),
                'area': 12000,  # کیلومتر مربع
                'threat_level': 'متوسط',
                'main_threats': ['حزب‌الله', 'قایق‌های انتحاری', 'موشک‌های ساحلی'],
                'patrol_frequency': 'روزانه',
                'assigned_vessels': ['INS_Magen', 'Dvora_Class'],
                'strategic_importance': 'بالا',
                'status': 'تحت کنترل کامل'
            },
            
            'Mediterranean_Central': {
                'name': 'مرکز دریای مدیترانه',
                'coordinates': (32.0, 34.8),
                'area': 15000,
                'threat_level': 'پایین',
                'main_threats': ['قاچاق', 'کشتی‌های مشکوک'],
                'patrol_frequency': 'هفتگی',
                'assigned_vessels': ['INS_Oz', 'INS_Atzmaut'],
                'strategic_importance': 'متوسط',
                'status': 'گشت‌زنی معمول'
            },
            
            'Gaza_Waters': {
                'name': 'آب‌های غزه',
                'coordinates': (31.5, 34.3),
                'area': 2000,
                'threat_level': 'بالا',
                'main_threats': ['غواصان تهاجمی', 'قایق‌های انفجاری', 'راکت‌های ساحلی'],
                'patrol_frequency': '24/7',
                'assigned_vessels': ['Shaldag_Class', 'Dvora_Class', 'Shayetet_13'],
                'strategic_importance': 'بحرانی',
                'status': 'محاصره کامل'
            },
            
            'Red_Sea': {
                'name': 'دریای سرخ (خلیج عقبه)',
                'coordinates': (29.5, 34.9),
                'area': 8000,
                'threat_level': 'متوسط',
                'main_threats': ['ایران', 'حوثی‌ها', 'قاچاق اسلحه'],
                'patrol_frequency': 'روزانه',
                'assigned_vessels': ['INS_Rahav', 'Shaldag_Class'],
                'strategic_importance': 'بالا',
                'status': 'نظارت فعال'
            }
        }
        
        # بنادر و پایگاه‌های دریایی
        self.naval_bases = {
            'Haifa': {
                'name': 'پایگاه دریایی حیفا',
                'type': 'پایگاه اصلی',
                'location': 'حیفا',
                'coordinates': (32.8, 35.0),
                'established': 1948,
                'personnel': 2500,
                'facilities': [
                    'اسکله زیردریایی', 'تعمیرگاه کشتی',
                    'انبار مهمات', 'مرکز فرماندهی',
                    'بیمارستان دریایی', 'آکادمی نیروی دریایی'
                ],
                'stationed_vessels': ['INS_Dakar', 'INS_Atzmaut', 'Dvora_Class'],
                'security_level': 'بالا',
                'status': 'فعال'
            },
            
            'Ashdod': {
                'name': 'پایگاه دریایی اشدود',
                'type': 'پایگاه عملیاتی',
                'location': 'اشدود',
                'coordinates': (31.8, 34.6),
                'established': 1956,
                'personnel': 800,
                'facilities': [
                    'اسکله قایق‌های سریع', 'مرکز کنترل ترافیک',
                    'تأسیسات نگهداری', 'برج مراقبت'
                ],
                'stationed_vessels': ['Dvora_Class', 'Shaldag_Class'],
                'security_level': 'متوسط',
                'status': 'فعال'
            },
            
            'Eilat': {
                'name': 'پایگاه دریایی ایلات',
                'type': 'پایگاه استراتژیک',
                'location': 'ایلات',
                'coordinates': (29.5, 34.9),
                'established': 1951,
                'personnel': 600,
                'facilities': [
                    'اسکله عمیق', 'مرکز جنگ الکترونیک',
                    'پادگان شایطت 13', 'سیستم راداری'
                ],
                'stationed_vessels': ['INS_Rahav', 'Shaldag_Class'],
                'security_level': 'بالا',
                'status': 'فعال'
            }
        }
        
        # عملیات دریایی فعال
        self.active_naval_operations = {}
        self.operation_counter = 3000
        
        # آمار عملیاتی
        self.naval_stats = {
            'total_patrols': 3247,
            'smuggling_intercepted': 156,
            'suspicious_vessels_boarded': 89,
            'rescue_operations': 67,
            'special_operations': 23,
            'naval_miles_patrolled': 125000,
            'training_exercises': 145,
            'port_security_checks': 1200,
            'maritime_arrests': 78,
            'weapons_seized': 234
        }
        
        # وضعیت آمادگی دریایی
        self.naval_readiness = 'CONDITION_YELLOW'
        self.blockade_status = 'فعال'
        
        # پرسنل دریایی
        self.naval_personnel = {
            'officers': 450,
            'petty_officers': 800,
            'sailors': 2200,
            'submarine_crew': 180,
            'shayetet_13': 200,
            'naval_engineers': 300,
            'medical_staff': 80,
            'trainees': 250
        }
        
    async def on_ready(self):
        """آماده‌سازی ربات نیروی دریایی"""
        print(f'⚓ {self.user} - מוכנים לשיט! (آماده دریانوردی!)')
        
        # شروع وظایف دوره‌ای
        if not self.coastal_patrol.is_running():
            self.coastal_patrol.start()
        if not self.blockade_enforcement.is_running():
            self.blockade_enforcement.start()
        if not self.submarine_operations.is_running():
            self.submarine_operations.start()
        if not self.vessel_maintenance.is_running():
            self.vessel_maintenance.start()
        if not self.maritime_intelligence.is_running():
            self.maritime_intelligence.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"آب‌های اسرائیل | {self.blockade_status} ⚓"
            )
        )
        
        # ایجاد کانال‌های اختصاصی
        guild = self.guilds[0] if self.guilds else None
        if guild:
            await self._setup_channels(guild)

    async def _setup_channels(self, guild):
        """ایجاد کانال‌های اختصاصی نیروی دریایی"""
        channels_to_create = [
            ('⚓│فرماندهی-دریایی', 'مرکز فرماندهی نیروی دریایی'),
            ('🌊│عملیات-دریایی', 'عملیات و ماموریت‌های دریایی'),
            ('🚢│کنترل-ناوگان', 'کنترل و هماهنگی ناوگان'),
            ('🏴‍☠️│محاصره-غزه', 'عملیات محاصره دریایی'),
            ('🤿│شایطت-13', 'یگان کماندوهای دریایی'),
            ('🛥️│گشت-ساحلی', 'گشت‌زنی و نظارت سواحل'),
            ('🔧│نگهداری-کشتی', 'تعمیر و نگهداری ناوگان'),
            ('📡│اطلاعات-دریایی', 'جمع‌آوری اطلاعات دریایی'),
            ('📊│گزارشات-دریایی', 'گزارشات و آمار دریایی')
        ]
        
        navy_category = await get_or_create_category(guild, "⚓ نیروی دریایی اسرائیل")
        
        for channel_name, description in channels_to_create:
            await get_or_create_channel(guild, channel_name, category=navy_category)

    @commands.command(name='وضعیت_ناوگان')
    async def fleet_status(self, ctx):
        """نمایش وضعیت کامل ناوگان دریایی"""
        
        # صفحه اول: زیردریایی‌ها
        embed1 = create_embed(
            "🚢 ناوگان زیردریایی اسرائیل",
            f"**وضعیت آمادگی:** {self.naval_readiness}\n**وضعیت محاصره:** {self.blockade_status}",
            EMBED_COLORS['primary']
        )
        
        for sub_id, submarine in self.submarine_fleet.items():
            # تعیین وضعیت بر اساس ماموریت
            if submarine['mission'] == 'ماموریت ویژه':
                status_emoji = "🔴"
                status_text = "ماموریت محرمانه"
            elif submarine['mission'] == 'گشت‌زنی':
                status_emoji = "🟡"
                status_text = "در حال گشت‌زنی"
            else:
                status_emoji = "🟢"
                status_text = "آماده"
            
            embed1.add_field(
                name=f"{status_emoji} {submarine['name']}",
                value=f"**کلاس:** {submarine['class']}\n"
                      f"**سال ساخت:** {submarine['commissioned']}\n"
                      f"**خدمه:** {submarine['crew']} نفر\n"
                      f"**جابجایی:** {submarine['displacement']} تن\n"
                      f"**عمق عملیاتی:** {submarine['max_depth']} متر\n"
                      f"**برد:** {submarine['range']} مایل دریایی\n"
                      f"**موقعیت:** {submarine['location']}\n"
                      f"**وضعیت:** {status_text}",
                inline=True
            )
        
        await ctx.send(embed=embed1)
        
        # صفحه دوم: کشتی‌های سطحی
        embed2 = create_embed(
            "⚔️ ناوگان سطحی اسرائیل",
            "کشتی‌های جنگی و کورت‌ها:",
            EMBED_COLORS['primary']
        )
        
        for ship_id, ship in self.surface_fleet.items():
            # تعیین وضعیت
            if ship['mission'] == 'دفاع ساحلی':
                status_emoji = "🔴"
                status_text = "آمادگی کامل"
            elif ship['mission'] == 'گشت‌زنی':
                status_emoji = "🟡"
                status_text = "در حال گشت"
            else:
                status_emoji = "🟢"
                status_text = "آماده"
            
            embed2.add_field(
                name=f"{status_emoji} {ship['name']}",
                value=f"**کلاس:** {ship['class']}\n"
                      f"**سال ساخت:** {ship['commissioned']}\n"
                      f"**خدمه:** {ship['crew']} نفر\n"
                      f"**جابجایی:** {ship['displacement']} تن\n"
                      f"**سرعت:** {ship['max_speed']} گره\n"
                      f"**برد:** {ship['range']} مایل دریایی\n"
                      f"**موقعیت:** {ship['location']}\n"
                      f"**وضعیت:** {status_text}",
                inline=True
            )
        
        await ctx.send(embed=embed2)
        
        # صفحه سوم: قایق‌های گشتی و شایطت 13
        embed3 = create_embed(
            "🛥️ قایق‌های گشتی و نیروهای ویژه",
            "قایق‌های سریع و یگان شایطت 13:",
            EMBED_COLORS['primary']
        )
        
        for boat_class_id, boat_class in self.patrol_boats.items():
            readiness = (boat_class['operational'] / boat_class['count']) * 100
            status_emoji = "🟢" if readiness >= 90 else "🟡" if readiness >= 75 else "🔴"
            
            embed3.add_field(
                name=f"{status_emoji} {boat_class['name']}",
                value=f"**نوع:** {boat_class['type']}\n"
                      f"**تعداد کل:** {boat_class['count']}\n"
                      f"**عملیاتی:** {boat_class['operational']}\n"
                      f"**تعمیرات:** {boat_class['maintenance']}\n"
                      f"**خدمه:** {boat_class['crew']} نفر\n"
                      f"**سرعت:** {boat_class['max_speed']} گره\n"
                      f"**نقش اصلی:** {boat_class['primary_role']}\n"
                      f"**آمادگی:** {readiness:.1f}%",
                inline=True
            )
        
        # شایطت 13
        shayetet_readiness = (self.shayetet_13['operational'] / self.shayetet_13['total_personnel']) * 100
        
        embed3.add_field(
            name="🏴‍☠️ یگان شایطت 13",
            value=f"**نوع:** {self.shayetet_13['type']}\n"
                  f"**تأسیس:** {self.shayetet_13['established']}\n"
                  f"**کل نیرو:** {self.shayetet_13['total_personnel']} نفر\n"
                  f"**عملیاتی:** {self.shayetet_13['operational']} نفر\n"
                  f"**آموزش:** {self.shayetet_13['training']} نفر\n"
                  f"**شعار:** {self.shayetet_13['motto']}\n"
                  f"**آمادگی:** {shayetet_readiness:.1f}%\n"
                  f"**وضعیت:** آماده عملیات ویژه",
            inline=True
        )
        
        await ctx.send(embed=embed3)

    @commands.command(name='مناطق_دریایی')
    async def naval_zones_status(self, ctx):
        """نمایش وضعیت مناطق دریایی تحت کنترل"""
        
        embed = create_embed(
            "🗺️ مناطق دریایی تحت کنترل",
            "وضعیت آب‌های اسرائیل:",
            EMBED_COLORS['primary']
        )
        
        threat_colors = {
            'بالا': '🔴',
            'متوسط': '🟡',
            'پایین': '🟢'
        }
        
        importance_colors = {
            'بحرانی': '🚨',
            'بالا': '🔴',
            'متوسط': '🟡'
        }
        
        for zone_id, zone in self.naval_zones.items():
            threat_emoji = threat_colors.get(zone['threat_level'], '⚪')
            importance_emoji = importance_colors.get(zone['strategic_importance'], '🔵')
            
            # محاسبه شناورهای مستقر
            assigned_vessels = []
            for vessel_type in zone['assigned_vessels']:
                if vessel_type in self.surface_fleet:
                    assigned_vessels.append(self.surface_fleet[vessel_type]['name'])
                elif vessel_type in self.patrol_boats:
                    assigned_vessels.append(self.patrol_boats[vessel_type]['name'])
                elif vessel_type == 'Shayetet_13':
                    assigned_vessels.append('یگان شایطت 13')
                else:
                    assigned_vessels.append(vessel_type.replace('_', ' '))
            
            embed.add_field(
                name=f"{threat_emoji} {zone['name']}",
                value=f"**مساحت:** {zone['area']:,} کیلومتر مربع\n"
                      f"**سطح تهدید:** {zone['threat_level']}\n"
                      f"**اهمیت استراتژیک:** {importance_emoji} {zone['strategic_importance']}\n"
                      f"**فرکانس گشت:** {zone['patrol_frequency']}\n"
                      f"**وضعیت:** {zone['status']}\n"
                      f"**تهدیدات اصلی:**\n" + 
                      "\n".join([f"• {threat}" for threat in zone['main_threats']]) + "\n" +
                      f"**شناورهای مستقر:**\n" +
                      "\n".join([f"• {vessel}" for vessel in assigned_vessels]),
                inline=True
            )
        
        # آمار کلی
        total_area = sum([zone['area'] for zone in self.naval_zones.values()])
        high_threat_zones = len([zone for zone in self.naval_zones.values() if zone['threat_level'] == 'بالا'])
        
        embed.add_field(
            name="📊 خلاصه کلی",
            value=f"**مجموع مساحت:** {total_area:,} کیلومتر مربع\n"
                  f"**مناطق پرخطر:** {high_threat_zones}\n"
                  f"**وضعیت کلی:** {'🟢 تحت کنترل' if high_threat_zones <= 1 else '🟡 نیاز به توجه'}\n"
                  f"**پوشش دریایی:** 100%",
            inline=False
        )
        
        embed.set_footer(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await ctx.send(embed=embed)

    @commands.command(name='ماموریت_دریایی')
    @has_role(['فرمانده دریایی', 'ناخدا', 'افسر عملیات', 'مدیر'])
    async def launch_naval_mission(self, ctx, mission_type: str, zone: str, vessel: str, *, objective: str = "هدف تعیین نشده"):
        """راه‌اندازی ماموریت دریایی جدید"""
        
        # انواع ماموریت مجاز
        valid_missions = {
            'گشت': 'گشت‌زنی دریایی',
            'محاصره': 'اجرای محاصره',
            'رهگیری': 'رهگیری کشتی مشکوک',
            'جاسوسی': 'جمع‌آوری اطلاعات',
            'امداد': 'عملیات امداد و نجات',
            'تمرین': 'تمرین دریایی',
            'اسکورت': 'اسکورت کشتی',
            'تخریب': 'عملیات تخریب زیردریایی',
            'ویژه': 'عملیات ویژه (شایطت 13)'
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
        
        # بررسی منطقه دریایی
        if zone not in self.naval_zones:
            embed = create_embed(
                "❌ منطقه نامعتبر",
                f"**مناطق دریایی موجود:**\n" + 
                "\n".join([f"• `{k}`: {v['name']}" for k, v in self.naval_zones.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی شناور
        vessel_data = None
        vessel_type = None
        
        if vessel in self.submarine_fleet:
            vessel_data = self.submarine_fleet[vessel]
            vessel_type = 'submarine'
        elif vessel in self.surface_fleet:
            vessel_data = self.surface_fleet[vessel]
            vessel_type = 'surface'
        elif vessel in self.patrol_boats:
            vessel_data = self.patrol_boats[vessel]
            vessel_type = 'patrol'
        elif vessel == 'Shayetet_13':
            vessel_data = self.shayetet_13
            vessel_type = 'special'
        
        if not vessel_data:
            all_vessels = (list(self.submarine_fleet.keys()) + 
                          list(self.surface_fleet.keys()) + 
                          list(self.patrol_boats.keys()) + 
                          ['Shayetet_13'])
            embed = create_embed(
                "❌ شناور نامعتبر",
                f"**شناورهای موجود:**\n" + 
                "\n".join([f"• `{v}`" for v in all_vessels[:15]]) +
                (f"\n• و {len(all_vessels)-15} شناور دیگر..." if len(all_vessels) > 15 else ""),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        zone_data = self.naval_zones[zone]
        
        # بررسی در دسترس بودن شناور
        if vessel_type == 'patrol':
            if vessel_data['operational'] < 1:
                embed = create_embed(
                    "❌ شناور در دسترس نیست",
                    f"**شناور:** {vessel_data['name']}\n"
                    f"**عملیاتی:** {vessel_data['operational']}\n"
                    f"**تعمیرات:** {vessel_data['maintenance']}",
                    EMBED_COLORS['error']
                )
                await ctx.send(embed=embed)
                return
        elif vessel_type == 'special':
            if vessel_data['operational'] < 10:  # حداقل 10 کماندو
                embed = create_embed(
                    "❌ نیروی کافی در دسترس نیست",
                    f"**یگان:** {vessel_data['name']}\n"
                    f"**نیروی عملیاتی:** {vessel_data['operational']}\n"
                    f"**حداقل مورد نیاز:** 10 نفر",
                    EMBED_COLORS['error']
                )
                await ctx.send(embed=embed)
                return
        else:  # submarine or surface
            if vessel_data['status'] != 'عملیاتی':
                embed = create_embed(
                    "❌ شناور آماده نیست",
                    f"**شناور:** {vessel_data['name']}\n"
                    f"**وضعیت فعلی:** {vessel_data['status']}\n"
                    f"**ماموریت فعلی:** {vessel_data.get('mission', 'نامشخص')}",
                    EMBED_COLORS['error']
                )
                await ctx.send(embed=embed)
                return
        
        # بررسی مناسب بودن شناور برای ماموریت
        mission_vessel_compatibility = {
            'گشت': ['patrol', 'surface'],
            'محاصره': ['surface', 'patrol'],
            'رهگیری': ['surface', 'patrol'],
            'جاسوسی': ['submarine', 'special'],
            'امداد': ['surface', 'patrol'],
            'تمرین': ['submarine', 'surface', 'patrol', 'special'],
            'اسکورت': ['surface'],
            'تخریب': ['submarine', 'special'],
            'ویژه': ['special']
        }
        
        if vessel_type not in mission_vessel_compatibility.get(mission_type, []):
            embed = create_embed(
                "⚠️ شناور نامناسب",
                f"**ماموریت:** {mission_type}\n"
                f"**شناور:** {vessel_data['name']}\n"
                f"**انواع شناور مناسب:** {', '.join(mission_vessel_compatibility.get(mission_type, []))}\n"
                "ماموریت ادامه می‌یابد اما ممکن است کارایی کمتری داشته باشد.",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
        
        # ایجاد ماموریت
        mission_id = f"NAV-{self.operation_counter}"
        self.operation_counter += 1
        
        # محاسبه مدت ماموریت
        base_duration = {
            'گشت': 360,      # 6 ساعت
            'محاصره': 720,    # 12 ساعت
            'رهگیری': 240,    # 4 ساعت
            'جاسوسی': 480,    # 8 ساعت
            'امداد': 180,     # 3 ساعت
            'تمرین': 120,     # 2 ساعت
            'اسکورت': 300,    # 5 ساعت
            'تخریب': 180,     # 3 ساعت
            'ویژه': 240      # 4 ساعت
        }
        
        duration = base_duration.get(mission_type, 240)
        duration += random.randint(-60, 120)  # تنوع زمانی
        duration = max(60, duration)
        
        # محاسبه نیروی درگیر
        if vessel_type == 'special':
            personnel = random.randint(10, 30)
        elif vessel_type == 'patrol':
            personnel = vessel_data['crew']
        else:
            personnel = vessel_data['crew']
        
        # محاسبه ریسک
        base_risk = {
            'بالا': 30,
            'متوسط': 20,
            'پایین': 10
        }[zone_data['threat_level']]
        
        mission_risk = {
            'گشت': 10,
            'محاصره': 25,
            'رهگیری': 20,
            'جاسوسی': 35,
            'امداد': 15,
            'تمرین': 5,
            'اسکورت': 15,
            'تخریب': 40,
            'ویژه': 45
        }[mission_type]
        
        total_risk = min(90, base_risk + mission_risk)
        success_probability = 100 - total_risk
        
        # محاسبه هزینه
        if vessel_type == 'patrol':
            cost = 5000 * (duration / 60)
        elif vessel_type == 'surface':
            cost = 15000 * (duration / 60)
        elif vessel_type == 'submarine':
            cost = 25000 * (duration / 60)
        else:  # special
            cost = 20000 * (duration / 60)
        
        operation_data = {
            'id': mission_id,
            'type': mission_type,
            'description': valid_missions[mission_type],
            'zone': zone,
            'zone_name': zone_data['name'],
            'vessel': vessel,
            'vessel_name': vessel_data['name'],
            'vessel_type': vessel_type,
            'objective': objective,
            'commander': ctx.author.display_name,
            'personnel_involved': personnel,
            'start_time': datetime.now(),
            'duration_minutes': duration,
            'status': 'در حال انجام',
            'risk_level': total_risk,
            'success_probability': success_probability,
            'cost': cost
        }
        
        # ذخیره ماموریت
        self.active_naval_operations[mission_id] = operation_data
        
        # تغییر وضعیت شناور
        if vessel_type == 'patrol':
            vessel_data['operational'] -= 1
        elif vessel_type == 'special':
            vessel_data['operational'] -= personnel
        else:
            vessel_data['status'] = 'در ماموریت'
            vessel_data['mission'] = mission_type
        
        # تولید توضیحات ماموریت
        mission_prompt = f"""
        یک ماموریت {mission_type} دریایی در {zone_data['name']} با {vessel_data['name']} آغاز شده است.
        هدف ماموریت: {objective}
        فرمانده: {ctx.author.display_name}
        سطح تهدید: {zone_data['threat_level']}
        نیروی درگیر: {personnel} نفر
        
        یک توضیح دریایی و تاکتیکی از این ماموریت بنویس (120-180 کلمه).
        از اصطلاحات دریایی و نظامی استفاده کن.
        """
        
        try:
            mission_description = await generate_text_with_gemini(mission_prompt)
        except Exception as e:
            logger.error(f"خطا در تولید توضیحات ماموریت: {e}")
            mission_description = f"ماموریت {mission_type} در {zone_data['name']} با هدف {objective} آغاز شد."
        
        # تعیین رنگ embed بر اساس ریسک
        if total_risk <= 20:
            embed_color = EMBED_COLORS['success']
            risk_emoji = "🟢"
        elif total_risk <= 35:
            embed_color = EMBED_COLORS['warning']
            risk_emoji = "🟡"
        else:
            embed_color = EMBED_COLORS['error']
            risk_emoji = "🔴"
        
        # ارسال پیام تأیید
        embed = create_embed(
            f"⚓ ماموریت {mission_type.upper()} آغاز شد",
            f"**شماره ماموریت:** `{mission_id}`\n"
            f"**نوع:** {valid_missions[mission_type]}\n"
            f"**منطقه:** {zone_data['name']}\n"
            f"**شناور:** {vessel_data['name']}\n"
            f"**فرمانده:** {ctx.author.mention}\n"
            f"**هدف:** {objective}\n"
            f"**نیروی درگیر:** {personnel} نفر\n"
            f"**مدت تخمینی:** {duration} دقیقه\n"
            f"**سطح ریسک:** {risk_emoji} {total_risk}%\n"
            f"**احتمال موفقیت:** {success_probability}%\n"
            f"**هزینه عملیاتی:** ${operation_data['cost']:,.0f}\n\n"
            f"**جزئیات ماموریت:**\n{mission_description}",
            embed_color
        )
        
        embed.set_footer(text=f"شروع: {datetime.now().strftime('%H:%M')} | تکمیل تقریبی: {(datetime.now() + timedelta(minutes=duration)).strftime('%H:%M')}")
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830284.png")
        
        await ctx.send(embed=embed)
        
        # اطلاع‌رسانی به کانال عملیات
        ops_channel = discord.utils.get(ctx.guild.channels, name='🌊│عملیات-دریایی')
        if ops_channel:
            ops_embed = create_embed(
                "⚓ ماموریت دریایی جدید",
                f"**{mission_id}** - {mission_type} در {zone_data['name']} توسط {ctx.author.mention}",
                EMBED_COLORS['primary']
            )
            await ops_channel.send(embed=ops_embed)
        
        # ماموریت‌های ویژه به کانال شایطت 13
        if mission_type == 'ویژه' or vessel == 'Shayetet_13':
            shayetet_channel = discord.utils.get(ctx.guild.channels, name='🤿│شایطت-13')
            if shayetet_channel:
                special_embed = create_embed(
                    "🏴‍☠️ ماموریت ویژه شایطت 13",
                    f"**کد ماموریت:** {mission_id}\n"
                    f"**طبقه‌بندی:** محرمانه\n"
                    f"**نیروی اعزامی:** {personnel} کماندو",
                    EMBED_COLORS['error']
                )
                await shayetet_channel.send(embed=special_embed)

    @commands.command(name='عملیات_فعال')
    async def active_naval_operations_status(self, ctx):
        """نمایش ماموریت‌های دریایی در حال انجام"""
        
        if not self.active_naval_operations:
            embed = create_embed(
                "📋 ماموریت‌های دریایی فعال",
                "در حال حاضر هیچ ماموریت دریایی در جریان نیست.\n\n"
                "⚓ آب‌های اسرائیل آرام است",
                EMBED_COLORS['primary']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            "🌊 ماموریت‌های دریایی فعال",
            f"تعداد ماموریت در حال انجام: **{len(self.active_naval_operations)}**",
            EMBED_COLORS['primary']
        )
        
        for mission_id, mission in list(self.active_naval_operations.items())[:6]:  # نمایش حداکثر 6 ماموریت
            elapsed_time = datetime.now() - mission['start_time']
            elapsed_minutes = int(elapsed_time.total_seconds() / 60)
            remaining_minutes = mission['duration_minutes'] - elapsed_minutes
            
            if remaining_minutes > 0:
                if remaining_minutes > 60:
                    hours = remaining_minutes // 60
                    minutes = remaining_minutes % 60
                    status_text = f"⏳ {hours}:{minutes:02d} باقیمانده"
                else:
                    status_text = f"⏳ {remaining_minutes} دقیقه باقیمانده"
                status_emoji = "🟡"
            else:
                status_text = "✅ آماده بازگشت به بندر"
                status_emoji = "🟢"
            
            # تعیین ایموجی ریسک
            risk_emoji = "🟢" if mission['risk_level'] <= 20 else "🟡" if mission['risk_level'] <= 35 else "🔴"
            
            # تعیین ایموجی نوع شناور
            vessel_emoji = {
                'submarine': '🚢',
                'surface': '⚔️',
                'patrol': '🛥️',
                'special': '🏴‍☠️'
            }.get(mission['vessel_type'], '⚓')
            
            # محاسبه پیشرفت
            progress = min(100, (elapsed_minutes / mission['duration_minutes']) * 100)
            progress_bar = "█" * int(progress / 12.5) + "░" * (8 - int(progress / 12.5))
            
            embed.add_field(
                name=f"{status_emoji} {mission['id']}",
                value=f"**نوع:** {mission['type']}\n"
                      f"**منطقه:** {mission['zone_name']}\n"
                      f"**شناور:** {vessel_emoji} {mission['vessel_name']}\n"
                      f"**فرمانده:** {mission['commander']}\n"
                      f"**نیرو:** {mission['personnel_involved']} نفر\n"
                      f"**ریسک:** {risk_emoji} {mission['risk_level']}%\n"
                      f"**پیشرفت:** {progress:.1f}%\n"
                      f"`{progress_bar}`\n"
                      f"**وضعیت:** {status_text}",
                inline=True
            )
        
        if len(self.active_naval_operations) > 6:
            embed.add_field(
                name="📊 سایر ماموریت‌ها",
                value=f"و {len(self.active_naval_operations) - 6} ماموریت دیگر در حال انجام...",
                inline=False
            )
        
        # آمار کلی
        total_personnel = sum([op['personnel_involved'] for op in self.active_naval_operations.values()])
        high_risk_ops = len([op for op in self.active_naval_operations.values() if op['risk_level'] > 35])
        submarine_ops = len([op for op in self.active_naval_operations.values() if op['vessel_type'] == 'submarine'])
        special_ops = len([op for op in self.active_naval_operations.values() if op['vessel_type'] == 'special'])
        
        embed.add_field(
            name="📈 آمار فعال",
            value=f"**کل نیروی درگیر:** {total_personnel:,} نفر\n"
                  f"**ماموریت‌های پرریسک:** {high_risk_ops}\n"
                  f"**عملیات زیردریایی:** {submarine_ops}\n"
                  f"**عملیات ویژه:** {special_ops}",
            inline=False
        )
        
        embed.set_footer(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        await ctx.send(embed=embed)

    @commands.command(name='آمار_دریایی')
    @has_role(['فرمانده دریایی', 'افسر عملیات', 'مدیر'])
    async def naval_statistics(self, ctx):
        """نمایش آمار کامل عملیاتی نیروی دریایی"""
        
        embed = create_embed(
            "📊 آمار عملیاتی نیروی دریایی اسرائیل",
            f"**دوره گزارش:** سال جاری\n**آخرین به‌روزرسانی:** {datetime.now().strftime('%Y/%m/%d')}",
            EMBED_COLORS['primary']
        )
        
        # آمار عملیات دریایی
        embed.add_field(
            name="⚓ آمار عملیات",
            value=f"**کل گشت‌زنی‌ها:** {self.naval_stats['total_patrols']:,}\n"
                  f"**مایل دریایی طی شده:** {self.naval_stats['naval_miles_patrolled']:,}\n"
                  f"**تمرینات دریایی:** {self.naval_stats['training_exercises']:,}\n"
                  f"**عملیات امداد:** {self.naval_stats['rescue_operations']:,}\n"
                  f"**عملیات ویژه:** {self.naval_stats['special_operations']:,}",
            inline=True
        )
        
        # آمار امنیتی
        embed.add_field(
            name="🔒 آمار امنیتی",
            value=f"**قاچاق جلوگیری شده:** {self.naval_stats['smuggling_intercepted']:,}\n"
                  f"**کشتی‌های بازرسی شده:** {self.naval_stats['suspicious_vessels_boarded']:,}\n"
                  f"**دستگیری‌های دریایی:** {self.naval_stats['maritime_arrests']:,}\n"
                  f"**اسلحه کشف شده:** {self.naval_stats['weapons_seized']:,}\n"
                  f"**بازرسی بندری:** {self.naval_stats['port_security_checks']:,}",
            inline=True
        )
        
        # آمار ناوگان
        total_submarines = len(self.submarine_fleet)
        operational_submarines = len([sub for sub in self.submarine_fleet.values() if sub['status'] == 'عملیاتی'])
        
        total_surface = len(self.surface_fleet)
        operational_surface = len([ship for ship in self.surface_fleet.values() if ship['status'] == 'عملیاتی'])
        
        total_patrol = sum([boat['count'] for boat in self.patrol_boats.values()])
        operational_patrol = sum([boat['operational'] for boat in self.patrol_boats.values()])
        
        embed.add_field(
            name="🚢 آمار ناوگان",
            value=f"**زیردریایی‌ها:** {operational_submarines}/{total_submarines}\n"
                  f"**کشتی‌های سطحی:** {operational_surface}/{total_surface}\n"
                  f"**قایق‌های گشتی:** {operational_patrol}/{total_patrol}\n"
                  f"**شایطت 13:** {self.shayetet_13['operational']}/{self.shayetet_13['total_personnel']}\n"
                  f"**آمادگی کلی:** {((operational_submarines + operational_surface + operational_patrol) / (total_submarines + total_surface + total_patrol) * 100):.1f}%",
            inline=True
        )
        
        # آمار پرسنل
        total_personnel = sum(self.naval_personnel.values())
        
        embed.add_field(
            name="👥 آمار نیرو",
            value=f"**کل پرسنل:** {total_personnel:,} نفر\n"
                  f"**افسران:** {self.naval_personnel['officers']:,}\n"
                  f"**درجه‌داران:** {self.naval_personnel['petty_officers']:,}\n"
                  f"**ملوانان:** {self.naval_personnel['sailors']:,}\n"
                  f"**خدمه زیردریایی:** {self.naval_personnel['submarine_crew']:,}\n"
                  f"**شایطت 13:** {self.naval_personnel['shayetet_13']:,}",
            inline=True
        )
        
        # محاسبه هزینه‌های عملیاتی
        submarine_daily_cost = len(self.submarine_fleet) * 50000  # 50K per day per submarine
        surface_daily_cost = len(self.surface_fleet) * 30000     # 30K per day per surface ship
        patrol_daily_cost = operational_patrol * 2000           # 2K per day per patrol boat
        
        total_daily_cost = submarine_daily_cost + surface_daily_cost + patrol_daily_cost
        monthly_cost = total_daily_cost * 30
        
        embed.add_field(
            name="💰 اقتصادی",
            value=f"**هزینه عملیاتی روزانه:** ${total_daily_cost:,.0f}\n"
                  f"**هزینه ماهانه:** ${monthly_cost:,.0f}\n"
                  f"**متوسط هزینه ماموریت:** ${monthly_cost / max(1, self.naval_stats['total_patrols']):,.0f}\n"
                  f"**صرفه‌جویی سوخت:** 15%\n"
                  f"**بازده عملیاتی:** بالا",
            inline=True
        )
        
        # وضعیت آمادگی
        embed.add_field(
            name="⚡ وضعیت آمادگی",
            value=f"**سطح آمادگی:** {self.naval_readiness}\n"
                  f"**وضعیت محاصره:** {self.blockade_status}\n"
                  f"**زمان پاسخ:** <30 دقیقه\n"
                  f"**پوشش دریایی:** 100%\n"
                  f"**عملیات 24/7:** ✅",
            inline=True
        )
        
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Israel_Defense_Forces_Logo.svg/200px-Israel_Defense_Forces_Logo.svg.png")
        embed.set_footer(text="שולטים בים | حاکمان دریا")
        
        await ctx.send(embed=embed)

    @commands.command(name='وضعیت_محاصره')
    @has_role(['فرمانده دریایی', 'افسر عملیات', 'مدیر'])
    async def blockade_status(self, ctx):
        """نمایش وضعیت محاصره دریایی غزه"""
        
        gaza_zone = self.naval_zones.get('Gaza_Waters', {})
        
        embed = create_embed(
            "🚫 وضعیت محاصره دریایی غزه",
            f"**وضعیت:** {self.blockade_status}\n**آخرین به‌روزرسانی:** {datetime.now().strftime('%H:%M')}",
            EMBED_COLORS['error']
        )
        
        # اطلاعات منطقه
        embed.add_field(
            name="🗺️ اطلاعات منطقه",
            value=f"**نام:** {gaza_zone.get('name', 'آب‌های غزه')}\n"
                  f"**مساحت:** {gaza_zone.get('area', 2000):,} کیلومتر مربع\n"
                  f"**سطح تهدید:** {gaza_zone.get('threat_level', 'بالا')}\n"
                  f"**اهمیت:** {gaza_zone.get('strategic_importance', 'بحرانی')}\n"
                  f"**نظارت:** {gaza_zone.get('patrol_frequency', '24/7')}",
            inline=True
        )
        
        # نیروهای مستقر
        assigned_vessels = gaza_zone.get('assigned_vessels', [])
        vessel_details = []
        
        for vessel_type in assigned_vessels:
            if vessel_type in self.patrol_boats:
                vessel_details.append(f"• {self.patrol_boats[vessel_type]['name']}: {self.patrol_boats[vessel_type]['operational']} قایق")
            elif vessel_type == 'Shayetet_13':
                vessel_details.append(f"• یگان شایطت 13: {self.shayetet_13['operational']} کماندو")
        
        embed.add_field(
            name="⚔️ نیروهای مستقر",
            value="\n".join(vessel_details) if vessel_details else "اطلاعات محرمانه",
            inline=True
        )
        
        # تهدیدات شناسایی شده
        threats = gaza_zone.get('main_threats', [])
        embed.add_field(
            name="🎯 تهدیدات اصلی",
            value="\n".join([f"• {threat}" for threat in threats]),
            inline=True
        )
        
        # آمار محاصره (تصادفی برای نمونه)
        blocked_attempts = random.randint(15, 45)
        inspected_vessels = random.randint(8, 25)
        seized_items = random.randint(3, 12)
        
        embed.add_field(
            name="📊 آمار این ماه",
            value=f"**تلاش‌های مسدود شده:** {blocked_attempts}\n"
                  f"**کشتی‌های بازرسی شده:** {inspected_vessels}\n"
                  f"**اقلام کشف شده:** {seized_items}\n"
                  f"**درصد موفقیت:** 98.5%\n"
                  f"**حوادث امنیتی:** 0",
            inline=True
        )
        
        # وضعیت فعلی
        current_status = [
            "✅ محاصره کامل فعال",
            "✅ تمام مسیرهای دریایی تحت کنترل",
            "✅ گشت‌زنی 24 ساعته",
            "✅ آمادگی کامل نیروها",
            "✅ هماهنگی با نیروی هوایی"
        ]
        
        embed.add_field(
            name="🔍 وضعیت فعلی",
            value="\n".join(current_status),
            inline=True
        )
        
        # هشدارها
        embed.add_field(
            name="⚠️ هشدارهای فعال",
            value="• ممنوعیت ورود کشتی‌ها بدون مجوز\n"
                  "• تهدید فوری علیه ناقضین\n"
                  "• نظارت راداری مداوم\n"
                  "• آمادگی کامل واحدهای ویژه",
            inline=True
        )
        
        embed.set_footer(text="محاصره به دستور فرماندهی کل و طبق قوانین بین‌المللی")
        await ctx.send(embed=embed)

    @commands.command(name='گزارش_دریایی')
    @has_role(['ناخدا', 'افسر عملیات', 'کماندو'])
    async def naval_report(self, ctx, mission_id: str, status: str, *, details: str = ""):
        """گزارش از ماموریت دریایی"""
        
        if mission_id not in self.active_naval_operations:
            embed = create_embed(
                "❌ ماموریت یافت نشد",
                f"ماموریت با شماره `{mission_id}` یافت نشد یا تکمیل شده است.",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        mission = self.active_naval_operations[mission_id]
        
        # بررسی دسترسی
        if mission['commander'] != ctx.author.display_name and not any(role.name in ['فرمانده دریایی', 'مدیر'] for role in ctx.author.roles):
            embed = create_embed(
                "❌ عدم دسترسی",
                "فقط فرمانده ماموریت یا فرماندهان ارشد می‌توانند گزارش ارسال کنند.",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        valid_statuses = ['موفق', 'ناموفق', 'در_حال_انجام', 'نیاز_به_پشتیبانی', 'اورژانسی', 'هدف_شناسایی', 'تماس_دشمن']
        
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
            'reporter': ctx.author.display_name,
            'status': status,
            'details': details,
            'coordinates': f"{random.randint(29, 34)}.{random.randint(100, 999)}°N, {random.randint(34, 36)}.{random.randint(100, 999)}°E"
        }
        
        mission['reports'].append(report)
        
        # تعیین رنگ و ایموجی
        status_info = {
            'موفق': ('🟢', 'ماموریت با موفقیت انجام شد', EMBED_COLORS['success']),
            'ناموفق': ('🔴', 'ماموریت ناموفق بود', EMBED_COLORS['error']),
            'در_حال_انجام': ('🟡', 'ماموریت در حال انجام', EMBED_COLORS['warning']),
            'نیاز_به_پشتیبانی': ('🟠', 'نیاز به پشتیبانی فوری', EMBED_COLORS['warning']),
            'اورژانسی': ('🚨', 'وضعیت اورژانسی!', EMBED_COLORS['error']),
            'هدف_شناسایی': ('🎯', 'هدف شناسایی شده', EMBED_COLORS['primary']),
            'تماس_دشمن': ('⚔️', 'تماس با نیروی دشمن', EMBED_COLORS['error'])
        }
        
        emoji, description, color = status_info[status]
        
        embed = create_embed(
            f"{emoji} گزارش دریایی - {mission_id}",
            f"**وضعیت:** {description}\n"
            f"**گزارش‌دهنده:** {ctx.author.mention}\n"
            f"**ماموریت:** {mission['type']} در {mission['zone_name']}\n"
            f"**شناور:** {mission['vessel_name']}\n"
            f"**موقعیت تقریبی:** {report['coordinates']}\n"
            f"**زمان گزارش:** {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"**جزئیات:**\n{details if details else 'بدون جزئیات اضافی'}",
            color
        )
        
        await ctx.send(embed=embed)
        
        # اطلاع‌رسانی به کانال عملیات
        ops_channel = discord.utils.get(ctx.guild.channels, name='🌊│عملیات-دریایی')
        if ops_channel and ops_channel != ctx.channel:
            await ops_channel.send(embed=embed)
        
        # در صورت اورژانسی یا تماس دشمن، اطلاع‌رسانی فوری
        if status in ['اورژانسی', 'تماس_دشمن']:
            command_channel = discord.utils.get(ctx.guild.channels, name='⚓│فرماندهی-دریایی')
            if command_channel:
                emergency_embed = create_embed(
                    "🚨 هشدار فوری دریایی",
                    f"**ماموریت:** {mission_id}\n"
                    f"**وضعیت:** {status}\n"
                    f"**منطقه:** {mission['zone_name']}\n"
                    f"**شناور:** {mission['vessel_name']}\n"
                    f"**گزارش‌دهنده:** {ctx.author.mention}\n\n"
                    f"**اقدام فوری مورد نیاز!**",
                    EMBED_COLORS['error']
                )
                await command_channel.send("@here", embed=emergency_embed)

    @tasks.loop(hours=3)
    async def coastal_patrol(self):
        """گشت‌زنی خودکار سواحل"""
        try:
            # انتخاب منطقه برای گشت اضافی
            patrol_zones = [zone_id for zone_id, zone in self.naval_zones.items() 
                           if zone['threat_level'] in ['بالا', 'متوسط']]
            
            if patrol_zones:
                selected_zone = random.choice(patrol_zones)
                zone_data = self.naval_zones[selected_zone]
                
                # انتخاب قایق گشتی موجود
                available_patrol_boats = []
                for boat_class_id, boat_class in self.patrol_boats.items():
                    if boat_class['operational'] > 0:
                        available_patrol_boats.append((boat_class_id, boat_class))
                
                if available_patrol_boats:
                    selected_boat_id, selected_boat = random.choice(available_patrol_boats)
                    
                    # ایجاد گشت خودکار
                    patrol_id = f"AUTO-{self.operation_counter}"
                    self.operation_counter += 1
                    
                    operation_data = {
                        'id': patrol_id,
                        'type': 'گشت خودکار',
                        'description': 'گشت‌زنی ساحلی خودکار',
                        'zone': selected_zone,
                        'zone_name': zone_data['name'],
                        'vessel': selected_boat_id,
                        'vessel_name': selected_boat['name'],
                        'vessel_type': 'patrol',
                        'objective': 'نظارت و کنترل ساحلی',
                        'commander': 'سیستم خودکار',
                        'personnel_involved': selected_boat['crew'],
                        'start_time': datetime.now(),
                        'duration_minutes': random.randint(180, 360),
                        'status': 'خودکار',
                        'risk_level': 15,
                        'success_probability': 92,
                        'cost': 5000
                    }
                    
                    self.active_naval_operations[patrol_id] = operation_data
                    selected_boat['operational'] -= 1
                    self.naval_stats['total_patrols'] += 1
                    
                    # شانس کشف قاچاق
                    if random.random() < 0.15:  # 15% احتمال
                        self.naval_stats['smuggling_intercepted'] += 1
                    
                    # اطلاع‌رسانی
                    guild = self.get_guild(GUILD_ID)
                    if guild:
                        ops_channel = discord.utils.get(guild.channels, name='🌊│عملیات-دریایی')
                        if ops_channel:
                            embed = create_embed(
                                "🔄 گشت ساحلی خودکار",
                                f"**شماره:** {patrol_id}\n"
                                f"**منطقه:** {zone_data['name']}\n"
                                f"**شناور:** {selected_boat['name']}\n"
                                f"**خدمه:** {selected_boat['crew']} نفر\n"
                                f"**مدت:** {operation_data['duration_minutes']} دقیقه",
                                EMBED_COLORS['primary']
                            )
                            await ops_channel.send(embed=embed)
                            
        except Exception as e:
            logger.error(f"خطا در گشت ساحلی خودکار: {e}")

    @tasks.loop(hours=6)
    async def blockade_enforcement(self):
        """اجرای محاصره دریایی"""
        try:
            # شبیه‌سازی فعالیت‌های محاصره
            blockade_activities = [
                'بازرسی کشتی مشکوک',
                'جلوگیری از نفوذ قایق',
                'کشف محموله قاچاق',
                'هشدار به ناقضین محاصره',
                'هماهنگی با نیروی هوایی'
            ]
            
            activity = random.choice(blockade_activities)
            
            # احتمال موفقیت در جلوگیری از قاچاق
            if random.random() < 0.3:  # 30% احتمال
                success = True
                self.naval_stats['smuggling_intercepted'] += 1
                if random.random() < 0.5:
                    self.naval_stats['weapons_seized'] += random.randint(1, 5)
            else:
                success = False
            
            # اطلاع‌رسانی در صورت موفقیت
            if success:
                guild = self.get_guild(GUILD_ID)
                if guild:
                    blockade_channel = discord.utils.get(guild.channels, name='🏴‍☠️│محاصره-غزه')
                    if blockade_channel:
                        embed = create_embed(
                            "🚫 فعالیت محاصره",
                            f"**فعالیت:** {activity}\n"
                            f"**نتیجه:** موفقیت‌آمیز\n"
                            f"**زمان:** {datetime.now().strftime('%H:%M')}\n"
                            f"**وضعیت محاصره:** فعال و مؤثر",
                            EMBED_COLORS['success']
                        )
                        await blockade_channel.send(embed=embed)
                        
        except Exception as e:
            logger.error(f"خطا در اجرای محاصره: {e}")

    @tasks.loop(hours=8)
    async def submarine_operations(self):
        """عملیات زیردریایی محرمانه"""
        try:
            # انتخاب زیردریایی برای ماموریت
            available_subs = [sub_id for sub_id, sub in self.submarine_fleet.items() 
                             if sub['status'] == 'عملیاتی' and sub['mission'] != 'ماموریت ویژه']
            
            if available_subs and random.random() < 0.4:  # 40% احتمال
                selected_sub = random.choice(available_subs)
                submarine = self.submarine_fleet[selected_sub]
                
                # تغییر وضعیت به ماموریت محرمانه
                submarine['mission'] = 'ماموریت ویژه'
                submarine['location'] = 'محرمانه'
                
                # به‌روزرسانی آمار
                self.naval_stats['special_operations'] += 1
                
                # اطلاع‌رسانی محدود
                guild = self.get_guild(GUILD_ID)
                if guild:
                    ops_channel = discord.utils.get(guild.channels, name='🌊│عملیات-دریایی')
                    if ops_channel:
                        embed = create_embed(
                            "🔒 عملیات محرمانه",
                            f"**زیردریایی:** [طبقه‌بندی شده]\n"
                            f"**ماموریت:** محرمانه\n"
                            f"**مدت تخمینی:** [طبقه‌بندی شده]\n"
                            f"**وضعیت:** در حال انجام",
                            EMBED_COLORS['error']
                        )
                        await ops_channel.send(embed=embed)
                
                # بازگشت زیردریایی بعد از مدتی (شبیه‌سازی)
                await asyncio.sleep(3600)  # 1 ساعت (در واقعیت طولانی‌تر)
                submarine['mission'] = 'گشت‌زنی'
                submarine['location'] = random.choice(['دریای مدیترانه', 'دریای سرخ'])
                
        except Exception as e:
            logger.error(f"خطا در عملیات زیردریایی: {e}")

    @tasks.loop(hours=12)
    async def vessel_maintenance(self):
        """تعمیر و نگهداری شناورها"""
        try:
            # تعمیر قایق‌های گشتی
            for boat_class_id, boat_class in self.patrol_boats.items():
                # تکمیل تعمیرات
                if boat_class['maintenance'] > 0:
                    if random.random() < 0.4:  # 40% احتمال
                        repaired = min(boat_class['maintenance'], random.randint(1, 2))
                        boat_class['maintenance'] -= repaired
                        boat_class['operational'] += repaired
                
                # نیاز به تعمیر جدید
                if boat_class['operational'] > 0:
                    if random.random() < 0.05:  # 5% احتمال
                        need_maintenance = min(boat_class['operational'], 1)
                        boat_class['operational'] -= need_maintenance
                        boat_class['maintenance'] += need_maintenance
            
            # تعمیر کشتی‌های بزرگ (شبیه‌سازی)
            for ship_id, ship in self.surface_fleet.items():
                if ship['status'] == 'تعمیرات' and random.random() < 0.3:
                    ship['status'] = 'عملیاتی'
                    ship['mission'] = 'آمادگی'
                elif ship['status'] == 'عملیاتی' and random.random() < 0.02:
                    ship['status'] = 'تعمیرات'
                    ship['mission'] = 'نگهداری'
            
        except Exception as e:
            logger.error(f"خطا در تعمیر و نگهداری: {e}")

    @tasks.loop(hours=4)
    async def maritime_intelligence(self):
        """جمع‌آوری اطلاعات دریایی"""
        try:
            # فعالیت‌های اطلاعاتی
            intel_activities = [
                'رصد ترافیک دریایی',
                'تحلیل الگوهای حرکتی',
                'نظارت بر ارتباطات دریایی',
                'شناسایی کشتی‌های مشکوک',
                'بررسی مسیرهای قاچاق'
            ]
            
            activity = random.choice(intel_activities)
            
            # احتمال کشف اطلاعات مهم
            if random.random() < 0.25:  # 25% احتمال
                intelligence_found = True
                intel_types = [
                    'مسیر قاچاق جدید',
                    'فعالیت مشکوک در بندر',
                    'تغییر در الگوهای ترافیکی',
                    'شناسایی کشتی مجهول'
                ]
                intel_type = random.choice(intel_types)
            else:
                intelligence_found = False
                intel_type = None
            
            # اطلاع‌رسانی در صورت کشف
            if intelligence_found:
                guild = self.get_guild(GUILD_ID)
                if guild:
                    intel_channel = discord.utils.get(guild.channels, name='📡│اطلاعات-دریایی')
                    if intel_channel:
                        embed = create_embed(
                            "🔍 گزارش اطلاعاتی دریایی",
                            f"**فعالیت:** {activity}\n"
                            f"**اطلاعات کشف شده:** {intel_type}\n"
                            f"**زمان:** {datetime.now().strftime('%H:%M')}\n"
                            f"**اولویت:** متوسط\n"
                            f"**وضعیت:** نیاز به بررسی بیشتر",
                            EMBED_COLORS['warning']
                        )
                        await intel_channel.send(embed=embed)
                        
        except Exception as e:
            logger.error(f"خطا در جمع‌آوری اطلاعات دریایی: {e}")

async def run_navy_bot():
    """اجرای ربات نیروی دریایی"""
    bot = IsraeliNavyBot()
    try:
        await bot.start(DISCORD_BOT_TOKEN_NAVY)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات نیروی دریایی: {e}")

if __name__ == "__main__":
    """
    ⚓ ربات نیروی دریایی اسرائیل
    
    این ربات مسئول مدیریت کامل نیروی دریایی اسرائیل است و شامل:
    
    🚢 ناوگان زیردریایی:
    - زیردریایی‌های کلاس دلفین (تانین، رهب، دکار)
    - قابلیت‌های جاسوسی و حمله زیردریایی
    
    ⚔️ ناوگان سطحی:
    - کورت‌های موشک‌انداز Sa'ar 6 و Sa'ar 5
    - سیستم‌های دفاع هوایی دریایی
    
    🛥️ قایق‌های گشتی:
    - کلاس دبورا (گشت ساحلی)
    - کلاس شلدگ (عملیات ویژه)
    
    🏴‍☠️ یگان شایطت 13:
    - کماندوهای دریایی نخبه
    - عملیات ویژه و تخریب زیردریایی
    
    🗺️ مناطق دریایی:
    - دریای مدیترانه (شمال و مرکز)
    - آب‌های غزه (محاصره کامل)
    - دریای سرخ (خلیج عقبه)
    
    ⚓ پایگاه‌های دریایی:
    - حیفا (پایگاه اصلی)
    - اشدود (عملیاتی)
    - ایلات (استراتژیک)
    
    🎯 قابلیت‌ها:
    - مدیریت ماموریت‌های دریایی
    - اجرای محاصره دریایی
    - عملیات زیردریایی محرمانه
    - گشت‌زنی خودکار
    - جمع‌آوری اطلاعات دریایی
    - تعمیر و نگهداری ناوگان
    
    دستورات اصلی:
    !دریایی_وضعیت_ناوگان - وضعیت کامل ناوگان
    !دریایی_مناطق_دریایی - مناطق تحت کنترل
    !دریایی_ماموریت_دریایی - شروع ماموریت جدید
    !دریایی_عملیات_فعال - ماموریت‌های جاری
    !دریایی_آمار_دریایی - آمار کامل
    !دریایی_وضعیت_محاصره - وضعیت محاصره غزه
    !دریایی_گزارش_دریایی - گزارش از ماموریت
    """
    
    import asyncio
    asyncio.run(run_navy_bot())