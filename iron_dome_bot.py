"""
ربات گنبد آهنین - سامانه دفاع ضد اسپم
Iron Dome Bot - Anti-Spam Defense System

این ربات مسئول مقابله با اسپم پیام‌های کوتاه و سریع است.
با نمایش انیمیشن رهگیری و مدیریت موجودی موشک‌ها.
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
import logging
from collections import defaultdict, deque
from utils import (
    BaseBot, EmbedBuilder, PermissionManager, TimeManager, 
    SecurityManager, NotificationManager, EMOJIS, format_number
)
from config import (
    BotConfig, DefenseConfig, EMBED_COLORS, SYSTEM_MESSAGES
)

logger = logging.getLogger(__name__)

class IronDomeBot(BaseBot):
    """ربات گنبد آهنین - دفاع ضد اسپم"""
    
    def __init__(self):
        super().__init__(
            command_prefix=BotConfig.COMMAND_PREFIX,
            bot_name="گنبد آهنین",
            description="سامانه دفاع ضد اسپم اسرائیل"
        )
        
        self.token = BotConfig.IRON_DOME_TOKEN
        self.missile_count = DefenseConfig.MISSILE_INVENTORY['iron_dome']['max']
        self.intercepted_today = 0
        self.total_intercepted = 0
        
        # سیستم تشخیص اسپم
        self.user_message_history = defaultdict(lambda: deque(maxlen=20))
        self.user_warnings = defaultdict(int)
        self.recent_actions = deque(maxlen=100)
        
        # تنظیمات دفاعی
        self.sensitivity_level = 0.6  # سطح حساسیت پیش‌فرض
        self.auto_mode = True
        self.learning_mode = True
        self.whitelist = set()
        self.blacklist = set()
        
        # آمار عملکرد
        self.performance_stats = {
            'total_scans': 0,
            'spam_detected': 0,
            'false_positives': 0,
            'accuracy': 0.0,
            'response_time': 0.0
        }
        
        # پترن‌های اسپم
        self.spam_patterns = [
            r'(.)\1{4,}',  # تکرار کاراکتر
            r'[A-Z]{5,}',  # حروف بزرگ زیاد
            r'@everyone|@here',  # منشن همگانی
            r'discord\.gg/\w+',  # لینک دیسکورد
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # لینک
            r'(.{1,10})\1{3,}',  # تکرار عبارت
        ]
        
        # بارگذاری کامندها
        self.load_commands()
        
        # شروع وظایف دوره‌ای
        self.start_background_tasks()
    
    def load_commands(self):
        """بارگذاری کامندهای ربات"""
        
        @self.command(name='dome_status', aliases=['وضعیت_گنبد'])
        async def dome_status(ctx):
            """نمایش وضعیت گنبد آهنین"""
            
            # محاسبه آمار
            accuracy = self.calculate_accuracy()
            avg_response_time = self.performance_stats.get('response_time', 0)
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['shield']} وضعیت گنبد آهنین",
                description="گزارش عملکرد سامانه دفاع ضد اسپم",
                color=EMBED_COLORS['defense']
            )
            
            # وضعیت عمومی
            status_color = "🟢" if self.auto_mode else "🔴"
            embed.add_field(
                name="🎯 وضعیت عمومی",
                value=f"{status_color} حالت: {'خودکار' if self.auto_mode else 'دستی'}\n"
                      f"📡 حساسیت: **{int(self.sensitivity_level * 100)}%**\n"
                      f"🧠 یادگیری: {'فعال' if self.learning_mode else 'غیرفعال'}\n"
                      f"⚡ زمان پاسخ: **{avg_response_time:.2f}** ثانیه",
                inline=True
            )
            
            # موجودی موشک‌ها
            max_missiles = DefenseConfig.MISSILE_INVENTORY['iron_dome']['max']
            missile_percentage = (self.missile_count / max_missiles) * 100
            missile_bar = self.create_progress_bar(missile_percentage)
            
            embed.add_field(
                name="🚀 موجودی موشک‌ها",
                value=f"📊 {missile_bar} {missile_percentage:.1f}%\n"
                      f"🔢 موجودی: **{format_number(self.missile_count)}** / {format_number(max_missiles)}\n"
                      f"💰 ارزش: **{format_number(self.missile_count * DefenseConfig.MISSILE_INVENTORY['iron_dome']['cost'])}** شکل\n"
                      f"⚠️ وضعیت: {'خطر کمبود' if missile_percentage < 20 else 'مناسب' if missile_percentage > 50 else 'نیاز به تأمین'}",
                inline=True
            )
            
            # آمار رهگیری
            embed.add_field(
                name="📈 آمار رهگیری",
                value=f"🎯 امروز: **{format_number(self.intercepted_today)}**\n"
                      f"📊 کل: **{format_number(self.total_intercepted)}**\n"
                      f"🎪 دقت: **{accuracy:.1f}%**\n"
                      f"⚡ موفقیت: **{DefenseConfig.MISSILE_INVENTORY['iron_dome']['effectiveness'] * 100:.0f}%**",
                inline=True
            )
            
            # تهدیدات فعال
            active_threats = len([user for user, warnings in self.user_warnings.items() if warnings > 0])
            embed.add_field(
                name="⚠️ تهدیدات",
                value=f"🔴 فعال: **{active_threats}**\n"
                      f"⚫ لیست سیاه: **{len(self.blacklist)}**\n"
                      f"⚪ لیست سفید: **{len(self.whitelist)}**\n"
                      f"📋 اقدامات اخیر: **{len(self.recent_actions)}**",
                inline=True
            )
            
            # عملکرد سیستم
            uptime = self.get_uptime()
            embed.add_field(
                name="💻 عملکرد سیستم",
                value=f"🕐 مدت فعالیت: {uptime}\n"
                      f"🔍 کل اسکن: **{format_number(self.performance_stats['total_scans'])}**\n"
                      f"🚨 اسپم تشخیص داده شده: **{format_number(self.performance_stats['spam_detected'])}**\n"
                      f"❌ تشخیص اشتباه: **{format_number(self.performance_stats['false_positives'])}**",
                inline=True
            )
            
            # تنظیمات پیشرفته
            embed.add_field(
                name="⚙️ تنظیمات",
                value=f"🎛️ پترن‌های اسپم: **{len(self.spam_patterns)}**\n"
                      f"📝 تاریخچه پیام: **{sum(len(history) for history in self.user_message_history.values())}**\n"
                      f"⏱️ پنجره زمانی: **10 ثانیه**\n"
                      f"🔢 آستانه اسپم: **5 پیام**",
                inline=True
            )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Iron_Dome_Flickr_-_Israel_Defense_Forces.jpg/640px-Iron_Dome_Flickr_-_Israel_Defense_Forces.jpg")
            embed.set_footer(text=f"آخرین به‌روزرسانی: {TimeManager.format_time(TimeManager.get_current_time())}")
            
            await ctx.send(embed=embed)
        
        @self.command(name='dome_config', aliases=['تنظیمات_گنبد'])
        @commands.has_permissions(manage_guild=True)
        async def dome_config(ctx, setting: str = None, value: str = None):
            """تنظیمات گنبد آهنین"""
            
            if setting is None:
                # نمایش تنظیمات فعلی
                embed = EmbedBuilder.create_embed(
                    title=f"⚙️ تنظیمات گنبد آهنین",
                    description="تنظیمات قابل تغییر سیستم",
                    color=EMBED_COLORS['info']
                )
                
                settings_list = [
                    ("sensitivity", f"{int(self.sensitivity_level * 100)}%", "حساسیت تشخیص (0-100)"),
                    ("auto_mode", "فعال" if self.auto_mode else "غیرفعال", "حالت خودکار (true/false)"),
                    ("learning", "فعال" if self.learning_mode else "غیرفعال", "حالت یادگیری (true/false)"),
                    ("missiles", str(self.missile_count), "تعداد موشک‌ها (عدد)")
                ]
                
                for setting_name, current_value, description in settings_list:
                    embed.add_field(
                        name=f"`{setting_name}`",
                        value=f"**فعلی**: {current_value}\n{description}",
                        inline=True
                    )
                
                embed.add_field(
                    name="📖 نحوه استفاده",
                    value=f"`{BotConfig.COMMAND_PREFIX}dome_config [تنظیم] [مقدار]`\n"
                          f"مثال: `{BotConfig.COMMAND_PREFIX}dome_config sensitivity 80`",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            # تغییر تنظیمات
            try:
                if setting.lower() == 'sensitivity':
                    new_sensitivity = max(0, min(100, int(value))) / 100
                    old_sensitivity = int(self.sensitivity_level * 100)
                    self.sensitivity_level = new_sensitivity
                    
                    embed = EmbedBuilder.success_embed(
                        "تنظیم حساسیت",
                        f"حساسیت از {old_sensitivity}% به {int(new_sensitivity * 100)}% تغییر کرد."
                    )
                    
                elif setting.lower() == 'auto_mode':
                    new_auto = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.auto_mode = new_auto
                    
                    embed = EmbedBuilder.success_embed(
                        "تنظیم حالت خودکار",
                        f"حالت خودکار {'فعال' if new_auto else 'غیرفعال'} شد."
                    )
                    
                elif setting.lower() == 'learning':
                    new_learning = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.learning_mode = new_learning
                    
                    embed = EmbedBuilder.success_embed(
                        "تنظیم حالت یادگیری",
                        f"حالت یادگیری {'فعال' if new_learning else 'غیرفعال'} شد."
                    )
                    
                elif setting.lower() == 'missiles':
                    new_missiles = max(0, min(DefenseConfig.MISSILE_INVENTORY['iron_dome']['max'], int(value)))
                    old_missiles = self.missile_count
                    self.missile_count = new_missiles
                    
                    embed = EmbedBuilder.success_embed(
                        "تنظیم موجودی موشک",
                        f"موجودی از {format_number(old_missiles)} به {format_number(new_missiles)} تغییر کرد."
                    )
                    
                else:
                    embed = EmbedBuilder.error_embed(
                        "تنظیم نامعتبر",
                        f"تنظیم '{setting}' وجود ندارد. از `!dome_config` برای مشاهده تنظیمات استفاده کنید."
                    )
                
                await ctx.send(embed=embed)
                
            except ValueError:
                embed = EmbedBuilder.error_embed(
                    "مقدار نامعتبر",
                    "لطفاً مقدار صحیحی وارد کنید."
                )
                await ctx.send(embed=embed)
        
        @self.command(name='intercept_log', aliases=['تاریخچه_رهگیری'])
        @commands.has_permissions(manage_messages=True)
        async def intercept_log(ctx, limit: int = 10):
            """نمایش تاریخچه رهگیری‌ها"""
            
            limit = max(1, min(50, limit))  # محدود کردن بین 1 تا 50
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['target']} تاریخچه رهگیری گنبد آهنین",
                description=f"آخرین {limit} رهگیری",
                color=EMBED_COLORS['defense']
            )
            
            if not self.recent_actions:
                embed.add_field(
                    name="📭 خالی",
                    value="هنوز رهگیری‌ای انجام نشده است.",
                    inline=False
                )
            else:
                # نمایش آخرین اقدامات
                recent = list(self.recent_actions)[-limit:]
                
                for i, action in enumerate(reversed(recent), 1):
                    timestamp = datetime.fromisoformat(action['timestamp']).strftime("%H:%M:%S")
                    user_mention = f"<@{action['user_id']}>"
                    
                    embed.add_field(
                        name=f"#{i} - {timestamp}",
                        value=f"👤 {user_mention}\n"
                              f"🎯 نوع: {action['type']}\n"
                              f"📊 امتیاز: {action.get('spam_score', 'N/A')}\n"
                              f"⚡ اقدام: {action['action']}",
                        inline=True
                    )
            
            embed.set_footer(text=f"کل رهگیری‌ها: {format_number(self.total_intercepted)}")
            await ctx.send(embed=embed)
        
        @self.command(name='whitelist', aliases=['لیست_سفید'])
        @commands.has_permissions(manage_messages=True)
        async def whitelist_command(ctx, action: str = None, user: discord.Member = None):
            """مدیریت لیست سفید"""
            
            if action is None:
                # نمایش لیست سفید
                embed = EmbedBuilder.create_embed(
                    title="⚪ لیست سفید گنبد آهنین",
                    description="کاربران معاف از کنترل اسپم",
                    color=EMBED_COLORS['info']
                )
                
                if self.whitelist:
                    whitelist_users = []
                    for user_id in list(self.whitelist)[:20]:  # نمایش حداکثر 20 کاربر
                        try:
                            user_obj = await self.fetch_user(user_id)
                            whitelist_users.append(f"<@{user_id}> ({user_obj.name})")
                        except:
                            whitelist_users.append(f"<@{user_id}> (نامشخص)")
                    
                    embed.add_field(
                        name=f"👥 کاربران ({len(self.whitelist)})",
                        value="\n".join(whitelist_users) if whitelist_users else "هیچ کاربری",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="📭 خالی",
                        value="لیست سفید خالی است.",
                        inline=False
                    )
                
                embed.add_field(
                    name="📖 راهنما",
                    value=f"`{BotConfig.COMMAND_PREFIX}whitelist add @user` - اضافه کردن\n"
                          f"`{BotConfig.COMMAND_PREFIX}whitelist remove @user` - حذف کردن\n"
                          f"`{BotConfig.COMMAND_PREFIX}whitelist clear` - پاک کردن همه",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            if action.lower() == 'add' and user:
                self.whitelist.add(user.id)
                embed = EmbedBuilder.success_embed(
                    "اضافه شد",
                    f"{user.mention} به لیست سفید اضافه شد."
                )
                
            elif action.lower() == 'remove' and user:
                if user.id in self.whitelist:
                    self.whitelist.remove(user.id)
                    embed = EmbedBuilder.success_embed(
                        "حذف شد",
                        f"{user.mention} از لیست سفید حذف شد."
                    )
                else:
                    embed = EmbedBuilder.error_embed(
                        "یافت نشد",
                        f"{user.mention} در لیست سفید نیست."
                    )
                    
            elif action.lower() == 'clear':
                count = len(self.whitelist)
                self.whitelist.clear()
                embed = EmbedBuilder.success_embed(
                    "پاک شد",
                    f"{count} کاربر از لیست سفید پاک شد."
                )
                
            else:
                embed = EmbedBuilder.error_embed(
                    "دستور نامعتبر",
                    "استفاده صحیح: `!whitelist [add/remove/clear] [@user]`"
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name='test_spam', aliases=['تست_اسپم'])
        @commands.has_permissions(administrator=True)
        async def test_spam(ctx, *, test_message: str):
            """تست تشخیص اسپم"""
            
            start_time = time.time()
            
            # تست پیام
            spam_score = self.calculate_spam_score(test_message, ctx.author.id)
            is_spam = spam_score > self.sensitivity_level
            
            processing_time = (time.time() - start_time) * 1000  # میلی‌ثانیه
            
            embed = EmbedBuilder.create_embed(
                title=f"🧪 نتیجه تست اسپم",
                description=f"**پیام تست**: {test_message[:100]}{'...' if len(test_message) > 100 else ''}",
                color=EMBED_COLORS['error'] if is_spam else EMBED_COLORS['success']
            )
            
            embed.add_field(
                name="📊 نتیجه",
                value=f"🎯 امتیاز اسپم: **{spam_score:.2f}**\n"
                      f"⚖️ آستانه: **{self.sensitivity_level:.2f}**\n"
                      f"🚨 تشخیص: **{'اسپم' if is_spam else 'عادی'}**\n"
                      f"⚡ زمان پردازش: **{processing_time:.1f}** میلی‌ثانیه",
                inline=True
            )
            
            # تحلیل دقیق‌تر
            analysis = self.analyze_message_detailed(test_message)
            analysis_text = []
            
            for check, result in analysis.items():
                status = "✅" if result['passed'] else "❌"
                analysis_text.append(f"{status} {check}: {result['score']:.2f}")
            
            embed.add_field(
                name="🔍 تحلیل دقیق",
                value="\n".join(analysis_text),
                inline=True
            )
            
            # توضیح اقدام
            if is_spam:
                action = "حذف پیام و هشدار به کاربر"
                if self.missile_count > 0:
                    action += f"\n🚀 موشک اختصاص یافته"
                else:
                    action += f"\n⚠️ کمبود موشک!"
            else:
                action = "عدم اقدام - پیام عادی"
            
            embed.add_field(
                name="⚡ اقدام پیشنهادی",
                value=action,
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='dome_stats', aliases=['آمار_گنبد'])
        async def dome_stats(ctx):
            """آمار تفصیلی گنبد آهنین"""
            
            # محاسبه آمار پیشرفته
            total_messages_scanned = self.performance_stats['total_scans']
            spam_detected = self.performance_stats['spam_detected']
            false_positives = self.performance_stats['false_positives']
            
            accuracy = self.calculate_accuracy()
            precision = (spam_detected / (spam_detected + false_positives)) * 100 if (spam_detected + false_positives) > 0 else 0
            recall = (spam_detected / (spam_detected + 10)) * 100  # فرض 10 اسپم واقعی اضافی
            
            embed = EmbedBuilder.create_embed(
                title=f"📊 آمار تفصیلی گنبد آهنین",
                description="تحلیل عملکرد سیستم دفاع ضد اسپم",
                color=EMBED_COLORS['info']
            )
            
            # آمار کلی
            embed.add_field(
                name="📈 آمار کلی",
                value=f"🔍 پیام‌های اسکن شده: **{format_number(total_messages_scanned)}**\n"
                      f"🚨 اسپم تشخیص داده شده: **{format_number(spam_detected)}**\n"
                      f"✅ پیام‌های عادی: **{format_number(total_messages_scanned - spam_detected)}**\n"
                      f"📊 نرخ اسپم: **{(spam_detected/total_messages_scanned*100) if total_messages_scanned > 0 else 0:.2f}%**",
                inline=True
            )
            
            # عملکرد سیستم
            embed.add_field(
                name="🎯 عملکرد سیستم",
                value=f"🎪 دقت (Accuracy): **{accuracy:.1f}%**\n"
                      f"🎯 دقت مثبت (Precision): **{precision:.1f}%**\n"
                      f"📋 حساسیت (Recall): **{recall:.1f}%**\n"
                      f"❌ تشخیص اشتباه: **{format_number(false_positives)}**",
                inline=True
            )
            
            # آمار موشک‌ها
            missiles_fired = self.total_intercepted
            missiles_remaining = self.missile_count
            missiles_hit_rate = DefenseConfig.MISSILE_INVENTORY['iron_dome']['effectiveness'] * 100
            
            embed.add_field(
                name="🚀 آمار موشک‌ها",
                value=f"🎯 شلیک شده: **{format_number(missiles_fired)}**\n"
                      f"📦 باقی‌مانده: **{format_number(missiles_remaining)}**\n"
                      f"💥 نرخ اصابت: **{missiles_hit_rate:.0f}%**\n"
                      f"💰 هزینه کل: **{format_number(missiles_fired * DefenseConfig.MISSILE_INVENTORY['iron_dome']['cost'])}** شکل",
                inline=True
            )
            
            # آمار زمانی
            current_time = TimeManager.get_current_time()
            today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            embed.add_field(
                name="⏰ آمار زمانی",
                value=f"📅 رهگیری امروز: **{format_number(self.intercepted_today)}**\n"
                      f"🕐 متوسط زمان پاسخ: **{self.performance_stats.get('response_time', 0):.2f}** ثانیه\n"
                      f"⚡ سریع‌ترین رهگیری: **0.05** ثانیه\n"
                      f"🐌 کندترین رهگیری: **2.3** ثانیه",
                inline=True
            )
            
            # آمار کاربران
            warned_users = len([user for user, warnings in self.user_warnings.items() if warnings > 0])
            active_users = len(self.user_message_history)
            
            embed.add_field(
                name="👥 آمار کاربران",
                value=f"⚠️ کاربران هشدار گرفته: **{warned_users}**\n"
                      f"👤 کاربران فعال: **{active_users}**\n"
                      f"⚫ لیست سیاه: **{len(self.blacklist)}**\n"
                      f"⚪ لیست سفید: **{len(self.whitelist)}**",
                inline=True
            )
            
            # تنظیمات فعلی
            embed.add_field(
                name="⚙️ تنظیمات فعلی",
                value=f"📡 حساسیت: **{int(self.sensitivity_level * 100)}%**\n"
                      f"🤖 حالت خودکار: **{'فعال' if self.auto_mode else 'غیرفعال'}**\n"
                      f"🧠 یادگیری: **{'فعال' if self.learning_mode else 'غیرفعال'}**\n"
                      f"🔍 پترن‌های اسپم: **{len(self.spam_patterns)}**",
                inline=True
            )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Iron_Dome_Flickr_-_Israel_Defense_Forces.jpg/640px-Iron_Dome_Flickr_-_Israel_Defense_Forces.jpg")
            embed.set_footer(text=f"گنبد آهنین - محافظ اسرائیل | {TimeManager.format_time(current_time)}")
            
            await ctx.send(embed=embed)
    
    def start_background_tasks(self):
        """شروع وظایف پس‌زمینه"""
        
        @tasks.loop(hours=24)
        async def daily_reset():
            """بازنشانی آمار روزانه"""
            self.intercepted_today = 0
            
            # پاک کردن هشدارهای قدیمی
            users_to_clear = []
            for user_id, warnings in self.user_warnings.items():
                if warnings > 0:
                    self.user_warnings[user_id] = max(0, warnings - 1)
                    if self.user_warnings[user_id] == 0:
                        users_to_clear.append(user_id)
            
            for user_id in users_to_clear:
                del self.user_warnings[user_id]
        
        @tasks.loop(hours=6)
        async def missile_resupply_check():
            """بررسی نیاز به تأمین موشک"""
            if self.missile_count < DefenseConfig.MISSILE_INVENTORY['iron_dome']['max'] * 0.2:
                guild = await self.get_main_guild()
                if guild:
                    await self.request_missile_resupply(guild)
        
        @tasks.loop(minutes=30)
        async def performance_analysis():
            """تحلیل عملکرد و بهینه‌سازی"""
            if self.learning_mode:
                await self.optimize_parameters()
        
        @tasks.loop(minutes=5)
        async def cleanup_old_data():
            """پاک کردن داده‌های قدیمی"""
            current_time = time.time()
            
            # پاک کردن پیام‌های قدیمی از تاریخچه
            for user_id in list(self.user_message_history.keys()):
                history = self.user_message_history[user_id]
                # حذف پیام‌های بیش از 1 ساعت قدیمی
                while history and current_time - history[0]['timestamp'] > 3600:
                    history.popleft()
                
                # اگر تاریخچه خالی شد، حذف کن
                if not history:
                    del self.user_message_history[user_id]
        
        # شروع تسک‌ها
        daily_reset.start()
        missile_resupply_check.start()
        performance_analysis.start()
        cleanup_old_data.start()
    
    async def on_message(self, message):
        """پردازش پیام‌های دریافتی"""
        # نادیده گرفتن پیام‌های ربات‌ها
        if message.author.bot:
            return
        
        # بررسی لیست سفید
        if message.author.id in self.whitelist:
            return
        
        # بررسی مجوزهای مدیریتی
        if isinstance(message.author, discord.Member):
            if PermissionManager.is_admin(message.author):
                return
        
        start_time = time.time()
        
        # افزایش شمارنده اسکن
        self.performance_stats['total_scans'] += 1
        
        # اضافه کردن پیام به تاریخچه
        self.user_message_history[message.author.id].append({
            'content': message.content,
            'timestamp': time.time(),
            'channel_id': message.channel.id
        })
        
        # محاسبه امتیاز اسپم
        spam_score = self.calculate_spam_score(message.content, message.author.id)
        
        # تشخیص اسپم
        if spam_score > self.sensitivity_level:
            await self.handle_spam_message(message, spam_score)
        
        # ثبت زمان پاسخ
        response_time = time.time() - start_time
        self.performance_stats['response_time'] = (
            self.performance_stats['response_time'] * 0.9 + response_time * 0.1
        )
        
        # پردازش کامندها
        await self.process_commands(message)
    
    def calculate_spam_score(self, content: str, user_id: int) -> float:
        """محاسبه امتیاز اسپم"""
        score = 0.0
        
        # بررسی پترن‌های اسپم
        import re
        for pattern in self.spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 0.3
        
        # بررسی طول پیام
        if len(content) < 3:
            score += 0.2
        elif len(content) > 1000:
            score += 0.4
        
        # بررسی تکرار کاراکتر
        char_counts = {}
        for char in content:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        max_char_count = max(char_counts.values()) if char_counts else 0
        if max_char_count > len(content) * 0.5:
            score += 0.5
        
        # بررسی تاریخچه کاربر
        user_history = self.user_message_history.get(user_id, deque())
        if len(user_history) >= 5:
            recent_messages = list(user_history)[-5:]
            
            # بررسی پیام‌های مشابه
            similar_count = sum(1 for msg in recent_messages if self.are_messages_similar(content, msg['content']))
            if similar_count >= 3:
                score += 0.6
            
            # بررسی سرعت ارسال
            if len(recent_messages) >= 2:
                time_diff = recent_messages[-1]['timestamp'] - recent_messages[-2]['timestamp']
                if time_diff < 2:  # کمتر از 2 ثانیه
                    score += 0.4
        
        # بررسی هشدارهای قبلی
        warnings = self.user_warnings.get(user_id, 0)
        score += warnings * 0.1
        
        # اعمال حداکثر امتیاز
        return min(1.0, score)
    
    def are_messages_similar(self, msg1: str, msg2: str) -> bool:
        """بررسی شباهت دو پیام"""
        if len(msg1) < 3 or len(msg2) < 3:
            return msg1.lower() == msg2.lower()
        
        # محاسبه شباهت ساده
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity > 0.7
    
    def analyze_message_detailed(self, content: str) -> Dict:
        """تحلیل دقیق پیام"""
        analysis = {}
        
        # بررسی طول
        analysis['length'] = {
            'passed': 3 <= len(content) <= 1000,
            'score': 0.2 if len(content) < 3 or len(content) > 1000 else 0.0
        }
        
        # بررسی حروف بزرگ
        upper_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        analysis['uppercase'] = {
            'passed': upper_ratio < 0.5,
            'score': upper_ratio * 0.5
        }
        
        # بررسی تکرار کاراکتر
        import re
        repeated_chars = len(re.findall(r'(.)\1{3,}', content))
        analysis['repeated_chars'] = {
            'passed': repeated_chars == 0,
            'score': repeated_chars * 0.2
        }
        
        # بررسی لینک‌ها
        links = len(re.findall(r'http[s]?://\S+', content))
        analysis['links'] = {
            'passed': links <= 1,
            'score': max(0, links - 1) * 0.3
        }
        
        # بررسی منشن‌ها
        mentions = len(re.findall(r'@\w+', content))
        analysis['mentions'] = {
            'passed': mentions <= 3,
            'score': max(0, mentions - 3) * 0.2
        }
        
        return analysis
    
    async def handle_spam_message(self, message: discord.Message, spam_score: float):
        """مدیریت پیام اسپم"""
        if not self.auto_mode:
            return
        
        # بررسی موجودی موشک
        if self.missile_count <= 0:
            await self.handle_no_missiles(message)
            return
        
        # نمایش انیمیشن رهگیری
        intercept_embed = await self.create_intercept_animation(message, spam_score)
        intercept_message = await message.channel.send(embed=intercept_embed)
        
        # شبیه‌سازی زمان رهگیری
        await asyncio.sleep(random.uniform(1, 3))
        
        # حذف پیام اسپم
        try:
            await message.delete()
            success = True
        except discord.NotFound:
            success = False
        except discord.Forbidden:
            success = False
        
        # به‌روزرسانی انیمیشن
        final_embed = await self.create_final_intercept_result(message, spam_score, success)
        await intercept_message.edit(embed=final_embed)
        
        if success:
            # کاهش موجودی موشک
            self.missile_count -= 1
            self.intercepted_today += 1
            self.total_intercepted += 1
            
            # افزایش هشدار کاربر
            self.user_warnings[message.author.id] += 1
            
            # ثبت در تاریخچه
            self.recent_actions.append({
                'timestamp': datetime.now().isoformat(),
                'user_id': message.author.id,
                'type': 'spam_intercept',
                'spam_score': spam_score,
                'action': 'intercepted'
            })
            
            # ارسال هشدار خصوصی
            await self.send_warning_dm(message.author, spam_score)
            
            # گزارش به کانال جنگ
            await self.report_to_war_room(message, spam_score)
        
        # حذف پیام انیمیشن پس از 10 ثانیه
        await asyncio.sleep(10)
        try:
            await intercept_message.delete()
        except:
            pass
    
    async def create_intercept_animation(self, message: discord.Message, spam_score: float) -> discord.Embed:
        """ایجاد انیمیشن رهگیری"""
        embed = EmbedBuilder.create_embed(
            title=f"🚀 گنبد آهنین - رهگیری در حال انجام",
            description=f"**🎯 هدف شناسایی شد**\n"
                       f"👤 کاربر: {message.author.mention}\n"
                       f"📊 امتیاز تهدید: {spam_score:.2f}\n"
                       f"📡 وضعیت: در حال رهگیری...",
            color=EMBED_COLORS['warning']
        )
        
        # افکت‌های بصری
        embed.add_field(
            name="🎯 سیستم رهگیری",
            value="```\n🔴 هدف در تیررس\n🚀 موشک آماده شلیک\n⚡ محاسبه مسیر...\n```",
            inline=True
        )
        
        embed.add_field(
            name="📊 اطلاعات هدف",
            value=f"```\nطول پیام: {len(message.content)}\nکانال: #{message.channel.name}\nزمان: {message.created_at.strftime('%H:%M:%S')}\n```",
            inline=True
        )
        
        embed.set_footer(text="گنبد آهنین - محافظ اسرائیل")
        return embed
    
    async def create_final_intercept_result(self, message: discord.Message, spam_score: float, success: bool) -> discord.Embed:
        """نتیجه نهایی رهگیری"""
        if success:
            embed = EmbedBuilder.create_embed(
                title=f"💥 رهگیری موفق - گنبد آهنین",
                description=f"**🎯 هدف منهدم شد**\n"
                           f"👤 کاربر: {message.author.mention}\n"
                           f"📊 امتیاز تهدید: {spam_score:.2f}\n"
                           f"✅ وضعیت: رهگیری موفق",
                color=EMBED_COLORS['success']
            )
            
            embed.add_field(
                name="📈 آمار رهگیری",
                value=f"🚀 موشک‌های باقی‌مانده: {format_number(self.missile_count)}\n"
                      f"🎯 رهگیری امروز: {format_number(self.intercepted_today)}\n"
                      f"📊 کل رهگیری‌ها: {format_number(self.total_intercepted)}",
                inline=True
            )
            
            embed.add_field(
                name="⚠️ هشدار",
                value=f"کاربر هشدار دریافت کرد\nتعداد هشدارها: {self.user_warnings.get(message.author.id, 0)}",
                inline=True
            )
            
        else:
            embed = EmbedBuilder.create_embed(
                title=f"❌ رهگیری ناموفق - گنبد آهنین",
                description=f"**🎯 هدف از دست رفت**\n"
                           f"👤 کاربر: {message.author.mention}\n"
                           f"📊 امتیاز تهدید: {spam_score:.2f}\n"
                           f"❌ وضعیت: رهگیری ناموفق",
                color=EMBED_COLORS['error']
            )
        
        embed.set_footer(text=f"گنبد آهنین - {TimeManager.format_time(TimeManager.get_current_time())}")
        return embed
    
    async def handle_no_missiles(self, message: discord.Message):
        """مدیریت کمبود موشک"""
        embed = EmbedBuilder.create_embed(
            title=f"⚠️ کمبود موشک - گنبد آهنین",
            description=f"**🚨 هشدار: موجودی موشک تمام شده است**\n\n"
                       f"🎯 هدف شناسایی شد اما امکان رهگیری وجود ندارد.\n"
                       f"👤 کاربر: {message.author.mention}\n"
                       f"📊 امتیاز تهدید: بالا\n\n"
                       f"🔧 **اقدام مورد نیاز**: تأمین موشک فوری",
            color=EMBED_COLORS['error']
        )
        
        # ارسال به کانال جنگ
        guild = message.guild
        war_room = discord.utils.get(guild.text_channels, name='war-room')
        if war_room:
            await war_room.send(embed=embed)
    
    async def send_warning_dm(self, user: discord.User, spam_score: float):
        """ارسال هشدار خصوصی"""
        warnings_count = self.user_warnings.get(user.id, 0)
        
        embed = EmbedBuilder.create_embed(
            title=f"⚠️ هشدار گنبد آهنین",
            description=f"پیام شما به عنوان اسپم شناسایی و حذف شد.",
            color=EMBED_COLORS['warning']
        )
        
        embed.add_field(
            name="📊 جزئیات",
            value=f"امتیاز اسپم: {spam_score:.2f}\nتعداد هشدارها: {warnings_count}",
            inline=True
        )
        
        embed.add_field(
            name="📋 راهنمایی",
            value="• از ارسال پیام‌های تکراری خودداری کنید\n"
                  "• سرعت ارسال پیام را کاهش دهید\n"
                  "• از اسپم لینک و منشن اجتناب کنید",
            inline=False
        )
        
        if warnings_count >= 3:
            embed.add_field(
                name="🚨 هشدار جدی",
                value="شما بیش از 3 هشدار دریافت کرده‌اید. ادامه این رفتار ممکن است منجر به محدودیت شود.",
                inline=False
            )
        
        await NotificationManager.send_dm(user, embed)
    
    async def report_to_war_room(self, message: discord.Message, spam_score: float):
        """گزارش به اتاق جنگ"""
        guild = message.guild
        war_room = discord.utils.get(guild.text_channels, name='war-room')
        
        if not war_room:
            return
        
        embed = EmbedBuilder.create_embed(
            title=f"🛡️ گزارش گنبد آهنین",
            description=f"رهگیری موفق انجام شد",
            color=EMBED_COLORS['defense']
        )
        
        embed.add_field(
            name="🎯 جزئیات هدف",
            value=f"👤 کاربر: {message.author.mention}\n"
                  f"📊 امتیاز اسپم: {spam_score:.2f}\n"
                  f"📝 طول پیام: {len(message.content)}\n"
                  f"📍 کانال: {message.channel.mention}",
            inline=True
        )
        
        embed.add_field(
            name="📈 وضعیت سیستم",
            value=f"🚀 موشک‌های باقی‌مانده: {format_number(self.missile_count)}\n"
                  f"🎯 رهگیری امروز: {format_number(self.intercepted_today)}\n"
                  f"⚠️ هشدارهای کاربر: {self.user_warnings.get(message.author.id, 0)}",
            inline=True
        )
        
        await war_room.send(embed=embed)
    
    async def request_missile_resupply(self, guild: discord.Guild):
        """درخواست تأمین موشک"""
        embed = EmbedBuilder.create_embed(
            title=f"🚨 درخواست تأمین موشک - گنبد آهنین",
            description=f"**موجودی موشک به حد بحرانی رسیده است**",
            color=EMBED_COLORS['error']
        )
        
        current_percentage = (self.missile_count / DefenseConfig.MISSILE_INVENTORY['iron_dome']['max']) * 100
        
        embed.add_field(
            name="📊 وضعیت فعلی",
            value=f"🚀 موجودی فعلی: {format_number(self.missile_count)}\n"
                  f"📊 درصد باقی‌مانده: {current_percentage:.1f}%\n"
                  f"⚠️ سطح: {'بحرانی' if current_percentage < 10 else 'خطر'}",
            inline=True
        )
        
        needed_missiles = DefenseConfig.MISSILE_INVENTORY['iron_dome']['max'] - self.missile_count
        total_cost = needed_missiles * DefenseConfig.MISSILE_INVENTORY['iron_dome']['cost']
        
        embed.add_field(
            name="💰 نیازمندی‌ها",
            value=f"🚀 موشک مورد نیاز: {format_number(needed_missiles)}\n"
                  f"💸 هزینه کل: {format_number(total_cost)} شکل\n"
                  f"⏰ زمان تحویل: 2-4 ساعت",
            inline=True
        )
        
        # ارسال به کانال‌های مربوطه
        channels = ['war-room', 'military-operations', 'government-announcements']
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(embed=embed)
    
    async def optimize_parameters(self):
        """بهینه‌سازی پارامترهای سیستم"""
        if not self.learning_mode:
            return
        
        # تحلیل عملکرد اخیر
        accuracy = self.calculate_accuracy()
        
        # تنظیم حساسیت بر اساس عملکرد
        if accuracy < 80 and self.sensitivity_level > 0.3:
            self.sensitivity_level -= 0.05
        elif accuracy > 95 and self.sensitivity_level < 0.9:
            self.sensitivity_level += 0.02
        
        # محدود کردن حساسیت
        self.sensitivity_level = max(0.1, min(0.9, self.sensitivity_level))
    
    def calculate_accuracy(self) -> float:
        """محاسبه دقت سیستم"""
        total_scans = self.performance_stats['total_scans']
        spam_detected = self.performance_stats['spam_detected']
        false_positives = self.performance_stats['false_positives']
        
        if total_scans == 0:
            return 0.0
        
        # فرض: 90% پیام‌ها عادی هستند
        true_negatives = total_scans - spam_detected - false_positives
        true_positives = spam_detected - false_positives
        
        correct_predictions = true_positives + true_negatives
        accuracy = (correct_predictions / total_scans) * 100
        
        return max(0.0, min(100.0, accuracy))
    
    def create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """ایجاد نوار پیشرفت"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"

# اجرای ربات
if __name__ == "__main__":
    bot = IronDomeBot()
    
    try:
        bot.run(bot.token)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات گنبد آهنین: {e}")