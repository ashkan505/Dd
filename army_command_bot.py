"""
ربات فرماندهی کل ارتش - مرکز کنترل نظامی
Army Command Bot - Military Control Center

این ربات مسئول هماهنگی کل نیروهای مسلح و مدیریت عملیات نظامی است.
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
    GeminiAI, NotificationManager, EMOJIS, format_number
)
from config import (
    BotConfig, DefenseConfig, EMBED_COLORS, SYSTEM_MESSAGES
)

logger = logging.getLogger(__name__)

class MilitaryUnit:
    """کلاس واحد نظامی"""
    
    def __init__(self, unit_id: str, name: str, unit_type: str, capacity: int):
        self.unit_id = unit_id
        self.name = name
        self.unit_type = unit_type  # 'air', 'ground', 'naval'
        self.capacity = capacity
        self.current_personnel = 0
        self.equipment = {}
        self.status = "ready"  # ready, deployed, maintenance, training
        self.location = "base"
        self.missions_completed = 0
        self.creation_date = datetime.now()
        self.last_activity = datetime.now()
    
    def get_readiness(self) -> float:
        """محاسبه آمادگی واحد"""
        personnel_ratio = self.current_personnel / self.capacity
        equipment_ratio = len(self.equipment) / max(1, self.capacity // 10)
        
        base_readiness = (personnel_ratio + equipment_ratio) / 2
        
        # تعدیل بر اساس وضعیت
        status_multiplier = {
            'ready': 1.0,
            'training': 0.8,
            'maintenance': 0.5,
            'deployed': 0.9
        }
        
        return min(1.0, base_readiness * status_multiplier.get(self.status, 1.0))
    
    def to_dict(self) -> Dict:
        """تبدیل به دیکشنری"""
        return {
            'unit_id': self.unit_id,
            'name': self.name,
            'unit_type': self.unit_type,
            'capacity': self.capacity,
            'current_personnel': self.current_personnel,
            'equipment': self.equipment,
            'status': self.status,
            'location': self.location,
            'missions_completed': self.missions_completed,
            'creation_date': self.creation_date.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }

class MissionManager:
    """مدیریت مأموریت‌ها"""
    
    def __init__(self):
        self.active_missions = {}
        self.mission_history = deque(maxlen=100)
        self.mission_templates = self.load_mission_templates()
    
    def load_mission_templates(self) -> List[Dict]:
        """بارگذاری قالب‌های مأموریت"""
        return [
            {
                'name': 'گشت‌زنی هوایی',
                'type': 'patrol',
                'required_units': ['air'],
                'duration': 120,  # دقیقه
                'difficulty': 'easy',
                'rewards': {'xp': 50, 'prestige': 10}
            },
            {
                'name': 'تمرین مشترک',
                'type': 'training',
                'required_units': ['air', 'ground'],
                'duration': 180,
                'difficulty': 'medium',
                'rewards': {'xp': 100, 'prestige': 20}
            },
            {
                'name': 'عملیات دفاعی',
                'type': 'defense',
                'required_units': ['ground', 'air'],
                'duration': 240,
                'difficulty': 'hard',
                'rewards': {'xp': 200, 'prestige': 50}
            },
            {
                'name': 'ماموریت دریایی',
                'type': 'naval_patrol',
                'required_units': ['naval'],
                'duration': 300,
                'difficulty': 'medium',
                'rewards': {'xp': 150, 'prestige': 30}
            },
            {
                'name': 'عملیات ویژه',
                'type': 'special_ops',
                'required_units': ['ground', 'air', 'naval'],
                'duration': 480,
                'difficulty': 'very_hard',
                'rewards': {'xp': 500, 'prestige': 100}
            }
        ]
    
    def create_mission(self, template: Dict, assigned_units: List[str]) -> str:
        """ایجاد مأموریت جدید"""
        mission_id = f"MISSION-{len(self.active_missions) + 1:04d}"
        
        mission = {
            'mission_id': mission_id,
            'name': template['name'],
            'type': template['type'],
            'assigned_units': assigned_units,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(minutes=template['duration'])).isoformat(),
            'status': 'active',
            'difficulty': template['difficulty'],
            'rewards': template['rewards'],
            'progress': 0.0
        }
        
        self.active_missions[mission_id] = mission
        return mission_id
    
    def update_mission_progress(self, mission_id: str, progress: float):
        """به‌روزرسانی پیشرفت مأموریت"""
        if mission_id in self.active_missions:
            self.active_missions[mission_id]['progress'] = min(100.0, progress)
            
            # اگر مأموریت تکمیل شد
            if progress >= 100.0:
                self.complete_mission(mission_id)
    
    def complete_mission(self, mission_id: str) -> Dict:
        """تکمیل مأموریت"""
        if mission_id not in self.active_missions:
            return None
        
        mission = self.active_missions[mission_id]
        mission['status'] = 'completed'
        mission['completion_time'] = datetime.now().isoformat()
        
        # انتقال به تاریخچه
        self.mission_history.append(mission.copy())
        del self.active_missions[mission_id]
        
        return mission
    
    def get_suitable_missions(self, available_units: List[str]) -> List[Dict]:
        """دریافت مأموریت‌های مناسب"""
        suitable = []
        
        for template in self.mission_templates:
            required_units = set(template['required_units'])
            available_units_set = set(available_units)
            
            if required_units.issubset(available_units_set):
                suitable.append(template)
        
        return suitable

class ArmyCommandBot(BaseBot):
    """ربات فرماندهی کل ارتش"""
    
    def __init__(self):
        super().__init__(
            command_prefix=BotConfig.COMMAND_PREFIX,
            bot_name="فرماندهی کل ارتش",
            description="مرکز کنترل و هماهنگی نیروهای مسلح اسرائیل"
        )
        
        self.token = BotConfig.ARMY_COMMAND_TOKEN
        
        # سیستم‌های اصلی
        self.military_units = {}
        self.mission_manager = MissionManager()
        self.personnel_database = defaultdict(dict)
        
        # آمار و عملکرد
        self.military_stats = {
            'total_personnel': 0,
            'active_missions': 0,
            'completed_missions': 0,
            'units_created': 0,
            'training_hours': 0,
            'operational_readiness': 0.0
        }
        
        # سیستم رتبه‌بندی
        self.rank_system = {
            'enlisted': ['سرباز', 'سرباز یکم', 'جوخه‌دار'],
            'nco': ['گروه‌بان', 'استوار سوم', 'استوار دوم', 'استوار یکم'],
            'officers': ['ستوان سوم', 'ستوان دوم', 'ستوان یکم', 'سرگرد', 'سرهنگ', 'سرتیپ', 'سپهبد']
        }
        
        # تجهیزات نظامی
        self.military_equipment = {
            'air': {
                'F-35I': {'count': 0, 'max': 50, 'cost': 100000000},
                'F-16I': {'count': 0, 'max': 100, 'cost': 50000000},
                'AH-64': {'count': 0, 'max': 48, 'cost': 35000000}
            },
            'ground': {
                'Merkava-4': {'count': 0, 'max': 200, 'cost': 6000000},
                'Namer': {'count': 0, 'max': 150, 'cost': 3000000},
                'Iron-Dome': {'count': 0, 'max': 10, 'cost': 50000000}
            },
            'naval': {
                'Sa\'ar-6': {'count': 0, 'max': 6, 'cost': 500000000},
                'Dolphin-2': {'count': 0, 'max': 6, 'cost': 700000000},
                'Patrol-Boat': {'count': 0, 'max': 20, 'cost': 10000000}
            }
        }
        
        # وضعیت دفاعی
        self.defense_status = "NORMAL"
        self.alert_level = 1
        self.active_operations = {}
        
        # بارگذاری کامندها
        self.load_commands()
        
        # شروع وظایف دوره‌ای
        self.start_background_tasks()
        
        # ایجاد واحدهای پیش‌فرض
        self.create_default_units()
    
    def load_commands(self):
        """بارگذاری کامندهای ربات"""
        
        @self.command(name='army_status', aliases=['وضعیت_ارتش'])
        async def army_status(ctx):
            """نمایش وضعیت کل ارتش"""
            
            # محاسبه آمار کلی
            total_units = len(self.military_units)
            ready_units = len([u for u in self.military_units.values() if u.status == 'ready'])
            deployed_units = len([u for u in self.military_units.values() if u.status == 'deployed'])
            
            overall_readiness = self.calculate_overall_readiness()
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['military']} وضعیت فرماندهی کل ارتش",
                description="گزارش جامع نیروهای مسلح اسرائیل",
                color=EMBED_COLORS['military']
            )
            
            # وضعیت کلی
            status_emoji = self.get_defense_status_emoji(self.defense_status)
            embed.add_field(
                name="🎯 وضعیت کلی",
                value=f"{status_emoji} وضعیت دفاعی: **{self.defense_status}**\n"
                      f"🚨 سطح آمادگی: **{self.alert_level}**\n"
                      f"📊 آمادگی عملیاتی: **{overall_readiness:.1f}%**\n"
                      f"⚡ عملیات فعال: **{len(self.active_operations)}**",
                inline=True
            )
            
            # آمار واحدها
            embed.add_field(
                name="🏛️ واحدهای نظامی",
                value=f"📊 کل واحدها: **{total_units}**\n"
                      f"✅ آماده: **{ready_units}**\n"
                      f"🚀 مستقر: **{deployed_units}**\n"
                      f"🔧 تعمیر: **{len([u for u in self.military_units.values() if u.status == 'maintenance'])}**",
                inline=True
            )
            
            # آمار پرسنل
            total_personnel = sum(unit.current_personnel for unit in self.military_units.values())
            max_personnel = sum(unit.capacity for unit in self.military_units.values())
            
            embed.add_field(
                name="👥 پرسنل",
                value=f"👤 پرسنل فعال: **{format_number(total_personnel)}**\n"
                      f"📈 ظرفیت کل: **{format_number(max_personnel)}**\n"
                      f"📊 درصد پرسنل: **{(total_personnel/max(1,max_personnel)*100):.1f}%**\n"
                      f"🎖️ افسران: **{len([p for p in self.personnel_database.values() if p.get('rank_category') == 'officers'])}**",
                inline=True
            )
            
            # آمار مأموریت‌ها
            embed.add_field(
                name="🎯 مأموریت‌ها",
                value=f"🔄 فعال: **{len(self.mission_manager.active_missions)}**\n"
                      f"✅ تکمیل شده: **{len(self.mission_manager.mission_history)}**\n"
                      f"📈 نرخ موفقیت: **{self.calculate_mission_success_rate():.1f}%**\n"
                      f"⏰ مدت تمرین: **{format_number(self.military_stats['training_hours'])}** ساعت",
                inline=True
            )
            
            # تجهیزات
            total_air = sum(eq['count'] for eq in self.military_equipment['air'].values())
            total_ground = sum(eq['count'] for eq in self.military_equipment['ground'].values())
            total_naval = sum(eq['count'] for eq in self.military_equipment['naval'].values())
            
            embed.add_field(
                name="🛡️ تجهیزات",
                value=f"✈️ هوایی: **{total_air}**\n"
                      f"🚗 زمینی: **{total_ground}**\n"
                      f"🚢 دریایی: **{total_naval}**\n"
                      f"💰 ارزش کل: **{self.calculate_equipment_value():,}** شکل",
                inline=True
            )
            
            # عملیات اخیر
            recent_missions = list(self.mission_manager.mission_history)[-3:]
            if recent_missions:
                mission_text = []
                for mission in reversed(recent_missions):
                    completion_time = datetime.fromisoformat(mission['completion_time']).strftime('%m/%d %H:%M')
                    mission_text.append(f"• {completion_time}: {mission['name']}")
                
                embed.add_field(
                    name="📋 عملیات اخیر",
                    value='\n'.join(mission_text),
                    inline=False
                )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Israel.svg/640px-Flag_of_Israel.svg.png")
            embed.set_footer(text=f"آخرین به‌روزرسانی: {TimeManager.format_time(TimeManager.get_current_time())}")
            
            await ctx.send(embed=embed)
        
        @self.command(name='create_unit', aliases=['ایجاد_واحد'])
        @commands.has_any_role('ژنرال', 'سرهنگ', 'نخست‌وزیر')
        async def create_unit(ctx, unit_type: str, name: str, capacity: int = 100):
            """ایجاد واحد نظامی جدید"""
            
            if unit_type.lower() not in ['air', 'ground', 'naval', 'هوایی', 'زمینی', 'دریایی']:
                embed = EmbedBuilder.error_embed(
                    "نوع واحد نامعتبر",
                    "نوع واحد باید یکی از موارد زیر باشد: air, ground, naval"
                )
                await ctx.send(embed=embed)
                return
            
            # تبدیل نام فارسی به انگلیسی
            type_mapping = {'هوایی': 'air', 'زمینی': 'ground', 'دریایی': 'naval'}
            unit_type = type_mapping.get(unit_type.lower(), unit_type.lower())
            
            capacity = max(10, min(1000, capacity))  # محدود کردن ظرفیت
            
            # ایجاد واحد
            unit_id = f"{unit_type.upper()}-{len([u for u in self.military_units.values() if u.unit_type == unit_type]) + 1:03d}"
            
            new_unit = MilitaryUnit(unit_id, name, unit_type, capacity)
            self.military_units[unit_id] = new_unit
            
            self.military_stats['units_created'] += 1
            
            embed = EmbedBuilder.success_embed(
                "واحد ایجاد شد",
                f"واحد {name} با موفقیت ایجاد شد."
            )
            
            embed.add_field(
                name="📊 مشخصات واحد",
                value=f"🆔 شناسه: `{unit_id}`\n"
                      f"📛 نام: {name}\n"
                      f"🏷️ نوع: {self.get_unit_type_persian(unit_type)}\n"
                      f"👥 ظرفیت: {capacity} نفر\n"
                      f"📅 تاریخ ایجاد: {TimeManager.format_time(new_unit.creation_date)}",
                inline=True
            )
            
            embed.add_field(
                name="⚡ وضعیت اولیه",
                value=f"📊 وضعیت: آماده\n"
                      f"📍 مکان: پایگاه\n"
                      f"👤 پرسنل: 0/{capacity}\n"
                      f"🎯 آمادگی: 0%",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
            # اعلام در کانال مربوطه
            await self.announce_unit_creation(ctx.guild, new_unit, ctx.author)
        
        @self.command(name='list_units', aliases=['لیست_واحدها'])
        async def list_units(ctx, unit_type: str = None):
            """نمایش لیست واحدهای نظامی"""
            
            units_to_show = list(self.military_units.values())
            
            # فیلتر بر اساس نوع
            if unit_type:
                type_mapping = {'هوایی': 'air', 'زمینی': 'ground', 'دریایی': 'naval'}
                unit_type = type_mapping.get(unit_type.lower(), unit_type.lower())
                units_to_show = [u for u in units_to_show if u.unit_type == unit_type]
            
            if not units_to_show:
                embed = EmbedBuilder.error_embed(
                    "واحدی یافت نشد",
                    "هیچ واحد نظامی با مشخصات مورد نظر یافت نشد."
                )
                await ctx.send(embed=embed)
                return
            
            embed = EmbedBuilder.create_embed(
                title=f"📋 لیست واحدهای نظامی",
                description=f"تعداد واحدها: {len(units_to_show)}",
                color=EMBED_COLORS['military']
            )
            
            # گروه‌بندی بر اساس نوع
            units_by_type = defaultdict(list)
            for unit in units_to_show:
                units_by_type[unit.unit_type].append(unit)
            
            for unit_type, units in units_by_type.items():
                unit_list = []
                for unit in units[:10]:  # نمایش حداکثر 10 واحد در هر نوع
                    readiness = unit.get_readiness() * 100
                    status_emoji = self.get_unit_status_emoji(unit.status)
                    
                    unit_list.append(
                        f"{status_emoji} **{unit.name}** (`{unit.unit_id}`)\n"
                        f"   👥 {unit.current_personnel}/{unit.capacity} | "
                        f"📊 {readiness:.0f}% | 📍 {unit.location}"
                    )
                
                embed.add_field(
                    name=f"{self.get_unit_type_emoji(unit_type)} {self.get_unit_type_persian(unit_type)} ({len(units)})",
                    value='\n'.join(unit_list) if unit_list else "واحدی موجود نیست",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name='unit_info', aliases=['اطلاعات_واحد'])
        async def unit_info(ctx, unit_id: str):
            """نمایش اطلاعات تفصیلی واحد"""
            
            unit = self.military_units.get(unit_id.upper())
            if not unit:
                embed = EmbedBuilder.error_embed(
                    "واحد یافت نشد",
                    f"واحد با شناسه `{unit_id}` یافت نشد."
                )
                await ctx.send(embed=embed)
                return
            
            readiness = unit.get_readiness() * 100
            
            embed = EmbedBuilder.create_embed(
                title=f"{self.get_unit_type_emoji(unit.unit_type)} {unit.name}",
                description=f"اطلاعات تفصیلی واحد `{unit.unit_id}`",
                color=EMBED_COLORS['military']
            )
            
            # اطلاعات پایه
            embed.add_field(
                name="📊 مشخصات کلی",
                value=f"🆔 شناسه: `{unit.unit_id}`\n"
                      f"🏷️ نوع: {self.get_unit_type_persian(unit.unit_type)}\n"
                      f"👥 پرسنل: {unit.current_personnel}/{unit.capacity}\n"
                      f"📍 مکان: {unit.location}\n"
                      f"📅 تاریخ ایجاد: {TimeManager.format_time(unit.creation_date)}",
                inline=True
            )
            
            # وضعیت عملیاتی
            status_emoji = self.get_unit_status_emoji(unit.status)
            embed.add_field(
                name="⚡ وضعیت عملیاتی",
                value=f"{status_emoji} وضعیت: {self.get_unit_status_persian(unit.status)}\n"
                      f"📊 آمادگی: **{readiness:.1f}%**\n"
                      f"🎯 مأموریت‌ها: {unit.missions_completed}\n"
                      f"⏰ آخرین فعالیت: {TimeManager.format_time(unit.last_activity)}",
                inline=True
            )
            
            # تجهیزات
            if unit.equipment:
                equipment_list = []
                for eq_name, eq_count in unit.equipment.items():
                    equipment_list.append(f"• {eq_name}: {eq_count}")
                
                embed.add_field(
                    name="🛡️ تجهیزات",
                    value='\n'.join(equipment_list[:10]),
                    inline=True
                )
            
            # نمودار آمادگی
            readiness_bar = self.create_readiness_bar(readiness)
            embed.add_field(
                name="📈 نمودار آمادگی",
                value=f"{readiness_bar} {readiness:.1f}%",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='assign_personnel', aliases=['تخصیص_پرسنل'])
        @commands.has_any_role('ژنرال', 'سرهنگ')
        async def assign_personnel(ctx, unit_id: str, member: discord.Member, rank: str = 'سرباز'):
            """تخصیص پرسنل به واحد"""
            
            unit = self.military_units.get(unit_id.upper())
            if not unit:
                embed = EmbedBuilder.error_embed(
                    "واحد یافت نشد",
                    f"واحد با شناسه `{unit_id}` یافت نشد."
                )
                await ctx.send(embed=embed)
                return
            
            # بررسی ظرفیت
            if unit.current_personnel >= unit.capacity:
                embed = EmbedBuilder.error_embed(
                    "واحد پر است",
                    f"واحد {unit.name} به حداکثر ظرفیت رسیده است."
                )
                await ctx.send(embed=embed)
                return
            
            # تخصیص پرسنل
            self.personnel_database[member.id] = {
                'unit_id': unit_id.upper(),
                'rank': rank,
                'join_date': datetime.now().isoformat(),
                'assigned_by': ctx.author.id
            }
            
            unit.current_personnel += 1
            unit.last_activity = datetime.now()
            
            # اعطای رول
            soldier_role = discord.utils.get(ctx.guild.roles, name=rank)
            if soldier_role:
                await member.add_roles(soldier_role)
            
            embed = EmbedBuilder.success_embed(
                "پرسنل تخصیص یافت",
                f"{member.mention} به واحد {unit.name} تخصیص یافت."
            )
            
            embed.add_field(
                name="📊 جزئیات تخصیص",
                value=f"👤 فرد: {member.mention}\n"
                      f"🏛️ واحد: {unit.name} (`{unit_id.upper()}`)\n"
                      f"🎖️ رتبه: {rank}\n"
                      f"👥 پرسنل واحد: {unit.current_personnel}/{unit.capacity}\n"
                      f"📅 تاریخ: {TimeManager.format_time(datetime.now())}",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='start_mission', aliases=['شروع_مأموریت'])
        @commands.has_any_role('ژنرال', 'سرهنگ', 'سرگرد')
        async def start_mission(ctx, mission_type: str = None):
            """شروع مأموریت جدید"""
            
            # دریافت واحدهای آماده
            ready_units = [unit for unit in self.military_units.values() if unit.status == 'ready']
            
            if not ready_units:
                embed = EmbedBuilder.error_embed(
                    "واحد آماده‌ای موجود نیست",
                    "برای شروع مأموریت، حداقل یک واحد آماده نیاز است."
                )
                await ctx.send(embed=embed)
                return
            
            # دریافت نوع واحدهای موجود
            available_unit_types = list(set(unit.unit_type for unit in ready_units))
            
            # دریافت مأموریت‌های مناسب
            suitable_missions = self.mission_manager.get_suitable_missions(available_unit_types)
            
            if not suitable_missions:
                embed = EmbedBuilder.error_embed(
                    "مأموریت مناسبی یافت نشد",
                    "برای واحدهای موجود، مأموریت مناسبی یافت نشد."
                )
                await ctx.send(embed=embed)
                return
            
            # انتخاب مأموریت
            if mission_type:
                selected_mission = next((m for m in suitable_missions if m['type'] == mission_type), None)
                if not selected_mission:
                    embed = EmbedBuilder.error_embed(
                        "نوع مأموریت نامعتبر",
                        f"مأموریت از نوع `{mission_type}` یافت نشد یا امکان‌پذیر نیست."
                    )
                    await ctx.send(embed=embed)
                    return
            else:
                # انتخاب تصادفی
                selected_mission = random.choice(suitable_missions)
            
            # انتخاب واحدهای مورد نیاز
            required_unit_types = selected_mission['required_units']
            assigned_units = []
            
            for unit_type in required_unit_types:
                suitable_units = [u for u in ready_units if u.unit_type == unit_type and u.unit_id not in assigned_units]
                if suitable_units:
                    # انتخاب بهترین واحد (بیشترین آمادگی)
                    best_unit = max(suitable_units, key=lambda x: x.get_readiness())
                    assigned_units.append(best_unit.unit_id)
                    best_unit.status = 'deployed'
                    best_unit.last_activity = datetime.now()
            
            # ایجاد مأموریت
            mission_id = self.mission_manager.create_mission(selected_mission, assigned_units)
            
            embed = EmbedBuilder.success_embed(
                "مأموریت آغاز شد",
                f"مأموریت **{selected_mission['name']}** با موفقیت آغاز شد."
            )
            
            embed.add_field(
                name="📊 مشخصات مأموریت",
                value=f"🆔 شناسه: `{mission_id}`\n"
                      f"📛 نام: {selected_mission['name']}\n"
                      f"🏷️ نوع: {selected_mission['type']}\n"
                      f"⏰ مدت: {selected_mission['duration']} دقیقه\n"
                      f"📊 سختی: {selected_mission['difficulty']}",
                inline=True
            )
            
            # واحدهای تخصیص یافته
            unit_names = []
            for unit_id in assigned_units:
                unit = self.military_units[unit_id]
                unit_names.append(f"• {unit.name} (`{unit_id}`)")
            
            embed.add_field(
                name="🏛️ واحدهای تخصیص یافته",
                value='\n'.join(unit_names),
                inline=True
            )
            
            # پاداش‌ها
            rewards = selected_mission['rewards']
            embed.add_field(
                name="🏆 پاداش‌های مورد انتظار",
                value=f"⭐ تجربه: {rewards['xp']} XP\n"
                      f"🏅 اعتبار: {rewards['prestige']} امتیاز",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
            # اعلام در کانال عملیات
            await self.announce_mission_start(ctx.guild, mission_id, selected_mission, assigned_units)
        
        @self.command(name='mission_status', aliases=['وضعیت_مأموریت'])
        async def mission_status(ctx, mission_id: str = None):
            """نمایش وضعیت مأموریت‌ها"""
            
            if mission_id:
                # نمایش مأموریت خاص
                mission = self.mission_manager.active_missions.get(mission_id.upper())
                if not mission:
                    embed = EmbedBuilder.error_embed(
                        "مأموریت یافت نشد",
                        f"مأموریت با شناسه `{mission_id}` یافت نشد یا تکمیل شده است."
                    )
                    await ctx.send(embed=embed)
                    return
                
                embed = await self.create_mission_detail_embed(mission)
                await ctx.send(embed=embed)
                
            else:
                # نمایش تمام مأموریت‌های فعال
                active_missions = list(self.mission_manager.active_missions.values())
                
                if not active_missions:
                    embed = EmbedBuilder.create_embed(
                        title="📋 وضعیت مأموریت‌ها",
                        description="در حال حاضر مأموریت فعالی وجود ندارد.",
                        color=EMBED_COLORS['info']
                    )
                    await ctx.send(embed=embed)
                    return
                
                embed = EmbedBuilder.create_embed(
                    title="📋 مأموریت‌های فعال",
                    description=f"تعداد مأموریت‌های فعال: {len(active_missions)}",
                    color=EMBED_COLORS['military']
                )
                
                for mission in active_missions[:10]:  # نمایش حداکثر 10 مأموریت
                    start_time = datetime.fromisoformat(mission['start_time'])
                    end_time = datetime.fromisoformat(mission['end_time'])
                    remaining = end_time - datetime.now()
                    
                    if remaining.total_seconds() > 0:
                        time_left = f"{int(remaining.total_seconds() // 60)} دقیقه"
                    else:
                        time_left = "آماده تکمیل"
                    
                    embed.add_field(
                        name=f"🎯 {mission['name']} (`{mission['mission_id']}`)",
                        value=f"📊 پیشرفت: {mission['progress']:.0f}%\n"
                              f"⏰ زمان باقی‌مانده: {time_left}\n"
                              f"🏛️ واحدها: {len(mission['assigned_units'])}",
                        inline=True
                    )
                
                await ctx.send(embed=embed)
        
        @self.command(name='set_defense_status', aliases=['تنظیم_وضعیت_دفاعی'])
        @commands.has_any_role('نخست‌وزیر', 'ژنرال')
        async def set_defense_status(ctx, status: str, alert_level: int = None):
            """تنظیم وضعیت دفاعی"""
            
            valid_statuses = ['NORMAL', 'ELEVATED', 'HIGH', 'CRITICAL', 'عادی', 'بالا', 'بحرانی']
            
            if status.upper() not in [s.upper() for s in valid_statuses]:
                embed = EmbedBuilder.error_embed(
                    "وضعیت نامعتبر",
                    "وضعیت دفاعی باید یکی از موارد زیر باشد: NORMAL, ELEVATED, HIGH, CRITICAL"
                )
                await ctx.send(embed=embed)
                return
            
            # تبدیل نام فارسی
            status_mapping = {'عادی': 'NORMAL', 'بالا': 'HIGH', 'بحرانی': 'CRITICAL'}
            status = status_mapping.get(status, status.upper())
            
            old_status = self.defense_status
            self.defense_status = status
            
            if alert_level:
                self.alert_level = max(1, min(5, alert_level))
            
            # اعمال تغییرات بر واحدها
            await self.apply_defense_status_changes()
            
            embed = EmbedBuilder.success_embed(
                "وضعیت دفاعی تغییر کرد",
                f"وضعیت دفاعی از **{old_status}** به **{status}** تغییر کرد."
            )
            
            embed.add_field(
                name="📊 جزئیات تغییر",
                value=f"🚨 وضعیت جدید: **{status}**\n"
                      f"📈 سطح آمادگی: **{self.alert_level}**\n"
                      f"👤 تغییر توسط: {ctx.author.mention}\n"
                      f"⏰ زمان: {TimeManager.format_time(datetime.now())}",
                inline=True
            )
            
            # اقدامات انجام شده
            actions = []
            if status == 'CRITICAL':
                actions.extend([
                    "🚨 تمام واحدها در حالت آماده‌باش قرار گرفتند",
                    "⚡ مأموریت‌های غیرضروری لغو شدند",
                    "📡 سیستم‌های دفاعی فعال شدند"
                ])
            elif status == 'HIGH':
                actions.extend([
                    "🔔 واحدهای کلیدی در آماده‌باش",
                    "📊 نظارت تشدید شد"
                ])
            
            if actions:
                embed.add_field(
                    name="⚡ اقدامات انجام شده",
                    value='\n'.join(actions),
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
            # اعلام در کانال‌های مربوطه
            await self.announce_defense_status_change(ctx.guild, old_status, status)
        
        @self.command(name='equipment_status', aliases=['وضعیت_تجهیزات'])
        async def equipment_status(ctx, equipment_type: str = None):
            """نمایش وضعیت تجهیزات نظامی"""
            
            embed = EmbedBuilder.create_embed(
                title="🛡️ وضعیت تجهیزات نظامی",
                description="گزارش جامع تجهیزات نیروهای مسلح",
                color=EMBED_COLORS['military']
            )
            
            if equipment_type:
                # نمایش نوع خاص
                type_mapping = {'هوایی': 'air', 'زمینی': 'ground', 'دریایی': 'naval'}
                equipment_type = type_mapping.get(equipment_type.lower(), equipment_type.lower())
                
                if equipment_type not in self.military_equipment:
                    embed = EmbedBuilder.error_embed(
                        "نوع تجهیزات نامعتبر",
                        "نوع تجهیزات باید یکی از موارد زیر باشد: air, ground, naval"
                    )
                    await ctx.send(embed=embed)
                    return
                
                equipment_dict = {equipment_type: self.military_equipment[equipment_type]}
            else:
                equipment_dict = self.military_equipment
            
            for eq_type, equipment in equipment_dict.items():
                equipment_list = []
                total_value = 0
                
                for eq_name, eq_data in equipment.items():
                    count = eq_data['count']
                    max_count = eq_data['max']
                    cost = eq_data['cost']
                    value = count * cost
                    total_value += value
                    
                    percentage = (count / max_count) * 100 if max_count > 0 else 0
                    status_emoji = "🟢" if percentage > 70 else "🟡" if percentage > 30 else "🔴"
                    
                    equipment_list.append(
                        f"{status_emoji} **{eq_name}**: {count}/{max_count} ({percentage:.0f}%)\n"
                        f"   💰 ارزش: {format_number(value)} شکل"
                    )
                
                embed.add_field(
                    name=f"{self.get_unit_type_emoji(eq_type)} {self.get_unit_type_persian(eq_type)}",
                    value='\n'.join(equipment_list) + f"\n\n💎 **کل ارزش**: {format_number(total_value)} شکل",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name='army_report', aliases=['گزارش_ارتش'])
        @commands.has_any_role('نخست‌وزیر', 'ژنرال')
        async def army_report(ctx):
            """گزارش تفصیلی ارتش برای مقامات"""
            
            # تولید گزارش با AI
            report_data = {
                'total_units': len(self.military_units),
                'total_personnel': sum(unit.current_personnel for unit in self.military_units.values()),
                'active_missions': len(self.mission_manager.active_missions),
                'defense_status': self.defense_status,
                'overall_readiness': self.calculate_overall_readiness()
            }
            
            ai_report = await self.ai.generate_content(
                f"یک گزارش نظامی رسمی و تفصیلی برای فرماندهی کل ارتش اسرائیل بنویس. "
                f"داده‌ها: {json.dumps(report_data, ensure_ascii=False)}. "
                f"گزارش باید شامل تحلیل وضعیت، نقاط قوت و ضعف، و توصیه‌های عملیاتی باشد."
            )
            
            embed = EmbedBuilder.create_embed(
                title="📊 گزارش تفصیلی فرماندهی کل ارتش",
                description="گزارش محرمانه برای مقامات عالی",
                color=EMBED_COLORS['military']
            )
            
            # خلاصه آمار
            embed.add_field(
                name="📈 خلاصه آمار",
                value=f"🏛️ واحدهای فعال: {report_data['total_units']}\n"
                      f"👥 کل پرسنل: {format_number(report_data['total_personnel'])}\n"
                      f"🎯 مأموریت‌های فعال: {report_data['active_missions']}\n"
                      f"📊 آمادگی کل: {report_data['overall_readiness']:.1f}%\n"
                      f"🚨 وضعیت دفاعی: {report_data['defense_status']}",
                inline=True
            )
            
            # گزارش AI
            embed.add_field(
                name="🤖 تحلیل هوشمند",
                value=ai_report[:1000] + "..." if len(ai_report) > 1000 else ai_report,
                inline=False
            )
            
            embed.add_field(
                name="🔒 طبقه‌بندی",
                value="**محرمانه** - فقط برای مقامات مجاز\n"
                      f"📅 تاریخ گزارش: {TimeManager.format_time(datetime.now())}\n"
                      f"👤 درخواست‌کننده: {ctx.author.mention}",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    def start_background_tasks(self):
        """شروع وظایف پس‌زمینه"""
        
        @tasks.loop(minutes=15)
        async def update_missions():
            """به‌روزرسانی وضعیت مأموریت‌ها"""
            current_time = datetime.now()
            completed_missions = []
            
            for mission_id, mission in self.mission_manager.active_missions.items():
                end_time = datetime.fromisoformat(mission['end_time'])
                
                if current_time >= end_time:
                    # تکمیل مأموریت
                    completed_mission = self.mission_manager.complete_mission(mission_id)
                    if completed_mission:
                        completed_missions.append(completed_mission)
                        
                        # آزاد کردن واحدها
                        for unit_id in completed_mission['assigned_units']:
                            if unit_id in self.military_units:
                                unit = self.military_units[unit_id]
                                unit.status = 'ready'
                                unit.missions_completed += 1
                                unit.last_activity = current_time
                else:
                    # به‌روزرسانی پیشرفت
                    total_duration = (end_time - datetime.fromisoformat(mission['start_time'])).total_seconds()
                    elapsed_time = (current_time - datetime.fromisoformat(mission['start_time'])).total_seconds()
                    progress = min(100.0, (elapsed_time / total_duration) * 100)
                    
                    self.mission_manager.update_mission_progress(mission_id, progress)
            
            # اعلام تکمیل مأموریت‌ها
            for completed_mission in completed_missions:
                guild = await self.get_main_guild()
                if guild:
                    await self.announce_mission_completion(guild, completed_mission)
        
        @tasks.loop(hours=6)
        async def generate_random_missions():
            """تولید مأموریت‌های تصادفی"""
            if random.random() < 0.3:  # ۳۰٪ احتمال
                guild = await self.get_main_guild()
                if guild:
                    await self.generate_random_mission(guild)
        
        @tasks.loop(hours=1)
        async def update_unit_status():
            """به‌روزرسانی وضعیت واحدها"""
            current_time = datetime.now()
            
            for unit in self.military_units.values():
                # بازگشت واحدهای در تعمیر به حالت آماده
                if unit.status == 'maintenance':
                    time_since_maintenance = (current_time - unit.last_activity).hours
                    if time_since_maintenance >= 24:  # 24 ساعت تعمیر
                        unit.status = 'ready'
                        unit.last_activity = current_time
        
        @tasks.loop(hours=24)
        async def daily_report():
            """گزارش روزانه"""
            guild = await self.get_main_guild()
            if guild:
                await self.send_daily_report(guild)
        
        # شروع تسک‌ها
        update_missions.start()
        generate_random_missions.start()
        update_unit_status.start()
        daily_report.start()
    
    def create_default_units(self):
        """ایجاد واحدهای پیش‌فرض"""
        default_units = [
            {'type': 'air', 'name': 'سرب هوایی ۱', 'capacity': 200},
            {'type': 'air', 'name': 'سرب هوایی ۲', 'capacity': 180},
            {'type': 'ground', 'name': 'تیپ زرهی ۱', 'capacity': 500},
            {'type': 'ground', 'name': 'تیپ پیاده ۱', 'capacity': 800},
            {'type': 'naval', 'name': 'ناوگان شمال', 'capacity': 300},
            {'type': 'naval', 'name': 'ناوگان جنوب', 'capacity': 250}
        ]
        
        for unit_data in default_units:
            unit_id = f"{unit_data['type'].upper()}-{len([u for u in self.military_units.values() if u.unit_type == unit_data['type']]) + 1:03d}"
            unit = MilitaryUnit(unit_id, unit_data['name'], unit_data['type'], unit_data['capacity'])
            
            # تخصیص پرسنل اولیه
            unit.current_personnel = random.randint(unit.capacity // 3, unit.capacity // 2)
            
            # تخصیص تجهیزات اولیه
            if unit_data['type'] == 'air':
                unit.equipment = {'F-16I': random.randint(5, 15), 'AH-64': random.randint(2, 8)}
            elif unit_data['type'] == 'ground':
                unit.equipment = {'Merkava-4': random.randint(10, 30), 'Namer': random.randint(15, 40)}
            elif unit_data['type'] == 'naval':
                unit.equipment = {'Patrol-Boat': random.randint(2, 6), 'Sa\'ar-6': random.randint(1, 2)}
            
            self.military_units[unit_id] = unit
            self.military_stats['units_created'] += 1
    
    # متدهای کمکی
    def calculate_overall_readiness(self) -> float:
        """محاسبه آمادگی کلی ارتش"""
        if not self.military_units:
            return 0.0
        
        total_readiness = sum(unit.get_readiness() for unit in self.military_units.values())
        return (total_readiness / len(self.military_units)) * 100
    
    def calculate_mission_success_rate(self) -> float:
        """محاسبه نرخ موفقیت مأموریت‌ها"""
        total_missions = len(self.mission_manager.mission_history)
        if total_missions == 0:
            return 100.0
        
        successful_missions = len([m for m in self.mission_manager.mission_history if m.get('success', True)])
        return (successful_missions / total_missions) * 100
    
    def calculate_equipment_value(self) -> int:
        """محاسبه ارزش کل تجهیزات"""
        total_value = 0
        
        for eq_type, equipment in self.military_equipment.items():
            for eq_name, eq_data in equipment.items():
                total_value += eq_data['count'] * eq_data['cost']
        
        return total_value
    
    def get_unit_type_persian(self, unit_type: str) -> str:
        """تبدیل نوع واحد به فارسی"""
        mapping = {'air': 'هوایی', 'ground': 'زمینی', 'naval': 'دریایی'}
        return mapping.get(unit_type, unit_type)
    
    def get_unit_type_emoji(self, unit_type: str) -> str:
        """دریافت اموجی نوع واحد"""
        mapping = {'air': '✈️', 'ground': '🚗', 'naval': '🚢'}
        return mapping.get(unit_type, '🏛️')
    
    def get_unit_status_emoji(self, status: str) -> str:
        """دریافت اموجی وضعیت واحد"""
        mapping = {
            'ready': '✅',
            'deployed': '🚀',
            'maintenance': '🔧',
            'training': '📚'
        }
        return mapping.get(status, '❓')
    
    def get_unit_status_persian(self, status: str) -> str:
        """تبدیل وضعیت واحد به فارسی"""
        mapping = {
            'ready': 'آماده',
            'deployed': 'مستقر',
            'maintenance': 'تعمیر',
            'training': 'تمرین'
        }
        return mapping.get(status, status)
    
    def get_defense_status_emoji(self, status: str) -> str:
        """دریافت اموجی وضعیت دفاعی"""
        mapping = {
            'NORMAL': '🟢',
            'ELEVATED': '🟡',
            'HIGH': '🟠',
            'CRITICAL': '🔴'
        }
        return mapping.get(status, '⚪')
    
    def create_readiness_bar(self, readiness: float, length: int = 10) -> str:
        """ایجاد نوار آمادگی"""
        filled = int(length * readiness / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
    
    async def create_mission_detail_embed(self, mission: Dict) -> discord.Embed:
        """ایجاد Embed جزئیات مأموریت"""
        
        embed = EmbedBuilder.create_embed(
            title=f"🎯 {mission['name']}",
            description=f"جزئیات مأموریت `{mission['mission_id']}`",
            color=EMBED_COLORS['military']
        )
        
        # اطلاعات پایه
        start_time = datetime.fromisoformat(mission['start_time'])
        end_time = datetime.fromisoformat(mission['end_time'])
        remaining = end_time - datetime.now()
        
        embed.add_field(
            name="📊 مشخصات",
            value=f"🆔 شناسه: `{mission['mission_id']}`\n"
                  f"🏷️ نوع: {mission['type']}\n"
                  f"📊 سختی: {mission['difficulty']}\n"
                  f"⚡ وضعیت: {mission['status']}",
            inline=True
        )
        
        # زمان‌بندی
        if remaining.total_seconds() > 0:
            time_left = f"{int(remaining.total_seconds() // 60)} دقیقه"
        else:
            time_left = "آماده تکمیل"
        
        embed.add_field(
            name="⏰ زمان‌بندی",
            value=f"📅 شروع: {start_time.strftime('%m/%d %H:%M')}\n"
                  f"🏁 پایان: {end_time.strftime('%m/%d %H:%M')}\n"
                  f"⏳ باقی‌مانده: {time_left}\n"
                  f"📈 پیشرفت: {mission['progress']:.0f}%",
            inline=True
        )
        
        # واحدهای تخصیص یافته
        unit_names = []
        for unit_id in mission['assigned_units']:
            if unit_id in self.military_units:
                unit = self.military_units[unit_id]
                unit_names.append(f"• {unit.name} (`{unit_id}`)")
        
        embed.add_field(
            name="🏛️ واحدهای مستقر",
            value='\n'.join(unit_names) if unit_names else "واحدی تخصیص نیافته",
            inline=False
        )
        
        # نوار پیشرفت
        progress_bar = self.create_readiness_bar(mission['progress'])
        embed.add_field(
            name="📈 پیشرفت مأموریت",
            value=f"{progress_bar} {mission['progress']:.0f}%",
            inline=False
        )
        
        return embed
    
    async def announce_unit_creation(self, guild: discord.Guild, unit: MilitaryUnit, creator: discord.Member):
        """اعلام ایجاد واحد جدید"""
        
        embed = EmbedBuilder.create_embed(
            title="🏛️ واحد نظامی جدید ایجاد شد",
            description=f"واحد **{unit.name}** به نیروهای مسلح اضافه شد",
            color=EMBED_COLORS['success']
        )
        
        embed.add_field(
            name="📊 مشخصات واحد",
            value=f"🆔 شناسه: `{unit.unit_id}`\n"
                  f"🏷️ نوع: {self.get_unit_type_persian(unit.unit_type)}\n"
                  f"👥 ظرفیت: {unit.capacity} نفر\n"
                  f"👤 ایجاد توسط: {creator.mention}",
            inline=True
        )
        
        # ارسال به کانال عملیات نظامی
        operations_channel = discord.utils.get(guild.text_channels, name='military-operations')
        if operations_channel:
            await operations_channel.send(embed=embed)
    
    async def announce_mission_start(self, guild: discord.Guild, mission_id: str, mission: Dict, assigned_units: List[str]):
        """اعلام شروع مأموریت"""
        
        embed = EmbedBuilder.create_embed(
            title="🚀 مأموریت جدید آغاز شد",
            description=f"مأموریت **{mission['name']}** شروع شد",
            color=EMBED_COLORS['military']
        )
        
        embed.add_field(
            name="📊 جزئیات",
            value=f"🆔 شناسه: `{mission_id}`\n"
                  f"⏰ مدت: {mission['duration']} دقیقه\n"
                  f"🏛️ واحدها: {len(assigned_units)}\n"
                  f"📊 سختی: {mission['difficulty']}",
            inline=True
        )
        
        operations_channel = discord.utils.get(guild.text_channels, name='military-operations')
        if operations_channel:
            await operations_channel.send(embed=embed)
    
    async def announce_mission_completion(self, guild: discord.Guild, mission: Dict):
        """اعلام تکمیل مأموریت"""
        
        success = random.choice([True, True, True, False])  # ۷۵٪ احتمال موفقیت
        
        embed = EmbedBuilder.create_embed(
            title=f"🏆 مأموریت {'موفقیت‌آمیز' if success else 'ناموفق'} تکمیل شد",
            description=f"مأموریت **{mission['name']}** به پایان رسید",
            color=EMBED_COLORS['success'] if success else EMBED_COLORS['warning']
        )
        
        embed.add_field(
            name="📊 نتیجه",
            value=f"🎯 وضعیت: {'موفقیت‌آمیز' if success else 'ناموفق'}\n"
                  f"⏰ مدت اجرا: {mission.get('duration', 0)} دقیقه\n"
                  f"🏛️ واحدهای شرکت‌کننده: {len(mission['assigned_units'])}\n"
                  f"🏆 پاداش: {'دریافت شد' if success else 'دریافت نشد'}",
            inline=True
        )
        
        operations_channel = discord.utils.get(guild.text_channels, name='military-operations')
        if operations_channel:
            await operations_channel.send(embed=embed)
    
    async def announce_defense_status_change(self, guild: discord.Guild, old_status: str, new_status: str):
        """اعلام تغییر وضعیت دفاعی"""
        
        embed = EmbedBuilder.create_embed(
            title="🚨 تغییر وضعیت دفاعی",
            description=f"وضعیت دفاعی از **{old_status}** به **{new_status}** تغییر کرد",
            color=EMBED_COLORS['warning']
        )
        
        channels = ['military-operations', 'defense-alerts', 'government-announcements']
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(embed=embed)
    
    async def generate_random_mission(self, guild: discord.Guild):
        """تولید مأموریت تصادفی"""
        
        # انتخاب مأموریت تصادفی با AI
        mission_prompt = "یک مأموریت نظامی جالب و واقع‌گرایانه برای ارتش اسرائیل تولید کن. شامل نام، نوع، و توضیحات کوتاه."
        
        try:
            ai_mission = await self.ai.generate_content(mission_prompt)
            
            embed = EmbedBuilder.create_embed(
                title="📢 مأموریت جدید در دسترس",
                description="مأموریت تازه‌ای برای نیروهای مسلح تعریف شده است",
                color=EMBED_COLORS['info']
            )
            
            embed.add_field(
                name="🎯 جزئیات مأموریت",
                value=ai_mission[:500] + "..." if len(ai_mission) > 500 else ai_mission,
                inline=False
            )
            
            embed.add_field(
                name="📋 راهنمای شرکت",
                value="برای شرکت در مأموریت از دستور `!start_mission` استفاده کنید.",
                inline=False
            )
            
            operations_channel = discord.utils.get(guild.text_channels, name='military-operations')
            if operations_channel:
                await operations_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"خطا در تولید مأموریت تصادفی: {e}")
    
    async def apply_defense_status_changes(self):
        """اعمال تغییرات وضعیت دفاعی بر واحدها"""
        
        if self.defense_status == 'CRITICAL':
            # تمام واحدها آماده‌باش
            for unit in self.military_units.values():
                if unit.status != 'deployed':
                    unit.status = 'ready'
                    unit.last_activity = datetime.now()
        
        elif self.defense_status == 'HIGH':
            # واحدهای کلیدی آماده‌باش
            for unit in self.military_units.values():
                if unit.unit_type in ['air', 'ground'] and unit.status == 'maintenance':
                    unit.status = 'ready'
                    unit.last_activity = datetime.now()
    
    async def send_daily_report(self, guild: discord.Guild):
        """ارسال گزارش روزانه"""
        
        embed = EmbedBuilder.create_embed(
            title="📊 گزارش روزانه فرماندهی کل ارتش",
            description=f"گزارش عملکرد {TimeManager.format_time(datetime.now())}",
            color=EMBED_COLORS['military']
        )
        
        # آمار کلی
        embed.add_field(
            name="📈 خلاصه عملکرد",
            value=f"🏛️ واحدهای فعال: {len(self.military_units)}\n"
                  f"👥 کل پرسنل: {sum(unit.current_personnel for unit in self.military_units.values())}\n"
                  f"🎯 مأموریت‌های تکمیل شده: {len(self.mission_manager.mission_history)}\n"
                  f"📊 آمادگی کل: {self.calculate_overall_readiness():.1f}%",
            inline=True
        )
        
        operations_channel = discord.utils.get(guild.text_channels, name='military-operations')
        if operations_channel:
            await operations_channel.send(embed=embed)

# اجرای ربات
if __name__ == "__main__":
    bot = ArmyCommandBot()
    
    try:
        bot.run(bot.token)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات فرماندهی کل ارتش: {e}")