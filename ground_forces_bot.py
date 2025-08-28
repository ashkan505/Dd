#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات نیروی زمینی اسرائیل (IDF Ground Forces)
Israeli Ground Forces Bot

این ربات مسئول مدیریت کامل نیروی زمینی اسرائیل است:
- مدیریت تانک‌ها و تجهیزات زرهی (مرکاوا، نامر)
- واحدهای پیاده‌نظام (گولانی، چترباز، نحال)
- توپخانه و سیستم‌های موشکی
- عملیات زمینی و تاکتیک‌های نبرد
- حفاظت مرزها و عملیات امنیتی

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

class IsraeliGroundForcesBot(commands.Bot):
    """
    ربات نیروی زمینی اسرائیل (IDF Ground Forces)
    "כוחות היבשה של צה״ל"
    
    مأموریت: دفاع از خاک اسرائیل و حفظ امنیت مرزها
    شعار: "אחריות, מקצועיות, חדשנות" (مسئولیت، تخصص، نوآوری)
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!زمینی_',
            intents=intents,
            help_command=None,
            description="🛡️ نیروی زمینی اسرائیل - محافظان خاک"
        )
        
        self.db = DatabaseManager()
        
        # تجهیزات زرهی و مکانیزه
        self.armored_units = {
            'Merkava_MK4': {
                'name': 'تانک مرکاوا MK4 (מרכבה)',
                'type': 'تانک اصلی نبرد',
                'manufacturer': 'IMI Systems',
                'total_count': 360,
                'operational': 340,
                'maintenance': 15,
                'training': 5,
                'crew_size': 4,
                'max_speed': 64,  # km/h
                'range': 500,  # km
                'main_gun': '120mm smoothbore',
                'armor': 'Trophy APS + composite',
                'cost_per_hour': 800,
                'capabilities': [
                    'نبرد تانک به تانک', 'پشتیبانی پیاده‌نظام', 
                    'عملیات شهری', 'حفاظت مرزی', 'سیستم Trophy'
                ],
                'weapons': [
                    'توپ 120mm', 'مسلسل سنگین 12.7mm',
                    'مسلسل 7.62mm', 'دودزای'
                ],
                'brigades': ['7th Armored', '188th Barak', '401st Iron Tracks'],
                'bases': ['Shizafon', 'Tzeelim', 'Paran']
            },
            
            'Merkava_MK3': {
                'name': 'تانک مرکاوا MK3',
                'type': 'تانک اصلی نبرد',
                'manufacturer': 'IMI Systems',
                'total_count': 780,
                'operational': 720,
                'maintenance': 40,
                'training': 20,
                'crew_size': 4,
                'max_speed': 60,
                'range': 500,
                'main_gun': '120mm smoothbore',
                'armor': 'composite armor',
                'cost_per_hour': 650,
                'capabilities': [
                    'نبرد زرهی', 'پشتیبانی آتش', 'عملیات دفاعی',
                    'گشت‌زنی مرزی', 'آموزش'
                ],
                'weapons': [
                    'توپ 120mm', 'مسلسل 12.7mm',
                    'مسلسل 7.62mm'
                ],
                'brigades': ['7th Armored', '188th Barak'],
                'bases': ['Shizafon', 'Tzeelim']
            },
            
            'Namer_APC': {
                'name': 'ناقل پرسنل نامر (נמ״ר)',
                'type': 'ناقل نیروی زرهی',
                'manufacturer': 'IMI Systems',
                'total_count': 200,
                'operational': 180,
                'maintenance': 15,
                'training': 5,
                'crew_size': 3,
                'passengers': 9,
                'max_speed': 60,
                'range': 500,
                'armor': 'Merkava-based',
                'cost_per_hour': 400,
                'capabilities': [
                    'حمل نیرو', 'پشتیبانی آتش', 'عملیات شهری',
                    'تخلیه زخمی', 'حمایت از پیاده‌نظام'
                ],
                'weapons': [
                    'مسلسل سنگین 12.7mm', 'دودزای',
                    'سیستم Trophy (برخی)'
                ],
                'brigades': ['Golani', 'Paratroopers', 'Nahal'],
                'bases': ['Tzeelim', 'Shizafon']
            },
            
            'Eitan_APC': {
                'name': 'ناقل پرسنل ایتان (איתן)',
                'type': 'ناقل نیروی چرخ‌دار',
                'manufacturer': 'General Dynamics',
                'total_count': 150,
                'operational': 135,
                'maintenance': 10,
                'training': 5,
                'crew_size': 2,
                'passengers': 9,
                'max_speed': 90,
                'range': 700,
                'armor': 'STANAG Level 4',
                'cost_per_hour': 300,
                'capabilities': [
                    'حرکت سریع', 'گشت‌زنی', 'عملیات امنیتی',
                    'حمل نیرو', 'پشتیبانی'
                ],
                'weapons': [
                    'برج Rafael Samson', 'مسلسل 12.7mm',
                    'موشک Spike'
                ],
                'brigades': ['Kfir', 'Border Guard'],
                'bases': ['Hebron', 'Jenin']
            }
        }
        
        # واحدهای پیاده‌نظام
        self.infantry_units = {
            'Golani_Brigade': {
                'name': 'تیپ گولانی (גולני)',
                'type': 'پیاده‌نظام رزمی',
                'established': 1948,
                'total_personnel': 3000,
                'operational': 2800,
                'training': 150,
                'reserves': 50,
                'specialization': 'عملیات پیاده، نبرد شهری',
                'motto': 'אחרי גולני (پس از گولانی)',
                'equipment': [
                    'تفنگ Tavor X95', 'نارنجک M67',
                    'RPG Matador', 'مسلسل Negev'
                ],
                'recent_operations': [
                    'عملیات محافظ دیوارها', 'عملیات شمشیر شکسته',
                    'گشت‌زنی مرز لبنان'
                ],
                'bases': ['Beit Lid', 'Shizafon'],
                'battalions': ['12th Battalion', '13th Battalion', '51st Battalion']
            },
            
            'Paratroopers_Brigade': {
                'name': 'تیپ چترباز (צנחנים)',
                'type': 'نیروی ویژه هوابرد',
                'established': 1948,
                'total_personnel': 1500,
                'operational': 1400,
                'training': 80,
                'reserves': 20,
                'specialization': 'عملیات ویژه، چتربازی، نفوذ عمقی',
                'motto': 'אחרי הצנחנים (پس از چتربازان)',
                'equipment': [
                    'تفنگ M4A1', 'چتر T-11',
                    'تجهیزات کوهنوردی', 'عینک دید در شب'
                ],
                'recent_operations': [
                    'عملیات انتقام', 'نجات گروگان‌ها',
                    'تخریب تونل‌ها'
                ],
                'bases': ['Tel Nof', 'Sirkin'],
                'battalions': ['101st Battalion', '202nd Battalion', '890th Battalion']
            },
            
            'Nahal_Brigade': {
                'name': 'تیپ نحال (נח״ל)',
                'type': 'پیاده‌نظام پیشگام',
                'established': 1948,
                'total_personnel': 2500,
                'operational': 2300,
                'training': 150,
                'reserves': 50,
                'specialization': 'عملیات مرزی، کشاورزی نظامی',
                'motto': 'נלחמים וחלוצים (جنگجو و پیشگام)',
                'equipment': [
                    'تفنگ Tavor', 'تجهیزات کشاورزی',
                    'سیستم ارتباطات', 'ادوات مهندسی'
                ],
                'recent_operations': [
                    'حفاظت مرز غزه', 'ایجاد اسکان جدید',
                    'عملیات امنیتی'
                ],
                'bases': ['Paran', 'Shizafon'],
                'battalions': ['50th Battalion', '932nd Battalion']
            },
            
            'Kfir_Brigade': {
                'name': 'تیپ کفیر (כפיר)',
                'type': 'پیاده‌نظام کرانه باختری',
                'established': 2005,
                'total_personnel': 2000,
                'operational': 1850,
                'training': 120,
                'reserves': 30,
                'specialization': 'عملیات ضدتروریسم، کنترل جمعیت',
                'motto': 'כמו אריה (مثل شیر)',
                'equipment': [
                    'تفنگ M4', 'تجهیزات ضدشورش',
                    'سیستم‌های نظارت', 'خودروهای زرهی'
                ],
                'recent_operations': [
                    'عملیات در کرانه باختری', 'دستگیری مظنونین',
                    'حفاظت شهرک‌ها'
                ],
                'bases': ['Ofer', 'Anatot'],
                'battalions': ['90th Battalion', '92nd Battalion', '97th Battalion']
            }
        }
        
        # سیستم‌های توپخانه و موشکی
        self.artillery_systems = {
            'M109_Howitzer': {
                'name': 'خودکشی M109 دوهر (דוהר)',
                'type': 'توپخانه خودکششی',
                'caliber': '155mm',
                'total_count': 600,
                'operational': 580,
                'maintenance': 20,
                'crew_size': 6,
                'max_range': 30000,  # متر
                'rate_of_fire': '4 rounds/min',
                'cost_per_round': 1000,
                'capabilities': [
                    'پشتیبانی آتش', 'حمله غیرمستقیم',
                    'آتش ضد بطری', 'آتش دقیق'
                ],
                'ammunition': [
                    'HE (انفجاری)', 'Smoke (دود)',
                    'Illumination (روشنایی)', 'Precision (دقیق)'
                ],
                'units': ['215th Artillery', '282nd Artillery'],
                'bases': ['Shivta', 'Paran']
            },
            
            'MLRS_Lynx': {
                'name': 'سیستم راکت چندلوله لینکس',
                'type': 'راکت انداز چندلوله',
                'caliber': '160mm',
                'total_count': 48,
                'operational': 45,
                'maintenance': 3,
                'crew_size': 3,
                'max_range': 45000,
                'rockets_per_pod': 18,
                'cost_per_rocket': 5000,
                'capabilities': [
                    'حمله منطقه‌ای', 'سرکوب آتش',
                    'تخریب تأسیسات', 'آتش ساتراسیون'
                ],
                'warheads': [
                    'HE-FRAG', 'Cluster', 'Smoke'
                ],
                'units': ['215th Artillery'],
                'bases': ['Shivta']
            },
            
            'Spike_NLOS': {
                'name': 'موشک اسپایک NLOS',
                'type': 'موشک ضدتانک برد بلند',
                'total_count': 500,
                'operational': 480,
                'maintenance': 20,
                'crew_size': 2,
                'max_range': 25000,
                'guidance': 'EO/IR + GPS',
                'cost_per_missile': 150000,
                'capabilities': [
                    'شکار تانک', 'حمله دقیق',
                    'عملیات شبانه', 'آتش و فراموش'
                ],
                'platforms': [
                    'خودروی نظامی', 'بالگرد',
                    'کشتی', 'پایگاه ثابت'
                ],
                'units': ['Anti-Tank Units'],
                'bases': ['Multiple']
            }
        }
        
        # مناطق عملیاتی
        self.operational_sectors = {
            'Gaza_Envelope': {
                'name': 'محیط غزه (עוטף עזה)',
                'threat_level': 'بالا',
                'border_length': 51,  # km
                'population': 70000,
                'main_threats': ['تونل‌ها', 'راکت‌ها', 'نفوذ', 'IED'],
                'deployed_units': [
                    'Golani_Brigade', 'Merkava_MK4', 
                    'Namer_APC', 'M109_Howitzer'
                ],
                'checkpoints': 12,
                'observation_posts': 25,
                'status': 'آمادگی کامل',
                'recent_incidents': 3
            },
            
            'Lebanon_Border': {
                'name': 'مرز لبنان (גבול לבנון)',
                'threat_level': 'متوسط',
                'border_length': 79,
                'population': 200000,
                'main_threats': ['حزب‌الله', 'تونل‌ها', 'موشک‌ها'],
                'deployed_units': [
                    'Paratroopers_Brigade', 'Merkava_MK3',
                    'Namer_APC'
                ],
                'checkpoints': 8,
                'observation_posts': 35,
                'status': 'گشت‌زنی فعال',
                'recent_incidents': 1
            },
            
            'West_Bank': {
                'name': 'کرانه باختری (הגדה המערבית)',
                'threat_level': 'متوسط',
                'area': 5655,  # km2
                'population': 400000,  # اسرائیلی
                'main_threats': ['تروریسم', 'اغتشاش', 'حملات فردی'],
                'deployed_units': [
                    'Kfir_Brigade', 'Nahal_Brigade',
                    'Eitan_APC'
                ],
                'checkpoints': 140,
                'observation_posts': 60,
                'status': 'عملیات امنیتی',
                'recent_incidents': 8
            },
            
            'Jordan_Valley': {
                'name': 'دره اردن (בקעת הירדן)',
                'threat_level': 'پایین',
                'border_length': 97,
                'population': 65000,
                'main_threats': ['قاچاق', 'نفوذ غیرقانونی'],
                'deployed_units': [
                    'Nahal_Brigade', 'Border_Guard'
                ],
                'checkpoints': 6,
                'observation_posts': 20,
                'status': 'گشت‌زنی معمول',
                'recent_incidents': 0
            }
        }
        
        # عملیات فعال
        self.active_operations = {}
        self.operation_counter = 2000
        
        # آمار عملیاتی
        self.operational_stats = {
            'total_operations': 1247,
            'successful_operations': 1189,
            'arrests_made': 2341,
            'weapons_seized': 456,
            'tunnels_destroyed': 89,
            'checkpoints_manned': 166,
            'patrols_conducted': 12450,
            'training_exercises': 890,
            'casualties_prevented': 234,
            'equipment_maintained': 15600
        }
        
        # وضعیت آمادگی
        self.readiness_level = 'NORMAL'
        self.alert_status = 'آمادگی عادی'
        
        # پرسنل
        self.personnel = {
            'officers': 1200,
            'ncos': 2800,
            'soldiers': 18000,
            'tank_crews': 2400,
            'infantry': 12000,
            'artillery': 1800,
            'engineers': 1500,
            'medics': 800,
            'trainees': 2500
        }
        
    async def on_ready(self):
        """آماده‌سازی ربات نیروی زمینی"""
        print(f'🛡️ {self.user} - מוכנים לפעולה! (آماده عمل!)')
        
        # شروع وظایف دوره‌ای
        if not self.border_patrol.is_running():
            self.border_patrol.start()
        if not self.equipment_maintenance.is_running():
            self.equipment_maintenance.start()
        if not self.training_exercises.is_running():
            self.training_exercises.start()
        if not self.intelligence_gathering.is_running():
            self.intelligence_gathering.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"مرزهای اسرائیل | {self.alert_status} 🛡️"
            )
        )
        
        # ایجاد کانال‌های اختصاصی
        guild = self.guilds[0] if self.guilds else None
        if guild:
            await self._setup_channels(guild)

    async def _setup_channels(self, guild):
        """ایجاد کانال‌های اختصاصی نیروی زمینی"""
        channels_to_create = [
            ('🛡️│فرماندهی-زمینی', 'مرکز فرماندهی نیروی زمینی'),
            ('🚁│عملیات-زمینی', 'عملیات و ماموریت‌های جاری'),
            ('🏰│کنترل-مرزها', 'کنترل و نظارت مرزها'),
            ('🎯│ماموریت‌های-ویژه', 'عملیات ویژه و تاکتیکی'),
            ('⚔️│واحدهای-رزمی', 'هماهنگی واحدهای رزمی'),
            ('🔧│نگهداری-تجهیزات', 'تعمیر و نگهداری'),
            ('🎓│آموزش-نظامی', 'آموزش و تربیت نیرو'),
            ('📊│گزارشات-زمینی', 'گزارشات و آمار عملیاتی'),
            ('🚨│هشدارهای-امنیتی', 'هشدارها و اطلاعیه‌های امنیتی')
        ]
        
        ground_forces_category = await get_or_create_category(guild, "🛡️ نیروی زمینی اسرائیل")
        
        for channel_name, description in channels_to_create:
            await get_or_create_channel(guild, channel_name, category=ground_forces_category)

    @commands.command(name='وضعیت_واحدها')
    async def units_status(self, ctx):
        """نمایش وضعیت کامل واحدهای زمینی"""
        
        # صفحه اول: تجهیزات زرهی
        embed1 = create_embed(
            "🛡️ وضعیت تجهیزات زرهی",
            f"**سطح آمادگی:** {self.readiness_level}\n**وضعیت هشدار:** {self.alert_status}",
            EMBED_COLORS['primary']
        )
        
        for unit_id, unit in self.armored_units.items():
            readiness_percent = (unit['operational'] / unit['total_count']) * 100
            
            if readiness_percent >= 90:
                status_emoji = "🟢"
                status_text = "عالی"
            elif readiness_percent >= 75:
                status_emoji = "🟡"
                status_text = "مطلوب"
            else:
                status_emoji = "🔴"
                status_text = "نیاز به توجه"
            
            embed1.add_field(
                name=f"{status_emoji} {unit['name']}",
                value=f"**نوع:** {unit['type']}\n"
                      f"**مجموع:** {unit['total_count']}\n"
                      f"**عملیاتی:** {unit['operational']}\n"
                      f"**تعمیرات:** {unit['maintenance']}\n"
                      f"**آموزش:** {unit['training']}\n"
                      f"**خدمه:** {unit['crew_size']} نفر\n"
                      f"**آمادگی:** {readiness_percent:.1f}% ({status_text})",
                inline=True
            )
        
        await ctx.send(embed=embed1)
        
        # صفحه دوم: واحدهای پیاده‌نظام
        embed2 = create_embed(
            "⚔️ وضعیت واحدهای پیاده‌نظام",
            "واحدهای رزمی و تخصصی:",
            EMBED_COLORS['primary']
        )
        
        for unit_id, unit in self.infantry_units.items():
            readiness_percent = (unit['operational'] / unit['total_personnel']) * 100
            
            if readiness_percent >= 90:
                status_emoji = "🟢"
            elif readiness_percent >= 80:
                status_emoji = "🟡"
            else:
                status_emoji = "🔴"
            
            embed2.add_field(
                name=f"{status_emoji} {unit['name']}",
                value=f"**تخصص:** {unit['specialization']}\n"
                      f"**کل نیرو:** {unit['total_personnel']:,}\n"
                      f"**عملیاتی:** {unit['operational']:,}\n"
                      f"**آموزش:** {unit['training']}\n"
                      f"**ذخیره:** {unit['reserves']}\n"
                      f"**تأسیس:** {unit['established']}\n"
                      f"**آمادگی:** {readiness_percent:.1f}%",
                inline=True
            )
        
        await ctx.send(embed=embed2)
        
        # صفحه سوم: سیستم‌های توپخانه
        embed3 = create_embed(
            "🎯 وضعیت سیستم‌های آتش",
            "توپخانه و سیستم‌های موشکی:",
            EMBED_COLORS['primary']
        )
        
        for system_id, system in self.artillery_systems.items():
            if 'total_count' in system:
                readiness_percent = (system['operational'] / system['total_count']) * 100
                status_emoji = "🟢" if readiness_percent >= 90 else "🟡" if readiness_percent >= 75 else "🔴"
                
                embed3.add_field(
                    name=f"{status_emoji} {system['name']}",
                    value=f"**نوع:** {system['type']}\n"
                          f"**کالیبر/برد:** {system.get('caliber', 'N/A')} / {system.get('max_range', 'N/A')}م\n"
                          f"**مجموع:** {system['total_count']}\n"
                          f"**عملیاتی:** {system['operational']}\n"
                          f"**تعمیرات:** {system['maintenance']}\n"
                          f"**آمادگی:** {readiness_percent:.1f}%",
                    inline=True
                )
            else:
                embed3.add_field(
                    name=f"🟢 {system['name']}",
                    value=f"**نوع:** {system['type']}\n"
                          f"**موجودی:** {system['operational']}\n"
                          f"**برد:** {system.get('max_range', 'N/A')}م\n"
                          f"**هدایت:** {system.get('guidance', 'N/A')}\n"
                          f"**وضعیت:** آماده",
                    inline=True
                )
        
        await ctx.send(embed=embed3)

    @commands.command(name='مناطق_عملیاتی')
    async def operational_sectors_status(self, ctx):
        """نمایش وضعیت مناطق عملیاتی"""
        
        embed = create_embed(
            "🗺️ مناطق عملیاتی نیروی زمینی",
            "وضعیت فعلی مناطق تحت کنترل:",
            EMBED_COLORS['primary']
        )
        
        threat_colors = {
            'بالا': '🔴',
            'متوسط': '🟡',
            'پایین': '🟢'
        }
        
        for sector_id, sector in self.operational_sectors.items():
            threat_emoji = threat_colors.get(sector['threat_level'], '⚪')
            
            # محاسبه واحدهای مستقر
            deployed_units = []
            for unit_type in sector['deployed_units']:
                if unit_type in self.armored_units:
                    deployed_units.append(self.armored_units[unit_type]['name'])
                elif unit_type in self.infantry_units:
                    deployed_units.append(self.infantry_units[unit_type]['name'])
                else:
                    deployed_units.append(unit_type.replace('_', ' '))
            
            # محاسبه میزان فعالیت بر اساس حوادث اخیر
            if sector['recent_incidents'] == 0:
                activity_status = "🟢 آرام"
            elif sector['recent_incidents'] <= 3:
                activity_status = "🟡 فعالیت معمول"
            else:
                activity_status = "🔴 فعالیت بالا"
            
            embed.add_field(
                name=f"{threat_emoji} {sector['name']}",
                value=f"**سطح تهدید:** {sector['threat_level']}\n"
                      f"**وضعیت:** {sector['status']}\n"
                      f"**فعالیت:** {activity_status}\n"
                      f"**حوادث اخیر:** {sector['recent_incidents']}\n"
                      f"**ایست‌ها:** {sector['checkpoints']}\n"
                      f"**پست‌های نظارت:** {sector['observation_posts']}\n"
                      f"**تهدیدات اصلی:** {', '.join(sector['main_threats'])}\n"
                      f"**واحدهای مستقر:**\n" + 
                      "\n".join([f"• {unit}" for unit in deployed_units[:3]]) +
                      (f"\n• و {len(deployed_units)-3} واحد دیگر..." if len(deployed_units) > 3 else ""),
                inline=True
            )
        
        # آمار کلی
        total_checkpoints = sum([sector['checkpoints'] for sector in self.operational_sectors.values()])
        total_posts = sum([sector['observation_posts'] for sector in self.operational_sectors.values()])
        total_incidents = sum([sector['recent_incidents'] for sector in self.operational_sectors.values()])
        
        embed.add_field(
            name="📊 خلاصه کلی",
            value=f"**مجموع ایست‌ها:** {total_checkpoints}\n"
                  f"**مجموع پست‌ها:** {total_posts}\n"
                  f"**حوادث این ماه:** {total_incidents}\n"
                  f"**وضعیت کلی:** {'🟢 تحت کنترل' if total_incidents < 10 else '🟡 نیاز به توجه'}",
            inline=False
        )
        
        embed.set_footer(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await ctx.send(embed=embed)

    @commands.command(name='عملیات')
    @has_role(['فرمانده زمینی', 'افسر عملیات', 'فرمانده واحد', 'مدیر'])
    async def launch_ground_operation(self, ctx, operation_type: str, sector: str, unit_type: str, *, objective: str = "هدف تعیین نشده"):
        """راه‌اندازی عملیات زمینی جدید"""
        
        # انواع عملیات مجاز
        valid_operations = {
            'گشت': 'گشت‌زنی و نظارت',
            'تأمین_امنیت': 'عملیات تأمین امنیت',
            'دستگیری': 'عملیات دستگیری مظنونین',
            'تخریب': 'تخریب تونل‌ها و تأسیسات',
            'حمله': 'عملیات تهاجمی',
            'دفاع': 'عملیات دفاعی',
            'امداد': 'عملیات امداد و نجات',
            'تمرین': 'تمرین نظامی',
            'اسکورت': 'اسکورت و حمایت'
        }
        
        if operation_type not in valid_operations:
            embed = create_embed(
                "❌ نوع عملیات نامعتبر",
                f"**انواع عملیات مجاز:**\n" + 
                "\n".join([f"• `{k}`: {v}" for k, v in valid_operations.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی منطقه عملیاتی
        if sector not in self.operational_sectors:
            embed = create_embed(
                "❌ منطقه نامعتبر",
                f"**مناطق عملیاتی موجود:**\n" + 
                "\n".join([f"• `{k}`: {v['name']}" for k, v in self.operational_sectors.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی واحد
        unit_found = False
        unit_data = None
        
        if unit_type in self.armored_units:
            unit_data = self.armored_units[unit_type]
            unit_found = True
        elif unit_type in self.infantry_units:
            unit_data = self.infantry_units[unit_type]
            unit_found = True
        elif unit_type in self.artillery_systems:
            unit_data = self.artillery_systems[unit_type]
            unit_found = True
        
        if not unit_found:
            all_units = list(self.armored_units.keys()) + list(self.infantry_units.keys()) + list(self.artillery_systems.keys())
            embed = create_embed(
                "❌ واحد نامعتبر",
                f"**واحدهای موجود:**\n" + 
                "\n".join([f"• `{unit}`" for unit in all_units[:10]]) +
                (f"\n• و {len(all_units)-10} واحد دیگر..." if len(all_units) > 10 else ""),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی در دسترس بودن واحد
        if unit_type in self.armored_units or unit_type in self.artillery_systems:
            if unit_data['operational'] < 1:
                embed = create_embed(
                    "❌ واحد در دسترس نیست",
                    f"**واحد:** {unit_data['name']}\n"
                    f"**عملیاتی:** {unit_data['operational']}\n"
                    f"**تعمیرات:** {unit_data['maintenance']}\n"
                    f"**آموزش:** {unit_data.get('training', 0)}",
                    EMBED_COLORS['error']
                )
                await ctx.send(embed=embed)
                return
        else:  # infantry
            if unit_data['operational'] < 50:  # حداقل 50 نفر برای عملیات
                embed = create_embed(
                    "❌ نیروی کافی در دسترس نیست",
                    f"**واحد:** {unit_data['name']}\n"
                    f"**نیروی عملیاتی:** {unit_data['operational']}\n"
                    f"**حداقل مورد نیاز:** 50 نفر",
                    EMBED_COLORS['error']
                )
                await ctx.send(embed=embed)
                return
        
        sector_data = self.operational_sectors[sector]
        
        # بررسی مناسب بودن واحد برای منطقه
        if unit_type not in sector_data['deployed_units']:
            embed = create_embed(
                "⚠️ واحد غیرمعمول",
                f"**واحد:** {unit_data['name']}\n"
                f"**منطقه:** {sector_data['name']}\n"
                "این واحد معمولاً در این منطقه مستقر نیست.\n"
                "عملیات ادامه می‌یابد...",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
        
        # ایجاد عملیات
        operation_id = f"GF-{self.operation_counter}"
        self.operation_counter += 1
        
        # محاسبه مدت عملیات
        base_duration = {
            'گشت': 180,
            'تأمین_امنیت': 480,
            'دستگیری': 120,
            'تخریب': 240,
            'حمله': 300,
            'دفاع': 720,
            'امداد': 200,
            'تمرین': 120,
            'اسکورت': 90
        }
        
        duration = base_duration.get(operation_type, 180)
        duration += random.randint(-30, 60)  # تنوع زمانی
        duration = max(30, duration)
        
        # محاسبه تعداد نیروی مورد نیاز
        if unit_type in self.infantry_units:
            personnel_needed = random.randint(50, 200)
            equipment_needed = 1
        else:
            personnel_needed = unit_data.get('crew_size', 4)
            equipment_needed = 1
        
        # محاسبه ریسک بر اساس منطقه و نوع عملیات
        base_risk = {
            'بالا': 25,
            'متوسط': 15,
            'پایین': 5
        }[sector_data['threat_level']]
        
        operation_risk = {
            'گشت': 5,
            'تأمین_امنیت': 10,
            'دستگیری': 20,
            'تخریب': 15,
            'حمله': 30,
            'دفاع': 20,
            'امداد': 10,
            'تمرین': 2,
            'اسکورت': 8
        }[operation_type]
        
        total_risk = min(95, base_risk + operation_risk)
        success_probability = 100 - total_risk
        
        operation_data = {
            'id': operation_id,
            'type': operation_type,
            'description': valid_operations[operation_type],
            'sector': sector,
            'sector_name': sector_data['name'],
            'unit_type': unit_type,
            'unit_name': unit_data['name'],
            'objective': objective,
            'commander': ctx.author.display_name,
            'personnel_involved': personnel_needed,
            'equipment_used': equipment_needed,
            'start_time': datetime.now(),
            'duration_minutes': duration,
            'status': 'در حال انجام',
            'risk_level': total_risk,
            'success_probability': success_probability,
            'cost': unit_data.get('cost_per_hour', 500) * (duration / 60)
        }
        
        # ذخیره عملیات
        self.active_operations[operation_id] = operation_data
        
        # کاهش نیروی موجود
        if unit_type in self.armored_units or unit_type in self.artillery_systems:
            unit_data['operational'] -= equipment_needed
        else:  # infantry
            unit_data['operational'] -= personnel_needed
        
        # تولید توضیحات عملیات با هوش مصنوعی
        operation_prompt = f"""
        یک عملیات {operation_type} زمینی در {sector_data['name']} با واحد {unit_data['name']} آغاز شده است.
        هدف عملیات: {objective}
        فرمانده: {ctx.author.display_name}
        سطح تهدید منطقه: {sector_data['threat_level']}
        مدت عملیات: {duration} دقیقه
        
        یک توضیح نظامی و تاکتیکی از این عملیات بنویس (100-150 کلمه).
        از اصطلاحات نظامی مناسب استفاده کن.
        """
        
        try:
            operation_description = await generate_text_with_gemini(operation_prompt)
        except Exception as e:
            logger.error(f"خطا در تولید توضیحات عملیات: {e}")
            operation_description = f"عملیات {operation_type} در {sector_data['name']} با هدف {objective} آغاز شد."
        
        # تعیین رنگ embed بر اساس ریسک
        if total_risk <= 15:
            embed_color = EMBED_COLORS['success']
            risk_emoji = "🟢"
        elif total_risk <= 30:
            embed_color = EMBED_COLORS['warning']
            risk_emoji = "🟡"
        else:
            embed_color = EMBED_COLORS['error']
            risk_emoji = "🔴"
        
        # ارسال پیام تأیید
        embed = create_embed(
            f"🚁 عملیات {operation_type.upper()} آغاز شد",
            f"**شماره عملیات:** `{operation_id}`\n"
            f"**نوع:** {valid_operations[operation_type]}\n"
            f"**منطقه:** {sector_data['name']}\n"
            f"**واحد:** {unit_data['name']}\n"
            f"**فرمانده:** {ctx.author.mention}\n"
            f"**هدف:** {objective}\n"
            f"**نیروی درگیر:** {personnel_needed} نفر\n"
            f"**مدت تخمینی:** {duration} دقیقه\n"
            f"**سطح ریسک:** {risk_emoji} {total_risk}%\n"
            f"**احتمال موفقیت:** {success_probability}%\n"
            f"**هزینه عملیاتی:** ${operation_data['cost']:,.0f}\n\n"
            f"**جزئیات عملیات:**\n{operation_description}",
            embed_color
        )
        
        embed.set_footer(text=f"شروع: {datetime.now().strftime('%H:%M')} | تکمیل تقریبی: {(datetime.now() + timedelta(minutes=duration)).strftime('%H:%M')}")
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830284.png")
        
        await ctx.send(embed=embed)
        
        # اطلاع‌رسانی به کانال عملیات
        ops_channel = discord.utils.get(ctx.guild.channels, name='🚁│عملیات-زمینی')
        if ops_channel:
            ops_embed = create_embed(
                "🛡️ عملیات زمینی جدید",
                f"**{operation_id}** - {operation_type} در {sector_data['name']} توسط {ctx.author.mention}",
                EMBED_COLORS['primary']
            )
            await ops_channel.send(embed=ops_embed)
        
        # در صورت عملیات پرریسک، اطلاع‌رسانی ویژه
        if total_risk > 40:
            command_channel = discord.utils.get(ctx.guild.channels, name='🛡️│فرماندهی-زمینی')
            if command_channel:
                high_risk_embed = create_embed(
                    "⚠️ عملیات پرریسک",
                    f"**عملیات:** {operation_id}\n"
                    f"**ریسک:** {total_risk}%\n"
                    f"**نظارت ویژه مورد نیاز**",
                    EMBED_COLORS['error']
                )
                await command_channel.send(embed=high_risk_embed)

    @commands.command(name='عملیات_فعال')
    async def active_operations_status(self, ctx):
        """نمایش عملیات زمینی در حال انجام"""
        
        if not self.active_operations:
            embed = create_embed(
                "📋 عملیات فعال",
                "در حال حاضر هیچ عملیات زمینی در جریان نیست.\n\n"
                "🛡️ وضعیت عادی در تمام مناطق",
                EMBED_COLORS['primary']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            "🚁 عملیات زمینی فعال",
            f"تعداد عملیات در حال انجام: **{len(self.active_operations)}**",
            EMBED_COLORS['primary']
        )
        
        for operation_id, operation in list(self.active_operations.items())[:8]:  # نمایش حداکثر 8 عملیات
            elapsed_time = datetime.now() - operation['start_time']
            elapsed_minutes = int(elapsed_time.total_seconds() / 60)
            remaining_minutes = operation['duration_minutes'] - elapsed_minutes
            
            if remaining_minutes > 0:
                status_text = f"⏳ {remaining_minutes} دقیقه باقیمانده"
                if remaining_minutes > 60:
                    hours = remaining_minutes // 60
                    minutes = remaining_minutes % 60
                    status_text = f"⏳ {hours}:{minutes:02d} باقیمانده"
                status_emoji = "🟡"
            else:
                status_text = "✅ آماده بازگشت"
                status_emoji = "🟢"
            
            # تعیین ایموجی ریسک
            risk_emoji = "🟢" if operation['risk_level'] <= 15 else "🟡" if operation['risk_level'] <= 30 else "🔴"
            
            # محاسبه پیشرفت
            progress = min(100, (elapsed_minutes / operation['duration_minutes']) * 100)
            progress_bar = "█" * int(progress / 12.5) + "░" * (8 - int(progress / 12.5))
            
            embed.add_field(
                name=f"{status_emoji} {operation['id']}",
                value=f"**نوع:** {operation['type']}\n"
                      f"**منطقه:** {operation['sector_name']}\n"
                      f"**واحد:** {operation['unit_name']}\n"
                      f"**فرمانده:** {operation['commander']}\n"
                      f"**نیرو:** {operation['personnel_involved']} نفر\n"
                      f"**ریسک:** {risk_emoji} {operation['risk_level']}%\n"
                      f"**پیشرفت:** {progress:.1f}%\n"
                      f"`{progress_bar}`\n"
                      f"**وضعیت:** {status_text}",
                inline=True
            )
        
        if len(self.active_operations) > 8:
            embed.add_field(
                name="📊 سایر عملیات",
                value=f"و {len(self.active_operations) - 8} عملیات دیگر در حال انجام...",
                inline=False
            )
        
        # آمار کلی عملیات فعال
        total_personnel = sum([op['personnel_involved'] for op in self.active_operations.values()])
        high_risk_ops = len([op for op in self.active_operations.values() if op['risk_level'] > 30])
        
        embed.add_field(
            name="📈 آمار کلی",
            value=f"**کل نیروی درگیر:** {total_personnel:,} نفر\n"
                  f"**عملیات پرریسک:** {high_risk_ops}\n"
                  f"**متوسط ریسک:** {sum([op['risk_level'] for op in self.active_operations.values()]) / len(self.active_operations):.1f}%",
            inline=False
        )
        
        embed.set_footer(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        await ctx.send(embed=embed)

    @commands.command(name='آمار_عملیاتی')
    @has_role(['فرمانده زمینی', 'افسر عملیات', 'مدیر'])
    async def operational_statistics(self, ctx):
        """نمایش آمار کامل عملیاتی نیروی زمینی"""
        
        embed = create_embed(
            "📊 آمار عملیاتی نیروی زمینی اسرائیل",
            f"**دوره گزارش:** سال جاری\n**آخرین به‌روزرسانی:** {datetime.now().strftime('%Y/%m/%d')}",
            EMBED_COLORS['primary']
        )
        
        # آمار عملیات
        success_rate = (self.operational_stats['successful_operations'] / max(1, self.operational_stats['total_operations'])) * 100
        
        embed.add_field(
            name="⚔️ آمار عملیات",
            value=f"**کل عملیات:** {self.operational_stats['total_operations']:,}\n"
                  f"**عملیات موفق:** {self.operational_stats['successful_operations']:,}\n"
                  f"**نرخ موفقیت:** {success_rate:.1f}%\n"
                  f"**گشت‌زنی‌ها:** {self.operational_stats['patrols_conducted']:,}\n"
                  f"**تمرینات:** {self.operational_stats['training_exercises']:,}",
            inline=True
        )
        
        # آمار امنیتی
        embed.add_field(
            name="🔒 آمار امنیتی",
            value=f"**دستگیری‌ها:** {self.operational_stats['arrests_made']:,}\n"
                  f"**اسلحه کشف شده:** {self.operational_stats['weapons_seized']:,}\n"
                  f"**تونل‌های تخریب شده:** {self.operational_stats['tunnels_destroyed']}\n"
                  f"**حملات جلوگیری شده:** {self.operational_stats['casualties_prevented']:,}\n"
                  f"**ایست‌های فعال:** {self.operational_stats['checkpoints_manned']:,}",
            inline=True
        )
        
        # آمار پرسنل
        total_personnel = sum(self.personnel.values())
        
        embed.add_field(
            name="👥 آمار نیرو",
            value=f"**کل پرسنل:** {total_personnel:,} نفر\n"
                  f"**افسران:** {self.personnel['officers']:,}\n"
                  f"**درجه‌داران:** {self.personnel['ncos']:,}\n"
                  f"**سربازان:** {self.personnel['soldiers']:,}\n"
                  f"**متخصصان:** {self.personnel['engineers'] + self.personnel['medics']:,}\n"
                  f"**آموزش‌دیدگان:** {self.personnel['trainees']:,}",
            inline=True
        )
        
        # آمار تجهیزات
        total_armored = sum([unit['total_count'] for unit in self.armored_units.values()])
        operational_armored = sum([unit['operational'] for unit in self.armored_units.values()])
        readiness_percent = (operational_armored / total_armored) * 100
        
        embed.add_field(
            name="🛡️ آمار تجهیزات",
            value=f"**تجهیزات زرهی:** {total_armored:,}\n"
                  f"**عملیاتی:** {operational_armored:,}\n"
                  f"**آمادگی کلی:** {readiness_percent:.1f}%\n"
                  f"**ساعات نگهداری:** {self.operational_stats['equipment_maintained']:,}\n"
                  f"**تانک‌های مرکاوا:** {self.armored_units['Merkava_MK4']['total_count'] + self.armored_units['Merkava_MK3']['total_count']}",
            inline=True
        )
        
        # محاسبه هزینه‌های عملیاتی
        daily_operational_cost = sum([
            unit['cost_per_hour'] * unit['operational'] * 8  # 8 ساعت فعالیت روزانه
            for unit in self.armored_units.values()
        ])
        
        monthly_cost = daily_operational_cost * 30
        
        embed.add_field(
            name="💰 اقتصادی",
            value=f"**هزینه عملیاتی روزانه:** ${daily_operational_cost:,.0f}\n"
                  f"**هزینه ماهانه:** ${monthly_cost:,.0f}\n"
                  f"**متوسط هزینه عملیات:** ${monthly_cost / max(1, self.operational_stats['total_operations']):,.0f}\n"
                  f"**بازده عملیاتی:** بالا\n"
                  f"**صرفه‌جویی سوخت:** 8%",
            inline=True
        )
        
        # وضعیت آمادگی
        embed.add_field(
            name="⚡ وضعیت آمادگی",
            value=f"**سطح آمادگی:** {self.readiness_level}\n"
                  f"**وضعیت هشدار:** {self.alert_status}\n"
                  f"**زمان پاسخ:** <15 دقیقه\n"
                  f"**پوشش مرزی:** 100%\n"
                  f"**آمادگی 24/7:** ✅",
            inline=True
        )
        
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Israel_Defense_Forces_Logo.svg/200px-Israel_Defense_Forces_Logo.svg.png")
        embed.set_footer(text="מוכנים תמיד | همیشه آماده")
        
        await ctx.send(embed=embed)

    @commands.command(name='تغییر_آمادگی')
    @has_role(['فرمانده کل', 'فرمانده زمینی', 'مدیر'])
    async def change_readiness_level(self, ctx, new_level: str):
        """تغییر سطح آمادگی نیروی زمینی"""
        
        valid_levels = {
            'HIGH': 'آمادگی بالا - تهدید فوری',
            'ELEVATED': 'آمادگی افزایش یافته',
            'NORMAL': 'آمادگی عادی',
            'LOW': 'آمادگی کم - وضعیت آرام'
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
            'HIGH': 'هشدار قرمز - آمادگی کامل',
            'ELEVATED': 'هشدار نارنجی - آمادگی افزایش یافته',
            'NORMAL': 'آمادگی عادی',
            'LOW': 'وضعیت آرام'
        }
        
        self.alert_status = alert_statuses[new_level]
        
        # رنگ embed بر اساس سطح
        level_colors = {
            'HIGH': 0xFF0000,     # قرمز
            'ELEVATED': 0xFF8800, # نارنجی
            'NORMAL': 0x00FF00,   # سبز
            'LOW': 0x0088FF       # آبی
        }
        
        embed = create_embed(
            f"⚡ تغییر سطح آمادگی نیروی زمینی",
            f"**سطح قبلی:** {old_level}\n"
            f"**سطح جدید:** {new_level}\n"
            f"**وضعیت:** {self.alert_status}\n"
            f"**تغییر توسط:** {ctx.author.mention}\n"
            f"**زمان:** {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            level_colors[new_level]
        )
        
        # اقدامات خودکار بر اساس سطح آمادگی
        if new_level == 'HIGH':
            embed.add_field(
                name="🚨 اقدامات فوری",
                value="• تمام واحدها در حالت آماده‌باش کامل\n"
                      "• افزایش گشت‌های مرزی\n"
                      "• فعال‌سازی تمام ایست‌های بازرسی\n"
                      "• لغو مرخصی‌ها و تعطیلات\n"
                      "• آمادگی کامل تجهیزات زرهی",
                inline=False
            )
        elif new_level == 'ELEVATED':
            embed.add_field(
                name="⚠️ اقدامات افزایش یافته",
                value="• افزایش گشت‌زنی‌ها\n"
                      "• تقویت ایست‌های کلیدی\n"
                      "• آمادگی واحدهای ویژه\n"
                      "• نظارت بیشتر بر مناطق حساس",
                inline=False
            )
        
        embed.set_footer(text="تمام واحدها اطلاع یافتند")
        await ctx.send(embed=embed)
        
        # به‌روزرسانی وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"مرزهای اسرائیل | {self.alert_status} 🛡️"
            )
        )
        
        # اطلاع‌رسانی به کانال فرماندهی
        command_channel = discord.utils.get(ctx.guild.channels, name='🛡️│فرماندهی-زمینی')
        if command_channel and command_channel != ctx.channel:
            await command_channel.send(embed=embed)

    @commands.command(name='گزارش_میدان')
    @has_role(['افسر عملیات', 'فرمانده واحد', 'سرباز'])
    async def field_report(self, ctx, operation_id: str, status: str, *, details: str = ""):
        """گزارش میدانی از عملیات"""
        
        if operation_id not in self.active_operations:
            embed = create_embed(
                "❌ عملیات یافت نشد",
                f"عملیات با شماره `{operation_id}` یافت نشد یا تکمیل شده است.",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        operation = self.active_operations[operation_id]
        
        # بررسی دسترسی
        if operation['commander'] != ctx.author.display_name and not any(role.name in ['فرمانده زمینی', 'مدیر'] for role in ctx.author.roles):
            embed = create_embed(
                "❌ عدم دسترسی",
                "فقط فرمانده عملیات یا فرماندهان ارشد می‌توانند گزارش ارسال کنند.",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        valid_statuses = ['موفق', 'ناموفق', 'در_حال_انجام', 'نیاز_به_پشتیبانی', 'اورژانسی', 'تلفات', 'تکمیل_جزئی']
        
        if status not in valid_statuses:
            embed = create_embed(
                "❌ وضعیت نامعتبر",
                f"**وضعیت‌های مجاز:** {', '.join(valid_statuses)}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # ثبت گزارش
        if 'field_reports' not in operation:
            operation['field_reports'] = []
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'reporter': ctx.author.display_name,
            'status': status,
            'details': details,
            'location': operation['sector_name']
        }
        
        operation['field_reports'].append(report)
        
        # تعیین رنگ و ایموجی
        status_info = {
            'موفق': ('🟢', 'عملیات با موفقیت انجام شد', EMBED_COLORS['success']),
            'ناموفق': ('🔴', 'عملیات ناموفق بود', EMBED_COLORS['error']),
            'در_حال_انجام': ('🟡', 'عملیات در حال انجام', EMBED_COLORS['warning']),
            'نیاز_به_پشتیبانی': ('🟠', 'نیاز به پشتیبانی فوری', EMBED_COLORS['warning']),
            'اورژانسی': ('🚨', 'وضعیت اورژانسی!', EMBED_COLORS['error']),
            'تلفات': ('💔', 'تلفات گزارش شده', EMBED_COLORS['error']),
            'تکمیل_جزئی': ('🔵', 'عملیات تا حدی انجام شد', EMBED_COLORS['primary'])
        }
        
        emoji, description, color = status_info[status]
        
        embed = create_embed(
            f"{emoji} گزارش میدانی - {operation_id}",
            f"**وضعیت:** {description}\n"
            f"**گزارش‌دهنده:** {ctx.author.mention}\n"
            f"**عملیات:** {operation['type']} در {operation['sector_name']}\n"
            f"**واحد:** {operation['unit_name']}\n"
            f"**زمان گزارش:** {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"**جزئیات:**\n{details if details else 'بدون جزئیات اضافی'}",
            color
        )
        
        await ctx.send(embed=embed)
        
        # اطلاع‌رسانی به کانال عملیات
        ops_channel = discord.utils.get(ctx.guild.channels, name='🚁│عملیات-زمینی')
        if ops_channel and ops_channel != ctx.channel:
            await ops_channel.send(embed=embed)
        
        # در صورت اورژانسی یا تلفات، اطلاع‌رسانی فوری
        if status in ['اورژانسی', 'تلفات']:
            command_channel = discord.utils.get(ctx.guild.channels, name='🛡️│فرماندهی-زمینی')
            if command_channel:
                emergency_embed = create_embed(
                    "🚨 هشدار فوری",
                    f"**عملیات:** {operation_id}\n"
                    f"**وضعیت:** {status}\n"
                    f"**منطقه:** {operation['sector_name']}\n"
                    f"**گزارش‌دهنده:** {ctx.author.mention}\n\n"
                    f"**اقدام فوری مورد نیاز!**",
                    EMBED_COLORS['error']
                )
                await command_channel.send("@here", embed=emergency_embed)

    @tasks.loop(hours=4)
    async def border_patrol(self):
        """گشت‌زنی خودکار مرزها"""
        try:
            # انتخاب منطقه با تهدید بالا برای گشت اضافی
            high_threat_sectors = [
                sector_id for sector_id, sector in self.operational_sectors.items() 
                if sector['threat_level'] == 'بالا'
            ]
            
            if high_threat_sectors:
                selected_sector = random.choice(high_threat_sectors)
                sector_data = self.operational_sectors[selected_sector]
                
                # انتخاب واحد مناسب برای گشت
                available_units = []
                for unit_type in sector_data['deployed_units']:
                    if unit_type in self.infantry_units:
                        unit = self.infantry_units[unit_type]
                        if unit['operational'] >= 100:  # حداقل 100 نفر
                            available_units.append((unit_type, unit))
                    elif unit_type in self.armored_units:
                        unit = self.armored_units[unit_type]
                        if unit['operational'] >= 2:  # حداقل 2 دستگاه
                            available_units.append((unit_type, unit))
                
                if available_units:
                    selected_unit_type, selected_unit = random.choice(available_units)
                    
                    # ایجاد گشت خودکار
                    patrol_id = f"AUTO-{self.operation_counter}"
                    self.operation_counter += 1
                    
                    if selected_unit_type in self.infantry_units:
                        personnel = 50
                        equipment = 1
                        selected_unit['operational'] -= personnel
                    else:
                        personnel = selected_unit['crew_size'] * 2
                        equipment = 2
                        selected_unit['operational'] -= equipment
                    
                    operation_data = {
                        'id': patrol_id,
                        'type': 'گشت خودکار',
                        'description': 'گشت‌زنی مرزی خودکار',
                        'sector': selected_sector,
                        'sector_name': sector_data['name'],
                        'unit_type': selected_unit_type,
                        'unit_name': selected_unit['name'],
                        'objective': 'نظارت و کنترل مرز',
                        'commander': 'سیستم خودکار',
                        'personnel_involved': personnel,
                        'equipment_used': equipment,
                        'start_time': datetime.now(),
                        'duration_minutes': random.randint(180, 360),
                        'status': 'خودکار',
                        'risk_level': 15,
                        'success_probability': 90,
                        'cost': selected_unit.get('cost_per_hour', 500) * 3
                    }
                    
                    self.active_operations[patrol_id] = operation_data
                    self.operational_stats['patrols_conducted'] += 1
                    
                    # اطلاع‌رسانی
                    guild = self.get_guild(GUILD_ID)
                    if guild:
                        ops_channel = discord.utils.get(guild.channels, name='🚁│عملیات-زمینی')
                        if ops_channel:
                            embed = create_embed(
                                "🔄 گشت خودکار آغاز شد",
                                f"**شماره:** {patrol_id}\n"
                                f"**منطقه:** {sector_data['name']}\n"
                                f"**واحد:** {selected_unit['name']}\n"
                                f"**نیرو:** {personnel} نفر\n"
                                f"**مدت:** {operation_data['duration_minutes']} دقیقه",
                                EMBED_COLORS['primary']
                            )
                            await ops_channel.send(embed=embed)
                            
        except Exception as e:
            logger.error(f"خطا در گشت‌زنی خودکار: {e}")

    @tasks.loop(hours=6)
    async def equipment_maintenance(self):
        """چرخه تعمیر و نگهداری تجهیزات"""
        try:
            # تعمیر تجهیزات زرهی
            for unit_id, unit in self.armored_units.items():
                # تکمیل تعمیرات
                if unit['maintenance'] > 0:
                    if random.random() < 0.4:  # 40% احتمال
                        repaired = min(unit['maintenance'], random.randint(1, 3))
                        unit['maintenance'] -= repaired
                        unit['operational'] += repaired
                
                # نیاز به تعمیر جدید
                if unit['operational'] > 0:
                    if random.random() < 0.03:  # 3% احتمال
                        need_maintenance = min(unit['operational'], random.randint(1, 2))
                        unit['operational'] -= need_maintenance
                        unit['maintenance'] += need_maintenance
            
            # تعمیر سیستم‌های توپخانه
            for system_id, system in self.artillery_systems.items():
                if 'maintenance' in system and system['maintenance'] > 0:
                    if random.random() < 0.3:
                        system['maintenance'] -= 1
                        system['operational'] += 1
                
                if random.random() < 0.02:  # 2% احتمال
                    if system['operational'] > 0:
                        system['operational'] -= 1
                        if 'maintenance' not in system:
                            system['maintenance'] = 0
                        system['maintenance'] += 1
            
            # به‌روزرسانی آمار
            self.operational_stats['equipment_maintained'] += random.randint(50, 150)
            
        except Exception as e:
            logger.error(f"خطا در تعمیر و نگهداری: {e}")

    @tasks.loop(hours=8)
    async def training_exercises(self):
        """تمرینات نظامی خودکار"""
        try:
            # احتمال برگزاری تمرین
            if random.random() < 0.4:  # 40% احتمال
                # انتخاب واحد برای تمرین
                training_units = []
                
                # واحدهای پیاده‌نظام
                for unit_id, unit in self.infantry_units.items():
                    if unit['training'] > 20:
                        training_units.append((unit_id, unit, 'infantry'))
                
                # تجهیزات زرهی
                for unit_id, unit in self.armored_units.items():
                    if unit['training'] > 0:
                        training_units.append((unit_id, unit, 'armored'))
                
                if training_units:
                    selected_unit_id, selected_unit, unit_type = random.choice(training_units)
                    
                    # نوع تمرین
                    training_types = [
                        'تمرین تیراندازی', 'تمرین تاکتیکی', 'تمرین مشترک',
                        'شبیه‌سازی نبرد', 'تمرین اضطراری', 'آموزش بقا'
                    ]
                    
                    training_type = random.choice(training_types)
                    
                    # به‌روزرسانی آمار
                    self.operational_stats['training_exercises'] += 1
                    
                    # اطلاع‌رسانی
                    guild = self.get_guild(GUILD_ID)
                    if guild:
                        training_channel = discord.utils.get(guild.channels, name='🎓│آموزش-نظامی')
                        if training_channel:
                            embed = create_embed(
                                "🎓 تمرین نظامی",
                                f"**واحد:** {selected_unit['name']}\n"
                                f"**نوع تمرین:** {training_type}\n"
                                f"**مدت:** {random.randint(120, 300)} دقیقه\n"
                                f"**شرکت‌کنندگان:** {random.randint(50, 200)} نفر",
                                EMBED_COLORS['primary']
                            )
                            await training_channel.send(embed=embed)
                            
        except Exception as e:
            logger.error(f"خطا در تمرینات نظامی: {e}")

    @tasks.loop(hours=12)
    async def intelligence_gathering(self):
        """جمع‌آوری اطلاعات و نظارت"""
        try:
            # شبیه‌سازی فعالیت‌های اطلاعاتی
            intel_activities = [
                'رصد فعالیت‌های مشکوک',
                'بررسی تردد مرزی',
                'نظارت بر ارتباطات',
                'تحلیل تصاویر ماهواره‌ای',
                'گزارش‌گیری از منابع'
            ]
            
            activity = random.choice(intel_activities)
            
            # احتمال کشف تهدید
            if random.random() < 0.2:  # 20% احتمال
                threat_detected = True
                threat_types = [
                    'تونل جدید', 'انبار اسلحه', 'گروه مسلح',
                    'فعالیت مشکوک', 'تجمع غیرعادی'
                ]
                threat = random.choice(threat_types)
            else:
                threat_detected = False
                threat = None
            
            # اطلاع‌رسانی در صورت کشف تهدید
            if threat_detected:
                guild = self.get_guild(GUILD_ID)
                if guild:
                    intel_channel = discord.utils.get(guild.channels, name='🚨│هشدارهای-امنیتی')
                    if intel_channel:
                        embed = create_embed(
                            "🔍 گزارش اطلاعاتی",
                            f"**فعالیت:** {activity}\n"
                            f"**تهدید شناسایی شده:** {threat}\n"
                            f"**زمان:** {datetime.now().strftime('%H:%M')}\n"
                            f"**وضعیت:** نیاز به بررسی بیشتر",
                            EMBED_COLORS['warning']
                        )
                        await intel_channel.send(embed=embed)
                        
                        # افزایش حوادث در یک منطقه تصادفی
                        random_sector = random.choice(list(self.operational_sectors.keys()))
                        self.operational_sectors[random_sector]['recent_incidents'] += 1
            
        except Exception as e:
            logger.error(f"خطا در جمع‌آوری اطلاعات: {e}")

    async def _check_operation_completion(self):
        """بررسی تکمیل عملیات‌ها"""
        try:
            current_time = datetime.now()
            completed_operations = []
            
            for operation_id, operation in self.active_operations.items():
                elapsed_time = current_time - operation['start_time']
                if elapsed_time.total_seconds() >= operation['duration_minutes'] * 60:
                    completed_operations.append(operation_id)
            
            for operation_id in completed_operations:
                await self._complete_operation(operation_id)
                
        except Exception as e:
            logger.error(f"خطا در بررسی تکمیل عملیات‌ها: {e}")

    async def _complete_operation(self, operation_id: str):
        """تکمیل عملیات"""
        try:
            if operation_id not in self.active_operations:
                return
            
            operation = self.active_operations[operation_id]
            
            # بازگرداندن نیرو و تجهیزات
            unit_type = operation['unit_type']
            
            if unit_type in self.armored_units or unit_type in self.artillery_systems:
                if unit_type in self.armored_units:
                    self.armored_units[unit_type]['operational'] += operation['equipment_used']
                else:
                    self.artillery_systems[unit_type]['operational'] += operation['equipment_used']
            elif unit_type in self.infantry_units:
                self.infantry_units[unit_type]['operational'] += operation['personnel_involved']
            
            # تعیین نتیجه عملیات
            success = random.random() < (operation['success_probability'] / 100)
            
            if success:
                result = "موفقیت‌آمیز"
                self.operational_stats['successful_operations'] += 1
                
                # پاداش‌های خاص برای انواع عملیات موفق
                if operation['type'] == 'دستگیری':
                    self.operational_stats['arrests_made'] += random.randint(1, 5)
                elif operation['type'] == 'تخریب':
                    self.operational_stats['tunnels_destroyed'] += 1
                elif operation['type'] in ['گشت', 'تأمین_امنیت']:
                    self.operational_stats['casualties_prevented'] += random.randint(0, 3)
            else:
                result = "نیمه‌موفق"
            
            # به‌روزرسانی آمار کلی
            self.operational_stats['total_operations'] += 1
            
            # حذف از عملیات فعال
            del self.active_operations[operation_id]
            
            # اطلاع‌رسانی
            guild = self.get_guild(GUILD_ID)
            if guild:
                ops_channel = discord.utils.get(guild.channels, name='🚁│عملیات-زمینی')
                if ops_channel:
                    embed = create_embed(
                        f"✅ عملیات {operation_id} تکمیل شد",
                        f"**نوع:** {operation['type']}\n"
                        f"**منطقه:** {operation['sector_name']}\n"
                        f"**واحد:** {operation['unit_name']}\n"
                        f"**فرمانده:** {operation['commander']}\n"
                        f"**مدت:** {operation['duration_minutes']} دقیقه\n"
                        f"**نتیجه:** {result}\n"
                        f"**هزینه:** ${operation['cost']:,.0f}",
                        EMBED_COLORS['success'] if success else EMBED_COLORS['warning']
                    )
                    await ops_channel.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"خطا در تکمیل عملیات {operation_id}: {e}")

async def run_ground_forces_bot():
    """اجرای ربات نیروی زمینی"""
    bot = IsraeliGroundForcesBot()
    try:
        await bot.start(DISCORD_BOT_TOKEN_GROUND_FORCES)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات نیروی زمینی: {e}")

if __name__ == "__main__":
    """
    🛡️ ربات نیروی زمینی اسرائیل
    
    این ربات مسئول مدیریت کامل نیروی زمینی اسرائیل است و شامل:
    
    🛡️ تجهیزات زرهی:
    - تانک مرکاوا MK4 و MK3
    - ناقل پرسنل نامر و ایتان
    - تجهیزات پیشرفته زرهی
    
    ⚔️ واحدهای پیاده‌نظام:
    - تیپ گولانی (رزمی)
    - تیپ چترباز (ویژه)
    - تیپ نحال (پیشگام)
    - تیپ کفیر (ضدتروریسم)
    
    🎯 سیستم‌های آتش:
    - توپخانه M109
    - راکت انداز چندلوله لینکس
    - موشک‌های ضدتانک اسپایک
    
    🗺️ مناطق عملیاتی:
    - محیط غزه، مرز لبنان، کرانه باختری، دره اردن
    
    🎯 قابلیت‌ها:
    - مدیریت عملیات زمینی
    - کنترل مرزها
    - آمار عملیاتی کامل
    - گشت‌زنی خودکار
    - تعمیر و نگهداری
    - تمرینات نظامی
    - جمع‌آوری اطلاعات
    
    دستورات اصلی:
    !زمینی_وضعیت_واحدها - وضعیت تجهیزات و واحدها
    !زمینی_مناطق_عملیاتی - مناطق تحت کنترل
    !زمینی_عملیات - شروع عملیات جدید
    !زمینی_عملیات_فعال - عملیات جاری
    !زمینی_آمار_عملیاتی - آمار کامل
    !زمینی_تغییر_آمادگی - تغییر سطح آمادگی
    !زمینی_گزارش_میدان - گزارش از عملیات
    """
    
    import asyncio
    asyncio.run(run_ground_forces_bot())