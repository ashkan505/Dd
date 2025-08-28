"""
ماژول دولت و کنست - شبیه‌سازی کامل سیستم حکومتی اسرائیل
Government and Knesset Module - Complete Israeli Government Simulation
"""

import discord
from discord.ext import commands
import asyncio
import logging
import json
import datetime
import random
from typing import Dict, List, Optional, Any, Union
from config import config
from models import db_manager, User, Government
from gemini_integration import gemini_ai

logger = logging.getLogger(__name__)

class GovernmentCog(commands.Cog):
    """ماژول دولت و کنست"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = db_manager
        self.government = Government(db_manager)
        self.gemini_ai = gemini_ai
        
        # Government state
        self.current_election = None
        self.active_laws = []
        self.cabinet_positions = [
            "وزیر دفاع", "وزیر امور خارجه", "وزیر اقتصاد", "وزیر آموزش",
            "وزیر بهداشت", "وزیر حمل و نقل", "وزیر کشاورزی", "وزیر انرژی",
            "وزیر محیط زیست", "وزیر فرهنگ", "وزیر ورزش", "وزیر دیجیتال"
        ]
        
        logger.info("Government Cog initialized")
    
    @commands.command(name="initialize_israel")
    @commands.has_permissions(administrator=True)
    async def initialize_israel(self, ctx):
        """پروتکل پیدایش - تبدیل سرور به اسرائیل کامل"""
        try:
            embed = discord.Embed(
                title="🌟 پروتکل پیدایش اسرائیل",
                description="در حال راه‌اندازی کامل سرور...",
                color=config.COLORS["government"],
                timestamp=datetime.datetime.now()
            )
            
            status_msg = await ctx.send(embed=embed)
            
            # Step 1: Create roles
            embed.add_field(name="🔧 مرحله 1", value="ایجاد رول‌های اصلی...", inline=False)
            await status_msg.edit(embed=embed)
            
            await self.create_government_roles(ctx.guild)
            
            # Step 2: Create categories and channels
            embed.add_field(name="🔧 مرحله 2", value="ایجاد کتگوری‌ها و کانال‌ها...", inline=False)
            await status_msg.edit(embed=embed)
            
            await self.create_government_structure(ctx.guild)
            
            # Step 3: Set up permissions
            embed.add_field(name="🔧 مرحله 3", value="تنظیم مجوزها...", inline=False)
            await status_msg.edit(embed=embed)
            
            await self.setup_permissions(ctx.guild)
            
            # Step 4: Initialize database
            embed.add_field(name="🔧 مرحله 4", value="راه‌اندازی پایگاه داده...", inline=False)
            await status_msg.edit(embed=embed)
            
            await self.initialize_database()
            
            # Step 5: Set up government
            embed.add_field(name="🔧 مرحله 5", value="راه‌اندازی دولت...", inline=False)
            await status_msg.edit(embed=embed)
            
            await self.setup_initial_government(ctx.author)
            
            # Final status
            embed.add_field(name="✅ تکمیل", value="سرور اسرائیل با موفقیت راه‌اندازی شد!", inline=False)
            embed.color = config.COLORS["success"]
            await status_msg.edit(embed=embed)
            
            # Send welcome message
            await self.send_welcome_message(ctx.channel)
            
            logger.info(f"Israel initialization completed by {ctx.author}")
            
        except Exception as e:
            logger.error(f"Error in Israel initialization: {e}")
            embed = discord.Embed(
                title="❌ خطا در راه‌اندازی",
                description=f"خطایی در راه‌اندازی سرور رخ داد: {str(e)}",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    async def create_government_roles(self, guild):
        """ایجاد رول‌های دولتی"""
        try:
            # Government roles
            government_roles = [
                ("نخست‌وزیر", 0x9932CC, ["manage_channels", "manage_messages", "manage_roles"]),
                ("وزیر", 0x8B008B, ["manage_messages", "manage_roles"]),
                ("عضو کنست", 0x9370DB, ["manage_messages"]),
                ("شهروند", 0x32CD32, ["send_messages", "use_external_emojis"]),
                ("سرباز", 0x8B0000, ["send_messages", "use_external_emojis", "attach_files"]),
                ("دانشمند", 0x4169E1, ["send_messages", "use_external_emojis", "attach_files"]),
                ("پزشک", 0xFF1493, ["send_messages", "use_external_emojis", "attach_files"]),
                ("خلبان", 0x00CED1, ["send_messages", "use_external_emojis", "attach_files"]),
                ("قاضی", 0xFFD700, ["send_messages", "use_external_emojis", "manage_messages"]),
                ("توریست", 0xC0C0C0, ["view_channel", "send_messages"])
            ]
            
            for role_name, color, permissions in government_roles:
                # Check if role already exists
                existing_role = discord.utils.get(guild.roles, name=role_name)
                if not existing_role:
                    # Create role
                    role = await guild.create_role(
                        name=role_name,
                        color=discord.Color(color),
                        permissions=discord.Permissions(**{perm: True for perm in permissions})
                    )
                    logger.info(f"Created role: {role_name}")
                else:
                    logger.info(f"Role already exists: {role_name}")
            
            # Set tourist role for new members
            tourist_role = discord.utils.get(guild.roles, name="توریست")
            if tourist_role:
                await guild.edit(default_role=tourist_role)
                logger.info("Set tourist as default role")
                
        except Exception as e:
            logger.error(f"Error creating government roles: {e}")
            raise
    
    async def create_government_structure(self, guild):
        """ایجاد ساختار دولتی"""
        try:
            # Government category
            gov_category = await guild.create_category("🏛️ دولت")
            
            # Government channels
            gov_channels = [
                ("دولت", "کانال اصلی دولت"),
                ("کنست", "مجلس قانون‌گذاری"),
                ("کابینه", "جلسات کابینه"),
                ("وزارت‌خانه‌ها", "وزارت‌های مختلف"),
                ("انتخابات", "فرآیندهای انتخاباتی"),
                ("قوانین", "آرشیو قوانین مصوب")
            ]
            
            for channel_name, description in gov_channels:
                channel = await guild.create_text_channel(
                    name=channel_name,
                    category=gov_category,
                    topic=description
                )
                logger.info(f"Created government channel: {channel_name}")
            
            # Military category
            mil_category = await guild.create_category("⚔️ ارتش")
            
            mil_channels = [
                ("ارتش", "فرماندهی کل ارتش"),
                ("نیروی_هوایی", "نیروی هوایی"),
                ("نیروی_زمینی", "نیروی زمینی"),
                ("نیروی_دریایی", "نیروی دریایی"),
                ("دفاع_هوایی", "سیستم‌های دفاع هوایی"),
                ("اتاق_جنگ", "مرکز فرماندهی عملیات")
            ]
            
            for channel_name, description in mil_channels:
                channel = await guild.create_text_channel(
                    name=channel_name,
                    category=mil_category,
                    topic=description
                )
                logger.info(f"Created military channel: {channel_name}")
            
            # Economy category
            eco_category = await guild.create_category("💰 اقتصاد")
            
            eco_channels = [
                ("اقتصاد", "اقتصاد ملی"),
                ("بانک_مرکزی", "بانک مرکزی اسرائیل"),
                ("بورس", "بورس تل‌آویو"),
                ("صنایع_نظامی", "صنایع دفاعی")
            ]
            
            for channel_name, description in eco_channels:
                channel = await guild.create_text_channel(
                    name=channel_name,
                    category=eco_category,
                    topic=description
                )
                logger.info(f"Created economy channel: {channel_name}")
            
            # Intelligence category
            int_category = await guild.create_category("🕵️ اطلاعات")
            
            int_channels = [
                ("موساد", "سازمان اطلاعات خارجی"),
                ("واحد_۸۲۰۰", "واحد اطلاعات سایبری"),
                ("اطلاعات_نظامی", "اطلاعات نظامی")
            ]
            
            for channel_name, description in int_channels:
                channel = await guild.create_text_channel(
                    name=channel_name,
                    category=int_category,
                    topic=description
                )
                logger.info(f"Created intelligence channel: {channel_name}")
            
            # Civilian category
            civ_category = await guild.create_category("👥 شهروندان")
            
            civ_channels = [
                ("شهروندان", "کانال اصلی شهروندان"),
                ("مهاجرت", "اداره مهاجرت"),
                ("کار", "اداره کار"),
                ("آموزش", "سیستم آموزشی"),
                ("بهداشت", "سیستم بهداشتی")
            ]
            
            for channel_name, description in civ_channels:
                channel = await guild.create_text_channel(
                    name=channel_name,
                    category=civ_category,
                    topic=description
                )
                logger.info(f"Created civilian channel: {channel_name}")
            
            # Media category
            med_category = await guild.create_category("📰 رسانه")
            
            med_channels = [
                ("اخبار_ملی", "اخبار رسمی کشور"),
                ("رادیو_اسرائیل", "رادیو ملی"),
                ("فرهنگ", "فرهنگ و هنر"),
                ("ورزش", "ورزش و تفریحات")
            ]
            
            for channel_name, description in med_channels:
                channel = await guild.create_text_channel(
                    name=channel_name,
                    category=med_category,
                    topic=description
                )
                logger.info(f"Created media channel: {channel_name}")
            
            # Private category
            priv_category = await guild.create_category("🔒 خصوصی")
            
            priv_channels = [
                ("خانه_خصوصی", "خانه‌های خصوصی"),
                ("دفتر_خصوصی", "دفاتر خصوصی"),
                ("اتاق_جلسات", "اتاق‌های جلسات")
            ]
            
            for channel_name, description in priv_channels:
                channel = await guild.create_text_channel(
                    name=channel_name,
                    category=priv_category,
                    topic=description
                )
                logger.info(f"Created private channel: {channel_name}")
                
        except Exception as e:
            logger.error(f"Error creating government structure: {e}")
            raise
    
    async def setup_permissions(self, guild):
        """تنظیم مجوزها"""
        try:
            # Get roles
            prime_minister_role = discord.utils.get(guild.roles, name="نخست‌وزیر")
            minister_role = discord.utils.get(guild.roles, name="وزیر")
            knesset_role = discord.utils.get(guild.roles, name="عضو کنست")
            citizen_role = discord.utils.get(guild.roles, name="شهروند")
            soldier_role = discord.utils.get(guild.roles, name="سرباز")
            tourist_role = discord.utils.get(guild.roles, name="توریست")
            
            # Set up channel permissions
            for category in guild.categories:
                if category.name == "🏛️ دولت":
                    # Government channels - restricted access
                    for channel in category.channels:
                        await channel.set_permissions(tourist_role, view_channel=False)
                        await channel.set_permissions(citizen_role, view_channel=True, send_messages=False)
                        await channel.set_permissions(soldier_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(knesset_role, view_channel=True, send_messages=True, manage_messages=True)
                        await channel.set_permissions(minister_role, view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
                        await channel.set_permissions(prime_minister_role, view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
                
                elif category.name == "⚔️ ارتش":
                    # Military channels - restricted access
                    for channel in category.channels:
                        await channel.set_permissions(tourist_role, view_channel=False)
                        await channel.set_permissions(citizen_role, view_channel=False)
                        await channel.set_permissions(soldier_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(minister_role, view_channel=True, send_messages=True, manage_messages=True)
                        await channel.set_permissions(prime_minister_role, view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
                
                elif category.name == "💰 اقتصاد":
                    # Economy channels - moderate access
                    for channel in category.channels:
                        await channel.set_permissions(tourist_role, view_channel=True, send_messages=False)
                        await channel.set_permissions(citizen_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(soldier_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(minister_role, view_channel=True, send_messages=True, manage_messages=True)
                        await channel.set_permissions(prime_minister_role, view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
                
                elif category.name == "🕵️ اطلاعات":
                    # Intelligence channels - highly restricted
                    for channel in category.channels:
                        await channel.set_permissions(tourist_role, view_channel=False)
                        await channel.set_permissions(citizen_role, view_channel=False)
                        await channel.set_permissions(soldier_role, view_channel=False)
                        await channel.set_permissions(minister_role, view_channel=True, send_messages=True, manage_messages=True)
                        await channel.set_permissions(prime_minister_role, view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
                
                elif category.name == "👥 شهروندان":
                    # Civilian channels - open access
                    for channel in category.channels:
                        await channel.set_permissions(tourist_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(citizen_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(soldier_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(minister_role, view_channel=True, send_messages=True, manage_messages=True)
                        await channel.set_permissions(prime_minister_role, view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
                
                elif category.name == "📰 رسانه":
                    # Media channels - open access
                    for channel in category.channels:
                        await channel.set_permissions(tourist_role, view_channel=True, send_messages=False)
                        await channel.set_permissions(citizen_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(soldier_role, view_channel=True, send_messages=True)
                        await channel.set_permissions(minister_role, view_channel=True, send_messages=True, manage_messages=True)
                        await channel.set_permissions(prime_minister_role, view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
                
                elif category.name == "🔒 خصوصی":
                    # Private channels - restricted access
                    for channel in category.channels:
                        await channel.set_permissions(tourist_role, view_channel=False)
                        await channel.set_permissions(citizen_role, view_channel=False)
                        await channel.set_permissions(soldier_role, view_channel=False)
                        await channel.set_permissions(minister_role, view_channel=True, send_messages=True, manage_messages=True)
                        await channel.set_permissions(prime_minister_role, view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
            
            logger.info("Channel permissions set up successfully")
            
        except Exception as e:
            logger.error(f"Error setting up permissions: {e}")
            raise
    
    async def initialize_database(self):
        """راه‌اندازی پایگاه داده"""
        try:
            # Initialize government
            self.government = Government(self.db_manager)
            
            # Initialize other components
            from models import Military, Economy
            self.military = Military(self.db_manager)
            self.economy = Economy(self.db_manager)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def setup_initial_government(self, owner):
        """راه‌اندازی دولت اولیه"""
        try:
            # Set owner as prime minister
            self.government.set_prime_minister(str(owner.id))
            
            # Add owner to knesset
            self.government.add_knesset_member(str(owner.id))
            
            # Create initial cabinet
            self.government.add_cabinet_member("وزیر دفاع", str(owner.id))
            self.government.add_cabinet_member("وزیر امور خارجه", str(owner.id))
            self.government.add_cabinet_member("وزیر اقتصاد", str(owner.id))
            
            # Set initial budget
            self.government.change_budget(1000000)
            
            logger.info(f"Initial government set up with {owner.name} as Prime Minister")
            
        except Exception as e:
            logger.error(f"Error setting up initial government: {e}")
            raise
    
    async def send_welcome_message(self, channel):
        """ارسال پیام خوش‌آمدگویی"""
        try:
            embed = discord.Embed(
                title="🌟 خوش آمدید به سرور رول‌پلی اسرائیل!",
                description="سرور با موفقیت راه‌اندازی شد و آماده پذیرش شهروندان جدید است.",
                color=config.COLORS["success"],
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(
                name="🏛️ دولت",
                value="سیستم کامل دولت و کنست راه‌اندازی شد",
                inline=True
            )
            
            embed.add_field(
                name="⚔️ ارتش",
                value="ساختار نظامی و دفاعی آماده است",
                inline=True
            )
            
            embed.add_field(
                name="💰 اقتصاد",
                value="سیستم اقتصادی و بانکی فعال است",
                inline=True
            )
            
            embed.add_field(
                name="👥 شهروندان",
                value="از کامند `!apply_citizenship` برای درخواست شهروندی استفاده کنید",
                inline=False
            )
            
            embed.add_field(
                name="📚 راهنما",
                value="از کامند `!help` برای مشاهده لیست کامندها استفاده کنید",
                inline=False
            )
            
            embed.set_footer(text="ستاره داوود - سیستم مرکزی")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
    
    @commands.command(name="apply_citizenship")
    async def apply_citizenship(self, ctx):
        """درخواست شهروندی اسرائیل"""
        try:
            # Check if user is already a citizen
            user = User(str(ctx.author.id), self.db_manager)
            
            if user.role != "توریست":
                embed = discord.Embed(
                    title="ℹ️ اطلاع",
                    description="شما قبلاً شهروند اسرائیل هستید.",
                    color=config.COLORS["info"]
                )
                await ctx.send(embed=embed)
                return
            
            # Generate citizenship questions using Gemini AI
            questions = await self.generate_citizenship_questions()
            
            # Create application embed
            embed = discord.Embed(
                title="📝 درخواست شهروندی اسرائیل",
                description="لطفاً به سوالات زیر پاسخ دهید:",
                color=config.COLORS["government"],
                timestamp=datetime.datetime.now()
            )
            
            for i, question in enumerate(questions, 1):
                embed.add_field(
                    name=f"سوال {i}",
                    value=question,
                    inline=False
                )
            
            embed.add_field(
                name="💡 راهنما",
                value="پاسخ‌های خود را در یک پیام ارسال کنید.",
                inline=False
            )
            
            embed.set_footer(text="ستاره داوود - اداره مهاجرت")
            
            await ctx.send(embed=embed)
            
            # Wait for response
            try:
                response = await self.bot.wait_for(
                    'message',
                    timeout=300.0,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
                
                # Process response
                await self.process_citizenship_application(ctx, user, response.content)
                
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="⏰ زمان تمام شد",
                    description="زمان پاسخگویی به پایان رسید. لطفاً دوباره تلاش کنید.",
                    color=config.COLORS["warning"]
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in citizenship application: {e}")
            embed = discord.Embed(
                title="❌ خطا",
                description="خطایی در پردازش درخواست رخ داد.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    async def generate_citizenship_questions(self) -> List[str]:
        """تولید سوالات شهروندی با استفاده از Gemini AI"""
        try:
            prompt = """
            شما یک افسر اداره مهاجرت اسرائیل هستید. 5 سوال مهم برای ارزیابی صلاحیت شهروندی تولید کنید.
            
            سوالات باید شامل موارد زیر باشند:
            - انگیزه مهاجرت به اسرائیل
            - تعهد به قوانین و ارزش‌های اسرائیل
            - مهارت‌ها و تخصص‌های مفید
            - برنامه‌های آینده در کشور
            - درک از فرهنگ و تاریخ اسرائیل
            
            هر سوال باید کوتاه، واضح و مرتبط باشد.
            """
            
            response = await self.gemini_ai.generate_response(prompt)
            
            # Parse questions (assuming they're numbered)
            lines = response.split('\n')
            questions = []
            
            for line in lines:
                line = line.strip()
                if line and any(char.isdigit() for char in line[:3]):
                    # Remove numbering and clean up
                    question = line.split('.', 1)[-1].strip()
                    if question:
                        questions.append(question)
            
            # If parsing failed, use fallback questions
            if len(questions) < 3:
                questions = [
                    "انگیزه اصلی شما برای مهاجرت به اسرائیل چیست؟",
                    "آیا با قوانین و ارزش‌های اسرائیل آشنا هستید؟",
                    "چه مهارت‌ها و تخصص‌هایی دارید که می‌تواند به کشور کمک کند؟",
                    "برنامه‌های آینده شما در اسرائیل چیست؟",
                    "آیا با فرهنگ و تاریخ اسرائیل آشنا هستید؟"
                ]
            
            return questions[:5]  # Return max 5 questions
            
        except Exception as e:
            logger.error(f"Error generating citizenship questions: {e}")
            # Return fallback questions
            return [
                "انگیزه اصلی شما برای مهاجرت به اسرائیل چیست؟",
                "آیا با قوانین و ارزش‌های اسرائیل آشنا هستید؟",
                "چه مهارت‌ها و تخصص‌هایی دارید که می‌تواند به کشور کمک کند؟",
                "برنامه‌های آینده شما در اسرائیل چیست؟",
                "آیا با فرهنگ و تاریخ اسرائیل آشنا هستید؟"
            ]
    
    async def process_citizenship_application(self, ctx, user, response):
        """پردازش درخواست شهروندی"""
        try:
            # Analyze response using Gemini AI
            analysis = await self.analyze_citizenship_response(response)
            
            if analysis.get("approved", False):
                # Grant citizenship
                user.change_role("شهروند")
                
                # Update Discord role
                guild = ctx.guild
                citizen_role = discord.utils.get(guild.roles, name="شهروند")
                tourist_role = discord.utils.get(guild.roles, name="توریست")
                
                if citizen_role and tourist_role:
                    await ctx.author.add_roles(citizen_role)
                    await ctx.author.remove_roles(tourist_role)
                
                embed = discord.Embed(
                    title="🎉 تبریک! شهروندی شما تأیید شد!",
                    description="به خانواده بزرگ اسرائیل خوش آمدید!",
                    color=config.COLORS["success"],
                    timestamp=datetime.datetime.now()
                )
                
                embed.add_field(
                    name="📋 رول جدید",
                    value="شهروند",
                    inline=True
                )
                
                embed.add_field(
                    name="💰 موجودی اولیه",
                    value=f"{config.STARTING_BALANCE:,} شِکِل",
                    inline=True
                )
                
                embed.add_field(
                    name="💡 راهنما",
                    value="از کامند `!help` برای مشاهده امکانات جدید استفاده کنید",
                    inline=False
                )
                
                embed.set_footer(text="ستاره داوود - اداره مهاجرت")
                
                await ctx.send(embed=embed)
                
                # Log the event
                logger.info(f"Citizenship granted to {ctx.author.name} ({ctx.author.id})")
                
            else:
                # Application rejected
                embed = discord.Embed(
                    title="❌ درخواست شهروندی رد شد",
                    description="متأسفانه درخواست شما تأیید نشد.",
                    color=config.COLORS["error"]
                )
                
                embed.add_field(
                    name="📝 دلیل رد",
                    value=analysis.get("reason", "پاسخ‌های شما کافی نبود"),
                    inline=False
                )
                
                embed.add_field(
                    name="💡 راهنما",
                    value="می‌توانید بعداً دوباره درخواست دهید",
                    inline=False
                )
                
                embed.set_footer(text="ستاره داوود - اداره مهاجرت")
                
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error processing citizenship application: {e}")
            embed = discord.Embed(
                title="❌ خطا",
                description="خطایی در پردازش درخواست رخ داد.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    async def analyze_citizenship_response(self, response: str) -> Dict[str, Any]:
        """تحلیل پاسخ درخواست شهروندی با استفاده از Gemini AI"""
        try:
            prompt = f"""
            شما یک افسر اداره مهاجرت اسرائیل هستید. پاسخ زیر را برای درخواست شهروندی تحلیل کنید:
            
            پاسخ متقاضی:
            {response}
            
            لطفاً تحلیل خود را به صورت JSON ارائه دهید:
            {{
                "approved": true/false,
                "score": "امتیاز از 100",
                "reason": "دلیل تأیید یا رد",
                "strengths": ["نقاط قوت"],
                "weaknesses": ["نقاط ضعف"],
                "recommendations": ["توصیه‌ها"]
            }}
            
            معیارهای ارزیابی:
            - تعهد به ارزش‌های اسرائیل
            - مهارت‌ها و تخصص‌های مفید
            - انگیزه و برنامه‌های آینده
            - درک از فرهنگ و تاریخ
            - صداقت و صراحت در پاسخ‌ها
            """
            
            ai_response = await self.gemini_ai.generate_response(prompt)
            
            try:
                # Try to parse JSON response
                if "```json" in ai_response:
                    ai_response = ai_response.split("```json")[1].split("```")[0]
                elif "```" in ai_response:
                    ai_response = ai_response.split("```")[1]
                
                analysis = json.loads(ai_response.strip())
                return analysis
                
            except json.JSONDecodeError:
                # Fallback analysis
                return {
                    "approved": len(response) > 50,  # Simple length check
                    "score": min(100, len(response) * 2),
                    "reason": "تحلیل خودکار بر اساس طول پاسخ",
                    "strengths": ["پاسخ کامل"],
                    "weaknesses": ["تحلیل دقیق انجام نشد"],
                    "recommendations": ["پاسخ‌های دقیق‌تر ارائه دهید"]
                }
                
        except Exception as e:
            logger.error(f"Error analyzing citizenship response: {e}")
            # Fallback analysis
            return {
                "approved": True,  # Default to approval
                "score": 75,
                "reason": "تحلیل خودکار",
                "strengths": ["پاسخ ارائه شده"],
                "weaknesses": ["تحلیل دقیق انجام نشد"],
                "recommendations": ["پاسخ‌های دقیق‌تر ارائه دهید"]
            }
    
    @commands.command(name="control_panel")
    @commands.has_permissions(administrator=True)
    async def control_panel(self, ctx):
        """داشبورد کنترل مرکزی"""
        try:
            embed = discord.Embed(
                title="🎛️ داشبورد کنترل مرکزی",
                description="وضعیت لحظه‌ای تمام سیستم‌ها",
                color=config.COLORS["government"],
                timestamp=datetime.datetime.now()
            )
            
            # Government status
            embed.add_field(
                name="🏛️ دولت",
                value=f"**نخست‌وزیر:** {'تعیین نشده' if not self.government.prime_minister_id else f'<@{self.government.prime_minister_id}>'}\n"
                      f"**عضو کنست:** {len(self.government.knesset_members)} نفر\n"
                      f"**وزیر کابینه:** {len(self.government.cabinet_members)} نفر\n"
                      f"**رضایت عمومی:** {self.government.public_approval}%",
                inline=False
            )
            
            # Military status
            embed.add_field(
                name="⚔️ ارتش",
                value=f"**سطح DEFCON:** {self.military.defcon_level}\n"
                      f"**نیروی کل:** {self.military.total_forces:,} نفر\n"
                      f"**نیروی هوایی:** {self.military.air_force:,} نفر\n"
                      f"**نیروی زمینی:** {self.military.ground_forces:,} نفر\n"
                      f"**نیروی دریایی:** {self.military.navy:,} نفر",
                inline=True
            )
            
            # Economy status
            embed.add_field(
                name="💰 اقتصاد",
                value=f"**تولید ناخالص:** {self.economy.gdp:,} شِکِل\n"
                      f"**بودجه ملی:** {self.government.budget:,} شِکِل\n"
                      f"**نرخ تورم:** {self.economy.inflation_rate:.2%}\n"
                      f"**بدهی ملی:** {self.economy.national_debt:,} شِکِل",
                inline=True
            )
            
            # Resources status
            embed.add_field(
                name="🌍 منابع",
                value=f"**آب:** {self.economy.resources.get('water', 0):,}\n"
                      f"**انرژی:** {self.economy.resources.get('energy', 0):,}\n"
                      f"**مواد:** {self.economy.resources.get('materials', 0):,}\n"
                      f"**فناوری:** {self.economy.resources.get('technology', 0):,}",
                inline=True
            )
            
            # System status
            embed.add_field(
                name="🔧 سیستم",
                value=f"**وضعیت:** {'فعال' if self.bot.is_initialized else 'غیرفعال'}\n"
                      f"**کانال‌ها:** {len(self.bot.server_guild.channels) if self.bot.server_guild else 0}\n"
                      f"**کاربران:** {self.bot.server_guild.member_count if self.bot.server_guild else 0}\n"
                      f"**ربات‌ها:** {len(self.bot.event_tasks)}",
                inline=True
            )
            
            embed.set_footer(text="ستاره داوود - سیستم کنترل مرکزی")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in control panel: {e}")
            embed = discord.Embed(
                title="❌ خطا",
                description="خطایی در نمایش داشبورد رخ داد.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)

async def setup(bot):
    """راه‌اندازی ماژول"""
    await bot.add_cog(GovernmentCog(bot))