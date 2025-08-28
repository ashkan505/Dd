#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سیستم مدیریت بحران اسرائیل
Crisis Management System for Israeli RP Server

این فایل شامل پیاده‌سازی سیستم مدیریت بحران است:
- بحران‌های تصادفی (بلایای طبیعی، رسوایی‌ها، اعتصابات)
- سیستم رضایت عمومی
- مدیریت اضطراری
- سیستم پیشرفت فردی و دستاوردها
- اقتصاد سیاه و فعالیت‌های غیرقانونی
- تکامل علمی و فرهنگی بلندمدت

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

# ======================= ربات مدیریت بحران =======================

class CrisisManagementBot(commands.Bot):
    """
    ربات مدیریت بحران
    مسئول مدیریت بحران‌های ملی، رضایت عمومی و شرایط اضطراری
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!بحران_',
            intents=intents,
            help_command=None,
            description="سیستم مدیریت بحران اسرائیل"
        )
        
        self.db = DatabaseManager()
        
        # سطح رضایت عمومی (0-100)
        self.public_approval = 75
        
        # بحران فعلی
        self.active_crisis = None
        
        # انواع بحران‌ها
        self.crisis_types = {
            'natural_disaster': {
                'name': 'بلای طبیعی',
                'severity_levels': {
                    'low': {'name': 'زلزله خفیف', 'approval_impact': -5, 'economic_impact': -100000},
                    'medium': {'name': 'سیل شدید', 'approval_impact': -15, 'economic_impact': -500000},
                    'high': {'name': 'زلزله مخرب', 'approval_impact': -25, 'economic_impact': -2000000}
                }
            },
            'political_scandal': {
                'name': 'رسوایی سیاسی',
                'severity_levels': {
                    'low': {'name': 'اتهام فساد مالی', 'approval_impact': -10, 'economic_impact': -50000},
                    'medium': {'name': 'رسوایی اطلاعاتی', 'approval_impact': -20, 'economic_impact': -200000},
                    'high': {'name': 'فساد گسترده', 'approval_impact': -35, 'economic_impact': -1000000}
                }
            },
            'economic_crisis': {
                'name': 'بحران اقتصادی',
                'severity_levels': {
                    'low': {'name': 'رکود خفیف', 'approval_impact': -8, 'economic_impact': -300000},
                    'medium': {'name': 'بحران مالی', 'approval_impact': -18, 'economic_impact': -800000},
                    'high': {'name': 'فروپاشی اقتصادی', 'approval_impact': -30, 'economic_impact': -3000000}
                }
            },
            'social_unrest': {
                'name': 'ناآرامی اجتماعی',
                'severity_levels': {
                    'low': {'name': 'اعتراض محدود', 'approval_impact': -5, 'economic_impact': -100000},
                    'medium': {'name': 'اعتصاب عمومی', 'approval_impact': -15, 'economic_impact': -600000},
                    'high': {'name': 'شورش گسترده', 'approval_impact': -25, 'economic_impact': -1500000}
                }
            },
            'security_threat': {
                'name': 'تهدید امنیتی',
                'severity_levels': {
                    'low': {'name': 'تهدید سایبری', 'approval_impact': -3, 'economic_impact': -150000},
                    'medium': {'name': 'حمله تروریستی', 'approval_impact': -12, 'economic_impact': -400000},
                    'high': {'name': 'تهدید نظامی', 'approval_impact': -20, 'economic_impact': -1000000}
                }
            }
        }
        
        # راه‌حل‌های بحران
        self.crisis_solutions = {
            'emergency_budget': {'name': 'تخصیص بودجه اضطراری', 'cost': 500000, 'approval_boost': 10},
            'public_statement': {'name': 'بیانیه عمومی', 'cost': 10000, 'approval_boost': 5},
            'aid_distribution': {'name': 'توزیع کمک‌های اضطراری', 'cost': 300000, 'approval_boost': 15},
            'investigation': {'name': 'تحقیق و بررسی', 'cost': 100000, 'approval_boost': 8},
            'military_response': {'name': 'پاسخ نظامی', 'cost': 800000, 'approval_boost': 12}
        }
        
        # آمار بحران‌ها
        self.crisis_history = []
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - سیستم مدیریت بحران آماده است!')
        
        if not self.random_crisis.is_running():
            self.random_crisis.start()
        if not self.approval_monitoring.is_running():
            self.approval_monitoring.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="امنیت ملی 🚨"
            )
        )

    @commands.command(name='وضعیت_ملی')
    async def national_status(self, ctx):
        """نمایش وضعیت کلی کشور"""
        # محاسبه آمارهای مختلف
        crisis_count = len(self.crisis_history)
        recent_crises = len([c for c in self.crisis_history if 
                           (datetime.now() - datetime.fromisoformat(c['date'])).days <= 30])
        
        # تعیین وضعیت کلی
        if self.public_approval >= 80:
            status = "🟢 عالی"
            status_color = EMBED_COLORS['success']
        elif self.public_approval >= 60:
            status = "🟡 مطلوب"
            status_color = EMBED_COLORS['warning']
        elif self.public_approval >= 40:
            status = "🟠 نگران‌کننده"
            status_color = EMBED_COLORS['error']
        else:
            status = "🔴 بحرانی"
            status_color = EMBED_COLORS['error']
        
        embed = create_embed(
            "📊 وضعیت ملی اسرائیل",
            f"**وضعیت کلی:** {status}",
            status_color
        )
        
        embed.add_field(
            name="رضایت عمومی",
            value=f"{self.public_approval}/100\n{'█' * int(self.public_approval/10)}{'░' * (10-int(self.public_approval/10))}",
            inline=False
        )
        
        embed.add_field(
            name="آمار بحران‌ها",
            value=f"**کل بحران‌ها:** {crisis_count}\n"
                  f"**بحران‌های اخیر:** {recent_crises} (ماه گذشته)",
            inline=True
        )
        
        if self.active_crisis:
            embed.add_field(
                name="🚨 بحران فعال",
                value=f"**نوع:** {self.active_crisis['name']}\n"
                      f"**شدت:** {self.active_crisis['severity']}\n"
                      f"**زمان شروع:** {self.active_crisis['start_time'][:16]}",
                inline=True
            )
        else:
            embed.add_field(
                name="✅ وضعیت امنیتی",
                value="هیچ بحران فعالی وجود ندارد",
                inline=True
            )
        
        # پیشنهادات بهبود
        suggestions = []
        if self.public_approval < 50:
            suggestions.append("• اجرای برنامه‌های رفاهی")
            suggestions.append("• کاهش مالیات‌ها")
        if recent_crises > 2:
            suggestions.append("• تقویت سیستم‌های پیشگیری")
            suggestions.append("• افزایش بودجه اضطراری")
        
        if suggestions:
            embed.add_field(
                name="💡 پیشنهادات",
                value="\n".join(suggestions),
                inline=False
            )
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830807.png")
        await ctx.send(embed=embed)

    @commands.command(name='شبیه‌سازی_بحران')
    @has_role(['مدیر', 'نخست‌وزیر'])
    async def simulate_crisis(self, ctx, crisis_type: str, severity: str = 'medium'):
        """شبیه‌سازی بحران برای تمرین"""
        if crisis_type not in self.crisis_types:
            embed = create_embed(
                "خطا ❌",
                f"نوع بحران نامعتبر!\nانواع موجود: {', '.join(self.crisis_types.keys())}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if severity not in ['low', 'medium', 'high']:
            embed = create_embed(
                "خطا ❌",
                "سطح شدت نامعتبر! (low, medium, high)",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        await self._trigger_crisis(crisis_type, severity, simulated=True)
        
        embed = create_embed(
            "🎭 شبیه‌سازی بحران",
            f"بحران شبیه‌سازی شده با موفقیت فعال شد!\n"
            f"این یک تمرین است و تأثیر واقعی ندارد.",
            EMBED_COLORS['warning']
        )
        await ctx.send(embed=embed)

    @commands.command(name='مدیریت_بحران')
    @has_role(['وزیر', 'نخست‌وزیر', 'مدیر'])
    async def manage_crisis(self, ctx, solution: str):
        """اعمال راه‌حل برای بحران فعال"""
        if not self.active_crisis:
            embed = create_embed(
                "خطا ❌",
                "هیچ بحران فعالی وجود ندارد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if solution not in self.crisis_solutions:
            embed = create_embed(
                "خطا ❌",
                f"راه‌حل نامعتبر!\nراه‌حل‌های موجود:\n" + 
                "\n".join([f"• {k}: {v['name']}" for k, v in self.crisis_solutions.items()]),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        solution_data = self.crisis_solutions[solution]
        
        # اعمال راه‌حل
        self.public_approval += solution_data['approval_boost']
        self.public_approval = min(100, self.public_approval)  # حداکثر 100
        
        # پایان بحران
        self.active_crisis['resolution'] = solution_data['name']
        self.active_crisis['resolved_by'] = ctx.author.display_name
        self.active_crisis['end_time'] = datetime.now().isoformat()
        
        self.crisis_history.append(self.active_crisis.copy())
        self.active_crisis = None
        
        embed = create_embed(
            "✅ بحران مدیریت شد",
            f"**راه‌حل اعمال شده:** {solution_data['name']}\n"
            f"**هزینه:** {solution_data['cost']:,} شکل\n"
            f"**تأثیر بر رضایت عمومی:** +{solution_data['approval_boost']}\n"
            f"**رضایت جدید:** {self.public_approval}/100\n\n"
            f"🎉 بحران با موفقیت حل شد!",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"حل شده توسط: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name='تاریخچه_بحران')
    async def crisis_history_cmd(self, ctx):
        """نمایش تاریخچه بحران‌ها"""
        if not self.crisis_history:
            embed = create_embed(
                "تاریخچه خالی",
                "هنوز هیچ بحرانی رخ نداده است!",
                EMBED_COLORS['primary']
            )
            await ctx.send(embed=embed)
            return
        
        # نمایش 10 بحران اخیر
        recent_crises = sorted(self.crisis_history, 
                             key=lambda x: x['date'], reverse=True)[:10]
        
        embed = create_embed(
            "📚 تاریخچه بحران‌ها",
            f"نمایش {len(recent_crises)} بحران اخیر از کل {len(self.crisis_history)} بحران:",
            EMBED_COLORS['primary']
        )
        
        for crisis in recent_crises:
            resolution_text = crisis.get('resolution', 'حل نشده')
            resolved_by = crisis.get('resolved_by', 'نامشخص')
            
            embed.add_field(
                name=f"{crisis['name']} ({crisis['severity']})",
                value=f"**تاریخ:** {crisis['date'][:10]}\n"
                      f"**راه‌حل:** {resolution_text}\n"
                      f"**حل‌کننده:** {resolved_by}",
                inline=True
            )
        
        await ctx.send(embed=embed)

    async def _trigger_crisis(self, crisis_type: str, severity: str, simulated: bool = False):
        """فعال‌سازی بحران"""
        crisis_info = self.crisis_types[crisis_type]['severity_levels'][severity]
        
        # تولید توضیحات با Gemini AI
        crisis_prompt = f"""
        یک بحران {self.crisis_types[crisis_type]['name']} با شدت {severity} در اسرائیل رخ داده است.
        نوع بحران: {crisis_info['name']}
        
        لطفاً یک توضیح واقع‌گرایانه و جذاب برای این بحران بنویس که شامل:
        - علت و نحوه وقوع
        - تأثیرات احتمالی
        - نیاز به اقدام فوری
        
        متن را در حدود 100-150 کلمه بنویس.
        """
        
        try:
            crisis_description = await generate_text_with_gemini(crisis_prompt)
        except:
            crisis_description = f"یک {crisis_info['name']} در سراسر کشور رخ داده و نیاز به مدیریت فوری دارد."
        
        # ایجاد بحران
        self.active_crisis = {
            'type': crisis_type,
            'name': crisis_info['name'],
            'severity': severity,
            'description': crisis_description,
            'approval_impact': crisis_info['approval_impact'],
            'economic_impact': crisis_info['economic_impact'],
            'date': datetime.now().isoformat(),
            'start_time': datetime.now().isoformat(),
            'simulated': simulated
        }
        
        if not simulated:
            # اعمال تأثیرات
            self.public_approval += crisis_info['approval_impact']
            self.public_approval = max(0, self.public_approval)  # حداقل 0
        
        # اطلاع‌رسانی
        guild = self.get_guild(GUILD_ID)
        if guild:
            # کانال اضطراری
            emergency_channel = discord.utils.get(guild.channels, name='اضطراری')
            if not emergency_channel:
                # ایجاد کانال اضطراری
                emergency_category = await get_or_create_category(guild, "مدیریت بحران")
                emergency_channel = await guild.create_text_channel(
                    "اضطراری",
                    category=emergency_category
                )
            
            severity_colors = {
                'low': EMBED_COLORS['warning'],
                'medium': EMBED_COLORS['error'],
                'high': 0xFF0000  # قرمز شدید
            }
            
            severity_emojis = {
                'low': '🟡',
                'medium': '🟠', 
                'high': '🔴'
            }
            
            embed = create_embed(
                f"🚨 هشدار بحران {severity_emojis[severity]}",
                f"**نوع بحران:** {crisis_info['name']}\n"
                f"**سطح شدت:** {severity.upper()}\n"
                f"**تأثیر بر رضایت عمومی:** {crisis_info['approval_impact']}\n"
                f"**تأثیر اقتصادی:** {crisis_info['economic_impact']:,} شکل\n\n"
                f"**جزئیات:**\n{crisis_description}\n\n"
                f"{'🎭 **این یک شبیه‌سازی است!**' if simulated else '⚠️ **نیاز به مدیریت فوری!**'}",
                severity_colors[severity]
            )
            
            if not simulated:
                embed.add_field(
                    name="راه‌حل‌های پیشنهادی",
                    value="\n".join([f"• `!بحران_مدیریت_بحران {k}`: {v['name']}" 
                                   for k, v in self.crisis_solutions.items()]),
                    inline=False
                )
            
            embed.set_footer(text=f"زمان وقوع: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
            
            await emergency_channel.send("@everyone", embed=embed)

    @tasks.loop(hours=random.randint(48, 168))  # هر 2 تا 7 روز
    async def random_crisis(self):
        """تولید بحران تصادفی"""
        try:
            # تنها در صورت عدم وجود بحران فعال
            if self.active_crisis:
                return
            
            # احتمال وقوع بحران (کاهش با افزایش رضایت عمومی)
            crisis_probability = max(0.1, 0.5 - (self.public_approval / 200))
            
            if random.random() < crisis_probability:
                crisis_type = random.choice(list(self.crisis_types.keys()))
                
                # سطح شدت بر اساس رضایت عمومی
                if self.public_approval >= 70:
                    severity_weights = {'low': 0.6, 'medium': 0.3, 'high': 0.1}
                elif self.public_approval >= 40:
                    severity_weights = {'low': 0.3, 'medium': 0.5, 'high': 0.2}
                else:
                    severity_weights = {'low': 0.2, 'medium': 0.4, 'high': 0.4}
                
                severity = random.choices(
                    list(severity_weights.keys()),
                    weights=list(severity_weights.values())
                )[0]
                
                await self._trigger_crisis(crisis_type, severity)
                
        except Exception as e:
            logger.error(f"خطا در تولید بحران تصادفی: {e}")

    @tasks.loop(hours=12)
    async def approval_monitoring(self):
        """نظارت بر رضایت عمومی"""
        try:
            guild = self.get_guild(GUILD_ID)
            if not guild:
                return
            
            # تغییرات طبیعی رضایت عمومی
            natural_change = random.uniform(-2, 1)  # کمی منفی‌تر
            self.public_approval += natural_change
            self.public_approval = max(0, min(100, self.public_approval))
            
            # هشدار در صورت رضایت پایین
            if self.public_approval < 30:
                government_channel = discord.utils.get(guild.channels, name='دولت')
                if government_channel:
                    embed = create_embed(
                        "⚠️ هشدار رضایت عمومی",
                        f"رضایت عمومی به {self.public_approval:.1f} رسیده است!\n"
                        "خطر ناآرامی‌های اجتماعی وجود دارد.\n\n"
                        "اقدامات پیشنهادی:\n"
                        "• کاهش مالیات‌ها\n"
                        "• افزایش خدمات رفاهی\n"
                        "• برگزاری رویدادهای ملی",
                        EMBED_COLORS['error']
                    )
                    await government_channel.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"خطا در نظارت رضایت عمومی: {e}")

# ======================= ربات پیشرفت فردی =======================

class PersonalProgressBot(commands.Bot):
    """
    ربات پیشرفت فردی
    مسئول مدیریت مهارت‌ها، دستاوردها و پیشرفت شخصی کاربران
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!پیشرفت_',
            intents=intents,
            help_command=None,
            description="سیستم پیشرفت فردی اسرائیل"
        )
        
        self.db = DatabaseManager()
        
        # درخت مهارت‌ها
        self.skill_tree = {
            'رهبری': {
                'max_level': 10,
                'benefits': {
                    1: 'افزایش 5% درآمد روزانه',
                    5: 'دسترسی به دستورات مدیریتی',
                    10: 'قابلیت تأسیس سازمان'
                }
            },
            'مذاکره': {
                'max_level': 10,
                'benefits': {
                    1: 'کاهش 10% هزینه خرید',
                    5: 'قابلیت میانجی‌گری در دعاوی',
                    10: 'دیپلماسی بین‌المللی'
                }
            },
            'فنی': {
                'max_level': 10,
                'benefits': {
                    1: 'سرعت 10% بیشتر در تولید',
                    5: 'قابلیت تعمیر تجهیزات',
                    10: 'اختراع فناوری جدید'
                }
            },
            'رزمی': {
                'max_level': 10,
                'benefits': {
                    1: 'افزایش 20% قدرت در نبرد',
                    5: 'قابلیت آموزش سربازان',
                    10: 'تاکتیک‌های پیشرفته'
                }
            },
            'اقتصادی': {
                'max_level': 10,
                'benefits': {
                    1: 'کاهش 5% مالیات',
                    5: 'قابلیت سرمایه‌گذاری پیشرفته',
                    10: 'مشاوره اقتصادی ملی'
                }
            }
        }
        
        # دستاوردها
        self.achievements = {
            'first_citizen': {
                'name': 'اولین شهروند',
                'description': 'اولین نفری که شهروندی گرفت',
                'reward_xp': 1000,
                'reward_money': 50000
            },
            'first_pm': {
                'name': 'اولین نخست‌وزیر',
                'description': 'اولین نخست‌وزیر منتخب',
                'reward_xp': 5000,
                'reward_money': 500000
            },
            'millionaire': {
                'name': 'میلیونر',
                'description': 'رسیدن به یک میلیون شکل',
                'reward_xp': 2000,
                'reward_money': 100000
            },
            'property_mogul': {
                'name': 'غول املاک',
                'description': 'خرید 3 ملک',
                'reward_xp': 1500,
                'reward_money': 200000
            },
            'crisis_manager': {
                'name': 'مدیر بحران',
                'description': 'حل 5 بحران ملی',
                'reward_xp': 3000,
                'reward_money': 300000
            }
        }
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - سیستم پیشرفت فردی آماده است!')
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="پیشرفت شهروندان 📈"
            )
        )

    @commands.command(name='پروفایل')
    async def user_profile(self, ctx, member: discord.Member = None):
        """نمایش پروفایل کامل کاربر"""
        if member is None:
            member = ctx.author
            
        user_id = str(member.id)
        
        # دریافت اطلاعات کاربر
        user_xp = self.db.get_user_data(user_id, 'xp') or 0
        user_level = int(user_xp / 1000) + 1
        user_skills = self.db.get_user_data(user_id, 'skills') or {}
        user_achievements = self.db.get_user_data(user_id, 'achievements') or []
        
        embed = create_embed(
            f"👤 پروفایل {member.display_name}",
            f"**سطح:** {user_level}\n"
            f"**تجربه:** {user_xp:,} XP\n"
            f"**تا سطح بعد:** {1000 - (user_xp % 1000)} XP",
            EMBED_COLORS['primary']
        )
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        # مهارت‌ها
        if user_skills:
            skills_text = ""
            for skill, level in user_skills.items():
                max_level = self.skill_tree[skill]['max_level']
                progress_bar = "█" * level + "░" * (max_level - level)
                skills_text += f"**{skill}:** {level}/{max_level} {progress_bar}\n"
            
            embed.add_field(
                name="🛠️ مهارت‌ها",
                value=skills_text,
                inline=False
            )
        
        # دستاوردها
        if user_achievements:
            achievements_text = "\n".join([f"🏆 {self.achievements[ach]['name']}" 
                                         for ach in user_achievements])
            embed.add_field(
                name="🏆 دستاوردها",
                value=achievements_text,
                inline=False
            )
        
        # آمار شغلی
        user_job = self.db.get_user_data(user_id, 'job')
        if user_job:
            job_start = self.db.get_user_data(user_id, 'job_start_date')
            if job_start:
                work_days = (datetime.now() - datetime.fromisoformat(job_start)).days
                embed.add_field(
                    name="💼 شغل",
                    value=f"**موقعیت:** {user_job}\n**مدت کار:** {work_days} روز",
                    inline=True
                )
        
        await ctx.send(embed=embed)

    @commands.command(name='ارتقا_مهارت')
    async def upgrade_skill(self, ctx, skill_name: str, points: int = 1):
        """ارتقاء مهارت با خرج کردن XP"""
        user_id = str(ctx.author.id)
        
        if skill_name not in self.skill_tree:
            embed = create_embed(
                "خطا ❌",
                f"مهارت '{skill_name}' یافت نشد!\nمهارت‌های موجود:\n" +
                "\n".join(self.skill_tree.keys()),
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        user_xp = self.db.get_user_data(user_id, 'xp') or 0
        user_skills = self.db.get_user_data(user_id, 'skills') or {}
        current_level = user_skills.get(skill_name, 0)
        max_level = self.skill_tree[skill_name]['max_level']
        
        # بررسی حداکثر سطح
        if current_level >= max_level:
            embed = create_embed(
                "خطا ❌",
                f"مهارت '{skill_name}' به حداکثر سطح رسیده است!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # محاسبه هزینه
        cost_per_point = (current_level + 1) * 500  # هزینه افزایشی
        total_cost = cost_per_point * points
        
        # بررسی امکان ارتقاء
        if current_level + points > max_level:
            embed = create_embed(
                "خطا ❌",
                f"نمی‌توانید بیش از {max_level - current_level} امتیاز اضافه کنید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی XP کافی
        if user_xp < total_cost:
            embed = create_embed(
                "XP ناکافی ❌",
                f"**هزینه مورد نیاز:** {total_cost:,} XP\n"
                f"**XP شما:** {user_xp:,} XP\n"
                f"**کمبود:** {total_cost - user_xp:,} XP",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # اعمال ارتقاء
        user_skills[skill_name] = current_level + points
        user_xp -= total_cost
        
        self.db.set_user_data(user_id, 'skills', user_skills)
        self.db.set_user_data(user_id, 'xp', user_xp)
        
        new_level = user_skills[skill_name]
        
        embed = create_embed(
            "ارتقاء موفق ✅",
            f"**مهارت:** {skill_name}\n"
            f"**سطح جدید:** {new_level}/{max_level}\n"
            f"**XP خرج شده:** {total_cost:,}\n"
            f"**XP باقیمانده:** {user_xp:,}",
            EMBED_COLORS['success']
        )
        
        # بررسی مزایای جدید
        benefits = self.skill_tree[skill_name]['benefits']
        if new_level in benefits:
            embed.add_field(
                name="🎁 مزیت جدید باز شد!",
                value=benefits[new_level],
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='دستاوردها')
    async def achievements_list(self, ctx, member: discord.Member = None):
        """لیست دستاوردها"""
        if member is None:
            member = ctx.author
            
        user_id = str(member.id)
        user_achievements = self.db.get_user_data(user_id, 'achievements') or []
        
        embed = create_embed(
            f"🏆 دستاوردهای {member.display_name}",
            f"تعداد دستاوردها: {len(user_achievements)}/{len(self.achievements)}",
            EMBED_COLORS['primary']
        )
        
        for ach_id, ach_data in self.achievements.items():
            if ach_id in user_achievements:
                status = "✅"
                color = "**"
            else:
                status = "❌"
                color = ""
            
            embed.add_field(
                name=f"{status} {color}{ach_data['name']}{color}",
                value=f"{ach_data['description']}\n"
                      f"پاداش: {ach_data['reward_xp']:,} XP + {ach_data['reward_money']:,} شکل",
                inline=True
            )
        
        await ctx.send(embed=embed)

    async def award_achievement(self, user_id: str, achievement_id: str):
        """اعطای دستاورد به کاربر"""
        user_achievements = self.db.get_user_data(user_id, 'achievements') or []
        
        if achievement_id not in user_achievements:
            user_achievements.append(achievement_id)
            self.db.set_user_data(user_id, 'achievements', user_achievements)
            
            # اعطای پاداش
            achievement = self.achievements[achievement_id]
            user_xp = self.db.get_user_data(user_id, 'xp') or 0
            user_xp += achievement['reward_xp']
            self.db.set_user_data(user_id, 'xp', user_xp)
            
            # اطلاع‌رسانی
            guild = self.get_guild(GUILD_ID)
            if guild:
                member = guild.get_member(int(user_id))
                if member:
                    embed = create_embed(
                        "🎉 دستاورد جدید!",
                        f"**{member.mention}** دستاورد **{achievement['name']}** را کسب کرد!\n\n"
                        f"**توضیحات:** {achievement['description']}\n"
                        f"**پاداش:** {achievement['reward_xp']:,} XP + {achievement['reward_money']:,} شکل",
                        EMBED_COLORS['success']
                    )
                    
                    achievements_channel = discord.utils.get(guild.channels, name='دستاوردها')
                    if not achievements_channel:
                        achievements_channel = discord.utils.get(guild.channels, name='عمومی')
                    
                    if achievements_channel:
                        await achievements_channel.send(embed=embed)

# ======================= ربات اقتصاد سیاه =======================

class UndergroundEconomyBot(commands.Bot):
    """
    ربات اقتصاد سیاه
    مسئول فعالیت‌های غیرقانونی و بازار سیاه
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!زیرزمین_',
            intents=intents,
            help_command=None,
            description="اقتصاد سیاه اسرائیل"
        )
        
        self.db = DatabaseManager()
        
        # آیتم‌های بازار سیاه
        self.black_market_items = {
            'اطلاعات_محرمانه': {
                'price': 100000,
                'description': 'اطلاعات حساس دولتی',
                'risk': 'high'
            },
            'اسلحه_غیرقانونی': {
                'price': 50000,
                'description': 'تجهیزات نظامی قاچاق',
                'risk': 'high'
            },
            'مواد_مخدر': {
                'price': 25000,
                'description': 'مواد ممنوعه',
                'risk': 'medium'
            },
            'پاسپورت_جعلی': {
                'price': 75000,
                'description': 'مدارک جعلی برای فرار',
                'risk': 'high'
            }
        }
        
        # مأموریت‌های غیرقانونی
        self.illegal_missions = [
            {
                'name': 'قاچاق اسلحه',
                'reward': 80000,
                'risk': 0.3,
                'description': 'انتقال تجهیزات نظامی به خارج از کشور'
            },
            {
                'name': 'هک کردن سیستم',
                'reward': 120000,
                'risk': 0.4,
                'description': 'نفوذ به سیستم‌های دولتی'
            },
            {
                'name': 'پولشویی',
                'reward': 60000,
                'risk': 0.2,
                'description': 'تبدیل پول کثیف به پول تمیز'
            }
        ]
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - اقتصاد سیاه آماده است!')
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="فعالیت‌های مشکوک 🕵️"
            )
        )

    @commands.command(name='ورود')
    async def enter_underground(self, ctx):
        """ورود به دنیای زیرزمین"""
        user_id = str(ctx.author.id)
        
        # بررسی سابقه کیفری
        criminal_record = self.db.get_user_data(user_id, 'criminal_record') or []
        
        if len(criminal_record) < 2:  # نیاز به حداقل 2 جرم
            embed = create_embed(
                "دسترسی محدود ❌",
                "برای ورود به دنیای زیرزمین نیاز به سابقه کیفری دارید!\n"
                "ابتدا چند فعالیت مشکوک انجام دهید...",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # ارسال پیام خصوصی
        embed = create_embed(
            "🕵️ خوش آمدید به دنیای زیرزمین",
            "شما وارد بخش محرمانه شدید.\n"
            "اینجا قوانین متفاوت است...\n\n"
            "**دستورات موجود:**\n"
            "• `!زیرزمین_بازار`: مشاهده بازار سیاه\n"
            "• `!زیرزمین_مأموریت`: دریافت مأموریت غیرقانونی\n"
            "• `!زیرزمین_خرید [آیتم]`: خرید از بازار سیاه",
            EMBED_COLORS['error']
        )
        embed.set_footer(text="⚠️ تمام فعالیت‌ها محرمانه است")
        
        try:
            await ctx.author.send(embed=embed)
            await ctx.message.delete()  # حذف پیام عمومی
        except:
            await ctx.send("پیام خصوصی ارسال نشد. DM خود را باز کنید.", delete_after=10)

# ======================= اجرای سیستم مدیریت بحران =======================

async def run_crisis_management():
    """اجرای ربات مدیریت بحران"""
    bot = CrisisManagementBot()
    await bot.start(DISCORD_BOT_TOKEN_CRISIS_MANAGEMENT)

async def run_personal_progress():
    """اجرای ربات پیشرفت فردی"""
    bot = PersonalProgressBot()
    await bot.start(DISCORD_BOT_TOKEN_PERSONAL_PROGRESS)

async def run_underground_economy():
    """اجرای ربات اقتصاد سیاه"""
    bot = UndergroundEconomyBot()
    await bot.start(DISCORD_BOT_TOKEN_UNDERGROUND)

if __name__ == "__main__":
    """
    راهنمای اجرا:
    
    1. نصب وابستگی‌ها:
       pip install -r requirements.txt
    
    2. تنظیم متغیرهای محیطی در فایل .env:
       DISCORD_BOT_TOKEN_CRISIS_MANAGEMENT=توکن_ربات_مدیریت_بحران
       DISCORD_BOT_TOKEN_PERSONAL_PROGRESS=توکن_ربات_پیشرفت_فردی
       DISCORD_BOT_TOKEN_UNDERGROUND=توکن_ربات_اقتصاد_سیاه
       GEMINI_API_KEY=کلید_API_جمنای
    
    3. اجرای ربات‌ها:
       python crisis_management.py
    
    دستورات اصلی:
    
    مدیریت بحران:
    - !بحران_وضعیت_ملی : وضعیت کلی کشور
    - !بحران_شبیه‌سازی_بحران [نوع] [شدت] : شبیه‌سازی بحران
    - !بحران_مدیریت_بحران [راه‌حل] : حل بحران فعال
    - !بحران_تاریخچه_بحران : تاریخچه بحران‌ها
    
    پیشرفت فردی:
    - !پیشرفت_پروفایل : نمایش پروفایل کامل
    - !پیشرفت_ارتقا_مهارت [مهارت] [امتیاز] : ارتقاء مهارت
    - !پیشرفت_دستاوردها : لیست دستاوردها
    
    اقتصاد سیاه:
    - !زیرزمین_ورود : ورود به دنیای زیرزمین
    - !زیرزمین_بازار : مشاهده بازار سیاه (در DM)
    - !زیرزمین_مأموریت : دریافت مأموریت غیرقانونی (در DM)
    """
    
    import asyncio
    
    async def main():
        # اجرای همزمان تمام سیستم‌های مدیریت بحران
        await asyncio.gather(
            run_crisis_management(),
            run_personal_progress(),
            run_underground_economy()
        )
    
    asyncio.run(main())