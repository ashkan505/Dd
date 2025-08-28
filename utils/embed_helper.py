"""
کمک‌کننده Embed برای ایجاد پیام‌های زیبا و تزئین شده
Embed Helper for Creating Beautiful and Decorated Discord Messages
"""

import discord
from config import EMBED_COLORS
from typing import Optional, List, Dict, Any
import datetime

class EmbedHelper:
    """کلاس کمکی برای ایجاد Embedهای زیبا و تزئین شده"""
    
    @staticmethod
    def create_success_embed(title: str, description: str, fields: List[Dict] = None) -> discord.Embed:
        """
        ایجاد Embed موفقیت
        
        Args:
            title: عنوان Embed
            description: توضیحات
            fields: فیلدهای اضافی
            
        Returns:
            Embed موفقیت
        """
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=EMBED_COLORS["success"],
            timestamp=datetime.datetime.now()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False)
                )
        
        embed.set_footer(text="سرور رول‌پلی اسرائیل", icon_url="https://i.imgur.com/star-of-david.png")
        return embed
    
    @staticmethod
    def create_error_embed(title: str, description: str, error_code: str = None) -> discord.Embed:
        """
        ایجاد Embed خطا
        
        Args:
            title: عنوان خطا
            description: توضیح خطا
            error_code: کد خطا (اختیاری)
            
        Returns:
            Embed خطا
        """
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=EMBED_COLORS["error"],
            timestamp=datetime.datetime.now()
        )
        
        if error_code:
            embed.add_field(name="کد خطا", value=f"`{error_code}`", inline=False)
        
        embed.set_footer(text="سرور رول‌پلی اسرائیل", icon_url="https://i.imgur.com/star-of-david.png")
        return embed
    
    @staticmethod
    def create_warning_embed(title: str, description: str) -> discord.Embed:
        """
        ایجاد Embed هشدار
        
        Args:
            title: عنوان هشدار
            description: توضیح هشدار
            
        Returns:
            Embed هشدار
        """
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=EMBED_COLORS["warning"],
            timestamp=datetime.datetime.now()
        )
        
        embed.set_footer(text="سرور رول‌پلی اسرائیل", icon_url="https://i.imgur.com/star-of-david.png")
        return embed
    
    @staticmethod
    def create_info_embed(title: str, description: str, fields: List[Dict] = None, thumbnail: str = None) -> discord.Embed:
        """
        ایجاد Embed اطلاعاتی
        
        Args:
            title: عنوان
            description: توضیحات
            fields: فیلدهای اضافی
            thumbnail: تصویر کوچک
            
        Returns:
            Embed اطلاعاتی
        """
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=EMBED_COLORS["info"],
            timestamp=datetime.datetime.now()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False)
                )
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        embed.set_footer(text="سرور رول‌پلی اسرائیل", icon_url="https://i.imgur.com/star-of-david.png")
        return embed
    
    @staticmethod
    def create_government_embed(title: str, description: str, fields: List[Dict] = None) -> discord.Embed:
        """
        ایجاد Embed دولتی
        
        Args:
            title: عنوان
            description: توضیحات
            fields: فیلدهای اضافی
            
        Returns:
            Embed دولتی
        """
        embed = discord.Embed(
            title=f"🏛️ {title}",
            description=description,
            color=EMBED_COLORS["government"],
            timestamp=datetime.datetime.now()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False)
                )
        
        embed.set_footer(text="دولت اسرائیل", icon_url="https://i.imgur.com/knesset.png")
        return embed
    
    @staticmethod
    def create_military_embed(title: str, description: str, fields: List[Dict] = None) -> discord.Embed:
        """
        ایجاد Embed نظامی
        
        Args:
            title: عنوان
            description: توضیحات
            fields: فیلدهای اضافی
            
        Returns:
            Embed نظامی
        """
        embed = discord.Embed(
            title=f"⚔️ {title}",
            description=description,
            color=EMBED_COLORS["military"],
            timestamp=datetime.datetime.now()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False)
                )
        
        embed.set_footer(text="ارتش دفاعی اسرائیل", icon_url="https://i.imgur.com/idf.png")
        return embed
    
    @staticmethod
    def create_economy_embed(title: str, description: str, fields: List[Dict] = None) -> discord.Embed:
        """
        ایجاد Embed اقتصادی
        
        Args:
            title: عنوان
            description: توضیحات
            fields: فیلدهای اضافی
            
        Returns:
            Embed اقتصادی
        """
        embed = discord.Embed(
            title=f"💰 {title}",
            description=description,
            color=EMBED_COLORS["economy"],
            timestamp=datetime.datetime.now()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False)
                )
        
        embed.set_footer(text="بانک مرکزی اسرائیل", icon_url="https://i.imgur.com/bank-of-israel.png")
        return embed
    
    @staticmethod
    def create_news_embed(title: str, description: str, author: str, category: str = "عمومی") -> discord.Embed:
        """
        ایجاد Embed خبری
        
        Args:
            title: عنوان خبر
            description: متن خبر
            author: نویسنده
            category: دسته‌بندی خبر
            
        Returns:
            Embed خبری
        """
        embed = discord.Embed(
            title=f"📰 {title}",
            description=description,
            color=EMBED_COLORS["news"],
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="دسته‌بندی", value=category, inline=True)
        embed.add_field(name="نویسنده", value=author, inline=True)
        embed.add_field(name="تاریخ انتشار", value=datetime.datetime.now().strftime("%Y/%m/%d %H:%M"), inline=True)
        
        embed.set_footer(text="رادیو اسرائیل", icon_url="https://i.imgur.com/radio-israel.png")
        return embed
    
    @staticmethod
    def create_citizenship_embed(questions: List[str], user: discord.Member) -> discord.Embed:
        """
        ایجاد Embed سوالات شهروندی
        
        Args:
            questions: لیست سوالات
            user: کاربر درخواست‌کننده
            
        Returns:
            Embed سوالات شهروندی
        """
        embed = discord.Embed(
            title="🏛️ درخواست شهروندی اسرائیل",
            description=f"کاربر گرامی {user.mention}، لطفاً به سوالات زیر پاسخ دهید:",
            color=EMBED_COLORS["government"],
            timestamp=datetime.datetime.now()
        )
        
        for i, question in enumerate(questions, 1):
            embed.add_field(
                name=f"سوال {i}",
                value=question,
                inline=False
            )
        
        embed.add_field(
            name="نحوه پاسخ",
            value="برای پاسخ به هر سوال، از کامند `!answer [شماره سوال] [پاسخ]` استفاده کنید.",
            inline=False
        )
        
        embed.set_footer(text="اداره مهاجرت اسرائیل", icon_url="https://i.imgur.com/immigration.png")
        return embed
    
    @staticmethod
    def create_election_embed(candidates: List[Dict], end_time: datetime.datetime) -> discord.Embed:
        """
        ایجاد Embed انتخابات
        
        Args:
            candidates: لیست کاندیداها
            end_time: زمان پایان انتخابات
            
        Returns:
            Embed انتخابات
        """
        embed = discord.Embed(
            title="🗳️ انتخابات نخست‌وزیری اسرائیل",
            description="انتخابات در حال برگزاری است. لطفاً رأی خود را ثبت کنید:",
            color=EMBED_COLORS["government"],
            timestamp=datetime.datetime.now()
        )
        
        for candidate in candidates:
            embed.add_field(
                name=f"🎯 {candidate['name']}",
                value=f"حزب: {candidate['party']}\nشعار: {candidate['slogan']}",
                inline=True
            )
        
        embed.add_field(
            name="⏰ زمان پایان",
            value=f"<t:{int(end_time.timestamp())}:R>",
            inline=False
        )
        
        embed.add_field(
            name="📝 نحوه رأی",
            value="از کامند `!vote [نام کاندیدا]` استفاده کنید.",
            inline=False
        )
        
        embed.set_footer(text="کمیسیون انتخابات اسرائیل", icon_url="https://i.imgur.com/elections.png")
        return embed
    
    @staticmethod
    def create_war_room_embed(defcon_level: int, status: str, alerts: List[str] = None) -> discord.Embed:
        """
        ایجاد Embed اتاق جنگ
        
        Args:
            defcon_level: سطح آمادگی دفاعی
            status: وضعیت فعلی
            alerts: هشدارهای فعال
            
        Returns:
            Embed اتاق جنگ
        """
        embed = discord.Embed(
            title="🚨 اتاق جنگ - وضعیت دفاعی",
            description=f"سطح آمادگی فعلی: **DEFCON {defcon_level}**",
            color=EMBED_COLORS["military"],
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📊 وضعیت",
            value=status,
            inline=False
        )
        
        if alerts:
            alert_text = "\n".join([f"• {alert}" for alert in alerts])
            embed.add_field(
                name="⚠️ هشدارهای فعال",
                value=alert_text,
                inline=False
            )
        
        embed.set_footer(text="فرماندهی کل ارتش اسرائیل", icon_url="https://i.imgur.com/idf.png")
        return embed
    
    @staticmethod
    def create_mission_embed(mission: Dict[str, Any]) -> discord.Embed:
        """
        ایجاد Embed مأموریت
        
        Args:
            mission: اطلاعات مأموریت
            
        Returns:
            Embed مأموریت
        """
        embed = discord.Embed(
            title=f"🎯 {mission.get('title', 'مأموریت جدید')}",
            description=mission.get('description', 'توضیحات مأموریت'),
            color=EMBED_COLORS["military"],
            timestamp=datetime.datetime.now()
        )
        
        if 'objectives' in mission:
            objectives_text = "\n".join([f"• {obj}" for obj in mission['objectives']])
            embed.add_field(
                name="🎯 اهداف",
                value=objectives_text,
                inline=False
            )
        
        embed.add_field(
            name="💰 پاداش",
            value=mission.get('reward', 'بدون پاداش'),
            inline=True
        )
        
        embed.add_field(
            name="⏰ محدودیت زمانی",
            value=mission.get('time_limit', 'بدون محدودیت'),
            inline=True
        )
        
        embed.add_field(
            name="📋 نیازمندی‌ها",
            value=mission.get('requirements', 'بدون نیازمندی خاص'),
            inline=False
        )
        
        embed.set_footer(text="ستاد فرماندهی ارتش", icon_url="https://i.imgur.com/idf.png")
        return embed