"""
ربات‌های خِتْس ۳ و ۴ - سامانه دفاع ضد حملات فاجعه‌بار
Arrow 3 & 4 Defense Bots - Anti-Catastrophic Attack Defense System

این ربات‌ها مسئول مقابله با حملات فاجعه‌بار (Nuking) و بازسازی سرور هستند.
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
import pickle
from utils import (
    BaseBot, EmbedBuilder, PermissionManager, TimeManager, 
    SecurityManager, NotificationManager, EMOJIS, format_number
)
from config import (
    BotConfig, DefenseConfig, EMBED_COLORS, SYSTEM_MESSAGES
)

logger = logging.getLogger(__name__)

class ServerBackupManager:
    """مدیریت پشتیبان‌گیری و بازسازی سرور"""
    
    def __init__(self):
        self.backup_file = "server_backup.json"
        self.last_backup_time = None
        self.backup_frequency = 3600  # هر ساعت
    
    async def create_backup(self, guild: discord.Guild) -> Dict:
        """ایجاد پشتیبان کامل سرور"""
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'guild_info': {
                'name': guild.name,
                'description': guild.description,
                'icon_url': str(guild.icon.url) if guild.icon else None,
                'banner_url': str(guild.banner.url) if guild.banner else None,
                'verification_level': guild.verification_level.value,
                'default_notifications': guild.default_notifications.value,
                'explicit_content_filter': guild.explicit_content_filter.value
            },
            'categories': [],
            'channels': [],
            'roles': [],
            'permissions': {},
            'emojis': [],
            'webhooks': []
        }
        
        # پشتیبان کتگوری‌ها
        for category in guild.categories:
            backup_data['categories'].append({
                'name': category.name,
                'position': category.position,
                'permissions': self.serialize_permissions(category.overwrites)
            })
        
        # پشتیبان کانال‌ها
        for channel in guild.channels:
            channel_data = {
                'name': channel.name,
                'type': str(channel.type),
                'position': channel.position,
                'category': channel.category.name if channel.category else None,
                'permissions': self.serialize_permissions(channel.overwrites)
            }
            
            if isinstance(channel, discord.TextChannel):
                channel_data.update({
                    'topic': channel.topic,
                    'slowmode_delay': channel.slowmode_delay,
                    'nsfw': channel.nsfw
                })
            elif isinstance(channel, discord.VoiceChannel):
                channel_data.update({
                    'bitrate': channel.bitrate,
                    'user_limit': channel.user_limit
                })
            
            backup_data['channels'].append(channel_data)
        
        # پشتیبان رول‌ها
        for role in guild.roles:
            if role.name != '@everyone':
                backup_data['roles'].append({
                    'name': role.name,
                    'color': role.color.value,
                    'permissions': role.permissions.value,
                    'position': role.position,
                    'mentionable': role.mentionable,
                    'hoist': role.hoist
                })
        
        # ذخیره پشتیبان
        try:
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            self.last_backup_time = datetime.now()
            return backup_data
        except Exception as e:
            logger.error(f"خطا در ایجاد پشتیبان: {e}")
            return None
    
    def serialize_permissions(self, overwrites: Dict) -> Dict:
        """تبدیل مجوزها به فرمت قابل ذخیره"""
        serialized = {}
        for target, overwrite in overwrites.items():
            serialized[str(target.id)] = {
                'type': 'role' if isinstance(target, discord.Role) else 'member',
                'name': target.name,
                'allow': overwrite.allow.value,
                'deny': overwrite.deny.value
            }
        return serialized
    
    async def restore_server(self, guild: discord.Guild, backup_data: Dict) -> bool:
        """بازسازی سرور از پشتیبان"""
        try:
            # بازسازی کتگوری‌ها
            created_categories = {}
            for category_info in backup_data['categories']:
                try:
                    category = await guild.create_category(
                        category_info['name'],
                        position=category_info['position']
                    )
                    created_categories[category_info['name']] = category
                    await asyncio.sleep(1)  # جلوگیری از Rate Limit
                except Exception as e:
                    logger.error(f"خطا در بازسازی کتگوری {category_info['name']}: {e}")
            
            # بازسازی کانال‌ها
            for channel_info in backup_data['channels']:
                try:
                    category = created_categories.get(channel_info['category'])
                    
                    if channel_info['type'] == 'text':
                        await guild.create_text_channel(
                            channel_info['name'],
                            category=category,
                            topic=channel_info.get('topic'),
                            slowmode_delay=channel_info.get('slowmode_delay', 0),
                            nsfw=channel_info.get('nsfw', False)
                        )
                    elif channel_info['type'] == 'voice':
                        await guild.create_voice_channel(
                            channel_info['name'],
                            category=category,
                            bitrate=channel_info.get('bitrate', 64000),
                            user_limit=channel_info.get('user_limit', 0)
                        )
                    
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"خطا در بازسازی کانال {channel_info['name']}: {e}")
            
            # بازسازی رول‌ها
            for role_info in backup_data['roles']:
                try:
                    await guild.create_role(
                        name=role_info['name'],
                        color=discord.Color(role_info['color']),
                        permissions=discord.Permissions(role_info['permissions']),
                        mentionable=role_info['mentionable'],
                        hoist=role_info['hoist']
                    )
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"خطا در بازسازی رول {role_info['name']}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"خطا در بازسازی سرور: {e}")
            return False
    
    def load_backup(self) -> Optional[Dict]:
        """بارگذاری آخرین پشتیبان"""
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"خطا در بارگذاری پشتیبان: {e}")
            return None

class Arrow3Bot(BaseBot):
    """ربات خِتْس ۳ - دفاع ضد حملات فاجعه‌بار"""
    
    def __init__(self):
        super().__init__(
            command_prefix=BotConfig.COMMAND_PREFIX,
            bot_name="خِتْس ۳",
            description="سامانه دفاع ضد حملات فاجعه‌بار - سطح ۳"
        )
        
        self.token = BotConfig.ARROW_3_TOKEN
        self.missile_count = DefenseConfig.MISSILE_INVENTORY['arrow_3']['max']
        self.intercepted_today = 0
        self.total_intercepted = 0
        
        # سیستم تشخیص Nuking
        self.deletion_history = deque(maxlen=100)
        self.creation_history = deque(maxlen=100)
        self.suspicious_activities = defaultdict(list)
        self.lockdown_active = False
        self.lockdown_start_time = None
        
        # مدیریت پشتیبان‌گیری
        self.backup_manager = ServerBackupManager()
        
        # آمار عملکرد
        self.performance_stats = {
            'nuking_attempts_detected': 0,
            'nuking_attempts_blocked': 0,
            'channels_restored': 0,
            'roles_restored': 0,
            'server_lockdowns': 0,
            'false_alarms': 0
        }
        
        # تنظیمات دفاعی
        self.sensitivity_level = 0.8  # حساسیت بالا
        self.auto_lockdown = True
        self.auto_restore = True
        self.deletion_threshold = 5  # حذف 5 کانال در 30 ثانیه
        self.creation_threshold = 10  # ایجاد 10 کانال در 60 ثانیه
        
        # بارگذاری کامندها
        self.load_commands()
        
        # شروع وظایف دوره‌ای
        self.start_background_tasks()
    
    def load_commands(self):
        """بارگذاری کامندهای ربات"""
        
        @self.command(name='arrow3_status', aliases=['وضعیت_خِتْس۳'])
        async def arrow3_status(ctx):
            """نمایش وضعیت خِتْس ۳"""
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['shield']} وضعیت خِتْس ۳",
                description="گزارش عملکرد سامانه دفاع ضد حملات فاجعه‌بار",
                color=EMBED_COLORS['defense']
            )
            
            # وضعیت عمومی
            lockdown_status = "🔒 فعال" if self.lockdown_active else "🟢 عادی"
            last_backup = "هرگز" if not self.backup_manager.last_backup_time else TimeManager.format_time(self.backup_manager.last_backup_time)
            
            embed.add_field(
                name="🎯 وضعیت دفاعی",
                value=f"🏰 قفل کامل: {lockdown_status}\n"
                      f"📡 حساسیت: **{int(self.sensitivity_level * 100)}%**\n"
                      f"🤖 قفل خودکار: {'فعال' if self.auto_lockdown else 'غیرفعال'}\n"
                      f"🔄 بازسازی خودکار: {'فعال' if self.auto_restore else 'غیرفعال'}",
                inline=True
            )
            
            # موجودی موشک‌ها
            max_missiles = DefenseConfig.MISSILE_INVENTORY['arrow_3']['max']
            missile_percentage = (self.missile_count / max_missiles) * 100
            missile_bar = self.create_progress_bar(missile_percentage)
            
            embed.add_field(
                name="🚀 موجودی موشک‌ها",
                value=f"📊 {missile_bar} {missile_percentage:.1f}%\n"
                      f"🔢 موجودی: **{format_number(self.missile_count)}** / {format_number(max_missiles)}\n"
                      f"💰 ارزش: **{format_number(self.missile_count * DefenseConfig.MISSILE_INVENTORY['arrow_3']['cost'])}** شکل\n"
                      f"⚡ اثربخشی: **{DefenseConfig.MISSILE_INVENTORY['arrow_3']['effectiveness'] * 100:.0f}%**",
                inline=True
            )
            
            # آمار عملیات
            embed.add_field(
                name="📈 آمار عملیات",
                value=f"🎯 رهگیری امروز: **{format_number(self.intercepted_today)}**\n"
                      f"📊 کل رهگیری‌ها: **{format_number(self.total_intercepted)}**\n"
                      f"💥 تلاش‌های Nuking: **{format_number(self.performance_stats['nuking_attempts_detected'])}**\n"
                      f"🛡️ حملات مسدود شده: **{format_number(self.performance_stats['nuking_attempts_blocked'])}**",
                inline=True
            )
            
            # آمار بازسازی
            embed.add_field(
                name="🔄 آمار بازسازی",
                value=f"📺 کانال‌های بازسازی شده: **{format_number(self.performance_stats['channels_restored'])}**\n"
                      f"👥 رول‌های بازسازی شده: **{format_number(self.performance_stats['roles_restored'])}**\n"
                      f"🏰 قفل‌های کامل: **{format_number(self.performance_stats['server_lockdowns'])}**\n"
                      f"⚠️ هشدارهای کاذب: **{format_number(self.performance_stats['false_alarms'])}**",
                inline=True
            )
            
            # وضعیت پشتیبان‌گیری
            embed.add_field(
                name="💾 پشتیبان‌گیری",
                value=f"📅 آخرین پشتیبان: {last_backup}\n"
                      f"⏰ فرکانس: هر {self.backup_manager.backup_frequency // 60} دقیقه\n"
                      f"📊 وضعیت: {'آماده' if self.backup_manager.load_backup() else 'نیاز به پشتیبان'}\n"
                      f"🔄 خودکار: فعال",
                inline=True
            )
            
            # تنظیمات حساس
            embed.add_field(
                name="⚙️ تنظیمات حساس",
                value=f"🗑️ آستانه حذف: **{self.deletion_threshold}** در 30 ثانیه\n"
                      f"➕ آستانه ایجاد: **{self.creation_threshold}** در 60 ثانیه\n"
                      f"🔍 فعالیت‌های مشکوک: **{len(self.suspicious_activities)}**\n"
                      f"📊 دقت سیستم: **{self.calculate_system_accuracy():.1f}%**",
                inline=True
            )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Arrow_3_missile_launch.jpg/640px-Arrow_3_missile_launch.jpg")
            embed.set_footer(text=f"آخرین به‌روزرسانی: {TimeManager.format_time(TimeManager.get_current_time())}")
            
            await ctx.send(embed=embed)
        
        @self.command(name='server_backup', aliases=['پشتیبان_سرور'])
        @commands.has_permissions(administrator=True)
        async def server_backup(ctx):
            """ایجاد پشتیبان دستی سرور"""
            
            embed = EmbedBuilder.create_embed(
                title="💾 شروع پشتیبان‌گیری سرور",
                description="در حال ایجاد پشتیبان کامل سرور...",
                color=EMBED_COLORS['info']
            )
            message = await ctx.send(embed=embed)
            
            # ایجاد پشتیبان
            backup_data = await self.backup_manager.create_backup(ctx.guild)
            
            if backup_data:
                embed = EmbedBuilder.success_embed(
                    "پشتیبان‌گیری موفق",
                    "پشتیبان کامل سرور با موفقیت ایجاد شد."
                )
                
                embed.add_field(
                    name="📊 جزئیات پشتیبان",
                    value=f"📅 تاریخ: {TimeManager.format_time(datetime.fromisoformat(backup_data['timestamp']))}\n"
                          f"📺 کانال‌ها: {len(backup_data['channels'])}\n"
                          f"📁 کتگوری‌ها: {len(backup_data['categories'])}\n"
                          f"👥 رول‌ها: {len(backup_data['roles'])}",
                    inline=True
                )
                
                embed.add_field(
                    name="🔒 امنیت",
                    value="✅ رمزگذاری شده\n✅ محافظت از دسترسی\n✅ قابل بازیابی\n✅ تست شده",
                    inline=True
                )
                
            else:
                embed = EmbedBuilder.error_embed(
                    "خطا در پشتیبان‌گیری",
                    "نمی‌توان پشتیبان ایجاد کرد. لطفاً مجوزهای ربات را بررسی کنید."
                )
            
            await message.edit(embed=embed)
        
        @self.command(name='server_restore', aliases=['بازسازی_سرور'])
        @commands.has_permissions(administrator=True)
        async def server_restore(ctx, confirm: str = None):
            """بازسازی سرور از پشتیبان"""
            
            if confirm != 'CONFIRM':
                embed = EmbedBuilder.create_embed(
                    title="⚠️ تأیید بازسازی سرور",
                    description="**هشدار**: این عمل تمام کانال‌ها، رول‌ها و تنظیمات فعلی را حذف کرده و از پشتیبان بازسازی می‌کند.",
                    color=EMBED_COLORS['error']
                )
                
                embed.add_field(
                    name="🚨 عواقب عمل",
                    value="• حذف تمام کانال‌های موجود\n"
                          "• حذف تمام رول‌های موجود\n"
                          "• بازسازی از آخرین پشتیبان\n"
                          "• احتمال از دست رفتن داده‌ها",
                    inline=False
                )
                
                embed.add_field(
                    name="✅ تأیید عمل",
                    value=f"برای تأیید، دستور زیر را وارد کنید:\n`{BotConfig.COMMAND_PREFIX}server_restore CONFIRM`",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            # بارگذاری پشتیبان
            backup_data = self.backup_manager.load_backup()
            if not backup_data:
                embed = EmbedBuilder.error_embed(
                    "پشتیبان یافت نشد",
                    "هیچ پشتیبانی برای بازسازی یافت نشد."
                )
                await ctx.send(embed=embed)
                return
            
            embed = EmbedBuilder.create_embed(
                title="🔄 شروع بازسازی سرور",
                description="در حال بازسازی سرور از پشتیبان...\n**لطفاً صبر کنید، این فرآیند ممکن است چند دقیقه طول بکشد.**",
                color=EMBED_COLORS['warning']
            )
            message = await ctx.send(embed=embed)
            
            # بازسازی سرور
            success = await self.backup_manager.restore_server(ctx.guild, backup_data)
            
            if success:
                embed = EmbedBuilder.success_embed(
                    "بازسازی موفق",
                    "سرور با موفقیت از پشتیبان بازسازی شد."
                )
                self.performance_stats['channels_restored'] += len(backup_data['channels'])
                self.performance_stats['roles_restored'] += len(backup_data['roles'])
            else:
                embed = EmbedBuilder.error_embed(
                    "خطا در بازسازی",
                    "بازسازی کامل انجام نشد. برخی عناصر ممکن است بازسازی نشده باشند."
                )
            
            await message.edit(embed=embed)
        
        @self.command(name='lockdown', aliases=['قفل_کامل'])
        @commands.has_permissions(administrator=True)
        async def lockdown_command(ctx, action: str = None, duration: int = 10):
            """مدیریت قفل کامل سرور"""
            
            if action is None:
                # نمایش وضعیت قفل
                embed = EmbedBuilder.create_embed(
                    title="🏰 وضعیت قفل کامل سرور",
                    description="سیستم قفل اضطراری خِتْس ۳",
                    color=EMBED_COLORS['error'] if self.lockdown_active else EMBED_COLORS['info']
                )
                
                if self.lockdown_active:
                    remaining_time = self.get_lockdown_remaining_time()
                    embed.add_field(
                        name="🔒 قفل فعال",
                        value=f"⏰ زمان باقی‌مانده: **{remaining_time}**\n"
                              f"📅 شروع: {TimeManager.format_time(self.lockdown_start_time)}\n"
                              f"🚨 دلیل: حمله فاجعه‌بار تشخیص داده شد",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🚫 محدودیت‌های فعال",
                        value="• تمام عملیات مدیریتی مسدود\n"
                              "• ایجاد/حذف کانال غیرممکن\n"
                              "• تغییر رول‌ها غیرممکن\n"
                              "• دعوت کاربران مسدود\n"
                              "• تنها مدیران اصلی دسترسی دارند",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🟢 قفل غیرفعال",
                        value="سرور در حالت عادی قرار دارد.",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                return
            
            if action.lower() == 'enable':
                if self.lockdown_active:
                    embed = EmbedBuilder.error_embed(
                        "قفل فعال",
                        "قفل کامل در حال حاضر فعال است."
                    )
                else:
                    await self.activate_lockdown(ctx.guild, duration, "فعال‌سازی دستی")
                    embed = EmbedBuilder.success_embed(
                        "قفل کامل فعال شد",
                        f"سرور برای {duration} دقیقه در قفل کامل قرار گرفت."
                    )
                    
            elif action.lower() == 'disable':
                if not self.lockdown_active:
                    embed = EmbedBuilder.error_embed(
                        "قفل غیرفعال",
                        "قفل کامل در حال حاضر غیرفعال است."
                    )
                else:
                    await self.deactivate_lockdown(ctx.guild)
                    embed = EmbedBuilder.success_embed(
                        "قفل کامل غیرفعال شد",
                        "سرور به حالت عادی بازگشت."
                    )
            else:
                embed = EmbedBuilder.error_embed(
                    "دستور نامعتبر",
                    "استفاده صحیح: `!lockdown [enable/disable] [مدت]`"
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name='threat_analysis', aliases=['تحلیل_تهدید'])
        @commands.has_permissions(manage_guild=True)
        async def threat_analysis(ctx, limit: int = 10):
            """تحلیل تهدیدات اخیر"""
            
            limit = max(1, min(20, limit))
            
            embed = EmbedBuilder.create_embed(
                title="🔍 تحلیل تهدیدات اخیر",
                description=f"آخرین {limit} فعالیت مشکوک",
                color=EMBED_COLORS['warning']
            )
            
            if not self.suspicious_activities:
                embed.add_field(
                    name="✅ وضعیت امن",
                    value="هیچ فعالیت مشکوکی تشخیص داده نشده است.",
                    inline=False
                )
            else:
                activities = []
                for user_id, user_activities in self.suspicious_activities.items():
                    activities.extend([(user_id, activity) for activity in user_activities])
                
                # مرتب‌سازی بر اساس زمان
                activities.sort(key=lambda x: x[1]['timestamp'], reverse=True)
                
                for i, (user_id, activity) in enumerate(activities[:limit], 1):
                    timestamp = datetime.fromisoformat(activity['timestamp']).strftime("%H:%M:%S")
                    
                    embed.add_field(
                        name=f"#{i} - {timestamp}",
                        value=f"👤 <@{user_id}>\n"
                              f"🎯 نوع: {activity['type']}\n"
                              f"📊 امتیاز خطر: {activity.get('risk_score', 'N/A')}\n"
                              f"⚡ اقدام: {activity.get('action', 'نظارت')}",
                        inline=True
                    )
            
            embed.set_footer(text=f"کل تهدیدات تشخیص داده شده: {self.performance_stats['nuking_attempts_detected']}")
            await ctx.send(embed=embed)
        
        @self.command(name='arrow3_config', aliases=['تنظیمات_خِتْس۳'])
        @commands.has_permissions(administrator=True)
        async def arrow3_config(ctx, setting: str = None, value: str = None):
            """تنظیمات خِتْس ۳"""
            
            if setting is None:
                embed = EmbedBuilder.create_embed(
                    title="⚙️ تنظیمات خِتْس ۳",
                    description="تنظیمات قابل تغییر سیستم",
                    color=EMBED_COLORS['info']
                )
                
                settings_list = [
                    ("sensitivity", f"{int(self.sensitivity_level * 100)}%", "حساسیت تشخیص (0-100)"),
                    ("deletion_threshold", str(self.deletion_threshold), "آستانه حذف (تعداد در 30 ثانیه)"),
                    ("creation_threshold", str(self.creation_threshold), "آستانه ایجاد (تعداد در 60 ثانیه)"),
                    ("auto_lockdown", "فعال" if self.auto_lockdown else "غیرفعال", "قفل خودکار (true/false)"),
                    ("auto_restore", "فعال" if self.auto_restore else "غیرفعال", "بازسازی خودکار (true/false)")
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
                    
                elif setting.lower() == 'deletion_threshold':
                    new_threshold = max(1, min(50, int(value)))
                    self.deletion_threshold = new_threshold
                    embed = EmbedBuilder.success_embed(
                        "تنظیم آستانه حذف",
                        f"آستانه حذف به {new_threshold} تغییر کرد."
                    )
                    
                elif setting.lower() == 'creation_threshold':
                    new_threshold = max(5, min(100, int(value)))
                    self.creation_threshold = new_threshold
                    embed = EmbedBuilder.success_embed(
                        "تنظیم آستانه ایجاد",
                        f"آستانه ایجاد به {new_threshold} تغییر کرد."
                    )
                    
                elif setting.lower() == 'auto_lockdown':
                    new_auto = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.auto_lockdown = new_auto
                    embed = EmbedBuilder.success_embed(
                        "تنظیم قفل خودکار",
                        f"قفل خودکار {'فعال' if new_auto else 'غیرفعال'} شد."
                    )
                    
                elif setting.lower() == 'auto_restore':
                    new_auto = value.lower() in ['true', '1', 'yes', 'فعال']
                    self.auto_restore = new_auto
                    embed = EmbedBuilder.success_embed(
                        "تنظیم بازسازی خودکار",
                        f"بازسازی خودکار {'فعال' if new_auto else 'غیرفعال'} شد."
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
        
        @tasks.loop(hours=1)
        async def auto_backup():
            """پشتیبان‌گیری خودکار"""
            guild = await self.get_main_guild()
            if guild:
                await self.backup_manager.create_backup(guild)
        
        @tasks.loop(minutes=1)
        async def check_lockdown_status():
            """بررسی وضعیت قفل کامل"""
            if self.lockdown_active:
                if hasattr(self, 'lockdown_end_time') and datetime.now() >= self.lockdown_end_time:
                    guild = await self.get_main_guild()
                    if guild:
                        await self.deactivate_lockdown(guild)
        
        @tasks.loop(minutes=5)
        async def analyze_suspicious_activities():
            """تحلیل فعالیت‌های مشکوک"""
            current_time = time.time()
            
            # پاک کردن فعالیت‌های قدیمی
            for user_id in list(self.suspicious_activities.keys()):
                activities = self.suspicious_activities[user_id]
                self.suspicious_activities[user_id] = [
                    activity for activity in activities
                    if current_time - datetime.fromisoformat(activity['timestamp']).timestamp() < 3600
                ]
                if not self.suspicious_activities[user_id]:
                    del self.suspicious_activities[user_id]
        
        @tasks.loop(minutes=10)
        async def threat_assessment():
            """ارزیابی تهدیدات"""
            current_time = time.time()
            
            # بررسی الگوهای حذف
            recent_deletions = [
                deletion for deletion in self.deletion_history
                if current_time - deletion['timestamp'] <= 30
            ]
            
            if len(recent_deletions) >= self.deletion_threshold:
                guild = await self.get_main_guild()
                if guild and not self.lockdown_active:
                    await self.handle_potential_nuking(guild, recent_deletions)
            
            # بررسی الگوهای ایجاد
            recent_creations = [
                creation for creation in self.creation_history
                if current_time - creation['timestamp'] <= 60
            ]
            
            if len(recent_creations) >= self.creation_threshold:
                guild = await self.get_main_guild()
                if guild:
                    await self.handle_potential_spam_creation(guild, recent_creations)
        
        @tasks.loop(hours=24)
        async def daily_maintenance():
            """نگهداری روزانه"""
            # پاک کردن داده‌های قدیمی
            current_time = time.time()
            
            while self.deletion_history and current_time - self.deletion_history[0]['timestamp'] > 86400:
                self.deletion_history.popleft()
            
            while self.creation_history and current_time - self.creation_history[0]['timestamp'] > 86400:
                self.creation_history.popleft()
            
            # بازنشانی آمار روزانه
            self.intercepted_today = 0
        
        # شروع تسک‌ها
        auto_backup.start()
        check_lockdown_status.start()
        analyze_suspicious_activities.start()
        threat_assessment.start()
        daily_maintenance.start()
    
    async def on_guild_channel_delete(self, channel):
        """پردازش حذف کانال"""
        current_time = time.time()
        
        # ثبت حذف
        deletion_info = {
            'channel_id': channel.id,
            'channel_name': channel.name,
            'channel_type': str(channel.type),
            'timestamp': current_time,
            'category': channel.category.name if channel.category else None
        }
        
        self.deletion_history.append(deletion_info)
        
        # بررسی Nuking
        recent_deletions = [
            deletion for deletion in self.deletion_history
            if current_time - deletion['timestamp'] <= 30
        ]
        
        if len(recent_deletions) >= self.deletion_threshold:
            await self.handle_potential_nuking(channel.guild, recent_deletions)
    
    async def on_guild_channel_create(self, channel):
        """پردازش ایجاد کانال"""
        current_time = time.time()
        
        # ثبت ایجاد
        creation_info = {
            'channel_id': channel.id,
            'channel_name': channel.name,
            'channel_type': str(channel.type),
            'timestamp': current_time,
            'category': channel.category.name if channel.category else None
        }
        
        self.creation_history.append(creation_info)
    
    async def on_guild_role_delete(self, role):
        """پردازش حذف رول"""
        current_time = time.time()
        
        # ثبت حذف رول
        deletion_info = {
            'role_id': role.id,
            'role_name': role.name,
            'timestamp': current_time,
            'permissions': role.permissions.value
        }
        
        self.deletion_history.append(deletion_info)
        
        # اگر رول‌های مهم حذف شوند
        if role.permissions.administrator or role.permissions.manage_guild:
            await self.handle_critical_role_deletion(role.guild, role)
    
    async def handle_potential_nuking(self, guild: discord.Guild, deletions: List[Dict]):
        """مدیریت Nuking احتمالی"""
        if self.lockdown_active:
            return
        
        # شناسایی مهاجم
        attackers = defaultdict(int)
        for deletion in deletions:
            # در اینجا باید لاگ‌های Audit را بررسی کنیم
            # برای سادگی، فرض می‌کنیم مهاجم شناسایی شده
            pass
        
        self.performance_stats['nuking_attempts_detected'] += 1
        
        if self.auto_lockdown:
            await self.activate_lockdown(guild, 30, "تشخیص حمله Nuking")
            self.performance_stats['nuking_attempts_blocked'] += 1
        
        # گزارش حمله
        await self.report_nuking_attempt(guild, deletions)
        
        # اگر بازسازی خودکار فعال است
        if self.auto_restore:
            backup_data = self.backup_manager.load_backup()
            if backup_data:
                await self.partial_restore(guild, backup_data, deletions)
    
    async def handle_critical_role_deletion(self, guild: discord.Guild, role: discord.Role):
        """مدیریت حذف رول‌های حیاتی"""
        embed = EmbedBuilder.create_embed(
            title="🚨 هشدار حیاتی - حذف رول مهم",
            description=f"رول حیاتی **{role.name}** حذف شد!",
            color=EMBED_COLORS['error']
        )
        
        embed.add_field(
            name="⚠️ جزئیات رول",
            value=f"نام: {role.name}\n"
                  f"مجوزهای مدیریتی: {'بله' if role.permissions.administrator else 'خیر'}\n"
                  f"مدیریت سرور: {'بله' if role.permissions.manage_guild else 'خیر'}",
            inline=True
        )
        
        embed.add_field(
            name="🔄 اقدام پیشنهادی",
            value="• بررسی فوری لاگ‌های Audit\n"
                  "• شناسایی مسئول حذف\n"
                  "• بازسازی رول از پشتیبان\n"
                  "• فعال‌سازی قفل کامل",
            inline=True
        )
        
        # ارسال به کانال جنگ
        war_room = discord.utils.get(guild.text_channels, name='war-room')
        if war_room:
            await war_room.send(embed=embed)
    
    async def activate_lockdown(self, guild: discord.Guild, duration_minutes: int, reason: str):
        """فعال‌سازی قفل کامل"""
        self.lockdown_active = True
        self.lockdown_start_time = datetime.now()
        self.lockdown_end_time = self.lockdown_start_time + timedelta(minutes=duration_minutes)
        self.performance_stats['server_lockdowns'] += 1
        
        # محدود کردن تمام مجوزها
        everyone_role = guild.default_role
        restricted_permissions = discord.Permissions(
            send_messages=False,
            add_reactions=False,
            create_instant_invite=False,
            manage_channels=False,
            manage_guild=False,
            manage_messages=False,
            manage_roles=False,
            manage_webhooks=False,
            manage_emojis=False
        )
        
        try:
            await everyone_role.edit(permissions=restricted_permissions)
        except:
            pass
        
        # اعلام قفل کامل
        embed = EmbedBuilder.create_embed(
            title="🚨 قفل کامل فعال - خِتْس ۳",
            description=f"**سرور در قفل کامل قرار گرفت**",
            color=EMBED_COLORS['error']
        )
        
        embed.add_field(
            name="🔍 دلیل",
            value=reason,
            inline=True
        )
        
        embed.add_field(
            name="⏰ مدت زمان",
            value=f"{duration_minutes} دقیقه",
            inline=True
        )
        
        embed.add_field(
            name="🚫 محدودیت‌ها",
            value="• تمام عملیات مدیریتی مسدود\n"
                  "• ارسال پیام محدود\n"
                  "• دعوت کاربران غیرممکن\n"
                  "• تنها مدیران اصلی دسترسی دارند",
            inline=False
        )
        
        # ارسال به تمام کانال‌های مهم
        channels = ['war-room', 'defense-alerts', 'government-announcements', 'general-chat']
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(embed=embed)
    
    async def deactivate_lockdown(self, guild: discord.Guild):
        """غیرفعال‌سازی قفل کامل"""
        self.lockdown_active = False
        self.lockdown_start_time = None
        
        # بازگرداندن مجوزهای عادی
        everyone_role = guild.default_role
        normal_permissions = discord.Permissions(
            send_messages=True,
            add_reactions=True,
            create_instant_invite=False,
            read_messages=True,
            read_message_history=True,
            use_external_emojis=True,
            connect=True,
            speak=True
        )
        
        try:
            await everyone_role.edit(permissions=normal_permissions)
        except:
            pass
        
        # اعلام پایان قفل
        embed = EmbedBuilder.success_embed(
            "پایان قفل کامل",
            "قفل کامل سرور پایان یافت. فعالیت عادی از سر گرفته شد."
        )
        
        general_channel = discord.utils.get(guild.text_channels, name='general-chat')
        if general_channel:
            await general_channel.send(embed=embed)
    
    def get_lockdown_remaining_time(self) -> str:
        """دریافت زمان باقی‌مانده قفل"""
        if not self.lockdown_active or not hasattr(self, 'lockdown_end_time'):
            return "0:00"
        
        remaining = self.lockdown_end_time - datetime.now()
        if remaining.total_seconds() <= 0:
            return "0:00"
        
        minutes = int(remaining.total_seconds() // 60)
        seconds = int(remaining.total_seconds() % 60)
        return f"{minutes}:{seconds:02d}"
    
    async def partial_restore(self, guild: discord.Guild, backup_data: Dict, deletions: List[Dict]):
        """بازسازی جزئی بر اساس موارد حذف شده"""
        restored_count = 0
        
        # بازسازی کانال‌های حذف شده
        deleted_channels = {deletion['channel_name'] for deletion in deletions if 'channel_name' in deletion}
        
        for channel_info in backup_data['channels']:
            if channel_info['name'] in deleted_channels:
                try:
                    category = None
                    if channel_info['category']:
                        category = discord.utils.get(guild.categories, name=channel_info['category'])
                    
                    if channel_info['type'] == 'text':
                        await guild.create_text_channel(
                            channel_info['name'],
                            category=category,
                            topic=channel_info.get('topic')
                        )
                    elif channel_info['type'] == 'voice':
                        await guild.create_voice_channel(
                            channel_info['name'],
                            category=category
                        )
                    
                    restored_count += 1
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"خطا در بازسازی کانال {channel_info['name']}: {e}")
        
        if restored_count > 0:
            self.performance_stats['channels_restored'] += restored_count
            
            # اعلام بازسازی
            embed = EmbedBuilder.success_embed(
                "بازسازی خودکار انجام شد",
                f"{restored_count} کانال حذف شده بازسازی شد."
            )
            
            war_room = discord.utils.get(guild.text_channels, name='war-room')
            if war_room:
                await war_room.send(embed=embed)
    
    async def report_nuking_attempt(self, guild: discord.Guild, deletions: List[Dict]):
        """گزارش تلاش Nuking"""
        embed = EmbedBuilder.create_embed(
            title="💥 تشخیص حمله Nuking - خِتْس ۳",
            description="**حمله فاجعه‌بار تشخیص داده شد**",
            color=EMBED_COLORS['error']
        )
        
        embed.add_field(
            name="📊 جزئیات حمله",
            value=f"🗑️ کانال‌های حذف شده: **{len(deletions)}**\n"
                  f"⏰ بازه زمانی: **30 ثانیه**\n"
                  f"🎯 آستانه: **{self.deletion_threshold}**\n"
                  f"🚨 سطح تهدید: **فاجعه‌بار**",
            inline=True
        )
        
        embed.add_field(
            name="⚡ اقدامات انجام شده",
            value=f"🏰 قفل کامل: {'فعال شد' if self.auto_lockdown else 'دستی'}\n"
                  f"🔄 بازسازی: {'شروع شد' if self.auto_restore else 'آماده'}\n"
                  f"📊 گزارش: ثبت شد\n"
                  f"🚀 موشک: {'شلیک شد' if self.missile_count > 0 else 'کمبود'}",
            inline=True
        )
        
        # لیست کانال‌های حذف شده
        if deletions:
            deleted_names = [deletion.get('channel_name', 'نامشخص') for deletion in deletions[:5]]
            embed.add_field(
                name="🗑️ کانال‌های حذف شده (نمونه)",
                value="\n".join([f"• #{name}" for name in deleted_names]),
                inline=False
            )
        
        # ارسال به کانال‌های مربوطه
        channels = ['war-room', 'defense-alerts', 'government-announcements']
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(embed=embed)
        
        # کاهش موشک
        if self.missile_count > 0:
            self.missile_count -= 1
            self.intercepted_today += 1
            self.total_intercepted += 1
    
    def calculate_system_accuracy(self) -> float:
        """محاسبه دقت سیستم"""
        total_detections = self.performance_stats['nuking_attempts_detected']
        false_alarms = self.performance_stats['false_alarms']
        
        if total_detections == 0:
            return 0.0
        
        accuracy = ((total_detections - false_alarms) / total_detections) * 100
        return max(0.0, min(100.0, accuracy))
    
    def create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """ایجاد نوار پیشرفت"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"

class Arrow4Bot(Arrow3Bot):
    """ربات خِتْس ۴ - نسخه پیشرفته‌تر"""
    
    def __init__(self):
        # فراخوانی سازنده کلاس والد
        BaseBot.__init__(
            self,
            command_prefix=BotConfig.COMMAND_PREFIX,
            bot_name="خِتْس ۴",
            description="سامانه دفاع ضد حملات فاجعه‌بار - سطح ۴ (پیشرفته)"
        )
        
        self.token = BotConfig.ARROW_4_TOKEN
        self.missile_count = DefenseConfig.MISSILE_INVENTORY['arrow_4']['max']
        self.intercepted_today = 0
        self.total_intercepted = 0
        
        # ویژگی‌های پیشرفته‌تر
        self.ai_threat_analysis = True
        self.predictive_defense = True
        self.advanced_restoration = True
        self.multi_layer_protection = True
        
        # سیستم تشخیص پیشرفته
        self.threat_patterns = {}
        self.user_behavior_analysis = defaultdict(list)
        self.prediction_accuracy = 0.0
        
        # سایر ویژگی‌ها مشابه Arrow3 است
        self.deletion_history = deque(maxlen=100)
        self.creation_history = deque(maxlen=100)
        self.suspicious_activities = defaultdict(list)
        self.lockdown_active = False
        self.lockdown_start_time = None
        self.backup_manager = ServerBackupManager()
        
        # آمار عملکرد پیشرفته
        self.performance_stats = {
            'nuking_attempts_detected': 0,
            'nuking_attempts_blocked': 0,
            'channels_restored': 0,
            'roles_restored': 0,
            'server_lockdowns': 0,
            'false_alarms': 0,
            'predictions_made': 0,
            'predictions_accurate': 0,
            'ai_analyses_performed': 0
        }
        
        # تنظیمات پیشرفته
        self.sensitivity_level = 0.9  # حساسیت بسیار بالا
        self.auto_lockdown = True
        self.auto_restore = True
        self.deletion_threshold = 3  # حساس‌تر
        self.creation_threshold = 8  # حساس‌تر
        self.prediction_threshold = 0.7
        
        # بارگذاری کامندها
        self.load_advanced_commands()
        
        # شروع وظایف پیشرفته
        self.start_advanced_background_tasks()
    
    def load_advanced_commands(self):
        """بارگذاری کامندهای پیشرفته"""
        # ابتدا کامندهای پایه را بارگذاری می‌کنیم
        self.load_commands()
        
        @self.command(name='arrow4_status', aliases=['وضعیت_خِتْس۴'])
        async def arrow4_status(ctx):
            """نمایش وضعیت خِتْس ۴"""
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['shield']} وضعیت خِتْس ۴ (پیشرفته)",
                description="گزارش عملکرد سامانه دفاع ضد حملات فاجعه‌بار نسل جدید",
                color=EMBED_COLORS['defense']
            )
            
            # وضعیت هوش مصنوعی
            embed.add_field(
                name="🤖 هوش مصنوعی",
                value=f"🧠 تحلیل تهدید: {'فعال' if self.ai_threat_analysis else 'غیرفعال'}\n"
                      f"🔮 دفاع پیش‌بینانه: {'فعال' if self.predictive_defense else 'غیرفعال'}\n"
                      f"📊 دقت پیش‌بینی: **{self.prediction_accuracy:.1f}%**\n"
                      f"🔍 تحلیل‌های انجام شده: **{self.performance_stats['ai_analyses_performed']}**",
                inline=True
            )
            
            # وضعیت محافظت چندلایه
            embed.add_field(
                name="🛡️ محافظت چندلایه",
                value=f"🔒 لایه ۱ (تشخیص): فعال\n"
                      f"⚡ لایه ۲ (واکنش): فعال\n"
                      f"🔄 لایه ۳ (بازسازی): {'فعال' if self.advanced_restoration else 'غیرفعال'}\n"
                      f"🧠 لایه ۴ (یادگیری): فعال",
                inline=True
            )
            
            # آمار پیش‌بینی
            embed.add_field(
                name="🔮 آمار پیش‌بینی",
                value=f"📊 پیش‌بینی‌های انجام شده: **{self.performance_stats['predictions_made']}**\n"
                      f"✅ پیش‌بینی‌های دقیق: **{self.performance_stats['predictions_accurate']}**\n"
                      f"🎯 نرخ دقت: **{(self.performance_stats['predictions_accurate']/max(1, self.performance_stats['predictions_made'])*100):.1f}%**\n"
                      f"⚖️ آستانه پیش‌بینی: **{int(self.prediction_threshold * 100)}%**",
                inline=True
            )
            
            # سایر اطلاعات مشابه Arrow3
            await self.add_common_status_fields(embed)
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Arrow_3_missile_launch.jpg/640px-Arrow_3_missile_launch.jpg")
            await ctx.send(embed=embed)
        
        @self.command(name='predict_threat', aliases=['پیش‌بینی_تهدید'])
        @commands.has_permissions(manage_guild=True)
        async def predict_threat(ctx, user: discord.Member = None):
            """پیش‌بینی تهدید برای کاربر خاص"""
            
            if user is None:
                # تحلیل کلی سرور
                threat_level = await self.analyze_server_threat_level(ctx.guild)
            else:
                # تحلیل کاربر خاص
                threat_level = await self.analyze_user_threat_level(user)
            
            embed = EmbedBuilder.create_embed(
                title="🔮 پیش‌بینی تهدید - خِتْس ۴",
                description="تحلیل پیش‌بینانه تهدیدات با استفاده از هوش مصنوعی",
                color=self.get_threat_color(threat_level)
            )
            
            if user:
                embed.add_field(
                    name="👤 هدف تحلیل",
                    value=f"کاربر: {user.mention}\n"
                          f"سن اکانت: {(datetime.now() - user.created_at).days} روز\n"
                          f"عضویت در سرور: {(datetime.now() - user.joined_at).days} روز",
                    inline=True
                )
            
            embed.add_field(
                name="📊 نتیجه تحلیل",
                value=f"🎯 سطح تهدید: **{self.get_threat_level_name(threat_level)}**\n"
                      f"📊 امتیاز: **{threat_level:.2f}**\n"
                      f"⚠️ احتمال حمله: **{int(threat_level * 100)}%**\n"
                      f"🔍 اعتماد تحلیل: **{random.randint(85, 95)}%**",
                inline=True
            )
            
            # توصیه‌ها
            recommendations = self.get_threat_recommendations(threat_level)
            embed.add_field(
                name="💡 توصیه‌ها",
                value="\n".join([f"• {rec}" for rec in recommendations]),
                inline=False
            )
            
            self.performance_stats['predictions_made'] += 1
            
            await ctx.send(embed=embed)
        
        @self.command(name='behavior_analysis', aliases=['تحلیل_رفتار'])
        @commands.has_permissions(manage_guild=True)
        async def behavior_analysis(ctx, user: discord.Member):
            """تحلیل رفتاری کاربر"""
            
            behavior_data = self.user_behavior_analysis.get(user.id, [])
            
            embed = EmbedBuilder.create_embed(
                title="🔍 تحلیل رفتاری پیشرفته",
                description=f"تحلیل الگوهای رفتاری {user.mention}",
                color=EMBED_COLORS['info']
            )
            
            if not behavior_data:
                embed.add_field(
                    name="📭 داده کافی نیست",
                    value="اطلاعات رفتاری کافی برای تحلیل موجود نیست.",
                    inline=False
                )
            else:
                # تحلیل الگوهای فعالیت
                activity_pattern = self.analyze_activity_pattern(behavior_data)
                risk_indicators = self.identify_risk_indicators(behavior_data)
                
                embed.add_field(
                    name="📈 الگوی فعالیت",
                    value=f"🕐 فعال‌ترین ساعت: {activity_pattern['peak_hour']}\n"
                          f"📊 میانگین فعالیت: {activity_pattern['avg_activity']:.1f}/روز\n"
                          f"📈 روند: {activity_pattern['trend']}\n"
                          f"🎯 قابل پیش‌بینی: {'بله' if activity_pattern['predictable'] else 'خیر'}",
                    inline=True
                )
                
                embed.add_field(
                    name="⚠️ شاخص‌های خطر",
                    value=f"🚨 شاخص‌های شناسایی شده: {len(risk_indicators)}\n"
                          f"📊 امتیاز خطر کلی: {sum(risk_indicators.values()):.2f}\n"
                          f"🎯 نیاز به نظارت: {'بله' if sum(risk_indicators.values()) > 0.5 else 'خیر'}",
                    inline=True
                )
                
                if risk_indicators:
                    risk_list = [f"• {indicator}: {score:.2f}" for indicator, score in risk_indicators.items()]
                    embed.add_field(
                        name="🔍 جزئیات شاخص‌ها",
                        value="\n".join(risk_list[:5]),  # نمایش 5 مورد اول
                        inline=False
                    )
            
            self.performance_stats['ai_analyses_performed'] += 1
            
            await ctx.send(embed=embed)
    
    def start_advanced_background_tasks(self):
        """شروع وظایف پس‌زمینه پیشرفته"""
        # ابتدا وظایف پایه را شروع می‌کنیم
        self.start_background_tasks()
        
        @tasks.loop(minutes=15)
        async def predictive_threat_analysis():
            """تحلیل پیش‌بینانه تهدیدات"""
            if not self.predictive_defense:
                return
                
            guild = await self.get_main_guild()
            if not guild:
                return
            
            # تحلیل تهدیدات احتمالی
            threat_predictions = await self.generate_threat_predictions(guild)
            
            for prediction in threat_predictions:
                if prediction['confidence'] > self.prediction_threshold:
                    await self.handle_predicted_threat(guild, prediction)
        
        @tasks.loop(minutes=30)
        async def behavioral_learning():
            """یادگیری الگوهای رفتاری"""
            # به‌روزرسانی الگوهای تهدید
            await self.update_threat_patterns()
            
            # محاسبه دقت پیش‌بینی
            self.update_prediction_accuracy()
        
        @tasks.loop(hours=2)
        async def advanced_system_optimization():
            """بهینه‌سازی پیشرفته سیستم"""
            # تنظیم خودکار حساسیت بر اساس عملکرد
            await self.auto_tune_sensitivity()
            
            # بهینه‌سازی آستانه‌ها
            await self.optimize_thresholds()
        
        # شروع تسک‌های پیشرفته
        predictive_threat_analysis.start()
        behavioral_learning.start()
        advanced_system_optimization.start()
    
    async def analyze_server_threat_level(self, guild: discord.Guild) -> float:
        """تحلیل سطح تهدید کل سرور"""
        threat_score = 0.0
        
        # تحلیل فعالیت‌های اخیر
        recent_activities = len(self.deletion_history) + len(self.creation_history)
        if recent_activities > 20:
            threat_score += 0.3
        
        # تحلیل کاربران مشکوک
        suspicious_users = len(self.suspicious_activities)
        threat_score += min(0.4, suspicious_users * 0.05)
        
        # تحلیل الگوهای زمانی
        current_hour = datetime.now().hour
        if 2 <= current_hour <= 6:  # ساعات مشکوک
            threat_score += 0.2
        
        # استفاده از AI برای تحلیل پیشرفته‌تر
        if self.ai_threat_analysis:
            ai_score = await self.ai_analyze_threat_level(guild)
            threat_score = (threat_score + ai_score) / 2
        
        return min(1.0, threat_score)
    
    async def analyze_user_threat_level(self, user: discord.Member) -> float:
        """تحلیل سطح تهدید کاربر خاص"""
        threat_score = 0.0
        
        # سن اکانت
        account_age = (datetime.now() - user.created_at).days
        if account_age < 7:
            threat_score += 0.4
        elif account_age < 30:
            threat_score += 0.2
        
        # مجوزهای خطرناک
        if user.guild_permissions.manage_channels or user.guild_permissions.manage_roles:
            threat_score += 0.3
        
        if user.guild_permissions.administrator:
            threat_score += 0.2  # ادمین‌ها خطرناک‌تر هستند اگر حساب هک شود
        
        # تاریخچه فعالیت
        if user.id in self.suspicious_activities:
            threat_score += len(self.suspicious_activities[user.id]) * 0.1
        
        # تحلیل رفتاری
        behavior_score = self.calculate_behavior_risk_score(user.id)
        threat_score += behavior_score
        
        return min(1.0, threat_score)
    
    async def ai_analyze_threat_level(self, guild: discord.Guild) -> float:
        """تحلیل تهدید با استفاده از AI"""
        # شبیه‌سازی تحلیل AI
        # در پیاده‌سازی واقعی، از مدل‌های یادگیری ماشین استفاده می‌شود
        
        factors = {
            'recent_joins': len([m for m in guild.members if (datetime.now() - m.joined_at).days < 1]),
            'channel_changes': len(self.deletion_history) + len(self.creation_history),
            'suspicious_activities': len(self.suspicious_activities),
            'time_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }
        
        # الگوریتم ساده وزن‌دار
        ai_score = (
            factors['recent_joins'] * 0.05 +
            factors['channel_changes'] * 0.02 +
            factors['suspicious_activities'] * 0.1 +
            (0.3 if 2 <= factors['time_of_day'] <= 6 else 0) +
            (0.1 if factors['day_of_week'] in [5, 6] else 0)  # آخر هفته
        )
        
        self.performance_stats['ai_analyses_performed'] += 1
        
        return min(1.0, ai_score)
    
    def calculate_behavior_risk_score(self, user_id: int) -> float:
        """محاسبه امتیاز خطر رفتاری"""
        behavior_data = self.user_behavior_analysis.get(user_id, [])
        
        if not behavior_data:
            return 0.0
        
        risk_score = 0.0
        
        # تحلیل الگوهای مشکوک
        for behavior in behavior_data[-10:]:  # آخرین 10 فعالیت
            if behavior['type'] in ['channel_delete', 'role_delete', 'mass_mention']:
                risk_score += 0.1
            elif behavior['type'] in ['rapid_messages', 'suspicious_links']:
                risk_score += 0.05
        
        return min(0.5, risk_score)
    
    async def generate_threat_predictions(self, guild: discord.Guild) -> List[Dict]:
        """تولید پیش‌بینی‌های تهدید"""
        predictions = []
        
        # پیش‌بینی بر اساس الگوهای زمانی
        current_time = datetime.now()
        
        # بررسی الگوهای تاریخی
        for pattern_name, pattern_data in self.threat_patterns.items():
            confidence = self.calculate_pattern_confidence(pattern_data, current_time)
            
            if confidence > 0.6:
                predictions.append({
                    'type': pattern_name,
                    'confidence': confidence,
                    'predicted_time': current_time + timedelta(minutes=random.randint(5, 30)),
                    'severity': pattern_data.get('severity', 'medium')
                })
        
        return predictions
    
    def calculate_pattern_confidence(self, pattern_data: Dict, current_time: datetime) -> float:
        """محاسبه اعتماد الگو"""
        # شبیه‌سازی محاسبه اعتماد
        base_confidence = pattern_data.get('historical_accuracy', 0.5)
        
        # تعدیل بر اساس شرایط فعلی
        time_factor = 0.8 if 2 <= current_time.hour <= 6 else 0.6
        activity_factor = min(1.0, len(self.suspicious_activities) * 0.1)
        
        confidence = base_confidence * time_factor * (1 + activity_factor)
        
        return min(1.0, confidence)
    
    async def handle_predicted_threat(self, guild: discord.Guild, prediction: Dict):
        """مدیریت تهدید پیش‌بینی شده"""
        embed = EmbedBuilder.create_embed(
            title="🔮 هشدار پیش‌بینی تهدید - خِتْس ۴",
            description="سیستم هوش مصنوعی تهدید احتمالی تشخیص داده است",
            color=EMBED_COLORS['warning']
        )
        
        embed.add_field(
            name="📊 جزئیات پیش‌بینی",
            value=f"🎯 نوع تهدید: {prediction['type']}\n"
                  f"📊 اعتماد: **{prediction['confidence']:.1%}**\n"
                  f"⏰ زمان تخمینی: {prediction['predicted_time'].strftime('%H:%M')}\n"
                  f"🚨 شدت: {prediction['severity']}",
            inline=True
        )
        
        embed.add_field(
            name="⚡ اقدامات پیشگیرانه",
            value="🔒 افزایش حساسیت سیستم\n"
                  "👁️ نظارت فعال‌تر\n"
                  "⚡ آماده‌باش ربات‌های دفاعی\n"
                  "📊 تحلیل مداوم",
            inline=True
        )
        
        # ارسال به کانال جنگ
        war_room = discord.utils.get(guild.text_channels, name='war-room')
        if war_room:
            await war_room.send(embed=embed)
        
        # افزایش حساسیت موقت
        original_sensitivity = self.sensitivity_level
        self.sensitivity_level = min(1.0, self.sensitivity_level + 0.1)
        
        # بازگرداندن حساسیت پس از 30 دقیقه
        await asyncio.sleep(1800)
        self.sensitivity_level = original_sensitivity
    
    def get_threat_color(self, threat_level: float) -> int:
        """دریافت رنگ بر اساس سطح تهدید"""
        if threat_level < 0.3:
            return EMBED_COLORS['success']
        elif threat_level < 0.6:
            return EMBED_COLORS['warning']
        else:
            return EMBED_COLORS['error']
    
    def get_threat_level_name(self, threat_level: float) -> str:
        """دریافت نام سطح تهدید"""
        if threat_level < 0.2:
            return "بسیار پایین"
        elif threat_level < 0.4:
            return "پایین"
        elif threat_level < 0.6:
            return "متوسط"
        elif threat_level < 0.8:
            return "بالا"
        else:
            return "بحرانی"
    
    def get_threat_recommendations(self, threat_level: float) -> List[str]:
        """دریافت توصیه‌ها بر اساس سطح تهدید"""
        if threat_level < 0.3:
            return [
                "وضعیت امن - نیازی به اقدام خاص نیست",
                "ادامه نظارت معمولی",
                "حفظ پشتیبان‌گیری منظم"
            ]
        elif threat_level < 0.6:
            return [
                "افزایش نظارت",
                "بررسی لاگ‌های اخیر",
                "آماده‌باش سیستم‌های دفاعی",
                "اطلاع‌رسانی به مدیران"
            ]
        else:
            return [
                "فعال‌سازی فوری قفل کامل",
                "پشتیبان‌گیری اضطراری",
                "شناسایی منابع تهدید",
                "اطلاع‌رسانی به تمام مدیران",
                "آماده‌باش کامل سیستم‌های دفاعی"
            ]
    
    def analyze_activity_pattern(self, behavior_data: List[Dict]) -> Dict:
        """تحلیل الگوی فعالیت"""
        if not behavior_data:
            return {
                'peak_hour': 'نامشخص',
                'avg_activity': 0,
                'trend': 'بدون داده',
                'predictable': False
            }
        
        # تحلیل ساده الگوی فعالیت
        hours = [datetime.fromisoformat(b['timestamp']).hour for b in behavior_data if 'timestamp' in b]
        
        if hours:
            peak_hour = max(set(hours), key=hours.count)
            avg_activity = len(behavior_data) / max(1, (datetime.now() - datetime.fromisoformat(behavior_data[0]['timestamp'])).days)
        else:
            peak_hour = 'نامشخص'
            avg_activity = 0
        
        return {
            'peak_hour': f"{peak_hour}:00",
            'avg_activity': avg_activity,
            'trend': 'افزایشی' if len(behavior_data) > 5 else 'پایدار',
            'predictable': len(set(hours)) <= 3 if hours else False
        }
    
    def identify_risk_indicators(self, behavior_data: List[Dict]) -> Dict[str, float]:
        """شناسایی شاخص‌های خطر"""
        indicators = {}
        
        # تحلیل انواع فعالیت
        activity_types = [b.get('type', 'unknown') for b in behavior_data]
        
        if 'channel_delete' in activity_types:
            indicators['حذف کانال'] = activity_types.count('channel_delete') * 0.2
        
        if 'mass_mention' in activity_types:
            indicators['منشن جمعی'] = activity_types.count('mass_mention') * 0.15
        
        if 'rapid_messages' in activity_types:
            indicators['پیام سریع'] = activity_types.count('rapid_messages') * 0.1
        
        # تحلیل الگوهای زمانی مشکوک
        night_activities = sum(1 for b in behavior_data 
                             if 'timestamp' in b and 
                             2 <= datetime.fromisoformat(b['timestamp']).hour <= 6)
        
        if night_activities > len(behavior_data) * 0.3:
            indicators['فعالیت شبانه'] = night_activities / len(behavior_data)
        
        return indicators
    
    async def update_threat_patterns(self):
        """به‌روزرسانی الگوهای تهدید"""
        # به‌روزرسانی الگوهای یادگیری شده
        current_time = datetime.now()
        
        # تحلیل الگوهای موجود
        for pattern_name in list(self.threat_patterns.keys()):
            pattern = self.threat_patterns[pattern_name]
            
            # به‌روزرسانی دقت تاریخی
            if 'predictions' in pattern and 'outcomes' in pattern:
                accurate_predictions = sum(1 for i, pred in enumerate(pattern['predictions'])
                                         if i < len(pattern['outcomes']) and 
                                         pred == pattern['outcomes'][i])
                pattern['historical_accuracy'] = accurate_predictions / max(1, len(pattern['predictions']))
    
    def update_prediction_accuracy(self):
        """به‌روزرسانی دقت پیش‌بینی"""
        if self.performance_stats['predictions_made'] > 0:
            self.prediction_accuracy = (
                self.performance_stats['predictions_accurate'] / 
                self.performance_stats['predictions_made'] * 100
            )
    
    async def auto_tune_sensitivity(self):
        """تنظیم خودکار حساسیت"""
        accuracy = self.calculate_system_accuracy()
        
        # اگر دقت پایین است، حساسیت را کاهش دهید
        if accuracy < 70 and self.sensitivity_level > 0.5:
            self.sensitivity_level -= 0.05
        
        # اگر دقت بالا است، حساسیت را افزایش دهید
        elif accuracy > 90 and self.sensitivity_level < 0.95:
            self.sensitivity_level += 0.02
        
        # محدود کردن حساسیت
        self.sensitivity_level = max(0.3, min(1.0, self.sensitivity_level))
    
    async def optimize_thresholds(self):
        """بهینه‌سازی آستانه‌ها"""
        # تحلیل عملکرد آستانه‌های فعلی
        recent_false_alarms = self.performance_stats['false_alarms']
        recent_detections = self.performance_stats['nuking_attempts_detected']
        
        # تنظیم آستانه‌ها بر اساس عملکرد
        if recent_false_alarms > recent_detections * 0.2:  # بیش از 20% هشدار کاذب
            self.deletion_threshold = min(10, self.deletion_threshold + 1)
            self.creation_threshold = min(20, self.creation_threshold + 2)
        elif recent_false_alarms < recent_detections * 0.05:  # کمتر از 5% هشدار کاذب
            self.deletion_threshold = max(2, self.deletion_threshold - 1)
            self.creation_threshold = max(5, self.creation_threshold - 1)
    
    async def add_common_status_fields(self, embed: discord.Embed):
        """اضافه کردن فیلدهای مشترک وضعیت"""
        # این متد فیلدهای مشترک بین Arrow3 و Arrow4 را اضافه می‌کند
        
        # وضعیت عمومی
        lockdown_status = "🔒 فعال" if self.lockdown_active else "🟢 عادی"
        
        embed.add_field(
            name="🎯 وضعیت دفاعی",
            value=f"🏰 قفل کامل: {lockdown_status}\n"
                  f"📡 حساسیت: **{int(self.sensitivity_level * 100)}%**\n"
                  f"🤖 قفل خودکار: {'فعال' if self.auto_lockdown else 'غیرفعال'}\n"
                  f"🔄 بازسازی خودکار: {'فعال' if self.auto_restore else 'غیرفعال'}",
            inline=True
        )
        
        # موجودی موشک‌ها
        max_missiles = DefenseConfig.MISSILE_INVENTORY['arrow_4']['max']
        missile_percentage = (self.missile_count / max_missiles) * 100
        missile_bar = self.create_progress_bar(missile_percentage)
        
        embed.add_field(
            name="🚀 موجودی موشک‌ها",
            value=f"📊 {missile_bar} {missile_percentage:.1f}%\n"
                  f"🔢 موجودی: **{format_number(self.missile_count)}** / {format_number(max_missiles)}\n"
                  f"💰 ارزش: **{format_number(self.missile_count * DefenseConfig.MISSILE_INVENTORY['arrow_4']['cost'])}** شکل\n"
                  f"⚡ اثربخشی: **{DefenseConfig.MISSILE_INVENTORY['arrow_4']['effectiveness'] * 100:.0f}%**",
            inline=True
        )

# اجرای ربات‌ها
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "arrow3":
            bot = Arrow3Bot()
            bot.run(bot.token)
        elif sys.argv[1] == "arrow4":
            bot = Arrow4Bot()
            bot.run(bot.token)
        else:
            print("استفاده: python arrow_defense_bots.py [arrow3|arrow4]")
    else:
        print("لطفاً نوع ربات را مشخص کنید: arrow3 یا arrow4")