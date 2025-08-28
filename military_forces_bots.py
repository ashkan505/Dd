#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات‌های نیروهای نظامی اسرائیل
Israeli Military Forces Bots

این فایل شامل پیاده‌سازی ربات‌های نیروهای سه‌گانه است:
- نیروی هوایی اسرائیل (IAF)
- نیروی زمینی اسرائیل (IDF Ground Forces)
- نیروی دریایی اسرائیل (Israeli Navy)

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

# ======================= ربات نیروی هوایی اسرائیل =======================

class IsraeliAirForceBot(commands.Bot):
    """
    ربات نیروی هوایی اسرائیل (IAF)
    مسئول مدیریت عملیات هوایی، جنگنده‌ها، پهپادها و دفاع هوایی
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!هوایی_',
            intents=intents,
            help_command=None,
            description="نیروی هوایی اسرائیل - حاکمیت آسمان"
        )
        
        self.db = DatabaseManager()
        
        # ناوگان هوایی
        self.aircraft_fleet = {
            'F-35I_Adir': {
                'name': 'F-35I آدیر',
                'type': 'جنگنده نسل 5',
                'count': 36,
                'available': 32,
                'maintenance': 4,
                'operational_cost': 50000,
                'capabilities': ['نامرئی', 'چندمنظوره', 'حمله زمینی', 'هوا به هوا']
            },
            'F-16I_Sufa': {
                'name': 'F-16I سوفا',
                'type': 'جنگنده چندمنظوره',
                'count': 175,
                'available': 160,
                'maintenance': 15,
                'operational_cost': 25000,
                'capabilities': ['حمله زمینی', 'هوا به هوا', 'اسکورت', 'گشت‌زنی']
            },
            'F-15I_RaAm': {
                'name': 'F-15I رعم',
                'type': 'جنگنده سنگین',
                'count': 25,
                'available': 22,
                'maintenance': 3,
                'operational_cost': 35000,
                'capabilities': ['برد بلند', 'حمله عمقی', 'برتری هوایی']
            },
            'AH-64_Apache': {
                'name': 'AH-64 آپاچی',
                'type': 'بالگرد تهاجمی',
                'count': 48,
                'available': 42,
                'maintenance': 6,
                'operational_cost': 20000,
                'capabilities': ['پشتیبانی زمینی', 'ضدتانک', 'عملیات شبانه']
            },
            'Eitan_UAV': {
                'name': 'پهپاد ایتان',
                'type': 'پهپاد MALE',
                'count': 10,
                'available': 8,
                'maintenance': 2,
                'operational_cost': 15000,
                'capabilities': ['جاسوسی', 'نظارت', 'حمله دقیق', 'پرواز طولانی']
            },
            'Hermes_450': {
                'name': 'پهپاد هرمس 450',
                'type': 'پهپاد تاکتیکی',
                'count': 30,
                'available': 26,
                'maintenance': 4,
                'operational_cost': 8000,
                'capabilities': ['شناسایی', 'نظارت', 'هدایت موشک']
            }
        }
        
        # پایگاه‌های هوایی
        self.airbases = {
            'Nevatim': {
                'name': 'پایگاه نواتیم',
                'location': 'جنوب اسرائیل',
                'aircraft': ['F-35I_Adir', 'F-16I_Sufa'],
                'status': 'فعال',
                'readiness': 'آمادگی کامل'
            },
            'Ramon': {
                'name': 'پایگاه رامون',
                'location': 'صحرای نگب',
                'aircraft': ['F-16I_Sufa', 'F-15I_RaAm'],
                'status': 'فعال',
                'readiness': 'آمادگی کامل'
            },
            'Hatzerim': {
                'name': 'پایگاه هتزریم',
                'location': 'مرکز اسرائیل',
                'aircraft': ['F-16I_Sufa', 'AH-64_Apache'],
                'status': 'فعال',
                'readiness': 'آمادگی کامل'
            },
            'Palmachim': {
                'name': 'پایگاه پالماخیم',
                'location': 'ساحل مدیترانه',
                'aircraft': ['Eitan_UAV', 'Hermes_450'],
                'status': 'فعال',
                'readiness': 'آمادگی کامل'
            }
        }
        
        # عملیات فعال
        self.active_operations = []
        
        # آمار عملیاتی
        self.operational_stats = {
            'total_sorties': 0,
            'combat_missions': 0,
            'recon_missions': 0,
            'training_flights': 0,
            'air_to_air_kills': 0,
            'ground_targets_destroyed': 0
        }
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - نیروی هوایی اسرائیل آماده است!')
        
        if not self.daily_operations.is_running():
            self.daily_operations.start()
        if not self.maintenance_cycle.is_running():
            self.maintenance_cycle.start()
        if not self.patrol_missions.is_running():
            self.patrol_missions.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="آسمان اسرائیل ✈️"
            )
        )

    @commands.command(name='ناوگان')
    async def fleet_status(self, ctx):
        """نمایش وضعیت ناوگان هوایی"""
        embed = create_embed(
            "✈️ ناوگان نیروی هوایی اسرائیل",
            "وضعیت فعلی تجهیزات هوایی:",
            EMBED_COLORS['primary']
        )
        
        total_aircraft = 0
        total_available = 0
        
        for aircraft_id, aircraft in self.aircraft_fleet.items():
            total_aircraft += aircraft['count']
            total_available += aircraft['available']
            
            availability_percent = (aircraft['available'] / aircraft['count']) * 100
            status_emoji = "🟢" if availability_percent >= 80 else "🟡" if availability_percent >= 60 else "🔴"
            
            embed.add_field(
                name=f"{status_emoji} {aircraft['name']}",
                value=f"**نوع:** {aircraft['type']}\n"
                      f"**تعداد کل:** {aircraft['count']}\n"
                      f"**در دسترس:** {aircraft['available']}\n"
                      f"**تعمیرات:** {aircraft['maintenance']}\n"
                      f"**آمادگی:** {availability_percent:.1f}%\n"
                      f"**هزینه عملیاتی:** ${aircraft['operational_cost']:,}",
                inline=True
            )
        
        embed.add_field(
            name="📊 خلاصه کلی",
            value=f"**مجموع هواپیماها:** {total_aircraft}\n"
                  f"**آماده عملیات:** {total_available}\n"
                  f"**آمادگی کلی:** {(total_available/total_aircraft)*100:.1f}%",
            inline=False
        )
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830411.png")
        await ctx.send(embed=embed)

    @commands.command(name='پایگاه‌ها')
    async def airbases_status(self, ctx):
        """نمایش وضعیت پایگاه‌های هوایی"""
        embed = create_embed(
            "🛩️ پایگاه‌های نیروی هوایی",
            "وضعیت پایگاه‌های هوایی اسرائیل:",
            EMBED_COLORS['primary']
        )
        
        for base_id, base in self.airbases.items():
            aircraft_list = []
            for aircraft_type in base['aircraft']:
                if aircraft_type in self.aircraft_fleet:
                    aircraft_list.append(self.aircraft_fleet[aircraft_type]['name'])
            
            status_emoji = "🟢" if base['status'] == 'فعال' else "🔴"
            readiness_emoji = "⚡" if base['readiness'] == 'آمادگی کامل' else "⚠️"
            
            embed.add_field(
                name=f"{status_emoji} {base['name']}",
                value=f"**موقعیت:** {base['location']}\n"
                      f"**وضعیت:** {base['status']}\n"
                      f"**آمادگی:** {readiness_emoji} {base['readiness']}\n"
                      f"**هواپیماهای مستقر:**\n" + 
                      "\n".join([f"• {aircraft}" for aircraft in aircraft_list]),
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='ماموریت')
    @has_role(['فرمانده', 'خلبان', 'مدیر'])
    async def launch_mission(self, ctx, mission_type: str, aircraft_type: str, target: str = None):
        """راه‌اندازی ماموریت هوایی"""
        valid_missions = ['حمله', 'گشت‌زنی', 'شناسایی', 'اسکورت', 'تمرین']
        
        if mission_type not in valid_missions:
            embed = create_embed(
                "خطا ❌",
                f"نوع ماموریت نامعتبر!\nانواع موجود: {', '.join(valid_missions)}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if aircraft_type not in self.aircraft_fleet:
            embed = create_embed(
                "خطا ❌",
                f"نوع هواپیما یافت نشد!\nهواپیماهای موجود:\n" +
                "\n".join([f"• {k}: {v['name']}" for k, v in self.aircraft_fleet.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        aircraft = self.aircraft_fleet[aircraft_type]
        
        # بررسی در دسترس بودن
        if aircraft['available'] < 1:
            embed = create_embed(
                "هواپیما در دسترس نیست ❌",
                f"{aircraft['name']} در حال حاضر در دسترس نیست!\n"
                f"تعداد موجود: {aircraft['available']}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی قابلیت‌ها
        mission_requirements = {
            'حمله': ['حمله زمینی', 'چندمنظوره', 'ضدتانک'],
            'گشت‌زنی': ['گشت‌زنی', 'هوا به هوا', 'برتری هوایی'],
            'شناسایی': ['جاسوسی', 'نظارت', 'شناسایی'],
            'اسکورت': ['اسکورت', 'هوا به هوا'],
            'تمرین': []  # همه هواپیماها می‌توانند تمرین کنند
        }
        
        required_caps = mission_requirements.get(mission_type, [])
        if required_caps and not any(cap in aircraft['capabilities'] for cap in required_caps):
            embed = create_embed(
                "قابلیت نامناسب ❌",
                f"{aircraft['name']} برای ماموریت {mission_type} مناسب نیست!\n"
                f"قابلیت‌های مورد نیاز: {', '.join(required_caps)}\n"
                f"قابلیت‌های موجود: {', '.join(aircraft['capabilities'])}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # ایجاد ماموریت
        mission_id = f"AF{random.randint(1000, 9999)}"
        duration = random.randint(30, 180)  # 30 تا 180 دقیقه
        
        mission = {
            'id': mission_id,
            'type': mission_type,
            'aircraft': aircraft_type,
            'aircraft_name': aircraft['name'],
            'target': target or 'نامشخص',
            'pilot': ctx.author.display_name,
            'start_time': datetime.now(),
            'duration': duration,
            'status': 'در حال انجام',
            'cost': aircraft['operational_cost']
        }
        
        self.active_operations.append(mission)
        
        # کاهش هواپیمای موجود
        aircraft['available'] -= 1
        
        # تولید جزئیات ماموریت با Gemini
        mission_prompt = f"""
        یک ماموریت {mission_type} با هواپیمای {aircraft['name']} شروع شده است.
        هدف: {target or 'عملیات معمول'}
        خلبان: {ctx.author.display_name}
        
        یک توضیح کوتاه و جذاب از این ماموریت بنویس (50-80 کلمه).
        """
        
        try:
            mission_description = await generate_text_with_gemini(mission_prompt)
        except:
            mission_description = f"ماموریت {mission_type} با موفقیت آغاز شد."
        
        embed = create_embed(
            f"✈️ ماموریت {mission_type} آغاز شد",
            f"**شماره ماموریت:** `{mission_id}`\n"
            f"**هواپیما:** {aircraft['name']}\n"
            f"**خلبان:** {ctx.author.mention}\n"
            f"**هدف:** {target or 'طبق برنامه'}\n"
            f"**مدت تخمینی:** {duration} دقیقه\n"
            f"**هزینه:** ${aircraft['operational_cost']:,}\n\n"
            f"**جزئیات:**\n{mission_description}",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"شروع: {datetime.now().strftime('%H:%M')}")
        await ctx.send(embed=embed)
        
        # اطلاع‌رسانی به کانال عملیات
        guild = ctx.guild
        ops_channel = discord.utils.get(guild.channels, name='عملیات-هوایی')
        if ops_channel:
            ops_embed = create_embed(
                "🚁 عملیات هوایی جدید",
                f"ماموریت `{mission_id}` توسط {ctx.author.mention} آغاز شد",
                EMBED_COLORS['primary']
            )
            await ops_channel.send(embed=ops_embed)

    @commands.command(name='عملیات_فعال')
    async def active_operations_cmd(self, ctx):
        """نمایش عملیات فعال"""
        if not self.active_operations:
            embed = create_embed(
                "عملیات فعال",
                "در حال حاضر هیچ عملیات هوایی در جریان نیست.",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            "🚁 عملیات هوایی فعال",
            f"تعداد عملیات در حال انجام: {len(self.active_operations)}",
            EMBED_COLORS['primary']
        )
        
        for mission in self.active_operations[:5]:  # نمایش 5 عملیات اول
            elapsed = datetime.now() - mission['start_time']
            remaining = mission['duration'] - int(elapsed.total_seconds() / 60)
            
            if remaining > 0:
                status = f"⏳ {remaining} دقیقه باقیمانده"
            else:
                status = "✅ آماده بازگشت"
            
            embed.add_field(
                name=f"ماموریت {mission['id']}",
                value=f"**نوع:** {mission['type']}\n"
                      f"**هواپیما:** {mission['aircraft_name']}\n"
                      f"**خلبان:** {mission['pilot']}\n"
                      f"**وضعیت:** {status}",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='آمار_عملیاتی')
    async def operational_statistics(self, ctx):
        """نمایش آمار عملیاتی"""
        embed = create_embed(
            "📊 آمار عملیاتی نیروی هوایی",
            "آمار کلی عملیات انجام شده:",
            EMBED_COLORS['primary']
        )
        
        embed.add_field(
            name="پرواز و ماموریت",
            value=f"**کل پروازها:** {self.operational_stats['total_sorties']:,}\n"
                  f"**ماموریت‌های رزمی:** {self.operational_stats['combat_missions']:,}\n"
                  f"**ماموریت‌های شناسایی:** {self.operational_stats['recon_missions']:,}\n"
                  f"**پروازهای تمرینی:** {self.operational_stats['training_flights']:,}",
            inline=True
        )
        
        embed.add_field(
            name="نتایج رزمی",
            value=f"**سرنگونی هوا به هوا:** {self.operational_stats['air_to_air_kills']}\n"
                  f"**اهداف زمینی منهدم شده:** {self.operational_stats['ground_targets_destroyed']}\n"
                  f"**نرخ موفقیت:** {95.7}%\n"
                  f"**تلفات:** 0",
            inline=True
        )
        
        # محاسبه هزینه کل
        total_cost = sum([aircraft['operational_cost'] * (aircraft['count'] - aircraft['available']) 
                         for aircraft in self.aircraft_fleet.values()])
        
        embed.add_field(
            name="اقتصادی",
            value=f"**هزینه عملیاتی امروز:** ${total_cost:,}\n"
                  f"**متوسط هزینه ماموریت:** ${25000:,}\n"
                  f"**بازده عملیاتی:** بالا",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @tasks.loop(hours=6)
    async def daily_operations(self):
        """عملیات روزانه خودکار"""
        try:
            # گشت‌زنی خودکار
            patrol_types = ['گشت مرزی', 'حفاظت آسمان', 'نظارت دریایی']
            patrol_type = random.choice(patrol_types)
            
            # انتخاب هواپیمای مناسب
            suitable_aircraft = []
            for aircraft_id, aircraft in self.aircraft_fleet.items():
                if aircraft['available'] > 0 and 'گشت‌زنی' in aircraft['capabilities']:
                    suitable_aircraft.append(aircraft_id)
            
            if suitable_aircraft:
                selected = random.choice(suitable_aircraft)
                aircraft = self.aircraft_fleet[selected]
                
                # ایجاد ماموریت خودکار
                mission_id = f"AUTO{random.randint(1000, 9999)}"
                mission = {
                    'id': mission_id,
                    'type': 'گشت‌زنی خودکار',
                    'aircraft': selected,
                    'aircraft_name': aircraft['name'],
                    'target': patrol_type,
                    'pilot': 'خودکار',
                    'start_time': datetime.now(),
                    'duration': 120,
                    'status': 'خودکار'
                }
                
                self.active_operations.append(mission)
                aircraft['available'] -= 1
                self.operational_stats['total_sorties'] += 1
                
                # اطلاع‌رسانی
                guild = self.get_guild(GUILD_ID)
                if guild:
                    ops_channel = discord.utils.get(guild.channels, name='عملیات-هوایی')
                    if ops_channel:
                        embed = create_embed(
                            "🔄 گشت خودکار",
                            f"**نوع:** {patrol_type}\n"
                            f"**هواپیما:** {aircraft['name']}\n"
                            f"**شماره ماموریت:** `{mission_id}`",
                            EMBED_COLORS['primary']
                        )
                        await ops_channel.send(embed=embed)
                        
        except Exception as e:
            logger.error(f"خطا در عملیات روزانه نیروی هوایی: {e}")

    @tasks.loop(hours=4)
    async def maintenance_cycle(self):
        """چرخه تعمیر و نگهداری"""
        try:
            for aircraft_id, aircraft in self.aircraft_fleet.items():
                # احتمال اتمام تعمیرات
                if aircraft['maintenance'] > 0 and random.random() < 0.3:
                    aircraft['maintenance'] -= 1
                    aircraft['available'] += 1
                
                # احتمال نیاز به تعمیر
                if aircraft['available'] > 0 and random.random() < 0.1:
                    aircraft['available'] -= 1
                    aircraft['maintenance'] += 1
                    
        except Exception as e:
            logger.error(f"خطا در چرخه تعمیرات: {e}")

    @tasks.loop(hours=2)
    async def patrol_missions(self):
        """بررسی و تکمیل ماموریت‌ها"""
        try:
            completed_missions = []
            current_time = datetime.now()
            
            for mission in self.active_operations:
                elapsed = current_time - mission['start_time']
                if elapsed.total_seconds() >= mission['duration'] * 60:
                    completed_missions.append(mission)
            
            for mission in completed_missions:
                # بازگرداندن هواپیما
                aircraft = self.aircraft_fleet[mission['aircraft']]
                aircraft['available'] += 1
                
                # به‌روزرسانی آمار
                if mission['type'] != 'تمرین':
                    if 'حمله' in mission['type']:
                        self.operational_stats['combat_missions'] += 1
                        self.operational_stats['ground_targets_destroyed'] += random.randint(1, 3)
                    elif 'شناسایی' in mission['type']:
                        self.operational_stats['recon_missions'] += 1
                    else:
                        self.operational_stats['training_flights'] += 1
                
                self.active_operations.remove(mission)
                
                # اطلاع‌رسانی تکمیل
                guild = self.get_guild(GUILD_ID)
                if guild:
                    ops_channel = discord.utils.get(guild.channels, name='عملیات-هوایی')
                    if ops_channel:
                        embed = create_embed(
                            "✅ ماموریت تکمیل شد",
                            f"**شماره:** `{mission['id']}`\n"
                            f"**نوع:** {mission['type']}\n"
                            f"**هواپیما:** {mission['aircraft_name']}\n"
                            f"**خلبان:** {mission['pilot']}\n"
                            f"**نتیجه:** موفقیت‌آمیز",
                            EMBED_COLORS['success']
                        )
                        await ops_channel.send(embed=embed)
                        
        except Exception as e:
            logger.error(f"خطا در بررسی ماموریت‌ها: {e}")

# ======================= ربات نیروی زمینی اسرائیل =======================

class IsraeliGroundForcesBot(commands.Bot):
    """
    ربات نیروی زمینی اسرائیل (IDF Ground Forces)
    مسئول مدیریت نیروهای زمینی، تانک‌ها، توپخانه و پیاده‌نظام
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!زمینی_',
            intents=intents,
            help_command=None,
            description="نیروی زمینی اسرائیل - محافظان خاک"
        )
        
        self.db = DatabaseManager()
        
        # واحدهای زمینی
        self.ground_units = {
            'Merkava_MK4': {
                'name': 'تانک مرکاوا MK4',
                'type': 'تانک اصلی',
                'count': 360,
                'available': 340,
                'maintenance': 20,
                'crew': 4,
                'capabilities': ['ضدتانک', 'پشتیبانی پیاده‌نظام', 'حفاظت شهری']
            },
            'Namer_APC': {
                'name': 'ناقل پرسنل نامر',
                'type': 'ناقل نیرو',
                'count': 200,
                'available': 180,
                'maintenance': 20,
                'crew': 3,
                'capabilities': ['حمل نیرو', 'حمایت آتش', 'عملیات شهری']
            },
            'M109_Howitzer': {
                'name': 'خودکشی M109',
                'type': 'توپخانه',
                'count': 600,
                'available': 580,
                'maintenance': 20,
                'crew': 6,
                'capabilities': ['پشتیبانی آتش', 'حمله غیرمستقیم', 'برد بلند']
            },
            'Spike_ATGM': {
                'name': 'موشک ضدتانک اسپایک',
                'type': 'موشک هدایت‌شونده',
                'count': 5000,
                'available': 4800,
                'maintenance': 200,
                'crew': 2,
                'capabilities': ['ضدتانک', 'دقت بالا', 'آتش و فراموش']
            },
            'Golani_Infantry': {
                'name': 'تیپ پیاده‌نظام گولانی',
                'type': 'پیاده‌نظام',
                'count': 3000,
                'available': 2800,
                'maintenance': 200,
                'crew': 1,
                'capabilities': ['عملیات پیاده', 'نبرد شهری', 'عملیات ویژه']
            },
            'Paratroopers': {
                'name': 'چترباز',
                'type': 'نیروی ویژه',
                'count': 1500,
                'available': 1400,
                'maintenance': 100,
                'crew': 1,
                'capabilities': ['چتربازی', 'عملیات ویژه', 'نفوذ عمقی']
            }
        }
        
        # مناطق عملیاتی
        self.operational_zones = {
            'Gaza_Border': {
                'name': 'مرز غزه',
                'threat_level': 'بالا',
                'deployed_units': ['Merkava_MK4', 'Golani_Infantry'],
                'status': 'آمادگی کامل'
            },
            'Lebanon_Border': {
                'name': 'مرز لبنان',
                'threat_level': 'متوسط',
                'deployed_units': ['Namer_APC', 'Paratroopers'],
                'status': 'گشت‌زنی'
            },
            'West_Bank': {
                'name': 'کرانه باختری',
                'threat_level': 'متوسط',
                'deployed_units': ['Golani_Infantry', 'Namer_APC'],
                'status': 'عملیات امنیتی'
            },
            'Golan_Heights': {
                'name': 'بلندی‌های جولان',
                'threat_level': 'پایین',
                'deployed_units': ['M109_Howitzer', 'Merkava_MK4'],
                'status': 'نظارت'
            }
        }
        
        # عملیات فعال
        self.active_ground_ops = []
        
        # آمار عملیاتی
        self.ground_stats = {
            'operations_conducted': 0,
            'targets_eliminated': 0,
            'areas_secured': 0,
            'casualties': 0,
            'equipment_lost': 0
        }
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - نیروی زمینی اسرائیل آماده است!')
        
        if not self.border_patrol.is_running():
            self.border_patrol.start()
        if not self.equipment_maintenance.is_running():
            self.equipment_maintenance.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="مرزهای اسرائیل 🛡️"
            )
        )

    @commands.command(name='واحدها')
    async def units_status(self, ctx):
        """نمایش وضعیت واحدهای زمینی"""
        embed = create_embed(
            "🛡️ واحدهای نیروی زمینی اسرائیل",
            "وضعیت فعلی واحدهای زمینی:",
            EMBED_COLORS['primary']
        )
        
        for unit_id, unit in self.ground_units.items():
            availability = (unit['available'] / unit['count']) * 100
            status_emoji = "🟢" if availability >= 85 else "🟡" if availability >= 70 else "🔴"
            
            embed.add_field(
                name=f"{status_emoji} {unit['name']}",
                value=f"**نوع:** {unit['type']}\n"
                      f"**تعداد:** {unit['count']}\n"
                      f"**آماده:** {unit['available']}\n"
                      f"**تعمیرات:** {unit['maintenance']}\n"
                      f"**خدمه:** {unit['crew']} نفر\n"
                      f"**آمادگی:** {availability:.1f}%",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='مناطق')
    async def operational_zones_cmd(self, ctx):
        """نمایش مناطق عملیاتی"""
        embed = create_embed(
            "🗺️ مناطق عملیاتی",
            "وضعیت مناطق تحت نظارت:",
            EMBED_COLORS['primary']
        )
        
        threat_colors = {
            'بالا': '🔴',
            'متوسط': '🟡',
            'پایین': '🟢'
        }
        
        for zone_id, zone in self.operational_zones.items():
            threat_emoji = threat_colors.get(zone['threat_level'], '⚪')
            
            deployed_units_names = []
            for unit_type in zone['deployed_units']:
                if unit_type in self.ground_units:
                    deployed_units_names.append(self.ground_units[unit_type]['name'])
            
            embed.add_field(
                name=f"{threat_emoji} {zone['name']}",
                value=f"**سطح تهدید:** {zone['threat_level']}\n"
                      f"**وضعیت:** {zone['status']}\n"
                      f"**واحدهای مستقر:**\n" +
                      "\n".join([f"• {unit}" for unit in deployed_units_names]),
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='عملیات')
    @has_role(['فرمانده', 'افسر', 'مدیر'])
    async def launch_ground_operation(self, ctx, operation_type: str, zone: str, unit_type: str):
        """راه‌اندازی عملیات زمینی"""
        valid_operations = ['گشت‌زنی', 'تأمین_امنیت', 'حمله', 'دفاع', 'تمرین']
        
        if operation_type not in valid_operations:
            embed = create_embed(
                "خطا ❌",
                f"نوع عملیات نامعتبر!\nانواع موجود: {', '.join(valid_operations)}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if zone not in self.operational_zones:
            embed = create_embed(
                "خطا ❌",
                f"منطقه نامعتبر!\nمناطق موجود: {', '.join(self.operational_zones.keys())}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if unit_type not in self.ground_units:
            embed = create_embed(
                "خطا ❌",
                f"واحد نامعتبر!\nواحدهای موجود:\n" +
                "\n".join([f"• {k}: {v['name']}" for k, v in self.ground_units.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        unit = self.ground_units[unit_type]
        zone_info = self.operational_zones[zone]
        
        # بررسی در دسترس بودن
        required_units = max(1, unit['count'] // 20)  # حداقل 5% از واحد
        if unit['available'] < required_units:
            embed = create_embed(
                "واحد ناکافی ❌",
                f"واحد {unit['name']} به تعداد کافی در دسترس نیست!\n"
                f"مورد نیاز: {required_units}\n"
                f"موجود: {unit['available']}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # ایجاد عملیات
        operation_id = f"GF{random.randint(1000, 9999)}"
        duration = random.randint(60, 300)  # 1 تا 5 ساعت
        
        operation = {
            'id': operation_id,
            'type': operation_type,
            'zone': zone,
            'zone_name': zone_info['name'],
            'unit_type': unit_type,
            'unit_name': unit['name'],
            'unit_count': required_units,
            'commander': ctx.author.display_name,
            'start_time': datetime.now(),
            'duration': duration,
            'status': 'در حال انجام'
        }
        
        self.active_ground_ops.append(operation)
        unit['available'] -= required_units
        
        # تولید توضیحات عملیات
        operation_prompt = f"""
        یک عملیات {operation_type} در منطقه {zone_info['name']} با واحد {unit['name']} آغاز شده است.
        فرمانده: {ctx.author.display_name}
        سطح تهدید منطقه: {zone_info['threat_level']}
        
        توضیح کوتاهی از این عملیات بنویس (50-80 کلمه).
        """
        
        try:
            operation_description = await generate_text_with_gemini(operation_prompt)
        except:
            operation_description = f"عملیات {operation_type} در {zone_info['name']} آغاز شد."
        
        embed = create_embed(
            f"🚁 عملیات {operation_type} آغاز شد",
            f"**شماره عملیات:** `{operation_id}`\n"
            f"**منطقه:** {zone_info['name']}\n"
            f"**واحد:** {unit['name']}\n"
            f"**تعداد:** {required_units} واحد\n"
            f"**فرمانده:** {ctx.author.mention}\n"
            f"**مدت تخمینی:** {duration} دقیقه\n"
            f"**سطح تهدید:** {zone_info['threat_level']}\n\n"
            f"**جزئیات:**\n{operation_description}",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"شروع: {datetime.now().strftime('%H:%M')}")
        await ctx.send(embed=embed)

    @commands.command(name='عملیات_فعال')
    async def active_ground_operations(self, ctx):
        """نمایش عملیات زمینی فعال"""
        if not self.active_ground_ops:
            embed = create_embed(
                "عملیات فعال",
                "در حال حاضر هیچ عملیات زمینی در جریان نیست.",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            "🚁 عملیات زمینی فعال",
            f"تعداد عملیات در حال انجام: {len(self.active_ground_ops)}",
            EMBED_COLORS['primary']
        )
        
        for operation in self.active_ground_ops[:5]:
            elapsed = datetime.now() - operation['start_time']
            remaining = operation['duration'] - int(elapsed.total_seconds() / 60)
            
            if remaining > 0:
                status = f"⏳ {remaining} دقیقه باقیمانده"
            else:
                status = "✅ آماده بازگشت"
            
            embed.add_field(
                name=f"عملیات {operation['id']}",
                value=f"**نوع:** {operation['type']}\n"
                      f"**منطقه:** {operation['zone_name']}\n"
                      f"**واحد:** {operation['unit_name']}\n"
                      f"**فرمانده:** {operation['commander']}\n"
                      f"**وضعیت:** {status}",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @tasks.loop(hours=8)
    async def border_patrol(self):
        """گشت‌زنی خودکار مرزها"""
        try:
            # انتخاب منطقه برای گشت‌زنی
            high_threat_zones = [zone_id for zone_id, zone in self.operational_zones.items() 
                               if zone['threat_level'] == 'بالا']
            
            if high_threat_zones:
                selected_zone = random.choice(high_threat_zones)
                zone_info = self.operational_zones[selected_zone]
                
                # انتخاب واحد مناسب
                suitable_units = []
                for unit_id, unit in self.ground_units.items():
                    if unit['available'] > 10 and unit_id in zone_info['deployed_units']:
                        suitable_units.append(unit_id)
                
                if suitable_units:
                    selected_unit = random.choice(suitable_units)
                    unit = self.ground_units[selected_unit]
                    
                    # ایجاد گشت خودکار
                    patrol_id = f"AUTO{random.randint(1000, 9999)}"
                    operation = {
                        'id': patrol_id,
                        'type': 'گشت خودکار',
                        'zone': selected_zone,
                        'zone_name': zone_info['name'],
                        'unit_type': selected_unit,
                        'unit_name': unit['name'],
                        'unit_count': 5,
                        'commander': 'خودکار',
                        'start_time': datetime.now(),
                        'duration': 240,  # 4 ساعت
                        'status': 'خودکار'
                    }
                    
                    self.active_ground_ops.append(operation)
                    unit['available'] -= 5
                    self.ground_stats['operations_conducted'] += 1
                    
                    # اطلاع‌رسانی
                    guild = self.get_guild(GUILD_ID)
                    if guild:
                        ops_channel = discord.utils.get(guild.channels, name='عملیات-زمینی')
                        if ops_channel:
                            embed = create_embed(
                                "🔄 گشت خودکار",
                                f"**منطقه:** {zone_info['name']}\n"
                                f"**واحد:** {unit['name']}\n"
                                f"**شماره عملیات:** `{patrol_id}`",
                                EMBED_COLORS['primary']
                            )
                            await ops_channel.send(embed=embed)
                            
        except Exception as e:
            logger.error(f"خطا در گشت‌زنی خودکار: {e}")

    @tasks.loop(hours=6)
    async def equipment_maintenance(self):
        """تعمیر و نگهداری تجهیزات"""
        try:
            for unit_id, unit in self.ground_units.items():
                # تکمیل تعمیرات
                if unit['maintenance'] > 0 and random.random() < 0.4:
                    repaired = min(unit['maintenance'], random.randint(1, 5))
                    unit['maintenance'] -= repaired
                    unit['available'] += repaired
                
                # نیاز به تعمیر جدید
                if unit['available'] > 0 and random.random() < 0.05:
                    need_repair = min(unit['available'], random.randint(1, 3))
                    unit['available'] -= need_repair
                    unit['maintenance'] += need_repair
                    
        except Exception as e:
            logger.error(f"خطا در تعمیرات: {e}")

# ======================= ربات نیروی دریایی اسرائیل =======================

class IsraeliNavyBot(commands.Bot):
    """
    ربات نیروی دریایی اسرائیل (Israeli Navy)
    مسئول مدیریت ناوگان دریایی، زیردریایی‌ها و حفاظت سواحل
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!دریایی_',
            intents=intents,
            help_command=None,
            description="نیروی دریایی اسرائیل - نگهبان دریاها"
        )
        
        self.db = DatabaseManager()
        
        # ناوگان دریایی
        self.naval_fleet = {
            'INS_Dolphin': {
                'name': 'زیردریایی دلفین',
                'type': 'زیردریایی',
                'class': 'دلفین',
                'count': 6,
                'available': 5,
                'maintenance': 1,
                'crew': 35,
                'capabilities': ['جاسوسی', 'حمله زیردریایی', 'عملیات مخفی']
            },
            'INS_Saar_6': {
                'name': 'کورت ساعر 6',
                'type': 'کورت',
                'class': 'ساعر 6',
                'count': 4,
                'available': 4,
                'maintenance': 0,
                'crew': 25,
                'capabilities': ['دفاع ساحلی', 'ضدکشتی', 'حمایت آتش']
            },
            'INS_Saar_5': {
                'name': 'کورت ساعر 5',
                'type': 'کورت',
                'class': 'ساعر 5',
                'count': 8,
                'available': 7,
                'maintenance': 1,
                'crew': 74,
                'capabilities': ['گشت‌زنی', 'ضدکشتی', 'دفاع هوایی']
            },
            'Dvora_Patrol': {
                'name': 'قایق گشتی دبورا',
                'type': 'قایق گشتی',
                'class': 'دبورا',
                'count': 30,
                'available': 28,
                'maintenance': 2,
                'crew': 9,
                'capabilities': ['گشت ساحلی', 'مقابله با قاچاق', 'امداد']
            },
            'Shayetet_13': {
                'name': 'یگان شایطت 13',
                'type': 'نیروی ویژه دریایی',
                'class': 'کماندو',
                'count': 200,
                'available': 180,
                'maintenance': 20,
                'crew': 1,
                'capabilities': ['عملیات ویژه', 'شنا تاکتیکی', 'تخریب زیردریایی']
            }
        }
        
        # مناطق دریایی
        self.naval_zones = {
            'Mediterranean': {
                'name': 'دریای مدیترانه',
                'threat_level': 'متوسط',
                'patrol_ships': ['INS_Saar_6', 'INS_Saar_5'],
                'status': 'گشت‌زنی فعال'
            },
            'Red_Sea': {
                'name': 'دریای سرخ',
                'threat_level': 'بالا',
                'patrol_ships': ['INS_Dolphin', 'INS_Saar_5'],
                'status': 'آمادگی کامل'
            },
            'Gaza_Coast': {
                'name': 'سواحل غزه',
                'threat_level': 'بالا',
                'patrol_ships': ['Dvora_Patrol', 'INS_Saar_6'],
                'status': 'محاصره دریایی'
            },
            'Haifa_Port': {
                'name': 'بندر حیفا',
                'threat_level': 'پایین',
                'patrol_ships': ['Dvora_Patrol'],
                'status': 'حفاظت بندری'
            }
        }
        
        # عملیات دریایی فعال
        self.active_naval_ops = []
        
        # آمار دریایی
        self.naval_stats = {
            'patrols_completed': 0,
            'smuggling_attempts_stopped': 0,
            'rescue_operations': 0,
            'special_operations': 0,
            'ships_intercepted': 0
        }
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - نیروی دریایی اسرائیل آماده است!')
        
        if not self.coastal_patrol.is_running():
            self.coastal_patrol.start()
        if not self.naval_maintenance.is_running():
            self.naval_maintenance.start()
        if not self.submarine_operations.is_running():
            self.submarine_operations.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="سواحل اسرائیل ⚓"
            )
        )

    @commands.command(name='ناوگان')
    async def fleet_status(self, ctx):
        """نمایش وضعیت ناوگان دریایی"""
        embed = create_embed(
            "⚓ ناوگان نیروی دریایی اسرائیل",
            "وضعیت فعلی شناورها:",
            EMBED_COLORS['primary']
        )
        
        for ship_id, ship in self.naval_fleet.items():
            availability = (ship['available'] / ship['count']) * 100
            status_emoji = "🟢" if availability >= 80 else "🟡" if availability >= 60 else "🔴"
            
            embed.add_field(
                name=f"{status_emoji} {ship['name']}",
                value=f"**کلاس:** {ship['class']}\n"
                      f"**تعداد:** {ship['count']}\n"
                      f"**آماده:** {ship['available']}\n"
                      f"**تعمیرات:** {ship['maintenance']}\n"
                      f"**خدمه:** {ship['crew']} نفر\n"
                      f"**آمادگی:** {availability:.1f}%",
                inline=True
            )
        
        total_ships = sum([ship['count'] for ship in self.naval_fleet.values()])
        total_available = sum([ship['available'] for ship in self.naval_fleet.values()])
        
        embed.add_field(
            name="📊 خلاصه ناوگان",
            value=f"**مجموع شناورها:** {total_ships}\n"
                  f"**آماده عملیات:** {total_available}\n"
                  f"**آمادگی کلی:** {(total_available/total_ships)*100:.1f}%",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='مناطق_دریایی')
    async def naval_zones_cmd(self, ctx):
        """نمایش مناطق دریایی تحت کنترل"""
        embed = create_embed(
            "🌊 مناطق دریایی",
            "وضعیت مناطق دریایی تحت نظارت:",
            EMBED_COLORS['primary']
        )
        
        threat_colors = {
            'بالا': '🔴',
            'متوسط': '🟡',
            'پایین': '🟢'
        }
        
        for zone_id, zone in self.naval_zones.items():
            threat_emoji = threat_colors.get(zone['threat_level'], '⚪')
            
            patrol_ships_names = []
            for ship_type in zone['patrol_ships']:
                if ship_type in self.naval_fleet:
                    patrol_ships_names.append(self.naval_fleet[ship_type]['name'])
            
            embed.add_field(
                name=f"{threat_emoji} {zone['name']}",
                value=f"**سطح تهدید:** {zone['threat_level']}\n"
                      f"**وضعیت:** {zone['status']}\n"
                      f"**شناورهای گشت:**\n" +
                      "\n".join([f"• {ship}" for ship in patrol_ships_names]),
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='ماموریت_دریایی')
    @has_role(['فرمانده', 'ناخدا', 'مدیر'])
    async def launch_naval_mission(self, ctx, mission_type: str, zone: str, ship_type: str):
        """راه‌اندازی ماموریت دریایی"""
        valid_missions = ['گشت‌زنی', 'محاصره', 'جاسوسی', 'امداد', 'تمرین', 'عملیات_ویژه']
        
        if mission_type not in valid_missions:
            embed = create_embed(
                "خطا ❌",
                f"نوع ماموریت نامعتبر!\nانواع موجود: {', '.join(valid_missions)}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if zone not in self.naval_zones:
            embed = create_embed(
                "خطا ❌",
                f"منطقه دریایی نامعتبر!\nمناطق موجود: {', '.join(self.naval_zones.keys())}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if ship_type not in self.naval_fleet:
            embed = create_embed(
                "خطا ❌",
                f"شناور نامعتبر!\nشناورهای موجود:\n" +
                "\n".join([f"• {k}: {v['name']}" for k, v in self.naval_fleet.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        ship = self.naval_fleet[ship_type]
        zone_info = self.naval_zones[zone]
        
        # بررسی در دسترس بودن
        if ship['available'] < 1:
            embed = create_embed(
                "شناور در دسترس نیست ❌",
                f"{ship['name']} در حال حاضر در دسترس نیست!\n"
                f"تعداد موجود: {ship['available']}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی مناسب بودن شناور برای منطقه
        if ship_type not in zone_info['patrol_ships'] and mission_type != 'تمرین':
            embed = create_embed(
                "شناور نامناسب ⚠️",
                f"{ship['name']} معمولاً در {zone_info['name']} مستقر نیست.\n"
                "آیا مطمئن هستید؟ (ادامه می‌دهیم...)",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
        
        # ایجاد ماموریت
        mission_id = f"NV{random.randint(1000, 9999)}"
        duration = random.randint(120, 480)  # 2 تا 8 ساعت
        
        mission = {
            'id': mission_id,
            'type': mission_type,
            'zone': zone,
            'zone_name': zone_info['name'],
            'ship_type': ship_type,
            'ship_name': ship['name'],
            'captain': ctx.author.display_name,
            'start_time': datetime.now(),
            'duration': duration,
            'status': 'در حال انجام'
        }
        
        self.active_naval_ops.append(mission)
        ship['available'] -= 1
        
        # تولید توضیحات ماموریت
        mission_prompt = f"""
        یک ماموریت {mission_type} دریایی در {zone_info['name']} با {ship['name']} آغاز شده است.
        ناخدا: {ctx.author.display_name}
        سطح تهدید: {zone_info['threat_level']}
        
        توضیح کوتاهی از این ماموریت دریایی بنویس (50-80 کلمه).
        """
        
        try:
            mission_description = await generate_text_with_gemini(mission_prompt)
        except:
            mission_description = f"ماموریت {mission_type} در {zone_info['name']} آغاز شد."
        
        embed = create_embed(
            f"⚓ ماموریت {mission_type} آغاز شد",
            f"**شماره ماموریت:** `{mission_id}`\n"
            f"**منطقه:** {zone_info['name']}\n"
            f"**شناور:** {ship['name']}\n"
            f"**ناخدا:** {ctx.author.mention}\n"
            f"**مدت تخمینی:** {duration} دقیقه\n"
            f"**سطح تهدید:** {zone_info['threat_level']}\n\n"
            f"**جزئیات:**\n{mission_description}",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"شروع: {datetime.now().strftime('%H:%M')}")
        await ctx.send(embed=embed)

    @commands.command(name='عملیات_دریایی_فعال')
    async def active_naval_operations(self, ctx):
        """نمایش عملیات دریایی فعال"""
        if not self.active_naval_ops:
            embed = create_embed(
                "عملیات فعال",
                "در حال حاضر هیچ عملیات دریایی در جریان نیست.",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            "⚓ عملیات دریایی فعال",
            f"تعداد عملیات در حال انجام: {len(self.active_naval_ops)}",
            EMBED_COLORS['primary']
        )
        
        for mission in self.active_naval_ops[:5]:
            elapsed = datetime.now() - mission['start_time']
            remaining = mission['duration'] - int(elapsed.total_seconds() / 60)
            
            if remaining > 0:
                status = f"⏳ {remaining} دقیقه باقیمانده"
            else:
                status = "✅ آماده بازگشت به بندر"
            
            embed.add_field(
                name=f"ماموریت {mission['id']}",
                value=f"**نوع:** {mission['type']}\n"
                      f"**منطقه:** {mission['zone_name']}\n"
                      f"**شناور:** {mission['ship_name']}\n"
                      f"**ناخدا:** {mission['captain']}\n"
                      f"**وضعیت:** {status}",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @tasks.loop(hours=6)
    async def coastal_patrol(self):
        """گشت‌زنی خودکار سواحل"""
        try:
            # انتخاب منطقه پرخطر
            high_threat_zones = [zone_id for zone_id, zone in self.naval_zones.items() 
                               if zone['threat_level'] == 'بالا']
            
            if high_threat_zones:
                selected_zone = random.choice(high_threat_zones)
                zone_info = self.naval_zones[selected_zone]
                
                # انتخاب شناور مناسب
                suitable_ships = []
                for ship_type in zone_info['patrol_ships']:
                    if ship_type in self.naval_fleet and self.naval_fleet[ship_type]['available'] > 0:
                        suitable_ships.append(ship_type)
                
                if suitable_ships:
                    selected_ship = random.choice(suitable_ships)
                    ship = self.naval_fleet[selected_ship]
                    
                    # ایجاد گشت خودکار
                    patrol_id = f"AUTO{random.randint(1000, 9999)}"
                    mission = {
                        'id': patrol_id,
                        'type': 'گشت خودکار',
                        'zone': selected_zone,
                        'zone_name': zone_info['name'],
                        'ship_type': selected_ship,
                        'ship_name': ship['name'],
                        'captain': 'خودکار',
                        'start_time': datetime.now(),
                        'duration': 360,  # 6 ساعت
                        'status': 'خودکار'
                    }
                    
                    self.active_naval_ops.append(mission)
                    ship['available'] -= 1
                    self.naval_stats['patrols_completed'] += 1
                    
                    # شانس توقف قاچاق
                    if random.random() < 0.3:
                        self.naval_stats['smuggling_attempts_stopped'] += 1
                    
                    # اطلاع‌رسانی
                    guild = self.get_guild(GUILD_ID)
                    if guild:
                        ops_channel = discord.utils.get(guild.channels, name='عملیات-دریایی')
                        if ops_channel:
                            embed = create_embed(
                                "🔄 گشت ساحلی خودکار",
                                f"**منطقه:** {zone_info['name']}\n"
                                f"**شناور:** {ship['name']}\n"
                                f"**شماره ماموریت:** `{patrol_id}`",
                                EMBED_COLORS['primary']
                            )
                            await ops_channel.send(embed=embed)
                            
        except Exception as e:
            logger.error(f"خطا در گشت ساحلی: {e}")

    @tasks.loop(hours=8)
    async def naval_maintenance(self):
        """تعمیر و نگهداری ناوگان"""
        try:
            for ship_id, ship in self.naval_fleet.items():
                # تکمیل تعمیرات
                if ship['maintenance'] > 0 and random.random() < 0.3:
                    ship['maintenance'] -= 1
                    ship['available'] += 1
                
                # نیاز به تعمیر
                if ship['available'] > 0 and random.random() < 0.08:
                    ship['available'] -= 1
                    ship['maintenance'] += 1
                    
        except Exception as e:
            logger.error(f"خطا در تعمیرات ناوگان: {e}")

    @tasks.loop(hours=12)
    async def submarine_operations(self):
        """عملیات زیردریایی محرمانه"""
        try:
            # عملیات زیردریایی‌ها
            dolphins = self.naval_fleet['INS_Dolphin']
            if dolphins['available'] > 0 and random.random() < 0.4:
                # ماموریت جاسوسی محرمانه
                dolphins['available'] -= 1
                self.naval_stats['special_operations'] += 1
                
                # بازگشت بعد از 8 ساعت
                await asyncio.sleep(8 * 3600)  # در واقعیت این کار نمی‌کند، فقط برای نمونه
                dolphins['available'] += 1
                
        except Exception as e:
            logger.error(f"خطا در عملیات زیردریایی: {e}")

# ======================= اجرای ربات‌های نیروهای نظامی =======================

async def run_air_force():
    """اجرای ربات نیروی هوایی"""
    bot = IsraeliAirForceBot()
    await bot.start(DISCORD_BOT_TOKEN_AIR_FORCE)

async def run_ground_forces():
    """اجرای ربات نیروی زمینی"""
    bot = IsraeliGroundForcesBot()
    await bot.start(DISCORD_BOT_TOKEN_GROUND_FORCES)

async def run_navy():
    """اجرای ربات نیروی دریایی"""
    bot = IsraeliNavyBot()
    await bot.start(DISCORD_BOT_TOKEN_NAVY)

if __name__ == "__main__":
    """
    راهنمای اجرا:
    
    1. نصب وابستگی‌ها:
       pip install -r requirements.txt
    
    2. تنظیم متغیرهای محیطی در فایل .env:
       DISCORD_BOT_TOKEN_AIR_FORCE=توکن_ربات_نیروی_هوایی
       DISCORD_BOT_TOKEN_GROUND_FORCES=توکن_ربات_نیروی_زمینی
       DISCORD_BOT_TOKEN_NAVY=توکن_ربات_نیروی_دریایی
       GEMINI_API_KEY=کلید_API_جمنای
    
    3. اجرای ربات‌ها:
       python military_forces_bots.py
    
    دستورات اصلی:
    
    نیروی هوایی:
    - !هوایی_ناوگان : وضعیت ناوگان هوایی
    - !هوایی_پایگاه‌ها : وضعیت پایگاه‌های هوایی
    - !هوایی_ماموریت نوع هواپیما هدف : راه‌اندازی ماموریت
    - !هوایی_عملیات_فعال : عملیات در حال انجام
    - !هوایی_آمار_عملیاتی : آمار کلی
    
    نیروی زمینی:
    - !زمینی_واحدها : وضعیت واحدهای زمینی
    - !زمینی_مناطق : مناطق عملیاتی
    - !زمینی_عملیات نوع منطقه واحد : راه‌اندازی عملیات
    - !زمینی_عملیات_فعال : عملیات در حال انجام
    
    نیروی دریایی:
    - !دریایی_ناوگان : وضعیت ناوگان دریایی
    - !دریایی_مناطق_دریایی : مناطق دریایی
    - !دریایی_ماموریت_دریایی نوع منطقه شناور : راه‌اندازی ماموریت
    - !دریایی_عملیات_دریایی_فعال : عملیات در حال انجام
    """
    
    import asyncio
    
    async def main():
        # اجرای همزمان تمام نیروهای نظامی
        await asyncio.gather(
            run_air_force(),
            run_ground_forces(),
            run_navy()
        )
    
    asyncio.run(main())