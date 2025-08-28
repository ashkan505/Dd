"""
ربات فلاخن داوود - سامانه دفاع ضد Raid و حملات متوسط
David's Sling Bot - Anti-Raid and Medium Threat Defense System

این ربات مسئول مقابله با اسپم منشن، لینک‌های مخرب و ورود ناگهانی کاربران است.
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import time
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Set
import logging
from collections import defaultdict, deque
from urllib.parse import urlparse
import aiohttp
from utils import (
    BaseBot, EmbedBuilder, PermissionManager, TimeManager, 
    SecurityManager, NotificationManager, EMOJIS, format_number
)
from config import (
    BotConfig, DefenseConfig, EMBED_COLORS, SYSTEM_MESSAGES
)

logger = logging.getLogger(__name__)

class DavidSlingBot(BaseBot):
    """ربات فلاخن داوود - دفاع ضد Raid و تهدیدات متوسط"""
    
    def __init__(self):
        super().__init__(
            command_prefix=BotConfig.COMMAND_PREFIX,
            bot_name="فلاخن داوود",
            description="سامانه دفاع ضد Raid و تهدیدات متوسط اسرائیل"
        )
        
        self.token = BotConfig.DAVID_SLING_TOKEN
        self.missile_count = DefenseConfig.MISSILE_INVENTORY['david_sling']['max']
        self.intercepted_today = 0
        self.total_intercepted = 0
        
        # سیستم تشخیص Raid
        self.recent_joins = deque(maxlen=50)
        self.suspicious_users = set()
        self.quarantine_active = False
        self.quarantine_start_time = None
        
        # سیستم تشخیص منشن اسپم
        self.mention_history = defaultdict(lambda: deque(maxlen=20))
        self.mention_cooldowns = {}
        self.mention_disabled_until = None
        
        # سیستم تشخیص لینک مخرب
        self.malicious_domains = {
            'discord.gg', 'discordapp.com/invite', 't.me',
            'bit.ly', 'tinyurl.com', 'short.link',
            'grabify.link', 'iplogger.org', 'blasze.tk'
        }
        self.link_whitelist = set()
        self.scanned_links = {}
        
        # آمار و عملکرد
        self.performance_stats = {
            'raids_detected': 0,
            'raids_blocked': 0,
            'malicious_links_blocked': 0,
            'mention_spam_blocked': 0,
            'users_quarantined': 0,
            'false_positives': 0
        }
        
        # تنظیمات دفاعی
        self.sensitivity_level = 0.7
        self.auto_quarantine = True
        self.auto_mention_disable = True
        self.link_scanning_enabled = True
        self.raid_threshold = 5  # تعداد کاربران برای تشخیص Raid
        self.raid_time_window = 60  # ثانیه
        
        # بارگذاری کامندها
        self.load_commands()
        
        # شروع وظایف دوره‌ای
        self.start_background_tasks()
    
    def load_commands(self):
        """بارگذاری کامندهای ربات"""
        
        @self.command(name='sling_status', aliases=['وضعیت_فلاخن'])
        async def sling_status(ctx):
            """نمایش وضعیت فلاخن داوود"""
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['shield']} وضعیت فلاخن داوود",
                description="گزارش عملکرد سامانه دفاع ضد Raid و تهدیدات متوسط",
                color=EMBED_COLORS['defense']
            )
            
            # وضعیت عمومی
            quarantine_status = "🔒 فعال" if self.quarantine_active else "🟢 عادی"
            mention_status = "🔇 غیرفعال" if self.mention_disabled_until else "🔊 فعال"
            
            embed.add_field(
                name="🎯 وضعیت دفاعی",
                value=f"🏰 قرنطینه: {quarantine_status}\n"
                      f"📢 منشن: {mention_status}\n"
                      f"🔗 اسکن لینک: {'🟢 فعال' if self.link_scanning_enabled else '🔴 غیرفعال'}\n"
                      f"📡 حساسیت: **{int(self.sensitivity_level * 100)}%**",
                inline=True
            )
            
            # موجودی موشک‌ها
            max_missiles = DefenseConfig.MISSILE_INVENTORY['david_sling']['max']
            missile_percentage = (self.missile_count / max_missiles) * 100
            missile_bar = self.create_progress_bar(missile_percentage)
            
            embed.add_field(
                name="🚀 موجودی موشک‌ها",
                value=f"📊 {missile_bar} {missile_percentage:.1f}%\n"
                      f"🔢 موجودی: **{format_number(self.missile_count)}** / {format_number(max_missiles)}\n"
                      f"💰 ارزش: **{format_number(self.missile_count * DefenseConfig.MISSILE_INVENTORY['david_sling']['cost'])}** شکل\n"
                      f"⚡ اثربخشی: **{DefenseConfig.MISSILE_INVENTORY['david_sling']['effectiveness'] * 100:.0f}%**",
                inline=True
            )
            
            # آمار رهگیری
            embed.add_field(
                name="📈 آمار عملیات",
                value=f"🎯 رهگیری امروز: **{format_number(self.intercepted_today)}**\n"
                      f"📊 کل رهگیری‌ها: **{format_number(self.total_intercepted)}**\n"
                      f"🛡️ Raid های مسدود شده: **{format_number(self.performance_stats['raids_blocked'])}**\n"
                      f"🔗 لینک‌های مخرب: **{format_number(self.performance_stats['malicious_links_blocked'])}**",
                inline=True
            )
            
            # تهدیدات فعال
            recent_joins_count = len([join for join in self.recent_joins 
                                    if time.time() - join['timestamp'] < 300])  # 5 دقیقه اخیر
            
            embed.add_field(
                name="⚠️ تهدیدات فعال",
                value=f"👥 ورود اخیر: **{recent_joins_count}**\n"
                      f"🔴 کاربران مشکوک: **{len(self.suspicious_users)}**\n"
                      f"🏰 کاربران قرنطینه: **{self.performance_stats['users_quarantined']}**\n"
                      f"🔗 دامنه‌های مسدود: **{len(self.malicious_domains)}**",
                inline=True
            )
            
            # عملکرد سیستم
            uptime = self.get_uptime()
            accuracy = self.calculate_system_accuracy()
            
            embed.add_field(
                name="💻 عملکرد سیستم",
                value=f"🕐 مدت فعالیت: {uptime}\n"
                      f"🎯 دقت سیستم: **{accuracy:.1f}%**\n"
                      f"❌ تشخیص اشتباه: **{format_number(self.performance_stats['false_positives'])}**\n"
                      f"⚡ وضعیت: **آنلاین**",
                inline=True
            )
            
            # تنظیمات پیشرفته
            embed.add_field(
                name="⚙️ تنظیمات",
                value=f"🚨 آستانه Raid: **{self.raid_threshold}** کاربر\n"
                      f"⏰ پنجره زمانی: **{self.raid_time_window}** ثانیه\n"
                      f"🤖 قرنطینه خودکار: **{'فعال' if self.auto_quarantine else 'غیرفعال'}**\n"
                      f"📢 غیرفعال‌سازی خودکار منشن: **{'فعال' if self.auto_mention_disable else 'غیرفعال'}**",
                inline=True
            )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/David%27s_Sling_missile_launch.jpg/640px-David%27s_Sling_missile_launch.jpg")
            embed.set_footer(text=f"آخرین به‌روزرسانی: {TimeManager.format_time(TimeManager.get_current_time())}")
            
            await ctx.send(embed=embed)
        
        @self.command(name='quarantine', aliases=['قرنطینه'])
        @commands.has_permissions(manage_guild=True)
        async def quarantine_command(ctx, action: str = None, duration: int = 30):
            """مدیریت قرنطینه سرور"""
            
            if action is None:
                # نمایش وضعیت قرنطینه
                embed = EmbedBuilder.create_embed(
                    title="🏰 وضعیت قرنطینه سرور",
                    description="اطلاعات سیستم قرنطینه فلاخن داوود",
                    color=EMBED_COLORS['warning'] if self.quarantine_active else EMBED_COLORS['info']
                )
                
                if self.quarantine_active:
                    remaining_time = self.get_quarantine_remaining_time()
                    embed.add_field(
                        name="🔒 قرنطینه فعال",
                        value=f"⏰ زمان باقی‌مانده: **{remaining_time}**\n"
                              f"📅 شروع: {TimeManager.format_time(self.quarantine_start_time)}\n"
                              f"👥 کاربران متأثر: **{self.performance_stats['users_quarantined']}**",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🚫 محدودیت‌های فعال",
                        value="• ورود کاربران جدید مسدود\n"
                              "• تغییر نام و آواتار مسدود\n"
                              "• ارسال پیام برای کاربران جدید محدود\n"
                              "• دعوت به سرور غیرفعال",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🟢 قرنطینه غیرفعال",
                        value="سرور در حالت عادی قرار دارد.",
                        inline=False
                    )
                
                embed.add_field(
                    name="📖 دستورات",
                    value=f"`{BotConfig.COMMAND_PREFIX}quarantine enable [مدت]` - فعال‌سازی\n"
                          f"`{BotConfig.COMMAND_PREFIX}quarantine disable` - غیرفعال‌سازی\n"
                          f"`{BotConfig.COMMAND_PREFIX}quarantine extend [مدت]` - تمدید",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            if action.lower() == 'enable':
                if self.quarantine_active:
                    embed = EmbedBuilder.error_embed(
                        "قرنطینه فعال",
                        "قرنطینه در حال حاضر فعال است."
                    )
                else:
                    await self.activate_quarantine(ctx.guild, duration)
                    embed = EmbedBuilder.success_embed(
                        "قرنطینه فعال شد",
                        f"سرور برای {duration} دقیقه در قرنطینه قرار گرفت."
                    )
                    
            elif action.lower() == 'disable':
                if not self.quarantine_active:
                    embed = EmbedBuilder.error_embed(
                        "قرنطینه غیرفعال",
                        "قرنطینه در حال حاضر غیرفعال است."
                    )
                else:
                    await self.deactivate_quarantine(ctx.guild)
                    embed = EmbedBuilder.success_embed(
                        "قرنطینه غیرفعال شد",
                        "سرور به حالت عادی بازگشت."
                    )
                    
            elif action.lower() == 'extend':
                if not self.quarantine_active:
                    embed = EmbedBuilder.error_embed(
                        "قرنطینه غیرفعال",
                        "قرنطینه فعال نیست تا تمدید شود."
                    )
                else:
                    await self.extend_quarantine(duration)
                    embed = EmbedBuilder.success_embed(
                        "قرنطینه تمدید شد",
                        f"قرنطینه {duration} دقیقه تمدید شد."
                    )
            else:
                embed = EmbedBuilder.error_embed(
                    "دستور نامعتبر",
                    "استفاده صحیح: `!quarantine [enable/disable/extend] [مدت]`"
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name='mention_control', aliases=['کنترل_منشن'])
        @commands.has_permissions(manage_messages=True)
        async def mention_control(ctx, action: str = None, duration: int = 10):
            """کنترل سیستم منشن"""
            
            if action is None:
                # نمایش وضعیت منشن
                embed = EmbedBuilder.create_embed(
                    title="📢 وضعیت سیستم منشن",
                    description="کنترل منشن‌های سرور",
                    color=EMBED_COLORS['warning'] if self.mention_disabled_until else EMBED_COLORS['info']
                )
                
                if self.mention_disabled_until:
                    remaining = self.mention_disabled_until - datetime.now()
                    if remaining.total_seconds() > 0:
                        embed.add_field(
                            name="🔇 منشن غیرفعال",
                            value=f"⏰ زمان باقی‌مانده: **{remaining.seconds // 60}:{remaining.seconds % 60:02d}**\n"
                                  f"📊 منشن‌های مسدود شده: **{self.performance_stats['mention_spam_blocked']}**",
                            inline=False
                        )
                    else:
                        self.mention_disabled_until = None
                        embed.add_field(
                            name="🔊 منشن فعال",
                            value="منشن‌ها در حالت عادی هستند.",
                            inline=False
                        )
                else:
                    embed.add_field(
                        name="🔊 منشن فعال",
                        value="منشن‌ها در حالت عادی هستند.",
                        inline=False
                    )
                
                # آمار منشن‌ها
                total_mentions_today = sum(len(history) for history in self.mention_history.values())
                embed.add_field(
                    name="📊 آمار منشن امروز",
                    value=f"📈 کل منشن‌ها: **{total_mentions_today}**\n"
                          f"🚨 منشن اسپم: **{self.performance_stats['mention_spam_blocked']}**\n"
                          f"👥 کاربران فعال: **{len(self.mention_history)}**",
                    inline=True
                )
                
                embed.add_field(
                    name="📖 دستورات",
                    value=f"`{BotConfig.COMMAND_PREFIX}mention_control disable [مدت]` - غیرفعال‌سازی\n"
                          f"`{BotConfig.COMMAND_PREFIX}mention_control enable` - فعال‌سازی\n"
                          f"`{BotConfig.COMMAND_PREFIX}mention_control stats` - آمار تفصیلی",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            if action.lower() == 'disable':
                self.mention_disabled_until = datetime.now() + timedelta(minutes=duration)
                
                # غیرفعال کردن مجوز منشن برای همه
                await self.disable_mentions_for_all(ctx.guild)
                
                embed = EmbedBuilder.success_embed(
                    "منشن غیرفعال شد",
                    f"منشن‌ها برای {duration} دقیقه غیرفعال شدند."
                )
                
            elif action.lower() == 'enable':
                self.mention_disabled_until = None
                
                # فعال کردن مجوز منشن
                await self.enable_mentions_for_all(ctx.guild)
                
                embed = EmbedBuilder.success_embed(
                    "منشن فعال شد",
                    "منشن‌ها مجدداً فعال شدند."
                )
                
            elif action.lower() == 'stats':
                embed = await self.create_mention_stats_embed()
                
            else:
                embed = EmbedBuilder.error_embed(
                    "دستور نامعتبر",
                    "استفاده صحیح: `!mention_control [disable/enable/stats] [مدت]`"
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name='link_scanner', aliases=['اسکنر_لینک'])
        @commands.has_permissions(manage_messages=True)
        async def link_scanner(ctx, action: str = None, *, url: str = None):
            """مدیریت اسکنر لینک"""
            
            if action is None:
                # نمایش وضعیت اسکنر
                embed = EmbedBuilder.create_embed(
                    title="🔗 وضعیت اسکنر لینک",
                    description="سیستم تشخیص لینک‌های مخرب",
                    color=EMBED_COLORS['info']
                )
                
                embed.add_field(
                    name="⚙️ وضعیت سیستم",
                    value=f"🔍 اسکن لینک: **{'فعال' if self.link_scanning_enabled else 'غیرفعال'}**\n"
                          f"🔗 لینک‌های اسکن شده: **{len(self.scanned_links)}**\n"
                          f"🚫 لینک‌های مسدود شده: **{self.performance_stats['malicious_links_blocked']}**",
                    inline=True
                )
                
                embed.add_field(
                    name="📋 لیست‌ها",
                    value=f"⚫ دامنه‌های مسدود: **{len(self.malicious_domains)}**\n"
                          f"⚪ دامنه‌های مجاز: **{len(self.link_whitelist)}**",
                    inline=True
                )
                
                # نمایش برخی دامنه‌های مسدود
                blocked_domains = list(self.malicious_domains)[:5]
                embed.add_field(
                    name="🚫 دامنه‌های مسدود (نمونه)",
                    value="\n".join([f"• `{domain}`" for domain in blocked_domains]),
                    inline=False
                )
                
                embed.add_field(
                    name="📖 دستورات",
                    value=f"`{BotConfig.COMMAND_PREFIX}link_scanner scan [URL]` - اسکن لینک\n"
                          f"`{BotConfig.COMMAND_PREFIX}link_scanner block [domain]` - مسدود کردن دامنه\n"
                          f"`{BotConfig.COMMAND_PREFIX}link_scanner whitelist [domain]` - اضافه به لیست سفید",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            if action.lower() == 'scan' and url:
                result = await self.scan_url(url)
                
                embed = EmbedBuilder.create_embed(
                    title="🔍 نتیجه اسکن لینک",
                    description=f"**URL**: {url[:100]}{'...' if len(url) > 100 else ''}",
                    color=EMBED_COLORS['error'] if result['malicious'] else EMBED_COLORS['success']
                )
                
                embed.add_field(
                    name="📊 نتیجه",
                    value=f"🎯 وضعیت: **{'مخرب' if result['malicious'] else 'امن'}**\n"
                          f"📊 امتیاز خطر: **{result['risk_score']:.2f}**\n"
                          f"🔍 دلیل: {result['reason']}",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
            elif action.lower() == 'block' and url:
                domain = self.extract_domain(url)
                if domain:
                    self.malicious_domains.add(domain)
                    embed = EmbedBuilder.success_embed(
                        "دامنه مسدود شد",
                        f"دامنه `{domain}` به لیست سیاه اضافه شد."
                    )
                else:
                    embed = EmbedBuilder.error_embed(
                        "دامنه نامعتبر",
                        "نمی‌توان دامنه را استخراج کرد."
                    )
                await ctx.send(embed=embed)
                
            elif action.lower() == 'whitelist' and url:
                domain = self.extract_domain(url)
                if domain:
                    self.link_whitelist.add(domain)
                    embed = EmbedBuilder.success_embed(
                        "دامنه به لیست سفید اضافه شد",
                        f"دامنه `{domain}` به لیست سفید اضافه شد."
                    )
                else:
                    embed = EmbedBuilder.error_embed(
                        "دامنه نامعتبر",
                        "نمی‌توان دامنه را استخراج کرد."
                    )
                await ctx.send(embed=embed)
                
            else:
                embed = EmbedBuilder.error_embed(
                    "دستور نامعتبر",
                    "استفاده صحیح: `!link_scanner [scan/block/whitelist] [URL/domain]`"
                )
                await ctx.send(embed=embed)
        
        @self.command(name='raid_log', aliases=['تاریخچه_raid'])
        @commands.has_permissions(manage_guild=True)
        async def raid_log(ctx, limit: int = 10):
            """نمایش تاریخچه تشخیص Raid"""
            
            limit = max(1, min(20, limit))
            
            embed = EmbedBuilder.create_embed(
                title="🛡️ تاریخچه تشخیص Raid",
                description=f"آخرین {limit} ورود مشکوک",
                color=EMBED_COLORS['warning']
            )
            
            if not self.recent_joins:
                embed.add_field(
                    name="📭 خالی",
                    value="هیچ ورود مشکوکی ثبت نشده است.",
                    inline=False
                )
            else:
                recent_joins = list(self.recent_joins)[-limit:]
                
                for i, join_info in enumerate(reversed(recent_joins), 1):
                    timestamp = datetime.fromtimestamp(join_info['timestamp']).strftime("%H:%M:%S")
                    user_id = join_info['user_id']
                    
                    embed.add_field(
                        name=f"#{i} - {timestamp}",
                        value=f"👤 <@{user_id}>\n"
                              f"🎯 امتیاز مشکوک: {join_info.get('suspicion_score', 'N/A')}\n"
                              f"⚡ اقدام: {join_info.get('action', 'نظارت')}",
                        inline=True
                    )
            
            embed.set_footer(text=f"کل Raid های مسدود شده: {self.performance_stats['raids_blocked']}")
            await ctx.send(embed=embed)
        
        @self.command(name='sling_config', aliases=['تنظیمات_فلاخن'])
        @commands.has_permissions(administrator=True)
        async def sling_config(ctx, setting: str = None, value: str = None):
            """تنظیمات فلاخن داوود"""
            
            if setting is None:
                # نمایش تنظیمات فعلی
                embed = EmbedBuilder.create_embed(
                    title="⚙️ تنظیمات فلاخن داوود",
                    description="تنظیمات قابل تغییر سیستم",
                    color=EMBED_COLORS['info']
                )
                
                settings_list = [
                    ("sensitivity", f"{int(self.sensitivity_level * 100)}%", "حساسیت تشخیص (0-100)"),
                    ("raid_threshold", str(self.raid_threshold), "آستانه تشخیص Raid (تعداد کاربر)"),
                    ("raid_window", str(self.raid_time_window), "پنجره زمانی Raid (ثانیه)"),
                    ("auto_quarantine", "فعال" if self.auto_quarantine else "غیرفعال", "قرنطینه خودکار (true/false)"),
                    ("link_scanning", "فعال" if self.link_scanning_enabled else "غیرفعال", "اسکن لینک (true/false)")
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
                if setting.lower() == 'sensitivity':
                    new_sensitivity = max(0, min(100, int(value))) / 100
                    self.sensitivity_level = new_sensitivity
                    embed = EmbedBuilder.success_embed(
                        "تنظیم حساسیت",
                        f"حساسیت به {int(new_sensitivity * 100)}% تغییر کرد."
                    )
                    
                elif setting.lower() == 'raid_threshold':
                    new_threshold = max(2, min(20, int(value)))
                    self.raid_threshold = new_threshold
                    embed = EmbedBuilder.success_embed(
                        "تنظیم آستانه Raid",
                        f"آستانه تشخیص Raid به {new_threshold} کاربر تغییر کرد."
                    )
                    
                elif setting.lower() == 'raid_window':
                    new_window = max(10, min(300, int(value)))
                    self.raid_time_window = new_window
                    embed = EmbedBuilder.success_embed(
                        "تنظیم پنجره زمانی",
                        f"پنجره زمانی Raid به {new_window} ثانیه تغییر کرد."
                    )
                    
                elif setting.lower() == 'auto_quarantine':
                    new_auto = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.auto_quarantine = new_auto
                    embed = EmbedBuilder.success_embed(
                        "تنظیم قرنطینه خودکار",
                        f"قرنطینه خودکار {'فعال' if new_auto else 'غیرفعال'} شد."
                    )
                    
                elif setting.lower() == 'link_scanning':
                    new_scanning = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.link_scanning_enabled = new_scanning
                    embed = EmbedBuilder.success_embed(
                        "تنظیم اسکن لینک",
                        f"اسکن لینک {'فعال' if new_scanning else 'غیرفعال'} شد."
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
    
    def start_background_tasks(self):
        """شروع وظایف پس‌زمینه"""
        
        @tasks.loop(minutes=1)
        async def check_quarantine_status():
            """بررسی وضعیت قرنطینه"""
            if self.quarantine_active:
                # بررسی انقضای قرنطینه
                if hasattr(self, 'quarantine_end_time') and datetime.now() >= self.quarantine_end_time:
                    guild = await self.get_main_guild()
                    if guild:
                        await self.deactivate_quarantine(guild)
        
        @tasks.loop(minutes=1)
        async def check_mention_status():
            """بررسی وضعیت منشن"""
            if self.mention_disabled_until and datetime.now() >= self.mention_disabled_until:
                self.mention_disabled_until = None
                guild = await self.get_main_guild()
                if guild:
                    await self.enable_mentions_for_all(guild)
        
        @tasks.loop(minutes=5)
        async def analyze_join_patterns():
            """تحلیل الگوهای ورود برای تشخیص Raid"""
            current_time = time.time()
            recent_joins_count = len([
                join for join in self.recent_joins 
                if current_time - join['timestamp'] <= self.raid_time_window
            ])
            
            if recent_joins_count >= self.raid_threshold:
                guild = await self.get_main_guild()
                if guild and self.auto_quarantine and not self.quarantine_active:
                    await self.handle_potential_raid(guild, recent_joins_count)
        
        @tasks.loop(hours=24)
        async def daily_cleanup():
            """تمیزکاری روزانه"""
            # پاک کردن داده‌های قدیمی
            current_time = time.time()
            
            # پاک کردن ورودهای قدیمی
            while self.recent_joins and current_time - self.recent_joins[0]['timestamp'] > 86400:  # 24 ساعت
                self.recent_joins.popleft()
            
            # پاک کردن تاریخچه منشن قدیمی
            for user_id in list(self.mention_history.keys()):
                history = self.mention_history[user_id]
                while history and current_time - history[0]['timestamp'] > 86400:
                    history.popleft()
                if not history:
                    del self.mention_history[user_id]
            
            # بازنشانی آمار روزانه
            self.intercepted_today = 0
        
        @tasks.loop(hours=6)
        async def missile_resupply_check():
            """بررسی نیاز به تأمین موشک"""
            if self.missile_count < DefenseConfig.MISSILE_INVENTORY['david_sling']['max'] * 0.3:
                guild = await self.get_main_guild()
                if guild:
                    await self.request_missile_resupply(guild)
        
        # شروع تسک‌ها
        check_quarantine_status.start()
        check_mention_status.start()
        analyze_join_patterns.start()
        daily_cleanup.start()
        missile_resupply_check.start()
    
    async def on_member_join(self, member: discord.Member):
        """پردازش ورود کاربر جدید"""
        current_time = time.time()
        
        # ثبت ورود
        join_info = {
            'user_id': member.id,
            'timestamp': current_time,
            'account_age': (datetime.now() - member.created_at).days,
            'avatar': member.avatar is not None,
            'username_suspicious': self.is_username_suspicious(member.name)
        }
        
        # محاسبه امتیاز مشکوک بودن
        suspicion_score = self.calculate_suspicion_score(join_info)
        join_info['suspicion_score'] = suspicion_score
        
        self.recent_joins.append(join_info)
        
        # اگر کاربر مشکوک است
        if suspicion_score > 0.7:
            self.suspicious_users.add(member.id)
            join_info['action'] = 'marked_suspicious'
            
            # گزارش به کانال جنگ
            await self.report_suspicious_join(member, suspicion_score)
        
        # اگر قرنطینه فعال است
        if self.quarantine_active:
            await self.handle_quarantine_join(member)
        
        # بررسی Raid
        recent_count = len([
            join for join in self.recent_joins 
            if current_time - join['timestamp'] <= self.raid_time_window
        ])
        
        if recent_count >= self.raid_threshold and not self.quarantine_active:
            if self.auto_quarantine:
                await self.handle_potential_raid(member.guild, recent_count)
    
    async def on_message(self, message):
        """پردازش پیام‌های دریافتی"""
        if message.author.bot:
            return
        
        # بررسی منشن اسپم
        if message.mentions or '@everyone' in message.content or '@here' in message.content:
            await self.check_mention_spam(message)
        
        # بررسی لینک‌های مخرب
        if self.link_scanning_enabled and ('http' in message.content or 'www.' in message.content):
            await self.check_malicious_links(message)
        
        # پردازش کامندها
        await self.process_commands(message)
    
    def calculate_suspicion_score(self, join_info: Dict) -> float:
        """محاسبه امتیاز مشکوک بودن کاربر"""
        score = 0.0
        
        # سن اکانت
        account_age = join_info['account_age']
        if account_age < 1:
            score += 0.5
        elif account_age < 7:
            score += 0.3
        elif account_age < 30:
            score += 0.1
        
        # عدم داشتن آواتار
        if not join_info['avatar']:
            score += 0.2
        
        # نام کاربری مشکوک
        if join_info['username_suspicious']:
            score += 0.3
        
        # الگوی زمانی ورود (اگر همزمان با دیگران)
        current_time = join_info['timestamp']
        similar_time_joins = len([
            join for join in self.recent_joins 
            if abs(current_time - join['timestamp']) <= 10  # 10 ثانیه
        ])
        
        if similar_time_joins >= 3:
            score += 0.4
        
        return min(1.0, score)
    
    def is_username_suspicious(self, username: str) -> bool:
        """بررسی مشکوک بودن نام کاربری"""
        suspicious_patterns = [
            r'^\w+\d{4,}$',  # نام + اعداد زیاد
            r'^[a-z]+[A-Z]+[a-z]+$',  # الگوی عجیب حروف
            r'(.)\1{3,}',  # تکرار کاراکتر
            r'discord|bot|spam|raid',  # کلمات مشکوک
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, username, re.IGNORECASE):
                return True
        
        return False
    
    async def check_mention_spam(self, message: discord.Message):
        """بررسی اسپم منشن"""
        user_id = message.author.id
        current_time = time.time()
        
        # اضافه کردن به تاریخچه
        mention_count = len(message.mentions) + message.content.count('@everyone') + message.content.count('@here')
        
        if mention_count > 0:
            self.mention_history[user_id].append({
                'timestamp': current_time,
                'mention_count': mention_count,
                'channel_id': message.channel.id
            })
        
        # بررسی اسپم
        recent_mentions = [
            entry for entry in self.mention_history[user_id]
            if current_time - entry['timestamp'] <= 60  # 1 دقیقه
        ]
        
        total_mentions = sum(entry['mention_count'] for entry in recent_mentions)
        
        # اگر بیش از 5 منشن در دقیقه
        if total_mentions > 5:
            await self.handle_mention_spam(message, total_mentions)
    
    async def check_malicious_links(self, message: discord.Message):
        """بررسی لینک‌های مخرب"""
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
        
        for url in urls:
            scan_result = await self.scan_url(url)
            
            if scan_result['malicious']:
                await self.handle_malicious_link(message, url, scan_result)
    
    async def scan_url(self, url: str) -> Dict:
        """اسکن URL برای تشخیص خطر"""
        domain = self.extract_domain(url)
        
        # بررسی کش
        if url in self.scanned_links:
            return self.scanned_links[url]
        
        result = {
            'malicious': False,
            'risk_score': 0.0,
            'reason': 'امن'
        }
        
        # بررسی لیست سفید
        if domain in self.link_whitelist:
            result['reason'] = 'در لیست سفید'
            self.scanned_links[url] = result
            return result
        
        # بررسی لیست سیاه
        if domain in self.malicious_domains:
            result['malicious'] = True
            result['risk_score'] = 1.0
            result['reason'] = 'در لیست سیاه'
            self.scanned_links[url] = result
            return result
        
        # بررسی‌های اضافی
        risk_score = 0.0
        reasons = []
        
        # بررسی URL shortener
        shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'short.link']
        if any(shortener in domain for shortener in shorteners):
            risk_score += 0.4
            reasons.append('URL کوتاه شده')
        
        # بررسی دامنه‌های مشکوک
        suspicious_keywords = ['discord', 'free', 'hack', 'cheat', 'bot', 'spam']
        if any(keyword in domain.lower() for keyword in suspicious_keywords):
            risk_score += 0.3
            reasons.append('دامنه مشکوک')
        
        # بررسی IP به جای دامنه
        if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
            risk_score += 0.5
            reasons.append('استفاده از IP')
        
        result['risk_score'] = min(1.0, risk_score)
        result['malicious'] = risk_score > 0.6
        result['reason'] = ', '.join(reasons) if reasons else 'امن'
        
        # ذخیره در کش
        self.scanned_links[url] = result
        
        return result
    
    def extract_domain(self, url: str) -> str:
        """استخراج دامنه از URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return url.lower()
    
    async def handle_mention_spam(self, message: discord.Message, mention_count: int):
        """مدیریت اسپم منشن"""
        if self.missile_count <= 0:
            return
        
        # حذف پیام
        try:
            await message.delete()
        except:
            pass
        
        # کاهش موشک
        self.missile_count -= 1
        self.intercepted_today += 1
        self.total_intercepted += 1
        self.performance_stats['mention_spam_blocked'] += 1
        
        # ارسال هشدار
        embed = EmbedBuilder.create_embed(
            title="🚀 فلاخن داوود - رهگیری اسپم منشن",
            description=f"**🎯 هدف منهدم شد**\n"
                       f"👤 کاربر: {message.author.mention}\n"
                       f"📊 تعداد منشن: {mention_count}\n"
                       f"⚡ اقدام: حذف پیام و هشدار",
            color=EMBED_COLORS['warning']
        )
        
        temp_message = await message.channel.send(embed=embed)
        
        # حذف پیام پس از 10 ثانیه
        await asyncio.sleep(10)
        try:
            await temp_message.delete()
        except:
            pass
        
        # اگر اسپم زیاد بود، منشن را غیرفعال کن
        if mention_count > 10 and self.auto_mention_disable:
            await self.disable_mentions_temporarily(message.guild, 5)  # 5 دقیقه
    
    async def handle_malicious_link(self, message: discord.Message, url: str, scan_result: Dict):
        """مدیریت لینک مخرب"""
        if self.missile_count <= 0:
            return
        
        # حذف پیام
        try:
            await message.delete()
        except:
            pass
        
        # کاهش موشک
        self.missile_count -= 1
        self.intercepted_today += 1
        self.total_intercepted += 1
        self.performance_stats['malicious_links_blocked'] += 1
        
        # ارسال هشدار
        embed = EmbedBuilder.create_embed(
            title="🚀 فلاخن داوود - رهگیری لینک مخرب",
            description=f"**🎯 لینک مخرب منهدم شد**\n"
                       f"👤 کاربر: {message.author.mention}\n"
                       f"🔗 URL: `{url[:50]}...`\n"
                       f"📊 امتیاز خطر: {scan_result['risk_score']:.2f}\n"
                       f"🔍 دلیل: {scan_result['reason']}",
            color=EMBED_COLORS['error']
        )
        
        temp_message = await message.channel.send(embed=embed)
        
        # گزارش به کانال جنگ
        await self.report_malicious_link(message, url, scan_result)
        
        # حذف پیام پس از 15 ثانیه
        await asyncio.sleep(15)
        try:
            await temp_message.delete()
        except:
            pass
    
    async def handle_potential_raid(self, guild: discord.Guild, join_count: int):
        """مدیریت Raid احتمالی"""
        if self.quarantine_active:
            return
        
        # فعال‌سازی قرنطینه
        await self.activate_quarantine(guild, 30)  # 30 دقیقه
        
        self.performance_stats['raids_detected'] += 1
        self.performance_stats['raids_blocked'] += 1
        
        # گزارش
        embed = EmbedBuilder.create_embed(
            title="🚨 تشخیص Raid - فلاخن داوود",
            description=f"**حمله جمعی تشخیص داده شد**",
            color=EMBED_COLORS['error']
        )
        
        embed.add_field(
            name="📊 جزئیات حمله",
            value=f"👥 تعداد ورود: **{join_count}**\n"
                  f"⏰ بازه زمانی: **{self.raid_time_window}** ثانیه\n"
                  f"🎯 آستانه: **{self.raid_threshold}** کاربر\n"
                  f"🚨 سطح تهدید: **بالا**",
            inline=True
        )
        
        embed.add_field(
            name="⚡ اقدامات انجام شده",
            value="🏰 قرنطینه فعال شد\n"
                  "🚫 ورود کاربران جدید مسدود\n"
                  "👮 مدیران مطلع شدند\n"
                  "📊 گزارش ثبت شد",
            inline=True
        )
        
        # ارسال به کانال‌های مربوطه
        channels = ['war-room', 'defense-alerts', 'government-announcements']
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(embed=embed)
    
    async def activate_quarantine(self, guild: discord.Guild, duration_minutes: int):
        """فعال‌سازی قرنطینه"""
        self.quarantine_active = True
        self.quarantine_start_time = datetime.now()
        self.quarantine_end_time = self.quarantine_start_time + timedelta(minutes=duration_minutes)
        
        # غیرفعال کردن دعوت‌ها
        try:
            invites = await guild.invites()
            for invite in invites:
                await invite.delete()
        except:
            pass
        
        # محدود کردن مجوزهای کاربران جدید
        everyone_role = guild.default_role
        await everyone_role.edit(permissions=discord.Permissions(send_messages=False, add_reactions=False))
    
    async def deactivate_quarantine(self, guild: discord.Guild):
        """غیرفعال‌سازی قرنطینه"""
        self.quarantine_active = False
        self.quarantine_start_time = None
        
        # بازگرداندن مجوزهای عادی
        everyone_role = guild.default_role
        await everyone_role.edit(permissions=discord.Permissions(send_messages=True, add_reactions=True))
        
        # اعلام پایان قرنطینه
        embed = EmbedBuilder.success_embed(
            "پایان قرنطینه",
            "قرنطینه سرور پایان یافت. فعالیت عادی از سر گرفته شد."
        )
        
        general_channel = discord.utils.get(guild.text_channels, name='general-chat')
        if general_channel:
            await general_channel.send(embed=embed)
    
    async def extend_quarantine(self, additional_minutes: int):
        """تمدید قرنطینه"""
        if hasattr(self, 'quarantine_end_time'):
            self.quarantine_end_time += timedelta(minutes=additional_minutes)
    
    def get_quarantine_remaining_time(self) -> str:
        """دریافت زمان باقی‌مانده قرنطینه"""
        if not self.quarantine_active or not hasattr(self, 'quarantine_end_time'):
            return "0:00"
        
        remaining = self.quarantine_end_time - datetime.now()
        if remaining.total_seconds() <= 0:
            return "0:00"
        
        minutes = int(remaining.total_seconds() // 60)
        seconds = int(remaining.total_seconds() % 60)
        return f"{minutes}:{seconds:02d}"
    
    async def disable_mentions_for_all(self, guild: discord.Guild):
        """غیرفعال کردن منشن برای همه"""
        # این تابع پیچیده است و نیاز به تنظیم مجوزهای دقیق دارد
        # برای سادگی، فقط یک پیام اعلام می‌کنیم
        
        embed = EmbedBuilder.create_embed(
            title="🔇 منشن غیرفعال شد",
            description="به دلیل اسپم منشن، قابلیت منشن موقتاً غیرفعال شد.",
            color=EMBED_COLORS['warning']
        )
        
        general_channel = discord.utils.get(guild.text_channels, name='general-chat')
        if general_channel:
            await general_channel.send(embed=embed)
    
    async def enable_mentions_for_all(self, guild: discord.Guild):
        """فعال کردن منشن برای همه"""
        embed = EmbedBuilder.success_embed(
            "🔊 منشن فعال شد",
            "قابلیت منشن مجدداً فعال شد."
        )
        
        general_channel = discord.utils.get(guild.text_channels, name='general-chat')
        if general_channel:
            await general_channel.send(embed=embed)
    
    async def disable_mentions_temporarily(self, guild: discord.Guild, minutes: int):
        """غیرفعال کردن موقت منشن"""
        self.mention_disabled_until = datetime.now() + timedelta(minutes=minutes)
        await self.disable_mentions_for_all(guild)
    
    async def create_mention_stats_embed(self) -> discord.Embed:
        """ایجاد آمار تفصیلی منشن"""
        embed = EmbedBuilder.create_embed(
            title="📊 آمار تفصیلی منشن",
            description="تحلیل استفاده از منشن در سرور",
            color=EMBED_COLORS['info']
        )
        
        # محاسبه آمار
        total_mentions = sum(
            sum(entry['mention_count'] for entry in history)
            for history in self.mention_history.values()
        )
        
        active_users = len(self.mention_history)
        avg_mentions = total_mentions / active_users if active_users > 0 else 0
        
        embed.add_field(
            name="📈 آمار کلی",
            value=f"📊 کل منشن‌ها: **{format_number(total_mentions)}**\n"
                  f"👥 کاربران فعال: **{active_users}**\n"
                  f"📊 میانگین منشن: **{avg_mentions:.1f}**\n"
                  f"🚨 منشن‌های مسدود: **{self.performance_stats['mention_spam_blocked']}**",
            inline=True
        )
        
        # کاربران پرمنشن
        top_mentioners = sorted(
            [(user_id, sum(entry['mention_count'] for entry in history))
             for user_id, history in self.mention_history.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        if top_mentioners:
            top_text = []
            for i, (user_id, count) in enumerate(top_mentioners, 1):
                top_text.append(f"{i}. <@{user_id}>: **{count}** منشن")
            
            embed.add_field(
                name="🏆 کاربران پرمنشن",
                value="\n".join(top_text),
                inline=True
            )
        
        return embed
    
    async def report_suspicious_join(self, member: discord.Member, suspicion_score: float):
        """گزارش ورود مشکوک"""
        embed = EmbedBuilder.create_embed(
            title="⚠️ ورود مشکوک - فلاخن داوود",
            description=f"کاربر مشکوک شناسایی شد",
            color=EMBED_COLORS['warning']
        )
        
        embed.add_field(
            name="👤 اطلاعات کاربر",
            value=f"نام: {member.name}\n"
                  f"ID: {member.id}\n"
                  f"سن اکانت: {(datetime.now() - member.created_at).days} روز\n"
                  f"آواتار: {'دارد' if member.avatar else 'ندارد'}",
            inline=True
        )
        
        embed.add_field(
            name="📊 تحلیل",
            value=f"امتیاز مشکوک: **{suspicion_score:.2f}**\n"
                  f"سطح خطر: **{'بالا' if suspicion_score > 0.8 else 'متوسط'}**\n"
                  f"توصیه: {'نظارت دقیق' if suspicion_score > 0.8 else 'نظارت معمولی'}",
            inline=True
        )
        
        # ارسال به کانال جنگ
        guild = member.guild
        war_room = discord.utils.get(guild.text_channels, name='war-room')
        if war_room:
            await war_room.send(embed=embed)
    
    async def handle_quarantine_join(self, member: discord.Member):
        """مدیریت ورود در زمان قرنطینه"""
        # کیک کردن کاربر جدید
        try:
            await member.kick(reason="ورود در زمان قرنطینه")
            self.performance_stats['users_quarantined'] += 1
        except:
            pass
    
    async def report_malicious_link(self, message: discord.Message, url: str, scan_result: Dict):
        """گزارش لینک مخرب"""
        embed = EmbedBuilder.create_embed(
            title="🔗 لینک مخرب مسدود شد",
            description="فلاخن داوود لینک مخرب را شناسایی و مسدود کرد",
            color=EMBED_COLORS['error']
        )
        
        embed.add_field(
            name="🎯 جزئیات",
            value=f"👤 کاربر: {message.author.mention}\n"
                  f"📍 کانال: {message.channel.mention}\n"
                  f"🔗 URL: `{url[:100]}...`\n"
                  f"📊 امتیاز خطر: {scan_result['risk_score']:.2f}",
            inline=False
        )
        
        embed.add_field(
            name="🔍 دلیل مسدودسازی",
            value=scan_result['reason'],
            inline=False
        )
        
        # ارسال به کانال جنگ
        guild = message.guild
        war_room = discord.utils.get(guild.text_channels, name='war-room')
        if war_room:
            await war_room.send(embed=embed)
    
    async def request_missile_resupply(self, guild: discord.Guild):
        """درخواست تأمین موشک"""
        embed = EmbedBuilder.create_embed(
            title="🚨 درخواست تأمین موشک - فلاخن داوود",
            description="موجودی موشک به حد بحرانی رسیده است",
            color=EMBED_COLORS['error']
        )
        
        current_percentage = (self.missile_count / DefenseConfig.MISSILE_INVENTORY['david_sling']['max']) * 100
        needed_missiles = DefenseConfig.MISSILE_INVENTORY['david_sling']['max'] - self.missile_count
        total_cost = needed_missiles * DefenseConfig.MISSILE_INVENTORY['david_sling']['cost']
        
        embed.add_field(
            name="📊 وضعیت فعلی",
            value=f"🚀 موجودی: {format_number(self.missile_count)}\n"
                  f"📊 درصد: {current_percentage:.1f}%\n"
                  f"⚠️ وضعیت: بحرانی",
            inline=True
        )
        
        embed.add_field(
            name="💰 نیازمندی‌ها",
            value=f"🚀 موشک مورد نیاز: {format_number(needed_missiles)}\n"
                  f"💸 هزینه: {format_number(total_cost)} شکل\n"
                  f"⏰ زمان تحویل: 4-6 ساعت",
            inline=True
        )
        
        # ارسال به کانال‌های مربوطه
        channels = ['war-room', 'military-operations']
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(embed=embed)
    
    def calculate_system_accuracy(self) -> float:
        """محاسبه دقت سیستم"""
        total_actions = (self.performance_stats['raids_blocked'] + 
                        self.performance_stats['malicious_links_blocked'] + 
                        self.performance_stats['mention_spam_blocked'])
        
        if total_actions == 0:
            return 0.0
        
        false_positives = self.performance_stats['false_positives']
        accuracy = ((total_actions - false_positives) / total_actions) * 100
        
        return max(0.0, min(100.0, accuracy))
    
    def create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """ایجاد نوار پیشرفت"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"

# اجرای ربات
if __name__ == "__main__":
    bot = DavidSlingBot()
    
    try:
        bot.run(bot.token)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات فلاخن داوود: {e}")