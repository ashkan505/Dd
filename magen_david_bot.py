"""
ربات مرکزی ستاره داوود - مغز متفکر اکوسیستم اسرائیل
Magen David Central Bot - The Mastermind of Israel RP Ecosystem

این ربات مسئول کنترل کل سرور و هماهنگی با سایر ربات‌های تخصصی است.
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from utils import (
    BaseBot, EmbedBuilder, PermissionManager, TimeManager, 
    EconomyManager, NotificationManager, GeminiAI, EMOJIS,
    format_number, calculate_percentage, weighted_random_choice
)
from config import (
    BotConfig, ServerStructure, EconomicConfig, DefenseConfig,
    GameplayConfig, EMBED_COLORS, SYSTEM_MESSAGES, CURRENT_DEFCON,
    PUBLIC_APPROVAL, NATIONAL_RESOURCES
)

logger = logging.getLogger(__name__)

class MagenDavidBot(BaseBot):
    """ربات مرکزی ستاره داوود"""
    
    def __init__(self):
        super().__init__(
            command_prefix=BotConfig.COMMAND_PREFIX,
            bot_name="ستاره داوود",
            description="ربات مرکزی مدیریت سرور رول‌پلی اسرائیل"
        )
        
        self.token = BotConfig.MAGEN_DAVID_TOKEN
        self.defcon_level = CURRENT_DEFCON
        self.public_approval = PUBLIC_APPROVAL
        self.national_resources = NATIONAL_RESOURCES.copy()
        self.active_crises = []
        self.election_active = False
        self.election_candidates = {}
        self.current_era = "مدرن"
        self.great_people = []
        
        # بارگذاری کامندها
        self.load_commands()
        
        # شروع وظایف دوره‌ای
        self.start_background_tasks()
    
    def load_commands(self):
        """بارگذاری تمام کامندهای ربات"""
        
        @self.command(name='initialize_israel', aliases=['init'])
        @commands.has_permissions(administrator=True)
        async def initialize_israel(ctx):
            """پروتکل پیدایش - تبدیل سرور خام به اسرائیل کامل"""
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['israel_flag']} شروع پروتکل پیدایش اسرائیل",
                description="در حال تبدیل سرور به دولت اسرائیل...",
                color=EMBED_COLORS['info']
            )
            message = await ctx.send(embed=embed)
            
            try:
                # مرحله ۱: ایجاد کتگوری‌ها
                await self.create_categories(ctx.guild)
                embed.add_field(name="✅ مرحله ۱", value="کتگوری‌ها ایجاد شد", inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(2)
                
                # مرحله ۲: ایجاد کانال‌ها
                await self.create_channels(ctx.guild)
                embed.add_field(name="✅ مرحله ۲", value="کانال‌ها ایجاد شد", inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(2)
                
                # مرحله ۳: ایجاد رول‌ها
                await self.create_roles(ctx.guild)
                embed.add_field(name="✅ مرحله ۳", value="رول‌ها ایجاد شد", inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(2)
                
                # مرحله ۴: تنظیم مجوزها
                await self.setup_permissions(ctx.guild)
                embed.add_field(name="✅ مرحله ۴", value="مجوزها تنظیم شد", inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(2)
                
                # مرحله ۵: ایجاد پیام‌های خوش‌آمدگویی
                await self.setup_welcome_messages(ctx.guild)
                embed.add_field(name="✅ مرحله ۵", value="پیام‌های خوش‌آمدگویی تنظیم شد", inline=False)
                await message.edit(embed=embed)
                
                # پیام نهایی
                final_embed = EmbedBuilder.success_embed(
                    f"{EMOJIS['star_of_david']} پیدایش اسرائیل کامل شد!",
                    f"سرور با موفقیت به دولت اسرائیل تبدیل شد.\n\n"
                    f"🏛️ **حکومت**: آماده برای تشکیل\n"
                    f"🪖 **ارتش**: آماده برای خدمت\n"
                    f"💰 **اقتصاد**: آماده برای رشد\n"
                    f"🛡️ **دفاع**: آماده برای محافظت\n\n"
                    f"**مرحله بعدی**: از دستور `!start_government` برای شروع فعالیت دولت استفاده کنید."
                )
                final_embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d4/Flag_of_Israel.svg")
                await message.edit(embed=final_embed)
                
                # ثبت در پایگاه داده
                self.db.data['server_initialized'] = True
                self.db.data['initialization_date'] = datetime.now().isoformat()
                self.db.save_data()
                
            except Exception as e:
                error_embed = EmbedBuilder.error_embed(
                    "خطا در پیدایش",
                    f"خطایی در فرآیند پیدایش رخ داد: {str(e)}"
                )
                await message.edit(embed=error_embed)
                logger.error(f"خطا در initialize_israel: {e}")
        
        @self.command(name='apply_citizenship', aliases=['شهروندی'])
        async def apply_citizenship(ctx):
            """درخواست شهروندی"""
            
            # بررسی اینکه کاربر در کانال مناسب است
            if ctx.channel.name != 'immigration-office':
                embed = EmbedBuilder.error_embed(
                    "مکان نامناسب",
                    f"لطفاً برای درخواست شهروندی به کانال #immigration-office مراجعه کنید."
                )
                await ctx.send(embed=embed)
                return
            
            # بررسی اینکه کاربر قبلاً شهروند نیست
            user_data = self.db.get_user(ctx.author.id)
            if user_data.get('role') != 'tourist':
                embed = EmbedBuilder.error_embed(
                    "درخواست نامعتبر",
                    "شما قبلاً شهروند هستید یا درخواست شما در حال بررسی است."
                )
                await ctx.send(embed=embed)
                return
            
            # تولید سوالات با AI
            questions = await self.generate_citizenship_questions()
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['israel_flag']} درخواست شهروندی اسرائیل",
                description=f"سلام {ctx.author.mention}!\n\n"
                           f"برای دریافت شهروندی اسرائیل، لطفاً به سوالات زیر پاسخ دهید.\n"
                           f"شما ۵ دقیقه وقت دارید.\n\n"
                           f"**سوال ۱**: {questions[0]}\n\n"
                           f"لطفاً پاسخ خود را در همین کانال بنویسید.",
                color=EMBED_COLORS['info']
            )
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d4/Flag_of_Israel.svg")
            
            await ctx.send(embed=embed)
            
            # منتظر پاسخ‌ها
            answers = []
            for i, question in enumerate(questions):
                if i > 0:  # برای سوالات بعدی
                    embed = EmbedBuilder.create_embed(
                        title=f"سوال {i+1}",
                        description=question,
                        color=EMBED_COLORS['info']
                    )
                    await ctx.send(embed=embed)
                
                try:
                    def check(message):
                        return message.author == ctx.author and message.channel == ctx.channel
                    
                    answer = await self.wait_for('message', check=check, timeout=300.0)  # ۵ دقیقه
                    answers.append(answer.content)
                    
                    # تأیید دریافت پاسخ
                    await answer.add_reaction(EMOJIS['success'])
                    
                except asyncio.TimeoutError:
                    timeout_embed = EmbedBuilder.error_embed(
                        "زمان تمام شد",
                        "متأسفانه زمان پاسخ‌دهی تمام شد. لطفاً مجدداً درخواست دهید."
                    )
                    await ctx.send(embed=timeout_embed)
                    return
            
            # ارزیابی پاسخ‌ها با AI
            evaluation = await self.evaluate_citizenship_answers(questions, answers)
            
            if evaluation['approved']:
                # اعطای شهروندی
                await self.grant_citizenship(ctx.author, ctx.guild)
                
                success_embed = EmbedBuilder.success_embed(
                    f"{EMOJIS['medal']} تبریک! شهروندی اعطا شد",
                    f"به اسرائیل خوش آمدید، {ctx.author.mention}!\n\n"
                    f"🎉 شما اکنون شهروند رسمی اسرائیل هستید.\n"
                    f"💰 حساب بانکی شما با ۱۰۰۰ شکل افتتاح شد.\n"
                    f"📚 از دستور `!help` برای آشنایی با امکانات استفاده کنید.\n\n"
                    f"**نظر کمیسیون**: {evaluation['comment']}"
                )
                await ctx.send(embed=success_embed)
                
                # اعلام در کانال اخبار
                news_channel = discord.utils.get(ctx.guild.text_channels, name='national-news')
                if news_channel:
                    news_embed = EmbedBuilder.create_embed(
                        title=f"{EMOJIS['loudspeaker']} شهروند جدید",
                        description=f"🎊 {ctx.author.mention} به جمع شهروندان اسرائیل پیوست!",
                        color=EMBED_COLORS['success']
                    )
                    await news_channel.send(embed=news_embed)
                
            else:
                # رد درخواست
                reject_embed = EmbedBuilder.error_embed(
                    "درخواست رد شد",
                    f"متأسفانه درخواست شهروندی شما رد شد.\n\n"
                    f"**دلیل**: {evaluation['comment']}\n\n"
                    f"شما می‌توانید پس از ۲۴ ساعت مجدداً درخواست دهید."
                )
                await ctx.send(embed=reject_embed)
                
                # ثبت زمان رد درخواست
                user_data['last_citizenship_attempt'] = datetime.now().isoformat()
                self.db.update_user(ctx.author.id, user_data)
        
        @self.command(name='control_panel', aliases=['پنل'])
        @commands.has_permissions(administrator=True)
        async def control_panel(ctx):
            """داشبورد کنترل مرکزی"""
            
            guild = ctx.guild
            
            # جمع‌آوری آمار
            total_members = guild.member_count
            citizens = len([m for m in guild.members if any(r.name == 'شهروند' for r in m.roles)])
            tourists = total_members - citizens
            
            # آمار اقتصادی
            national_budget = self.db.data['economy']['national_budget']
            tax_collected = self.db.data['economy']['tax_collected']
            
            # آمار نظامی
            iron_dome_missiles = self.db.data['military']['equipment']['iron_dome_missiles']
            defcon_info = DefenseConfig.DEFCON_LEVELS[self.defcon_level]
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['star_of_david']} داشبورد کنترل مرکزی اسرائیل",
                description=f"گزارش وضعیت لحظه‌ای سیستم‌ها",
                color=EMBED_COLORS['government']
            )
            
            # بخش جمعیت
            embed.add_field(
                name=f"{EMOJIS['israel_flag']} جمعیت",
                value=f"👥 کل اعضا: **{format_number(total_members)}**\n"
                      f"🏠 شهروندان: **{format_number(citizens)}**\n"
                      f"✈️ توریست‌ها: **{format_number(tourists)}**\n"
                      f"📊 نرخ شهروندی: **{calculate_percentage(citizens, total_members)}%**",
                inline=True
            )
            
            # بخش اقتصاد
            embed.add_field(
                name=f"{EMOJIS['money']} اقتصاد",
                value=f"🏦 بودجه ملی: **{format_number(national_budget)}** {EconomicConfig.CURRENCY_SYMBOL}\n"
                      f"💸 مالیات جمع‌آوری شده: **{format_number(tax_collected)}** {EconomicConfig.CURRENCY_SYMBOL}\n"
                      f"💧 آب: **{self.national_resources['water']}%**\n"
                      f"⚡ انرژی: **{self.national_resources['energy']}%**",
                inline=True
            )
            
            # بخش دفاع
            embed.add_field(
                name=f"{EMOJIS['shield']} دفاع",
                value=f"🚨 سطح DEFCON: **{self.defcon_level}** ({defcon_info['name']})\n"
                      f"🚀 موشک‌های گنبد آهنین: **{format_number(iron_dome_missiles)}**\n"
                      f"📊 رضایت عمومی: **{self.public_approval}%**\n"
                      f"⚠️ بحران‌های فعال: **{len(self.active_crises)}**",
                inline=True
            )
            
            # بخش حکومت
            prime_minister = self.db.data['government'].get('prime_minister')
            pm_name = f"<@{prime_minister}>" if prime_minister else "انتخاب نشده"
            
            embed.add_field(
                name=f"{EMOJIS['government']} حکومت",
                value=f"👑 نخست‌وزیر: {pm_name}\n"
                      f"📜 قوانین مصوب: **{len(self.db.data['government']['laws'])}**\n"
                      f"🗳️ انتخابات فعال: **{'بله' if self.election_active else 'خیر'}**\n"
                      f"🏛️ وزرا: **{len(self.db.data['government']['ministers'])}**",
                inline=True
            )
            
            # بخش سیستم
            uptime = self.get_uptime()
            embed.add_field(
                name=f"{EMOJIS['info']} سیستم",
                value=f"🕐 آپتایم: {uptime}\n"
                      f"🌍 عصر فعلی: **{self.current_era}**\n"
                      f"⭐ شخصیت‌های بزرگ: **{len(self.great_people)}**\n"
                      f"📡 وضعیت: **آنلاین**",
                inline=True
            )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d4/Flag_of_Israel.svg")
            embed.set_footer(text=f"آخرین به‌روزرسانی: {TimeManager.format_time(TimeManager.get_current_time())}")
            
            await ctx.send(embed=embed)
        
        @self.command(name='propose_law', aliases=['قانون'])
        @commands.has_role('عضو کنست')
        async def propose_law(ctx, *, law_text):
            """پیشنهاد قانون جدید توسط اعضای کنست"""
            
            if not law_text:
                embed = EmbedBuilder.error_embed(
                    "متن قانون الزامی است",
                    "لطفاً متن قانون را همراه دستور ارسال کنید."
                )
                await ctx.send(embed=embed)
                return
            
            # تولید شماره قانون
            law_id = f"LAW-{len(self.db.data['government']['laws']) + 1:04d}"
            
            # ایجاد قانون
            law = {
                'id': law_id,
                'title': law_text[:100] + "..." if len(law_text) > 100 else law_text,
                'full_text': law_text,
                'proposer': ctx.author.id,
                'proposed_date': datetime.now().isoformat(),
                'status': 'voting',
                'votes_for': [],
                'votes_against': [],
                'votes_abstain': []
            }
            
            # ایجاد Embed برای رأی‌گیری
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['government']} لایحه قانونی جدید - {law_id}",
                description=f"**پیشنهاددهنده**: {ctx.author.mention}\n\n"
                           f"**متن قانون**:\n{law_text}\n\n"
                           f"اعضای کنست می‌توانند با استفاده از واکنش‌ها رأی دهند:\n"
                           f"✅ موافق\n"
                           f"❌ مخالف\n"
                           f"😐 ممتنع",
                color=EMBED_COLORS['government']
            )
            embed.set_footer(text="رأی‌گیری تا ۲۴ ساعت آینده ادامه دارد")
            
            # ارسال در کانال کنست
            knesset_channel = discord.utils.get(ctx.guild.text_channels, name='knesset-hall')
            if knesset_channel:
                message = await knesset_channel.send(embed=embed)
                
                # اضافه کردن واکنش‌ها
                await message.add_reaction('✅')
                await message.add_reaction('❌')
                await message.add_reaction('😐')
                
                # ذخیره قانون
                law['message_id'] = message.id
                self.db.data['government']['laws'].append(law)
                self.db.save_data()
                
                success_embed = EmbedBuilder.success_embed(
                    "لایحه ثبت شد",
                    f"لایحه {law_id} برای رأی‌گیری ارسال شد."
                )
                await ctx.send(embed=success_embed)
            else:
                error_embed = EmbedBuilder.error_embed(
                    "کانال یافت نشد",
                    "کانال کنست یافت نشد. لطفاً ابتدا سرور را مقداردهی اولیه کنید."
                )
                await ctx.send(embed=error_embed)
        
        @self.command(name='start_election', aliases=['انتخابات'])
        @commands.has_permissions(manage_guild=True)
        async def start_election(ctx):
            """شروع انتخابات نخست‌وزیری"""
            
            if self.election_active:
                embed = EmbedBuilder.error_embed(
                    "انتخابات فعال",
                    "انتخابات در حال حاضر در جریان است."
                )
                await ctx.send(embed=embed)
                return
            
            self.election_active = True
            self.election_candidates = {}
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['government']} آغاز انتخابات نخست‌وزیری",
                description=f"🗳️ **انتخابات نخست‌وزیری اسرائیل آغاز شد!**\n\n"
                           f"📋 **مراحل انتخابات**:\n"
                           f"1️⃣ ثبت‌نام کاندیداها (۲۴ ساعت)\n"
                           f"2️⃣ مبارزات انتخاباتی (۴۸ ساعت)\n"
                           f"3️⃣ رأی‌گیری (۲۴ ساعت)\n\n"
                           f"**شرایط کاندیداتوری**:\n"
                           f"• داشتن رول شهروند\n"
                           f"• حداقل ۷ روز عضویت در سرور\n"
                           f"• عدم سابقه محکومیت جدی\n\n"
                           f"برای ثبت‌نام از دستور `!register_candidate` استفاده کنید.",
                color=EMBED_COLORS['government']
            )
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d4/Flag_of_Israel.svg")
            
            # اعلام در کانال‌های مختلف
            channels_to_announce = ['general-chat', 'national-news', 'knesset-hall']
            for channel_name in channels_to_announce:
                channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
                if channel:
                    await channel.send(embed=embed)
            
            # ذخیره اطلاعات انتخابات
            election_data = {
                'start_date': datetime.now().isoformat(),
                'phase': 'registration',
                'candidates': {},
                'votes': {}
            }
            self.db.data['government']['current_election'] = election_data
            self.db.save_data()
        
        @self.command(name='register_candidate', aliases=['کاندیدا'])
        async def register_candidate(ctx, *, campaign_message):
            """ثبت‌نام کاندیدا در انتخابات"""
            
            if not self.election_active:
                embed = EmbedBuilder.error_embed(
                    "انتخابات غیرفعال",
                    "در حال حاضر انتخاباتی در جریان نیست."
                )
                await ctx.send(embed=embed)
                return
            
            # بررسی شرایط
            if not PermissionManager.has_role(ctx.author, 'شهروند'):
                embed = EmbedBuilder.error_embed(
                    "عدم واجد شرایط",
                    "فقط شهروندان می‌توانند کاندیدا شوند."
                )
                await ctx.send(embed=embed)
                return
            
            # بررسی تکراری نبودن
            if ctx.author.id in self.election_candidates:
                embed = EmbedBuilder.error_embed(
                    "ثبت‌نام قبلی",
                    "شما قبلاً ثبت‌نام کرده‌اید."
                )
                await ctx.send(embed=embed)
                return
            
            # ثبت کاندیدا
            self.election_candidates[ctx.author.id] = {
                'name': ctx.author.display_name,
                'campaign_message': campaign_message,
                'votes': 0,
                'registration_date': datetime.now().isoformat()
            }
            
            success_embed = EmbedBuilder.success_embed(
                "ثبت‌نام موفق",
                f"🎉 {ctx.author.mention} با موفقیت به عنوان کاندیدای نخست‌وزیری ثبت‌نام شد!\n\n"
                f"**پیام انتخاباتی**: {campaign_message}"
            )
            await ctx.send(embed=success_embed)
            
            # اعلام در کانال اخبار
            news_channel = discord.utils.get(ctx.guild.text_channels, name='national-news')
            if news_channel:
                news_embed = EmbedBuilder.create_embed(
                    title=f"{EMOJIS['loudspeaker']} کاندیدای جدید",
                    description=f"🗳️ {ctx.author.mention} وارد رقابت انتخاباتی شد!",
                    color=EMBED_COLORS['info']
                )
                await news_channel.send(embed=news_embed)
        
        @self.command(name='declare_war', aliases=['جنگ'])
        @commands.has_role('نخست‌وزیر')
        async def declare_war(ctx, target_server: str, *, reason):
            """اعلام جنگ به سرور دیگر"""
            
            # تولید پیام جنگ با AI
            war_declaration = await self.ai.generate_content(
                f"یک اعلامیه جنگ رسمی و دیپلماتیک علیه {target_server} با دلیل {reason} بنویس. "
                f"پیام باید رسمی، قدرتمند و مطابق با اصول دیپلماسی باشد."
            )
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['sword']} اعلامیه جنگ",
                description=f"**هدف**: {target_server}\n"
                           f"**دلیل**: {reason}\n\n"
                           f"**متن اعلامیه**:\n{war_declaration}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"امضا: {ctx.author.display_name}، نخست‌وزیر اسرائیل")
            
            # ارسال در کانال‌های مختلف
            channels = ['national-news', 'high-command', 'government-announcements']
            for channel_name in channels:
                channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
                if channel:
                    await channel.send(embed=embed)
            
            # کاهش رضایت عمومی (جنگ محبوب نیست)
            self.public_approval = max(0, self.public_approval - random.randint(5, 15))
            
            # افزایش سطح DEFCON
            if self.defcon_level > 2:
                self.defcon_level = 2
                await self.announce_defcon_change(ctx.guild)
        
        @self.command(name='form_alliance', aliases=['اتحاد'])
        @commands.has_role('نخست‌وزیر')
        async def form_alliance(ctx, partner_server: str, *, terms):
            """تشکیل اتحاد با سرور دیگر"""
            
            # تولید پیام اتحاد با AI
            alliance_proposal = await self.ai.generate_content(
                f"یک پیشنهاد اتحاد دیپلماتیک با {partner_server} با شرایط {terms} بنویس. "
                f"پیام باید رسمی، دوستانه و مطابق با اصول دیپلماسی باشد."
            )
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['star_of_david']} پیشنهاد اتحاد",
                description=f"**شریک**: {partner_server}\n"
                           f"**شرایط**: {terms}\n\n"
                           f"**متن پیشنهاد**:\n{alliance_proposal}",
                color=EMBED_COLORS['success']
            )
            embed.set_footer(text=f"امضا: {ctx.author.display_name}، نخست‌وزیر اسرائیل")
            
            # ارسال در کانال‌های دیپلماتیک
            channels = ['national-news', 'government-announcements']
            for channel_name in channels:
                channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
                if channel:
                    await channel.send(embed=embed)
            
            # افزایش رضایت عمومی (اتحاد خوب است)
            self.public_approval = min(100, self.public_approval + random.randint(3, 8))
        
        @self.command(name='crisis_response', aliases=['پاسخ_بحران'])
        @commands.has_role('نخست‌وزیر')
        async def crisis_response(ctx, crisis_id: str, *, response):
            """پاسخ دولت به بحران"""
            
            # یافتن بحران
            crisis = None
            for c in self.active_crises:
                if c['id'] == crisis_id:
                    crisis = c
                    break
            
            if not crisis:
                embed = EmbedBuilder.error_embed(
                    "بحران یافت نشد",
                    f"بحران با شناسه {crisis_id} یافت نشد."
                )
                await ctx.send(embed=embed)
                return
            
            # ارزیابی پاسخ با AI
            evaluation = await self.ai.generate_content(
                f"پاسخ دولت به بحران '{crisis['title']}' ارزیابی کن: {response}. "
                f"نتیجه را به صورت JSON با کلیدهای effectiveness (0-100), "
                f"public_reaction (-20 to +20), cost (0-1000000) برگردان."
            )
            
            try:
                import re
                json_match = re.search(r'\{.*\}', evaluation, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {'effectiveness': 50, 'public_reaction': 0, 'cost': 100000}
            except:
                result = {'effectiveness': 50, 'public_reaction': 0, 'cost': 100000}
            
            # اعمال نتایج
            effectiveness = result.get('effectiveness', 50)
            public_reaction = result.get('public_reaction', 0)
            cost = result.get('cost', 100000)
            
            self.public_approval = max(0, min(100, self.public_approval + public_reaction))
            self.db.data['economy']['national_budget'] -= cost
            
            # اگر پاسخ مؤثر بود، بحران حل می‌شود
            if effectiveness >= 70:
                self.active_crises.remove(crisis)
                status = "حل شد"
                status_color = EMBED_COLORS['success']
            elif effectiveness >= 40:
                crisis['severity'] = max(1, crisis.get('severity', 5) - 2)
                status = "بهبود یافت"
                status_color = EMBED_COLORS['warning']
            else:
                crisis['severity'] = min(10, crisis.get('severity', 5) + 1)
                status = "تشدید شد"
                status_color = EMBED_COLORS['error']
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['government']} پاسخ دولت به بحران",
                description=f"**بحران**: {crisis['title']}\n"
                           f"**پاسخ دولت**: {response}\n\n"
                           f"**نتایج**:\n"
                           f"📊 میزان اثربخشی: **{effectiveness}%**\n"
                           f"👥 واکنش مردم: **{public_reaction:+d}**\n"
                           f"💰 هزینه: **{format_number(cost)}** شکل\n"
                           f"🎯 وضعیت بحران: **{status}**",
                color=status_color
            )
            
            await ctx.send(embed=embed)
            
            # اعلام در کانال اخبار
            news_channel = discord.utils.get(ctx.guild.text_channels, name='national-news')
            if news_channel:
                await news_channel.send(embed=embed)
        
        @self.command(name='national_stats', aliases=['آمار'])
        async def national_stats(ctx):
            """نمایش آمار ملی"""
            
            # جمع‌آوری آمار کامل
            guild = ctx.guild
            total_members = guild.member_count
            
            # آمار نقش‌ها
            role_stats = {}
            for role_name in ['شهروند', 'سرباز', 'پزشک', 'مهندس', 'دانشمند']:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    role_stats[role_name] = len(role.members)
            
            # آمار اقتصادی
            total_money_in_circulation = sum(
                user_data.get('balance', 0) 
                for user_data in self.db.data['users'].values()
            )
            
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['israel_flag']} آمار ملی اسرائیل",
                description="گزارش جامع وضعیت کشور",
                color=EMBED_COLORS['info']
            )
            
            # آمار جمعیتی
            population_text = f"👥 کل جمعیت: **{format_number(total_members)}**\n"
            for role, count in role_stats.items():
                percentage = calculate_percentage(count, total_members)
                population_text += f"{role}: **{format_number(count)}** ({percentage}%)\n"
            
            embed.add_field(
                name="📊 جمعیت",
                value=population_text,
                inline=True
            )
            
            # آمار اقتصادی
            economy_text = (
                f"🏦 بودجه ملی: **{format_number(self.db.data['economy']['national_budget'])}** ₪\n"
                f"💰 پول در گردش: **{format_number(total_money_in_circulation)}** ₪\n"
                f"💸 مالیات جمع‌آوری شده: **{format_number(self.db.data['economy']['tax_collected'])}** ₪\n"
                f"📈 تراکنش‌های کل: **{format_number(self.db.data['economy']['total_transactions'])}**"
            )
            
            embed.add_field(
                name="💰 اقتصاد",
                value=economy_text,
                inline=True
            )
            
            # آمار دفاعی
            defense_text = (
                f"🚨 سطح DEFCON: **{self.defcon_level}**\n"
                f"🚀 موشک‌های آماده: **{format_number(self.db.data['military']['equipment']['iron_dome_missiles'])}**\n"
                f"📊 رضایت عمومی: **{self.public_approval}%**\n"
                f"⚠️ بحران‌های فعال: **{len(self.active_crises)}**"
            )
            
            embed.add_field(
                name="🛡️ دفاع",
                value=defense_text,
                inline=True
            )
            
            # آمار حکومتی
            government_text = (
                f"👑 نخست‌وزیر: {'انتخاب شده' if self.db.data['government']['prime_minister'] else 'انتخاب نشده'}\n"
                f"🏛️ تعداد وزرا: **{len(self.db.data['government']['ministers'])}**\n"
                f"📜 قوانین مصوب: **{len(self.db.data['government']['laws'])}**\n"
                f"🗳️ انتخابات فعال: **{'بله' if self.election_active else 'خیر'}**"
            )
            
            embed.add_field(
                name="🏛️ حکومت",
                value=government_text,
                inline=True
            )
            
            # منابع ملی
            resources_text = (
                f"💧 آب: **{self.national_resources['water']}%**\n"
                f"⚡ انرژی: **{self.national_resources['energy']}%**\n"
                f"🌍 عصر فعلی: **{self.current_era}**\n"
                f"⭐ شخصیت‌های بزرگ: **{len(self.great_people)}**"
            )
            
            embed.add_field(
                name="🌍 منابع و پیشرفت",
                value=resources_text,
                inline=True
            )
            
            # آمار فعالیت
            activity_text = (
                f"📅 روز‌های فعالیت: **{(datetime.now() - datetime.fromisoformat(self.db.data.get('initialization_date', datetime.now().isoformat()))).days}**\n"
                f"📊 کل رویدادها: **{len(self.db.data.get('events', []))}**\n"
                f"🏠 املاک ثبت شده: **{len(self.db.data.get('properties', {}))}**\n"
                f"🏢 شرکت‌های فعال: **{len(self.db.data.get('companies', {}))}**"
            )
            
            embed.add_field(
                name="📈 فعالیت",
                value=activity_text,
                inline=True
            )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d4/Flag_of_Israel.svg")
            embed.set_footer(text=f"آخرین به‌روزرسانی: {TimeManager.format_time(TimeManager.get_current_time())}")
            
            await ctx.send(embed=embed)
        
        @self.command(name='help', aliases=['راهنما'])
        async def help_command(ctx, category: str = None):
            """راهنمای کامل دستورات"""
            
            if category is None:
                # نمایش کتگوری‌های اصلی
                embed = EmbedBuilder.create_embed(
                    title=f"{EMOJIS['star_of_david']} راهنمای ربات ستاره داوود",
                    description="برای مشاهده دستورات هر بخش، از `!help [نام بخش]` استفاده کنید.",
                    color=EMBED_COLORS['info']
                )
                
                categories = [
                    ("government", "🏛️ حکومت", "مدیریت دولت و قانون‌گذاری"),
                    ("citizen", "👥 شهروندی", "خدمات شهروندی و مهاجرت"),
                    ("economy", "💰 اقتصاد", "مدیریت مالی و تجارت"),
                    ("military", "🪖 نظامی", "امور دفاعی و نظامی"),
                    ("social", "🎭 اجتماعی", "فعالیت‌های اجتماعی و فرهنگی"),
                    ("admin", "⚙️ مدیریت", "دستورات مدیریتی")
                ]
                
                for cat_id, cat_name, cat_desc in categories:
                    embed.add_field(
                        name=cat_name,
                        value=f"{cat_desc}\n`!help {cat_id}`",
                        inline=True
                    )
                
            else:
                # نمایش دستورات بخش خاص
                commands_data = self.get_commands_by_category(category)
                if commands_data:
                    embed = EmbedBuilder.create_embed(
                        title=f"راهنمای دستورات {commands_data['title']}",
                        description=commands_data['description'],
                        color=EMBED_COLORS['info']
                    )
                    
                    for cmd in commands_data['commands']:
                        embed.add_field(
                            name=f"`{BotConfig.COMMAND_PREFIX}{cmd['name']}`",
                            value=f"{cmd['description']}\n**استفاده**: `{cmd['usage']}`",
                            inline=False
                        )
                else:
                    embed = EmbedBuilder.error_embed(
                        "بخش یافت نشد",
                        f"بخش '{category}' یافت نشد. از `!help` برای مشاهده بخش‌های موجود استفاده کنید."
                    )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d4/Flag_of_Israel.svg")
            await ctx.send(embed=embed)
    
    def start_background_tasks(self):
        """شروع وظایف پس‌زمینه"""
        
        @tasks.loop(hours=6)
        async def generate_random_events():
            """تولید رویدادهای تصادفی"""
            if not self.is_ready():
                return
                
            guild = await self.get_main_guild()
            if not guild:
                return
            
            # احتمال رخداد رویداد
            if random.random() < 0.3:  # ۳۰٪ احتمال هر ۶ ساعت
                event = await self.generate_random_event()
                await self.announce_event(guild, event)
        
        @tasks.loop(hours=12)
        async def generate_crisis():
            """تولید بحران‌های تصادفی"""
            if not self.is_ready() or len(self.active_crises) >= 3:
                return
                
            guild = await self.get_main_guild()
            if not guild:
                return
            
            # احتمال بحران بر اساس رضایت عمومی
            crisis_probability = 0.1 + (100 - self.public_approval) / 1000
            
            if random.random() < crisis_probability:
                crisis = await self.ai.generate_crisis()
                crisis['id'] = f"CRISIS-{len(self.active_crises) + 1:03d}"
                crisis['start_date'] = datetime.now().isoformat()
                crisis['severity'] = random.randint(3, 7)
                
                self.active_crises.append(crisis)
                await self.announce_crisis(guild, crisis)
        
        @tasks.loop(hours=24)
        async def daily_economy_update():
            """به‌روزرسانی روزانه اقتصاد"""
            if not self.is_ready():
                return
                
            # پرداخت حقوق روزانه
            await self.pay_daily_salaries()
            
            # کاهش منابع
            self.national_resources['water'] = max(0, self.national_resources['water'] - random.randint(1, 3))
            self.national_resources['energy'] = max(0, self.national_resources['energy'] - random.randint(1, 3))
            
            # تولید گزارش اقتصادی
            guild = await self.get_main_guild()
            if guild:
                await self.send_economic_report(guild)
        
        @tasks.loop(minutes=30)
        async def update_day_night_cycle():
            """به‌روزرسانی چرخه شب و روز"""
            if not self.is_ready():
                return
                
            guild = await self.get_main_guild()
            if not guild:
                return
            
            current_hour = TimeManager.get_current_time().hour
            
            # تغییر نام کانال بر اساس زمان
            general_channel = discord.utils.get(guild.text_channels, name='general-chat')
            if general_channel:
                if 6 <= current_hour < 18:
                    new_name = f"☀️-general-chat-day"
                else:
                    new_name = f"🌙-general-chat-night"
                
                if general_channel.name != new_name:
                    try:
                        await general_channel.edit(name=new_name)
                    except:
                        pass  # در صورت خطا ادامه می‌دهد
        
        # شروع تسک‌ها
        generate_random_events.start()
        generate_crisis.start()
        daily_economy_update.start()
        update_day_night_cycle.start()
    
    async def create_categories(self, guild: discord.Guild):
        """ایجاد کتگوری‌های سرور"""
        for category_id, category_name in ServerStructure.CATEGORIES.items():
            try:
                await guild.create_category(category_name)
                await asyncio.sleep(1)  # جلوگیری از Rate Limit
            except discord.HTTPException as e:
                logger.error(f"خطا در ایجاد کتگوری {category_name}: {e}")
    
    async def create_channels(self, guild: discord.Guild):
        """ایجاد کانال‌های سرور"""
        for category_id, channels in ServerStructure.CHANNELS.items():
            category = discord.utils.get(guild.categories, name=ServerStructure.CATEGORIES.get(category_id, category_id))
            
            for channel_info in channels:
                try:
                    if channel_info['type'] == 'text':
                        await guild.create_text_channel(
                            channel_info['name'],
                            category=category,
                            topic=channel_info['description']
                        )
                    elif channel_info['type'] == 'voice':
                        await guild.create_voice_channel(
                            channel_info['name'],
                            category=category
                        )
                    await asyncio.sleep(1)
                except discord.HTTPException as e:
                    logger.error(f"خطا در ایجاد کانال {channel_info['name']}: {e}")
    
    async def create_roles(self, guild: discord.Guild):
        """ایجاد رول‌های سرور"""
        for role_id, role_info in ServerStructure.ROLES.items():
            try:
                permissions = discord.Permissions()
                for perm in role_info.get('permissions', []):
                    setattr(permissions, perm, True)
                
                await guild.create_role(
                    name=role_info['name'],
                    color=discord.Color(role_info['color']),
                    permissions=permissions,
                    mentionable=True
                )
                await asyncio.sleep(1)
            except discord.HTTPException as e:
                logger.error(f"خطا در ایجاد رول {role_info['name']}: {e}")
    
    async def setup_permissions(self, guild: discord.Guild):
        """تنظیم مجوزهای کانال‌ها"""
        # این بخش پیچیده است و نیاز به تنظیم دقیق مجوزها دارد
        # برای سادگی، فقط مجوزهای اصلی تنظیم می‌شود
        
        tourist_role = discord.utils.get(guild.roles, name='توریست')
        citizen_role = discord.utils.get(guild.roles, name='شهروند')
        
        if tourist_role and citizen_role:
            # محدود کردن دسترسی توریست‌ها
            for channel in guild.text_channels:
                if channel.name in ['immigration-office', 'general-chat']:
                    await channel.set_permissions(tourist_role, read_messages=True, send_messages=True)
                else:
                    await channel.set_permissions(tourist_role, read_messages=False, send_messages=False)
    
    async def setup_welcome_messages(self, guild: discord.Guild):
        """تنظیم پیام‌های خوش‌آمدگویی"""
        welcome_channel = discord.utils.get(guild.text_channels, name='general-chat')
        if welcome_channel:
            embed = EmbedBuilder.create_embed(
                title=f"{EMOJIS['israel_flag']} به اسرائیل خوش آمدید!",
                description=f"🎉 **سرور رول‌پلی اسرائیل آماده است!**\n\n"
                           f"📋 **برای شروع**:\n"
                           f"1️⃣ برای دریافت شهروندی به #immigration-office بروید\n"
                           f"2️⃣ از دستور `!apply_citizenship` استفاده کنید\n"
                           f"3️⃣ پس از دریافت شهروندی، از `!help` استفاده کنید\n\n"
                           f"🎯 **هدف**: ایجاد یک جامعه مجازی زنده و پویا\n"
                           f"🤝 **قوانین**: احترام متقابل و رول‌پلی مناسب\n\n"
                           f"موفق باشید! 🇮🇱",
                color=EMBED_COLORS['success']
            )
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d4/Flag_of_Israel.svg")
            await welcome_channel.send(embed=embed)
    
    async def generate_citizenship_questions(self) -> List[str]:
        """تولید سوالات شهروندی با AI"""
        questions_prompt = """
        ۳ سوال مناسب برای درخواست شهروندی در سرور رول‌پلی اسرائیل تولید کن.
        سوالات باید:
        1. مرتبط با اسرائیل باشند (تاریخ، فرهنگ، جغرافیا)
        2. نه خیلی آسان و نه خیلی سخت باشند
        3. برای سنجش علاقه و دانش عمومی باشند
        
        فقط سوالات را برگردان، هر سوال در یک خط.
        """
        
        try:
            response = await self.ai.generate_content(questions_prompt)
            questions = [q.strip() for q in response.split('\n') if q.strip()]
            
            # اگر AI نتوانست سوالات مناسب تولید کند، از سوالات پیش‌فرض استفاده می‌کنیم
            if len(questions) < 3:
                questions = [
                    "پایتخت اسرائیل کدام شهر است؟",
                    "چرا تمایل دارید در این سرور شرکت کنید؟",
                    "یک جاذبه مشهور اسرائیل را نام ببرید."
                ]
            
            return questions[:3]  # فقط ۳ سوال اول
            
        except Exception as e:
            logger.error(f"خطا در تولید سوالات شهروندی: {e}")
            return [
                "پایتخت اسرائیل کدام شهر است؟",
                "چرا تمایل دارید در این سرور شرکت کنید؟",
                "یک جاذبه مشهور اسرائیل را نام ببرید."
            ]
    
    async def evaluate_citizenship_answers(self, questions: List[str], answers: List[str]) -> Dict:
        """ارزیابی پاسخ‌های شهروندی با AI"""
        evaluation_prompt = f"""
        پاسخ‌های زیر را برای درخواست شهروندی ارزیابی کن:
        
        سوال ۱: {questions[0]}
        پاسخ ۱: {answers[0]}
        
        سوال ۲: {questions[1]}
        پاسخ ۲: {answers[1]}
        
        سوال ۳: {questions[2]}
        پاسخ ۳: {answers[2]}
        
        نتیجه را به صورت JSON با کلیدهای زیر برگردان:
        - approved: true/false
        - comment: نظر کوتاه درباره پاسخ‌ها
        - score: نمره از ۰ تا ۱۰۰
        """
        
        try:
            response = await self.ai.generate_content(evaluation_prompt)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                # اطمینان از وجود کلیدهای مورد نیاز
                if 'approved' not in result:
                    result['approved'] = result.get('score', 50) >= 60
                if 'comment' not in result:
                    result['comment'] = "پاسخ‌های شما بررسی شد."
                return result
            else:
                # اگر AI نتوانست JSON مناسب تولید کند
                return {
                    'approved': True,  # به صورت پیش‌فرض تأیید می‌کنیم
                    'comment': 'پاسخ‌های شما قابل قبول است. خوش آمدید!',
                    'score': 75
                }
                
        except Exception as e:
            logger.error(f"خطا در ارزیابی پاسخ‌ها: {e}")
            return {
                'approved': True,
                'comment': 'خوش آمدید به اسرائیل!',
                'score': 70
            }
    
    async def grant_citizenship(self, member: discord.Member, guild: discord.Guild):
        """اعطای شهروندی"""
        # حذف رول توریست
        tourist_role = discord.utils.get(guild.roles, name='توریست')
        if tourist_role and tourist_role in member.roles:
            await member.remove_roles(tourist_role)
        
        # اضافه کردن رول شهروند
        citizen_role = discord.utils.get(guild.roles, name='شهروند')
        if citizen_role:
            await member.add_roles(citizen_role)
        
        # به‌روزرسانی اطلاعات کاربر
        user_data = self.db.get_user(member.id)
        user_data['role'] = 'citizen'
        user_data['citizenship_date'] = datetime.now().isoformat()
        user_data['balance'] = 1000  # پول اولیه
        self.db.update_user(member.id, user_data)
    
    async def announce_defcon_change(self, guild: discord.Guild):
        """اعلام تغییر سطح DEFCON"""
        defcon_info = DefenseConfig.DEFCON_LEVELS[self.defcon_level]
        
        embed = EmbedBuilder.create_embed(
            title=f"🚨 تغییر سطح DEFCON",
            description=f"سطح آمادگی دفاعی به **DEFCON {self.defcon_level}** تغییر کرد.\n\n"
                       f"**وضعیت**: {defcon_info['name']}\n"
                       f"**حساسیت سیستم‌ها**: {int(defcon_info['sensitivity'] * 100)}%",
            color=defcon_info['color']
        )
        
        # ارسال به کانال‌های مربوطه
        channels = ['war-room', 'national-news', 'defense-alerts']
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(embed=embed)
    
    async def generate_random_event(self) -> Dict:
        """تولید رویداد تصادفی"""
        event_types = [
            "اکتشاف علمی", "موفقیت دیپلماتیک", "رشد اقتصادی",
            "جشنواره فرهنگی", "پیروزی ورزشی", "نوآوری فناورانه"
        ]
        
        event_type = random.choice(event_types)
        event_data = await self.ai.generate_content(
            f"یک رویداد مثبت از نوع '{event_type}' برای سرور رول‌پلی اسرائیل تولید کن. "
            f"رویداد باید شامل عنوان، توضیحات و تأثیرات مثبت باشد."
        )
        
        return {
            'type': event_type,
            'title': f"رویداد ویژه: {event_type}",
            'description': event_data,
            'timestamp': datetime.now().isoformat(),
            'effects': {
                'public_approval': random.randint(2, 8),
                'economy_boost': random.randint(50000, 200000)
            }
        }
    
    async def announce_event(self, guild: discord.Guild, event: Dict):
        """اعلام رویداد در سرور"""
        embed = EmbedBuilder.create_embed(
            title=f"🎉 {event['title']}",
            description=event['description'],
            color=EMBED_COLORS['success']
        )
        
        # اعمال تأثیرات
        if 'effects' in event:
            effects = event['effects']
            self.public_approval = min(100, self.public_approval + effects.get('public_approval', 0))
            self.db.data['economy']['national_budget'] += effects.get('economy_boost', 0)
            
            effects_text = []
            if effects.get('public_approval', 0) > 0:
                effects_text.append(f"📈 رضایت عمومی: +{effects['public_approval']}%")
            if effects.get('economy_boost', 0) > 0:
                effects_text.append(f"💰 تقویت اقتصاد: +{format_number(effects['economy_boost'])} شکل")
            
            if effects_text:
                embed.add_field(
                    name="تأثیرات",
                    value="\n".join(effects_text),
                    inline=False
                )
        
        # ارسال به کانال اخبار
        news_channel = discord.utils.get(guild.text_channels, name='national-news')
        if news_channel:
            await news_channel.send(embed=embed)
    
    async def announce_crisis(self, guild: discord.Guild, crisis: Dict):
        """اعلام بحران در سرور"""
        embed = EmbedBuilder.create_embed(
            title=f"⚠️ بحران: {crisis['title']}",
            description=f"**شناسه**: {crisis['id']}\n\n"
                       f"**توضیحات**: {crisis['description']}\n\n"
                       f"**راه‌حل‌های پیشنهادی**:\n" + 
                       "\n".join([f"• {solution}" for solution in crisis.get('solutions', [])]),
            color=EMBED_COLORS['error']
        )
        
        embed.add_field(
            name="نیاز به اقدام",
            value=f"نخست‌وزیر می‌تواند با دستور `!crisis_response {crisis['id']} [پاسخ]` به این بحران پاسخ دهد.",
            inline=False
        )
        
        # ارسال به کانال‌های مربوطه
        channels = ['national-news', 'government-announcements']
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(embed=embed)
    
    async def pay_daily_salaries(self):
        """پرداخت حقوق روزانه"""
        for user_id, user_data in self.db.data['users'].items():
            role = user_data.get('role', 'tourist')
            daily_income = EconomicConfig.DAILY_INCOME.get(role, 0)
            
            if daily_income > 0:
                user_data['balance'] = user_data.get('balance', 0) + daily_income
                
                # کسر از بودجه ملی
                self.db.data['economy']['national_budget'] -= daily_income
        
        self.db.save_data()
    
    async def send_economic_report(self, guild: discord.Guild):
        """ارسال گزارش اقتصادی روزانه"""
        total_salaries_paid = sum(
            EconomicConfig.DAILY_INCOME.get(user_data.get('role', 'tourist'), 0)
            for user_data in self.db.data['users'].values()
        )
        
        embed = EmbedBuilder.create_embed(
            title=f"📊 گزارش اقتصادی روزانه",
            description=f"خلاصه فعالیت‌های اقتصادی امروز",
            color=EMBED_COLORS['economy']
        )
        
        embed.add_field(
            name="💰 حقوق پرداختی",
            value=f"{format_number(total_salaries_paid)} شکل",
            inline=True
        )
        
        embed.add_field(
            name="🏦 بودجه ملی",
            value=f"{format_number(self.db.data['economy']['national_budget'])} شکل",
            inline=True
        )
        
        embed.add_field(
            name="💧 منابع ملی",
            value=f"آب: {self.national_resources['water']}%\nانرژی: {self.national_resources['energy']}%",
            inline=True
        )
        
        # ارسال به کانال اقتصاد
        economy_channel = discord.utils.get(guild.text_channels, name='economic-reports')
        if economy_channel:
            await economy_channel.send(embed=embed)
    
    def get_commands_by_category(self, category: str) -> Optional[Dict]:
        """دریافت دستورات بر اساس کتگوری"""
        commands_data = {
            'government': {
                'title': '🏛️ حکومت',
                'description': 'دستورات مربوط به مدیریت دولت و قانون‌گذاری',
                'commands': [
                    {
                        'name': 'propose_law [متن قانون]',
                        'description': 'پیشنهاد قانون جدید (فقط اعضای کنست)',
                        'usage': '!propose_law ممنوعیت اسپم در کانال‌های عمومی'
                    },
                    {
                        'name': 'start_election',
                        'description': 'شروع انتخابات نخست‌وزیری (فقط مدیران)',
                        'usage': '!start_election'
                    },
                    {
                        'name': 'register_candidate [پیام انتخاباتی]',
                        'description': 'ثبت‌نام در انتخابات',
                        'usage': '!register_candidate من برای رفاه مردم تلاش می‌کنم'
                    },
                    {
                        'name': 'declare_war [سرور] [دلیل]',
                        'description': 'اعلام جنگ (فقط نخست‌وزیر)',
                        'usage': '!declare_war ServerX نقض توافقنامه'
                    },
                    {
                        'name': 'form_alliance [سرور] [شرایط]',
                        'description': 'تشکیل اتحاد (فقط نخست‌وزیر)',
                        'usage': '!form_alliance ServerY همکاری اقتصادی'
                    }
                ]
            },
            'citizen': {
                'title': '👥 شهروندی',
                'description': 'خدمات شهروندی و مهاجرت',
                'commands': [
                    {
                        'name': 'apply_citizenship',
                        'description': 'درخواست شهروندی (در کانال immigration-office)',
                        'usage': '!apply_citizenship'
                    },
                    {
                        'name': 'national_stats',
                        'description': 'مشاهده آمار ملی',
                        'usage': '!national_stats'
                    },
                    {
                        'name': 'profile [کاربر]',
                        'description': 'مشاهده پروفایل شخصی یا دیگران',
                        'usage': '!profile @user'
                    }
                ]
            },
            'admin': {
                'title': '⚙️ مدیریت',
                'description': 'دستورات مدیریتی سیستم',
                'commands': [
                    {
                        'name': 'initialize_israel',
                        'description': 'مقداردهی اولیه سرور (فقط مدیران)',
                        'usage': '!initialize_israel'
                    },
                    {
                        'name': 'control_panel',
                        'description': 'داشبورد کنترل مرکزی (فقط مدیران)',
                        'usage': '!control_panel'
                    },
                    {
                        'name': 'crisis_response [شناسه] [پاسخ]',
                        'description': 'پاسخ به بحران (فقط نخست‌وزیر)',
                        'usage': '!crisis_response CRISIS-001 تخصیص بودجه اضطراری'
                    }
                ]
            }
        }
        
        return commands_data.get(category)

# اجرای ربات
if __name__ == "__main__":
    bot = MagenDavidBot()
    
    try:
        bot.run(bot.token)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات: {e}")