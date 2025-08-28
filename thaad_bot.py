"""
ربات تاد (THAAD) - سامانه دفاع پیشگیرانه
THAAD Bot - Preemptive Defense System

این ربات مسئول دفاع پیشگیرانه، اسکن کاربران جدید و تشخیص تهدیدات قبل از وقوع است.
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import time
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Set, Tuple
import logging
from collections import defaultdict, deque
import aiohttp
import hashlib
from utils import (
    BaseBot, EmbedBuilder, PermissionManager, TimeManager, 
    SecurityManager, NotificationManager, GeminiAI, EMOJIS, format_number
)
from config import (
    BotConfig, DefenseConfig, EMBED_COLORS, SYSTEM_MESSAGES
)

logger = logging.getLogger(__name__)

class ThreatDatabase:
    """پایگاه داده تهدیدات"""
    
    def __init__(self):
        self.known_threats = set()
        self.suspicious_patterns = []
        self.blacklisted_ips = set()
        self.malicious_usernames = set()
        self.threat_indicators = {}
        
        # بارگذاری داده‌های پیش‌فرض
        self.load_default_threats()
    
    def load_default_threats(self):
        """بارگذاری تهدیدات شناخته شده"""
        # الگوهای نام کاربری مشکوک
        self.malicious_usernames.update([
            'discord', 'moderator', 'admin', 'owner', 'bot',
            'official', 'support', 'help', 'system'
        ])
        
        # الگوهای مشکوک
        self.suspicious_patterns.extend([
            r'^\w+\d{4,}$',  # نام + اعداد زیاد
            r'^[a-zA-Z]+[0-9]+[a-zA-Z]+$',  # حروف-اعداد-حروف
            r'(.)\1{3,}',  # تکرار کاراکتر
            r'discord|bot|spam|raid|nuke|hack',  # کلمات خطرناک
            r'^(test|user|member)\d+$',  # نام‌های عمومی با عدد
        ])
    
    def add_threat(self, threat_id: str, threat_data: Dict):
        """اضافه کردن تهدید جدید"""
        self.known_threats.add(threat_id)
        self.threat_indicators[threat_id] = threat_data
    
    def is_threat(self, identifier: str) -> bool:
        """بررسی تهدید بودن"""
        return identifier in self.known_threats
    
    def check_username_suspicious(self, username: str) -> Tuple[bool, List[str]]:
        """بررسی مشکوک بودن نام کاربری"""
        reasons = []
        
        # بررسی نام‌های مسدود شده
        if username.lower() in self.malicious_usernames:
            reasons.append("نام کاربری در لیست سیاه")
        
        # بررسی الگوهای مشکوک
        for pattern in self.suspicious_patterns:
            if re.search(pattern, username, re.IGNORECASE):
                reasons.append(f"الگوی مشکوک: {pattern[:20]}...")
        
        # بررسی طول نام
        if len(username) < 3 or len(username) > 20:
            reasons.append("طول نام نامناسب")
        
        # بررسی کاراکترهای خاص
        special_chars = len(re.findall(r'[^a-zA-Z0-9_]', username))
        if special_chars > 3:
            reasons.append("کاراکترهای خاص زیاد")
        
        return len(reasons) > 0, reasons

class UserProfileAnalyzer:
    """تحلیلگر پروفایل کاربران"""
    
    def __init__(self):
        self.analysis_cache = {}
        self.reputation_scores = defaultdict(float)
    
    async def analyze_user_profile(self, user: discord.User) -> Dict:
        """تحلیل کامل پروفایل کاربر"""
        user_id = user.id
        
        # بررسی کش
        if user_id in self.analysis_cache:
            cached_analysis = self.analysis_cache[user_id]
            # اگر تحلیل کمتر از 1 ساعت قدیمی است
            if time.time() - cached_analysis['timestamp'] < 3600:
                return cached_analysis
        
        analysis = {
            'user_id': user_id,
            'username': user.name,
            'discriminator': user.discriminator,
            'timestamp': time.time(),
            'risk_score': 0.0,
            'risk_factors': [],
            'recommendations': []
        }
        
        # تحلیل سن اکانت
        account_age = (datetime.now() - user.created_at).days
        analysis['account_age_days'] = account_age
        
        if account_age < 1:
            analysis['risk_score'] += 0.5
            analysis['risk_factors'].append("اکانت بسیار جدید (کمتر از 1 روز)")
        elif account_age < 7:
            analysis['risk_score'] += 0.3
            analysis['risk_factors'].append("اکانت جدید (کمتر از 1 هفته)")
        elif account_age < 30:
            analysis['risk_score'] += 0.1
            analysis['risk_factors'].append("اکانت نسبتاً جدید (کمتر از 1 ماه)")
        
        # تحلیل آواتار
        analysis['has_avatar'] = user.avatar is not None
        if not user.avatar:
            analysis['risk_score'] += 0.2
            analysis['risk_factors'].append("عدم داشتن آواتار شخصی")
        
        # تحلیل نام کاربری
        threat_db = ThreatDatabase()
        is_suspicious, username_reasons = threat_db.check_username_suspicious(user.name)
        if is_suspicious:
            analysis['risk_score'] += 0.3
            analysis['risk_factors'].extend(username_reasons)
        
        # تحلیل ID کاربر (الگوهای مشکوک در ID)
        user_id_str = str(user_id)
        if len(set(user_id_str)) <= 3:  # ID با ارقام تکراری زیاد
            analysis['risk_score'] += 0.1
            analysis['risk_factors'].append("ID با الگوی مشکوک")
        
        # محاسبه سطح خطر نهایی
        analysis['risk_score'] = min(1.0, analysis['risk_score'])
        
        if analysis['risk_score'] > 0.7:
            analysis['threat_level'] = 'high'
            analysis['recommendations'].extend([
                "نظارت دقیق",
                "محدودیت دسترسی",
                "بررسی فعالیت‌ها"
            ])
        elif analysis['risk_score'] > 0.4:
            analysis['threat_level'] = 'medium'
            analysis['recommendations'].extend([
                "نظارت معمولی",
                "بررسی دوره‌ای"
            ])
        else:
            analysis['threat_level'] = 'low'
            analysis['recommendations'].append("نظارت استاندارد")
        
        # ذخیره در کش
        self.analysis_cache[user_id] = analysis
        
        return analysis
    
    def update_reputation(self, user_id: int, score_change: float, reason: str):
        """به‌روزرسانی امتیاز اعتبار کاربر"""
        self.reputation_scores[user_id] += score_change
        
        # محدود کردن امتیاز بین -100 تا 100
        self.reputation_scores[user_id] = max(-100, min(100, self.reputation_scores[user_id]))
    
    def get_reputation(self, user_id: int) -> float:
        """دریافت امتیاز اعتبار کاربر"""
        return self.reputation_scores.get(user_id, 0.0)

class THAADBot(BaseBot):
    """ربات تاد - سامانه دفاع پیشگیرانه"""
    
    def __init__(self):
        super().__init__(
            command_prefix=BotConfig.COMMAND_PREFIX,
            bot_name="تاد",
            description="سامانه دفاع پیشگیرانه اسرائیل"
        )
        
        self.token = BotConfig.THAAD_TOKEN
        self.missile_count = 100  # تاد موشک ندارد، اما برای سازگاری
        self.intercepted_today = 0
        self.total_intercepted = 0
        
        # سیستم‌های اصلی
        self.threat_database = ThreatDatabase()
        self.profile_analyzer = UserProfileAnalyzer()
        
        # سیستم نظارت
        self.monitored_users = defaultdict(dict)
        self.scan_queue = deque()
        self.scan_results = {}
        self.alert_history = deque(maxlen=200)
        
        # سیستم یادگیری
        self.learning_data = defaultdict(list)
        self.behavior_patterns = {}
        self.false_positive_feedback = []
        
        # آمار عملکرد
        self.performance_stats = {
            'users_scanned': 0,
            'threats_detected': 0,
            'false_positives': 0,
            'successful_predictions': 0,
            'total_alerts': 0,
            'reputation_updates': 0
        }
        
        # تنظیمات
        self.auto_scan = True
        self.alert_threshold = 0.6
        self.deep_scan_enabled = True
        self.learning_mode = True
        self.reputation_system_enabled = True
        
        # بارگذاری کامندها
        self.load_commands()
        
        # شروع وظایف دوره‌ای
        self.start_background_tasks()
    
    def load_commands(self):
        """بارگذاری کامندهای ربات"""
        
        @self.command(name='thaad_status', aliases=['وضعیت_تاد'])
        async def thaad_status(ctx):
            """نمایش وضعیت تاد"""
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['shield']} وضعیت تاد (THAAD)",
                description="گزارش عملکرد سامانه دفاع پیشگیرانه",
                color=EMBED_COLORS['defense']
            )
            
            # وضعیت عمومی سیستم
            embed.add_field(
                name="🎯 وضعیت سیستم",
                value=f"🔍 اسکن خودکار: {'فعال' if self.auto_scan else 'غیرفعال'}\n"
                      f"🧠 حالت یادگیری: {'فعال' if self.learning_mode else 'غیرفعال'}\n"
                      f"🏆 سیستم اعتبار: {'فعال' if self.reputation_system_enabled else 'غیرفعال'}\n"
                      f"🔬 اسکن عمیق: {'فعال' if self.deep_scan_enabled else 'غیرفعال'}",
                inline=True
            )
            
            # آمار اسکن
            embed.add_field(
                name="📊 آمار اسکن",
                value=f"👥 کاربران اسکن شده: **{format_number(self.performance_stats['users_scanned'])}**\n"
                      f"🚨 تهدیدات تشخیص داده شده: **{format_number(self.performance_stats['threats_detected'])}**\n"
                      f"📈 پیش‌بینی‌های موفق: **{format_number(self.performance_stats['successful_predictions'])}**\n"
                      f"⚠️ هشدارهای کل: **{format_number(self.performance_stats['total_alerts'])}**",
                inline=True
            )
            
            # صف اسکن
            embed.add_field(
                name="⏳ صف اسکن",
                value=f"📋 در انتظار: **{len(self.scan_queue)}**\n"
                      f"👁️ تحت نظارت: **{len(self.monitored_users)}**\n"
                      f"💾 نتایج ذخیره شده: **{len(self.scan_results)}**\n"
                      f"🎯 آستانه هشدار: **{int(self.alert_threshold * 100)}%**",
                inline=True
            )
            
            # دقت سیستم
            accuracy = self.calculate_system_accuracy()
            embed.add_field(
                name="🎯 عملکرد سیستم",
                value=f"📊 دقت کلی: **{accuracy:.1f}%**\n"
                      f"❌ تشخیص اشتباه: **{format_number(self.performance_stats['false_positives'])}**\n"
                      f"🔄 به‌روزرسانی اعتبار: **{format_number(self.performance_stats['reputation_updates'])}**\n"
                      f"📚 داده‌های یادگیری: **{len(self.learning_data)}**",
                inline=True
            )
            
            # پایگاه داده تهدیدات
            embed.add_field(
                name="🗄️ پایگاه داده تهدیدات",
                value=f"🚫 تهدیدات شناخته شده: **{len(self.threat_database.known_threats)}**\n"
                      f"🔍 الگوهای مشکوک: **{len(self.threat_database.suspicious_patterns)}**\n"
                      f"🌐 IP های مسدود: **{len(self.threat_database.blacklisted_ips)}**\n"
                      f"👤 نام‌های مخرب: **{len(self.threat_database.malicious_usernames)}**",
                inline=True
            )
            
            # وضعیت آخرین فعالیت
            uptime = self.get_uptime()
            embed.add_field(
                name="⏰ وضعیت زمانی",
                value=f"🕐 مدت فعالیت: {uptime}\n"
                      f"📅 اسکن امروز: **{self.intercepted_today}**\n"
                      f"📊 کل اسکن‌ها: **{format_number(self.total_intercepted)}**\n"
                      f"🔄 آخرین به‌روزرسانی: **اکنون**",
                inline=True
            )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/THAAD_missile_launch.jpg/640px-THAAD_missile_launch.jpg")
            embed.set_footer(text=f"آخرین به‌روزرسانی: {TimeManager.format_time(TimeManager.get_current_time())}")
            
            await ctx.send(embed=embed)
        
        @self.command(name='scan_user', aliases=['اسکن_کاربر'])
        @commands.has_permissions(manage_guild=True)
        async def scan_user(ctx, user: discord.Member = None, deep: bool = False):
            """اسکن دستی کاربر"""
            
            if user is None:
                embed = EmbedBuilder.error_embed(
                    "کاربر مشخص نشده",
                    "لطفاً کاربر مورد نظر را منشن کنید."
                )
                await ctx.send(embed=embed)
                return
            
            # شروع اسکن
            embed = EmbedBuilder.create_embed(
                title="🔍 شروع اسکن کاربر",
                description=f"در حال اسکن {user.mention}...",
                color=EMBED_COLORS['info']
            )
            message = await ctx.send(embed=embed)
            
            # انجام اسکن
            scan_result = await self.perform_user_scan(user, deep_scan=deep)
            
            # نمایش نتایج
            result_embed = await self.create_scan_result_embed(user, scan_result)
            await message.edit(embed=result_embed)
            
            # اگر تهدید تشخیص داده شد
            if scan_result['risk_score'] > self.alert_threshold:
                await self.handle_threat_detection(ctx.guild, user, scan_result)
        
        @self.command(name='threat_report', aliases=['گزارش_تهدید'])
        @commands.has_permissions(manage_guild=True)
        async def threat_report(ctx, limit: int = 10):
            """گزارش تهدیدات اخیر"""
            
            limit = max(1, min(50, limit))
            
            embed = EmbedBuilder.create_embed(
                title="📋 گزارش تهدیدات اخیر",
                description=f"آخرین {limit} تهدید تشخیص داده شده",
                color=EMBED_COLORS['warning']
            )
            
            if not self.alert_history:
                embed.add_field(
                    name="✅ وضعیت امن",
                    value="هیچ تهدیدی در دوره اخیر تشخیص داده نشده است.",
                    inline=False
                )
            else:
                recent_alerts = list(self.alert_history)[-limit:]
                
                for i, alert in enumerate(reversed(recent_alerts), 1):
                    timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%m/%d %H:%M")
                    user_id = alert.get('user_id', 'نامشخص')
                    threat_level = alert.get('threat_level', 'متوسط')
                    
                    embed.add_field(
                        name=f"#{i} - {timestamp}",
                        value=f"👤 <@{user_id}>\n"
                              f"🚨 سطح: {threat_level}\n"
                              f"📊 امتیاز: {alert.get('risk_score', 0):.2f}\n"
                              f"⚡ اقدام: {alert.get('action', 'نظارت')}",
                        inline=True
                    )
            
            embed.set_footer(text=f"کل تهدیدات تشخیص داده شده: {self.performance_stats['threats_detected']}")
            await ctx.send(embed=embed)
        
        @self.command(name='reputation', aliases=['اعتبار'])
        async def reputation_command(ctx, user: discord.Member = None):
            """نمایش امتیاز اعتبار کاربر"""
            
            target_user = user if user else ctx.author
            reputation_score = self.profile_analyzer.get_reputation(target_user.id)
            
            embed = EmbedBuilder.create_embed(
                title="🏆 امتیاز اعتبار کاربر",
                description=f"اعتبار {target_user.mention} در سیستم تاد",
                color=self.get_reputation_color(reputation_score)
            )
            
            # نمایش امتیاز
            reputation_bar = self.create_reputation_bar(reputation_score)
            embed.add_field(
                name="📊 امتیاز اعتبار",
                value=f"{reputation_bar}\n"
                      f"**امتیاز**: {reputation_score:.1f}/100\n"
                      f"**سطح**: {self.get_reputation_level(reputation_score)}\n"
                      f"**وضعیت**: {self.get_reputation_status(reputation_score)}",
                inline=False
            )
            
            # راهنمایی
            embed.add_field(
                name="📖 راهنما",
                value="• امتیاز بالاتر = اعتماد بیشتر\n"
                      "• فعالیت مثبت امتیاز را افزایش می‌دهد\n"
                      "• رفتار مشکوک امتیاز را کاهش می‌دهد\n"
                      "• امتیاز بر دسترسی‌ها تأثیر می‌گذارد",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='monitor_user', aliases=['نظارت_کاربر'])
        @commands.has_permissions(manage_guild=True)
        async def monitor_user(ctx, user: discord.Member, duration: int = 24):
            """قرار دادن کاربر تحت نظارت"""
            
            duration = max(1, min(168, duration))  # حداکثر 1 هفته
            end_time = datetime.now() + timedelta(hours=duration)
            
            self.monitored_users[user.id] = {
                'start_time': datetime.now().isoformat(),
                'end_time': end_time.isoformat(),
                'monitor_type': 'manual',
                'reason': f'دستور مدیر {ctx.author.name}',
                'activities': []
            }
            
            embed = EmbedBuilder.success_embed(
                "نظارت فعال شد",
                f"{user.mention} برای {duration} ساعت تحت نظارت قرار گرفت."
            )
            
            embed.add_field(
                name="📊 جزئیات نظارت",
                value=f"⏰ مدت: {duration} ساعت\n"
                      f"📅 پایان: {end_time.strftime('%Y/%m/%d %H:%M')}\n"
                      f"👮 مسئول: {ctx.author.mention}\n"
                      f"🔍 نوع: نظارت دستی",
                inline=True
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='unmonitor_user', aliases=['لغو_نظارت'])
        @commands.has_permissions(manage_guild=True)
        async def unmonitor_user(ctx, user: discord.Member):
            """لغو نظارت از کاربر"""
            
            if user.id not in self.monitored_users:
                embed = EmbedBuilder.error_embed(
                    "کاربر تحت نظارت نیست",
                    f"{user.mention} در حال حاضر تحت نظارت نیست."
                )
                await ctx.send(embed=embed)
                return
            
            # حذف از لیست نظارت
            del self.monitored_users[user.id]
            
            embed = EmbedBuilder.success_embed(
                "نظارت لغو شد",
                f"نظارت از {user.mention} لغو شد."
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='thaad_config', aliases=['تنظیمات_تاد'])
        @commands.has_permissions(administrator=True)
        async def thaad_config(ctx, setting: str = None, value: str = None):
            """تنظیمات تاد"""
            
            if setting is None:
                embed = EmbedBuilder.create_embed(
                    title="⚙️ تنظیمات تاد",
                    description="تنظیمات قابل تغییر سیستم",
                    color=EMBED_COLORS['info']
                )
                
                settings_list = [
                    ("auto_scan", "فعال" if self.auto_scan else "غیرفعال", "اسکن خودکار (true/false)"),
                    ("alert_threshold", f"{int(self.alert_threshold * 100)}%", "آستانه هشدار (0-100)"),
                    ("deep_scan", "فعال" if self.deep_scan_enabled else "غیرفعال", "اسکن عمیق (true/false)"),
                    ("learning_mode", "فعال" if self.learning_mode else "غیرفعال", "حالت یادگیری (true/false)"),
                    ("reputation_system", "فعال" if self.reputation_system_enabled else "غیرفعال", "سیستم اعتبار (true/false)")
                ]
                
                for setting_name, current_value, description in settings_list:
                    embed.add_field(
                        name=f"`{setting_name}`",
                        value=f"**فعلی**: {current_value}\n{description}",
                        inline=True
                    )
                
                await ctx.send(embed=embed)
                return
            
            # تغییر تنظیمات
            try:
                if setting.lower() == 'auto_scan':
                    new_auto = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.auto_scan = new_auto
                    embed = EmbedBuilder.success_embed(
                        "تنظیم اسکن خودکار",
                        f"اسکن خودکار {'فعال' if new_auto else 'غیرفعال'} شد."
                    )
                    
                elif setting.lower() == 'alert_threshold':
                    new_threshold = max(0, min(100, int(value))) / 100
                    self.alert_threshold = new_threshold
                    embed = EmbedBuilder.success_embed(
                        "تنظیم آستانه هشدار",
                        f"آستانه هشدار به {int(new_threshold * 100)}% تغییر کرد."
                    )
                    
                elif setting.lower() == 'deep_scan':
                    new_deep = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.deep_scan_enabled = new_deep
                    embed = EmbedBuilder.success_embed(
                        "تنظیم اسکن عمیق",
                        f"اسکن عمیق {'فعال' if new_deep else 'غیرفعال'} شد."
                    )
                    
                elif setting.lower() == 'learning_mode':
                    new_learning = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.learning_mode = new_learning
                    embed = EmbedBuilder.success_embed(
                        "تنظیم حالت یادگیری",
                        f"حالت یادگیری {'فعال' if new_learning else 'غیرفعال'} شد."
                    )
                    
                elif setting.lower() == 'reputation_system':
                    new_reputation = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.reputation_system_enabled = new_reputation
                    embed = EmbedBuilder.success_embed(
                        "تنظیم سیستم اعتبار",
                        f"سیستم اعتبار {'فعال' if new_reputation else 'غیرفعال'} شد."
                    )
                    
                else:
                    embed = EmbedBuilder.error_embed(
                        "تنظیم نامعتبر",
                        f"تنظیم '{setting}' وجود ندارد."
                    )
                
                await ctx.send(embed=embed)
                
            except ValueError:
                embed = EmbedBuilder.error_embed(
                    "مقدار نامعتبر",
                    "لطفاً مقدار صحیحی وارد کنید."
                )
                await ctx.send(embed=embed)
        
        @self.command(name='add_threat', aliases=['افزودن_تهدید'])
        @commands.has_permissions(administrator=True)
        async def add_threat(ctx, threat_type: str, *, threat_data: str):
            """اضافه کردن تهدید جدید به پایگاه داده"""
            
            threat_id = hashlib.md5(threat_data.encode()).hexdigest()[:8]
            
            threat_info = {
                'type': threat_type,
                'data': threat_data,
                'added_by': ctx.author.id,
                'added_date': datetime.now().isoformat(),
                'severity': 'high'
            }
            
            self.threat_database.add_threat(threat_id, threat_info)
            
            embed = EmbedBuilder.success_embed(
                "تهدید اضافه شد",
                f"تهدید جدید با شناسه `{threat_id}` به پایگاه داده اضافه شد."
            )
            
            embed.add_field(
                name="📊 جزئیات تهدید",
                value=f"🔍 نوع: {threat_type}\n"
                      f"📝 داده: {threat_data[:50]}{'...' if len(threat_data) > 50 else ''}\n"
                      f"👤 اضافه شده توسط: {ctx.author.mention}\n"
                      f"🆔 شناسه: `{threat_id}`",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='false_positive', aliases=['تشخیص_اشتباه'])
        @commands.has_permissions(manage_guild=True)
        async def false_positive_feedback(ctx, user: discord.Member):
            """گزارش تشخیص اشتباه"""
            
            # ثبت بازخورد
            feedback = {
                'user_id': user.id,
                'reported_by': ctx.author.id,
                'timestamp': datetime.now().isoformat(),
                'type': 'false_positive'
            }
            
            self.false_positive_feedback.append(feedback)
            self.performance_stats['false_positives'] += 1
            
            # بهبود امتیاز اعتبار کاربر
            if self.reputation_system_enabled:
                self.profile_analyzer.update_reputation(user.id, 10, "تشخیص اشتباه گزارش شد")
                self.performance_stats['reputation_updates'] += 1
            
            embed = EmbedBuilder.success_embed(
                "بازخورد ثبت شد",
                f"تشخیص اشتباه برای {user.mention} ثبت شد و سیستم به‌روزرسانی شد."
            )
            
            embed.add_field(
                name="🔄 اقدامات انجام شده",
                value="• بازخورد در سیستم ثبت شد\n"
                      "• امتیاز اعتبار کاربر بهبود یافت\n"
                      "• الگوریتم یادگیری به‌روزرسانی شد\n"
                      "• آمار دقت سیستم اصلاح شد",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    def start_background_tasks(self):
        """شروع وظایف پس‌زمینه"""
        
        @tasks.loop(minutes=10)
        async def process_scan_queue():
            """پردازش صف اسکن"""
            if not self.auto_scan or not self.scan_queue:
                return
            
            # پردازش حداکثر 5 اسکن در هر دور
            for _ in range(min(5, len(self.scan_queue))):
                if not self.scan_queue:
                    break
                
                scan_request = self.scan_queue.popleft()
                user = scan_request['user']
                
                try:
                    scan_result = await self.perform_user_scan(user)
                    
                    # اگر تهدید تشخیص داده شد
                    if scan_result['risk_score'] > self.alert_threshold:
                        guild = scan_request.get('guild')
                        if guild:
                            await self.handle_threat_detection(guild, user, scan_result)
                
                except Exception as e:
                    logger.error(f"خطا در اسکن کاربر {user.id}: {e}")
        
        @tasks.loop(hours=1)
        async def monitor_users():
            """نظارت بر کاربران تحت نظارت"""
            current_time = datetime.now()
            expired_monitors = []
            
            for user_id, monitor_data in self.monitored_users.items():
                end_time = datetime.fromisoformat(monitor_data['end_time'])
                
                if current_time >= end_time:
                    expired_monitors.append(user_id)
                else:
                    # ادامه نظارت - تحلیل فعالیت‌های اخیر
                    await self.analyze_monitored_user_activity(user_id, monitor_data)
            
            # حذف نظارت‌های منقضی شده
            for user_id in expired_monitors:
                await self.end_user_monitoring(user_id)
                del self.monitored_users[user_id]
        
        @tasks.loop(hours=6)
        async def update_threat_database():
            """به‌روزرسانی پایگاه داده تهدیدات"""
            if self.learning_mode:
                await self.learn_from_data()
        
        @tasks.loop(hours=24)
        async def daily_maintenance():
            """نگهداری روزانه"""
            # پاک کردن داده‌های قدیمی
            await self.cleanup_old_data()
            
            # بازنشانی آمار روزانه
            self.intercepted_today = 0
            
            # تحلیل عملکرد
            await self.analyze_daily_performance()
        
        @tasks.loop(minutes=30)
        async def reputation_decay():
            """کاهش تدریجی امتیازات اعتبار"""
            if not self.reputation_system_enabled:
                return
            
            # کاهش تدریجی امتیازات منفی (بخشش)
            for user_id in list(self.profile_analyzer.reputation_scores.keys()):
                current_score = self.profile_analyzer.reputation_scores[user_id]
                
                if current_score < 0:
                    # بهبود تدریجی امتیازات منفی
                    new_score = min(0, current_score + 0.5)
                    self.profile_analyzer.reputation_scores[user_id] = new_score
                elif current_score > 50:
                    # کاهش تدریجی امتیازات بسیار بالا
                    new_score = max(50, current_score - 0.1)
                    self.profile_analyzer.reputation_scores[user_id] = new_score
        
        # شروع تسک‌ها
        process_scan_queue.start()
        monitor_users.start()
        update_threat_database.start()
        daily_maintenance.start()
        reputation_decay.start()
    
    async def on_member_join(self, member: discord.Member):
        """پردازش ورود کاربر جدید"""
        if not self.auto_scan:
            return
        
        # اضافه کردن به صف اسکن
        scan_request = {
            'user': member,
            'guild': member.guild,
            'priority': 'high',  # کاربران جدید اولویت بالا دارند
            'timestamp': time.time()
        }
        
        self.scan_queue.append(scan_request)
        
        # اسکن فوری برای کاربران بسیار مشکوک
        quick_risk = await self.quick_risk_assessment(member)
        if quick_risk > 0.8:
            # اسکن فوری
            scan_result = await self.perform_user_scan(member, deep_scan=True)
            if scan_result['risk_score'] > self.alert_threshold:
                await self.handle_threat_detection(member.guild, member, scan_result)
    
    async def on_message(self, message):
        """پردازش پیام‌های دریافتی"""
        if message.author.bot:
            return
        
        # اگر کاربر تحت نظارت است
        if message.author.id in self.monitored_users:
            await self.log_monitored_activity(message.author.id, {
                'type': 'message',
                'content_length': len(message.content),
                'channel_id': message.channel.id,
                'timestamp': datetime.now().isoformat()
            })
        
        # بررسی الگوهای مشکوک در پیام
        if await self.is_message_suspicious(message):
            await self.handle_suspicious_message(message)
        
        # پردازش کامندها
        await self.process_commands(message)
    
    async def perform_user_scan(self, user: discord.User, deep_scan: bool = False) -> Dict:
        """انجام اسکن کامل کاربر"""
        
        # تحلیل پایه پروفایل
        profile_analysis = await self.profile_analyzer.analyze_user_profile(user)
        
        scan_result = {
            'user_id': user.id,
            'username': user.name,
            'scan_timestamp': time.time(),
            'scan_type': 'deep' if deep_scan else 'standard',
            'risk_score': profile_analysis['risk_score'],
            'threat_level': profile_analysis['threat_level'],
            'risk_factors': profile_analysis['risk_factors'].copy(),
            'recommendations': profile_analysis['recommendations'].copy()
        }
        
        # اسکن عمیق
        if deep_scan and self.deep_scan_enabled:
            deep_analysis = await self.perform_deep_scan(user)
            
            # ترکیب نتایج
            scan_result['risk_score'] = (scan_result['risk_score'] + deep_analysis['risk_score']) / 2
            scan_result['risk_factors'].extend(deep_analysis['additional_risks'])
            scan_result['deep_scan_data'] = deep_analysis
        
        # بررسی با پایگاه داده تهدیدات
        threat_check = await self.check_against_threat_database(user)
        if threat_check['is_threat']:
            scan_result['risk_score'] = min(1.0, scan_result['risk_score'] + 0.4)
            scan_result['risk_factors'].append(f"مطابقت با تهدید شناخته شده: {threat_check['threat_type']}")
        
        # به‌روزرسانی آمار
        self.performance_stats['users_scanned'] += 1
        self.total_intercepted += 1
        
        # ذخیره نتیجه
        self.scan_results[user.id] = scan_result
        
        return scan_result
    
    async def perform_deep_scan(self, user: discord.User) -> Dict:
        """اسکن عمیق کاربر"""
        
        deep_analysis = {
            'risk_score': 0.0,
            'additional_risks': [],
            'advanced_checks': {}
        }
        
        # بررسی تاریخچه نام‌های کاربری (شبیه‌سازی)
        username_history_risk = await self.analyze_username_history(user)
        deep_analysis['risk_score'] += username_history_risk
        deep_analysis['advanced_checks']['username_history'] = username_history_risk
        
        # بررسی الگوهای فعالیت
        activity_pattern_risk = await self.analyze_activity_patterns(user)
        deep_analysis['risk_score'] += activity_pattern_risk
        deep_analysis['advanced_checks']['activity_patterns'] = activity_pattern_risk
        
        # بررسی شباهت با کاربران مشکوک شناخته شده
        similarity_risk = await self.analyze_user_similarity(user)
        deep_analysis['risk_score'] += similarity_risk
        deep_analysis['advanced_checks']['user_similarity'] = similarity_risk
        
        # بررسی متادیتای پیشرفته
        metadata_risk = await self.analyze_advanced_metadata(user)
        deep_analysis['risk_score'] += metadata_risk
        deep_analysis['advanced_checks']['metadata'] = metadata_risk
        
        # محدود کردن امتیاز
        deep_analysis['risk_score'] = min(1.0, deep_analysis['risk_score'])
        
        return deep_analysis
    
    async def quick_risk_assessment(self, user: discord.User) -> float:
        """ارزیابی سریع خطر"""
        risk_score = 0.0
        
        # بررسی سن اکانت
        account_age = (datetime.now() - user.created_at).days
        if account_age < 1:
            risk_score += 0.6
        elif account_age < 7:
            risk_score += 0.3
        
        # بررسی آواتار
        if not user.avatar:
            risk_score += 0.2
        
        # بررسی نام کاربری
        is_suspicious, _ = self.threat_database.check_username_suspicious(user.name)
        if is_suspicious:
            risk_score += 0.4
        
        return min(1.0, risk_score)
    
    async def check_against_threat_database(self, user: discord.User) -> Dict:
        """بررسی کاربر در برابر پایگاه داده تهدیدات"""
        
        # بررسی ID کاربر
        if str(user.id) in self.threat_database.known_threats:
            return {'is_threat': True, 'threat_type': 'known_user_id'}
        
        # بررسی نام کاربری
        if user.name.lower() in self.threat_database.malicious_usernames:
            return {'is_threat': True, 'threat_type': 'malicious_username'}
        
        # بررسی الگوهای مشکوک
        for pattern in self.threat_database.suspicious_patterns:
            if re.search(pattern, user.name, re.IGNORECASE):
                return {'is_threat': True, 'threat_type': f'suspicious_pattern: {pattern[:20]}'}
        
        return {'is_threat': False, 'threat_type': None}
    
    async def handle_threat_detection(self, guild: discord.Guild, user: discord.User, scan_result: Dict):
        """مدیریت تهدید تشخیص داده شده"""
        
        self.performance_stats['threats_detected'] += 1
        self.performance_stats['total_alerts'] += 1
        
        # ایجاد هشدار
        alert = {
            'user_id': user.id,
            'username': user.name,
            'risk_score': scan_result['risk_score'],
            'threat_level': scan_result['threat_level'],
            'timestamp': datetime.now().isoformat(),
            'guild_id': guild.id,
            'action': 'alert_sent'
        }
        
        self.alert_history.append(alert)
        
        # ارسال گزارش به کانال جنگ
        await self.send_threat_alert(guild, user, scan_result)
        
        # قرار دادن تحت نظارت خودکار
        if scan_result['risk_score'] > 0.8:
            self.monitored_users[user.id] = {
                'start_time': datetime.now().isoformat(),
                'end_time': (datetime.now() + timedelta(hours=48)).isoformat(),
                'monitor_type': 'automatic',
                'reason': f'تهدید سطح بالا تشخیص داده شد (امتیاز: {scan_result["risk_score"]:.2f})',
                'activities': []
            }
            alert['action'] = 'monitoring_activated'
        
        # به‌روزرسانی امتیاز اعتبار
        if self.reputation_system_enabled:
            reputation_penalty = -20 * scan_result['risk_score']
            self.profile_analyzer.update_reputation(user.id, reputation_penalty, "تهدید تشخیص داده شد")
            self.performance_stats['reputation_updates'] += 1
    
    async def send_threat_alert(self, guild: discord.Guild, user: discord.User, scan_result: Dict):
        """ارسال هشدار تهدید"""
        
        embed = EmbedBuilder.create_embed(
            title="🚨 هشدار تهدید - تاد (THAAD)",
            description="کاربر مشکوک تشخیص داده شد",
            color=self.get_threat_color(scan_result['risk_score'])
        )
        
        embed.add_field(
            name="👤 اطلاعات کاربر",
            value=f"نام: {user.name}#{user.discriminator}\n"
                  f"ID: `{user.id}`\n"
                  f"سن اکانت: {(datetime.now() - user.created_at).days} روز\n"
                  f"آواتار: {'دارد' if user.avatar else 'ندارد'}",
            inline=True
        )
        
        embed.add_field(
            name="📊 تحلیل تهدید",
            value=f"امتیاز خطر: **{scan_result['risk_score']:.2f}**\n"
                  f"سطح تهدید: **{scan_result['threat_level']}**\n"
                  f"نوع اسکن: {scan_result['scan_type']}\n"
                  f"اعتبار کاربر: {self.profile_analyzer.get_reputation(user.id):.1f}",
            inline=True
        )
        
        # عوامل خطر
        if scan_result['risk_factors']:
            risk_text = '\n'.join([f"• {factor}" for factor in scan_result['risk_factors'][:5]])
            embed.add_field(
                name="⚠️ عوامل خطر",
                value=risk_text,
                inline=False
            )
        
        # توصیه‌ها
        if scan_result['recommendations']:
            rec_text = '\n'.join([f"• {rec}" for rec in scan_result['recommendations'][:3]])
            embed.add_field(
                name="💡 توصیه‌ها",
                value=rec_text,
                inline=False
            )
        
        # اقدامات انجام شده
        actions = ["🔍 اسکن کامل انجام شد", "📊 گزارش ثبت شد"]
        if scan_result['risk_score'] > 0.8:
            actions.append("👁️ نظارت فعال شد")
        if self.reputation_system_enabled:
            actions.append("📉 امتیاز اعتبار کاهش یافت")
        
        embed.add_field(
            name="⚡ اقدامات انجام شده",
            value='\n'.join(actions),
            inline=False
        )
        
        embed.set_thumbnail(url=str(user.avatar.url) if user.avatar else None)
        embed.set_footer(text=f"تاد - سامانه دفاع پیشگیرانه | {TimeManager.format_time(TimeManager.get_current_time())}")
        
        # ارسال به کانال جنگ
        war_room = discord.utils.get(guild.text_channels, name='war-room')
        if war_room:
            await war_room.send(embed=embed)
        
        # اگر تهدید بسیار بالا باشد، به کانال‌های بیشتری ارسال کن
        if scan_result['risk_score'] > 0.9:
            channels = ['defense-alerts', 'government-announcements']
            for channel_name in channels:
                channel = discord.utils.get(guild.text_channels, name=channel_name)
                if channel:
                    await channel.send(embed=embed)
    
    async def create_scan_result_embed(self, user: discord.User, scan_result: Dict) -> discord.Embed:
        """ایجاد Embed نتیجه اسکن"""
        
        embed = EmbedBuilder.create_embed(
            title="🔍 نتیجه اسکن کاربر",
            description=f"تحلیل امنیتی {user.mention}",
            color=self.get_threat_color(scan_result['risk_score'])
        )
        
        # اطلاعات پایه
        embed.add_field(
            name="👤 اطلاعات کاربر",
            value=f"نام: {user.name}#{user.discriminator}\n"
                  f"ID: `{user.id}`\n"
                  f"سن اکانت: {(datetime.now() - user.created_at).days} روز\n"
                  f"تاریخ ایجاد: {user.created_at.strftime('%Y/%m/%d')}",
            inline=True
        )
        
        # نتیجه اسکن
        threat_level_emoji = self.get_threat_level_emoji(scan_result['threat_level'])
        embed.add_field(
            name="📊 نتیجه اسکن",
            value=f"امتیاز خطر: **{scan_result['risk_score']:.2f}**\n"
                  f"سطح تهدید: {threat_level_emoji} **{scan_result['threat_level']}**\n"
                  f"نوع اسکن: {scan_result['scan_type']}\n"
                  f"زمان اسکن: {datetime.fromtimestamp(scan_result['scan_timestamp']).strftime('%H:%M:%S')}",
            inline=True
        )
        
        # امتیاز اعتبار
        reputation = self.profile_analyzer.get_reputation(user.id)
        reputation_bar = self.create_reputation_bar(reputation, length=8)
        embed.add_field(
            name="🏆 امتیاز اعتبار",
            value=f"{reputation_bar}\n**{reputation:.1f}**/100",
            inline=True
        )
        
        # عوامل خطر
        if scan_result['risk_factors']:
            risk_text = '\n'.join([f"• {factor}" for factor in scan_result['risk_factors'][:6]])
            embed.add_field(
                name="⚠️ عوامل خطر شناسایی شده",
                value=risk_text,
                inline=False
            )
        
        # توصیه‌ها
        if scan_result['recommendations']:
            rec_text = '\n'.join([f"• {rec}" for rec in scan_result['recommendations']])
            embed.add_field(
                name="💡 توصیه‌های امنیتی",
                value=rec_text,
                inline=False
            )
        
        embed.set_thumbnail(url=str(user.avatar.url) if user.avatar else None)
        embed.set_footer(text="تاد - سامانه دفاع پیشگیرانه")
        
        return embed
    
    async def is_message_suspicious(self, message: discord.Message) -> bool:
        """بررسی مشکوک بودن پیام"""
        content = message.content.lower()
        
        # الگوهای مشکوک
        suspicious_patterns = [
            r'discord\.gg/\w+',  # لینک دعوت
            r'@everyone|@here',  # منشن همگانی
            r'(free|hack|cheat|bot|spam)',  # کلمات مشکوک
            r'(.)\1{5,}',  # تکرار کاراکتر
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content):
                return True
        
        # بررسی طول پیام
        if len(content) > 1000 or len(content) < 2:
            return True
        
        # بررسی تعداد منشن‌ها
        if len(message.mentions) > 5:
            return True
        
        return False
    
    async def handle_suspicious_message(self, message: discord.Message):
        """مدیریت پیام مشکوک"""
        
        # اگر کاربر تحت نظارت نیست، قرار دادن تحت نظارت کوتاه مدت
        if message.author.id not in self.monitored_users:
            self.monitored_users[message.author.id] = {
                'start_time': datetime.now().isoformat(),
                'end_time': (datetime.now() + timedelta(hours=2)).isoformat(),
                'monitor_type': 'automatic',
                'reason': 'پیام مشکوک ارسال شد',
                'activities': []
            }
        
        # ثبت فعالیت
        await self.log_monitored_activity(message.author.id, {
            'type': 'suspicious_message',
            'content_preview': message.content[:50],
            'channel_id': message.channel.id,
            'timestamp': datetime.now().isoformat()
        })
        
        # کاهش امتیاز اعتبار
        if self.reputation_system_enabled:
            self.profile_analyzer.update_reputation(message.author.id, -5, "ارسال پیام مشکوک")
            self.performance_stats['reputation_updates'] += 1
    
    async def log_monitored_activity(self, user_id: int, activity: Dict):
        """ثبت فعالیت کاربر تحت نظارت"""
        if user_id in self.monitored_users:
            self.monitored_users[user_id]['activities'].append(activity)
            
            # محدود کردن تعداد فعالیت‌های ذخیره شده
            if len(self.monitored_users[user_id]['activities']) > 50:
                self.monitored_users[user_id]['activities'] = self.monitored_users[user_id]['activities'][-50:]
    
    async def analyze_monitored_user_activity(self, user_id: int, monitor_data: Dict):
        """تحلیل فعالیت کاربر تحت نظارت"""
        activities = monitor_data['activities']
        
        if not activities:
            return
        
        # تحلیل الگوهای فعالیت
        suspicious_activity_count = sum(1 for activity in activities if activity['type'] in ['suspicious_message', 'mass_mention'])
        
        if suspicious_activity_count > 5:
            # گزارش فعالیت مشکوک
            guild = await self.get_main_guild()
            if guild:
                await self.report_monitored_user_activity(guild, user_id, activities, 'high_suspicion')
    
    async def report_monitored_user_activity(self, guild: discord.Guild, user_id: int, activities: List[Dict], alert_level: str):
        """گزارش فعالیت کاربر تحت نظارت"""
        
        try:
            user = await self.fetch_user(user_id)
        except:
            return
        
        embed = EmbedBuilder.create_embed(
            title="👁️ گزارش نظارت - تاد",
            description=f"فعالیت مشکوک از کاربر تحت نظارت",
            color=EMBED_COLORS['warning']
        )
        
        embed.add_field(
            name="👤 کاربر",
            value=f"{user.name}#{user.discriminator}\n`{user.id}`",
            inline=True
        )
        
        embed.add_field(
            name="📊 آمار فعالیت",
            value=f"کل فعالیت‌ها: {len(activities)}\n"
                  f"فعالیت‌های مشکوک: {sum(1 for a in activities if 'suspicious' in a['type'])}\n"
                  f"سطح هشدار: {alert_level}",
            inline=True
        )
        
        # نمایش آخرین فعالیت‌ها
        recent_activities = activities[-5:]
        activity_text = []
        for activity in recent_activities:
            timestamp = datetime.fromisoformat(activity['timestamp']).strftime('%H:%M')
            activity_text.append(f"• {timestamp}: {activity['type']}")
        
        embed.add_field(
            name="📋 آخرین فعالیت‌ها",
            value='\n'.join(activity_text),
            inline=False
        )
        
        # ارسال به کانال جنگ
        war_room = discord.utils.get(guild.text_channels, name='war-room')
        if war_room:
            await war_room.send(embed=embed)
    
    async def end_user_monitoring(self, user_id: int):
        """پایان نظارت کاربر"""
        if user_id not in self.monitored_users:
            return
        
        monitor_data = self.monitored_users[user_id]
        activities = monitor_data['activities']
        
        # تحلیل نهایی
        if activities:
            suspicious_count = sum(1 for a in activities if 'suspicious' in a.get('type', ''))
            total_count = len(activities)
            
            # به‌روزرسانی امتیاز اعتبار بر اساس رفتار در طول نظارت
            if self.reputation_system_enabled:
                if suspicious_count == 0:
                    # رفتار خوب - بهبود امتیاز
                    self.profile_analyzer.update_reputation(user_id, 5, "رفتار مناسب در طول نظارت")
                elif suspicious_count > total_count * 0.3:
                    # رفتار بد - کاهش امتیاز
                    self.profile_analyzer.update_reputation(user_id, -10, "رفتار مشکوک در طول نظارت")
                
                self.performance_stats['reputation_updates'] += 1
    
    # متدهای تحلیل پیشرفته
    async def analyze_username_history(self, user: discord.User) -> float:
        """تحلیل تاریخچه نام کاربری (شبیه‌سازی)"""
        # در پیاده‌سازی واقعی، از API های خارجی یا لاگ‌های داخلی استفاده می‌شود
        return random.uniform(0, 0.2)
    
    async def analyze_activity_patterns(self, user: discord.User) -> float:
        """تحلیل الگوهای فعالیت"""
        # شبیه‌سازی تحلیل الگوی فعالیت
        return random.uniform(0, 0.15)
    
    async def analyze_user_similarity(self, user: discord.User) -> float:
        """تحلیل شباهت با کاربران مشکوک"""
        # شبیه‌سازی تحلیل شباهت
        return random.uniform(0, 0.1)
    
    async def analyze_advanced_metadata(self, user: discord.User) -> float:
        """تحلیل متادیتای پیشرفته"""
        # شبیه‌سازی تحلیل متادیتا
        return random.uniform(0, 0.1)
    
    async def learn_from_data(self):
        """یادگیری از داده‌ها"""
        # شبیه‌سازی یادگیری ماشین
        if self.false_positive_feedback:
            # تحلیل بازخوردهای تشخیص اشتباه
            for feedback in self.false_positive_feedback[-10:]:
                # بهبود الگوریتم بر اساس بازخورد
                pass
    
    async def cleanup_old_data(self):
        """پاک کردن داده‌های قدیمی"""
        current_time = time.time()
        
        # پاک کردن نتایج اسکن قدیمی (بیش از 7 روز)
        old_scans = []
        for user_id, scan_result in self.scan_results.items():
            if current_time - scan_result['scan_timestamp'] > 604800:  # 7 روز
                old_scans.append(user_id)
        
        for user_id in old_scans:
            del self.scan_results[user_id]
        
        # پاک کردن کش تحلیل پروفایل
        old_analyses = []
        for user_id, analysis in self.profile_analyzer.analysis_cache.items():
            if current_time - analysis['timestamp'] > 86400:  # 24 ساعت
                old_analyses.append(user_id)
        
        for user_id in old_analyses:
            del self.profile_analyzer.analysis_cache[user_id]
    
    async def analyze_daily_performance(self):
        """تحلیل عملکرد روزانه"""
        # محاسبه آمار عملکرد
        total_scans = self.performance_stats['users_scanned']
        threats_detected = self.performance_stats['threats_detected']
        false_positives = self.performance_stats['false_positives']
        
        if total_scans > 0:
            detection_rate = (threats_detected / total_scans) * 100
            accuracy = ((threats_detected - false_positives) / threats_detected * 100) if threats_detected > 0 else 100
            
            # ثبت آمار برای بهبود سیستم
            daily_stats = {
                'date': datetime.now().isoformat(),
                'total_scans': total_scans,
                'detection_rate': detection_rate,
                'accuracy': accuracy,
                'false_positive_rate': (false_positives / total_scans) * 100
            }
            
            # ذخیره آمار (در پیاده‌سازی واقعی در پایگاه داده)
            if not hasattr(self, 'daily_stats'):
                self.daily_stats = []
            self.daily_stats.append(daily_stats)
    
    # متدهای کمکی
    def calculate_system_accuracy(self) -> float:
        """محاسبه دقت سیستم"""
        total_detections = self.performance_stats['threats_detected']
        false_positives = self.performance_stats['false_positives']
        
        if total_detections == 0:
            return 100.0
        
        accuracy = ((total_detections - false_positives) / total_detections) * 100
        return max(0.0, min(100.0, accuracy))
    
    def get_threat_color(self, risk_score: float) -> int:
        """دریافت رنگ بر اساس امتیاز خطر"""
        if risk_score < 0.3:
            return EMBED_COLORS['success']
        elif risk_score < 0.6:
            return EMBED_COLORS['warning']
        else:
            return EMBED_COLORS['error']
    
    def get_threat_level_emoji(self, threat_level: str) -> str:
        """دریافت اموجی بر اساس سطح تهدید"""
        emoji_map = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴'
        }
        return emoji_map.get(threat_level, '⚪')
    
    def get_reputation_color(self, reputation: float) -> int:
        """دریافت رنگ بر اساس امتیاز اعتبار"""
        if reputation >= 50:
            return EMBED_COLORS['success']
        elif reputation >= 0:
            return EMBED_COLORS['info']
        elif reputation >= -50:
            return EMBED_COLORS['warning']
        else:
            return EMBED_COLORS['error']
    
    def get_reputation_level(self, reputation: float) -> str:
        """دریافت سطح اعتبار"""
        if reputation >= 80:
            return "عالی"
        elif reputation >= 50:
            return "خوب"
        elif reputation >= 20:
            return "متوسط"
        elif reputation >= 0:
            return "پایین"
        elif reputation >= -50:
            return "بد"
        else:
            return "بسیار بد"
    
    def get_reputation_status(self, reputation: float) -> str:
        """دریافت وضعیت اعتبار"""
        if reputation >= 50:
            return "قابل اعتماد"
        elif reputation >= 0:
            return "عادی"
        elif reputation >= -50:
            return "مشکوک"
        else:
            return "خطرناک"
    
    def create_reputation_bar(self, reputation: float, length: int = 10) -> str:
        """ایجاد نوار اعتبار"""
        # تبدیل امتیاز -100 تا 100 به 0 تا 100
        normalized_score = (reputation + 100) / 2
        filled = int(length * normalized_score / 100)
        
        if reputation >= 50:
            bar_char = "🟢"
        elif reputation >= 0:
            bar_char = "🟡"
        else:
            bar_char = "🔴"
        
        bar = bar_char * filled + "⚪" * (length - filled)
        return f"[{bar}]"

# اجرای ربات
if __name__ == "__main__":
    bot = THAADBot()
    
    try:
        bot.run(bot.token)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات تاد: {e}")