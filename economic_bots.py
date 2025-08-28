#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات‌های اقتصادی و صنعتی اسرائیل
Economic and Industrial Bots for Israeli RP Server

این فایل شامل پیاده‌سازی ربات‌های اقتصادی و صنعتی است:
- بانک مرکزی اسرائیل (Central Bank of Israel)
- صنایع نظامی (Military Industries)
- بورس تل‌آویو (Tel Aviv Stock Exchange)
- وزارت اقتصاد (Ministry of Economy)

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

# ======================= ربات بانک مرکزی اسرائیل =======================

class CentralBankBot(commands.Bot):
    """
    ربات بانک مرکزی اسرائیل
    مسئول مدیریت سیستم بانکی، حقوق و دستمزد، مالیات و بودجه ملی
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!بانک_',
            intents=intents,
            help_command=None,
            description="بانک مرکزی اسرائیل - مدیریت اقتصاد ملی"
        )
        
        # پایگاه داده داخلی
        self.db = DatabaseManager()
        
        # تنظیمات اقتصادی
        self.base_salary = {
            'شهروند': 1000,
            'سرباز': 1500,
            'افسر': 2500,
            'پزشک': 3000,
            'مهندس': 2800,
            'دانشمند': 3500,
            'وزیر': 5000,
            'نخست‌وزیر': 10000
        }
        
        self.tax_rates = {
            'income': 0.15,  # مالیات بر درآمد
            'transaction': 0.05,  # مالیات بر تراکنش
            'business': 0.20  # مالیات شرکت‌ها
        }
        
        # آمار اقتصادی
        self.economic_stats = {
            'gdp': 1000000,
            'inflation': 2.5,
            'unemployment': 4.2,
            'interest_rate': 1.75,
            'national_debt': 500000,
            'budget_deficit': 0
        }
        
        # بودجه دولتی
        self.government_budget = {
            'defense': 0,
            'education': 0,
            'health': 0,
            'infrastructure': 0,
            'social': 0,
            'total': 0
        }
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - بانک مرکزی اسرائیل آماده است!')
        
        # شروع کارهای دوره‌ای
        if not self.daily_salary.is_running():
            self.daily_salary.start()
        if not self.economic_update.is_running():
            self.economic_update.start()
        if not self.budget_management.is_running():
            self.budget_management.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="اقتصاد اسرائیل 💰"
            )
        )

    @commands.command(name='ایجاد_حساب')
    async def create_account(self, ctx, member: discord.Member = None):
        """ایجاد حساب بانکی جدید"""
        if member is None:
            member = ctx.author
            
        user_id = str(member.id)
        
        # بررسی وجود حساب
        if self.db.get_user_data(user_id, 'bank_account'):
            embed = create_embed(
                "خطا ❌",
                f"{member.mention} قبلاً حساب بانکی دارد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # ایجاد حساب جدید
        account_data = {
            'balance': 5000,  # موجودی اولیه
            'account_number': f"IL{random.randint(100000, 999999)}",
            'created_at': datetime.now().isoformat(),
            'transactions': [],
            'credit_score': 750,
            'loans': []
        }
        
        self.db.set_user_data(user_id, 'bank_account', account_data)
        
        embed = create_embed(
            "حساب بانکی ایجاد شد ✅",
            f"**صاحب حساب:** {member.mention}\n"
            f"**شماره حساب:** `{account_data['account_number']}`\n"
            f"**موجودی اولیه:** {account_data['balance']:,} شکل\n"
            f"**امتیاز اعتباری:** {account_data['credit_score']}/850",
            EMBED_COLORS['success']
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830284.png")
        await ctx.send(embed=embed)

    @commands.command(name='موجودی')
    async def check_balance(self, ctx, member: discord.Member = None):
        """چک کردن موجودی حساب"""
        if member is None:
            member = ctx.author
            
        user_id = str(member.id)
        account = self.db.get_user_data(user_id, 'bank_account')
        
        if not account:
            embed = create_embed(
                "خطا ❌",
                f"{member.mention} حساب بانکی ندارد!\nبرای ایجاد حساب: `!بانک_ایجاد_حساب`",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # محاسبه درآمد روزانه
        user_roles = [role.name for role in member.roles]
        daily_income = 0
        for role, salary in self.base_salary.items():
            if role in user_roles:
                daily_income = max(daily_income, salary)
        
        embed = create_embed(
            f"💰 حساب بانکی {member.display_name}",
            f"**شماره حساب:** `{account['account_number']}`\n"
            f"**موجودی فعلی:** {account['balance']:,} شکل\n"
            f"**درآمد روزانه:** {daily_income:,} شکل\n"
            f"**امتیاز اعتباری:** {account['credit_score']}/850\n"
            f"**تعداد تراکنش‌ها:** {len(account['transactions'])}",
            EMBED_COLORS['primary']
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        # نمایش وام‌ها
        if account['loans']:
            loans_text = ""
            for loan in account['loans']:
                loans_text += f"• {loan['amount']:,} شکل (سود: {loan['interest']}%)\n"
            embed.add_field(name="وام‌های فعال", value=loans_text, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='انتقال')
    async def transfer_money(self, ctx, recipient: discord.Member, amount: int, *, description: str = "انتقال وجه"):
        """انتقال پول بین حساب‌ها"""
        sender_id = str(ctx.author.id)
        recipient_id = str(recipient.id)
        
        # بررسی حساب‌ها
        sender_account = self.db.get_user_data(sender_id, 'bank_account')
        recipient_account = self.db.get_user_data(recipient_id, 'bank_account')
        
        if not sender_account:
            embed = create_embed(
                "خطا ❌",
                "شما حساب بانکی ندارید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if not recipient_account:
            embed = create_embed(
                "خطا ❌",
                f"{recipient.mention} حساب بانکی ندارد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی مقدار
        if amount <= 0:
            embed = create_embed(
                "خطا ❌",
                "مقدار انتقال باید مثبت باشد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # محاسبه مالیات
        tax_amount = int(amount * self.tax_rates['transaction'])
        total_deduction = amount + tax_amount
        
        # بررسی موجودی
        if sender_account['balance'] < total_deduction:
            embed = create_embed(
                "موجودی ناکافی ❌",
                f"**مبلغ درخواستی:** {amount:,} شکل\n"
                f"**مالیات:** {tax_amount:,} شکل\n"
                f"**مجموع:** {total_deduction:,} شکل\n"
                f"**موجودی شما:** {sender_account['balance']:,} شکل",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # انجام انتقال
        sender_account['balance'] -= total_deduction
        recipient_account['balance'] += amount
        
        # ثبت تراکنش
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        timestamp = datetime.now().isoformat()
        
        sender_transaction = {
            'id': transaction_id,
            'type': 'transfer_out',
            'amount': -amount,
            'tax': -tax_amount,
            'description': description,
            'recipient': recipient.display_name,
            'timestamp': timestamp
        }
        
        recipient_transaction = {
            'id': transaction_id,
            'type': 'transfer_in',
            'amount': amount,
            'description': description,
            'sender': ctx.author.display_name,
            'timestamp': timestamp
        }
        
        sender_account['transactions'].append(sender_transaction)
        recipient_account['transactions'].append(recipient_transaction)
        
        # ذخیره تغییرات
        self.db.set_user_data(sender_id, 'bank_account', sender_account)
        self.db.set_user_data(recipient_id, 'bank_account', recipient_account)
        
        # اضافه کردن مالیات به بودجه دولت
        self.add_to_government_budget(tax_amount)
        
        # ارسال تأیید
        embed = create_embed(
            "انتقال موفق ✅",
            f"**فرستنده:** {ctx.author.mention}\n"
            f"**گیرنده:** {recipient.mention}\n"
            f"**مبلغ:** {amount:,} شکل\n"
            f"**مالیات:** {tax_amount:,} شکل\n"
            f"**شماره تراکنش:** `{transaction_id}`\n"
            f"**توضیحات:** {description}",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await ctx.send(embed=embed)

    @commands.command(name='درخواست_وام')
    async def request_loan(self, ctx, amount: int, months: int = 12):
        """درخواست وام از بانک"""
        user_id = str(ctx.author.id)
        account = self.db.get_user_data(user_id, 'bank_account')
        
        if not account:
            embed = create_embed(
                "خطا ❌",
                "شما حساب بانکی ندارید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی شرایط وام
        if amount < 10000:
            embed = create_embed(
                "خطا ❌",
                "حداقل مبلغ وام 10,000 شکل است!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if amount > 500000:
            embed = create_embed(
                "خطا ❌",
                "حداکثر مبلغ وام 500,000 شکل است!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی امتیاز اعتباری
        credit_score = account['credit_score']
        if credit_score < 650:
            embed = create_embed(
                "درخواست وام رد شد ❌",
                f"امتیاز اعتباری شما ({credit_score}) برای دریافت وام کافی نیست!\n"
                "حداقل امتیاز مورد نیاز: 650",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # محاسبه نرخ سود بر اساس امتیاز اعتباری
        if credit_score >= 800:
            interest_rate = 3.5
        elif credit_score >= 750:
            interest_rate = 4.5
        elif credit_score >= 700:
            interest_rate = 6.0
        else:
            interest_rate = 8.0
        
        # محاسبه اقساط
        monthly_interest = interest_rate / 100 / 12
        monthly_payment = amount * (monthly_interest * (1 + monthly_interest)**months) / ((1 + monthly_interest)**months - 1)
        total_payment = monthly_payment * months
        total_interest = total_payment - amount
        
        # ایجاد وام
        loan_id = f"LOAN{random.randint(100000, 999999)}"
        loan_data = {
            'id': loan_id,
            'amount': amount,
            'interest': interest_rate,
            'months': months,
            'monthly_payment': int(monthly_payment),
            'remaining': amount,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        account['loans'].append(loan_data)
        account['balance'] += amount
        
        # ثبت تراکنش
        transaction = {
            'id': f"TXN{random.randint(100000, 999999)}",
            'type': 'loan',
            'amount': amount,
            'description': f"دریافت وام {loan_id}",
            'timestamp': datetime.now().isoformat()
        }
        account['transactions'].append(transaction)
        
        # ذخیره تغییرات
        self.db.set_user_data(user_id, 'bank_account', account)
        
        embed = create_embed(
            "وام تصویب شد ✅",
            f"**مبلغ وام:** {amount:,} شکل\n"
            f"**نرخ سود:** {interest_rate}% سالانه\n"
            f"**مدت:** {months} ماه\n"
            f"**قسط ماهانه:** {int(monthly_payment):,} شکل\n"
            f"**مجموع سود:** {int(total_interest):,} شکل\n"
            f"**شماره وام:** `{loan_id}`",
            EMBED_COLORS['success']
        )
        embed.set_footer(text="وام به حساب شما واریز شد")
        await ctx.send(embed=embed)

    @commands.command(name='آمار_اقتصادی')
    @has_role(['وزیر', 'نخست‌وزیر', 'مدیر'])
    async def economic_statistics(self, ctx):
        """نمایش آمار اقتصادی کشور"""
        # محاسبه آمار جدید
        total_accounts = len([user for user in self.db.users.values() if 'bank_account' in user])
        total_money = sum([user['bank_account']['balance'] for user in self.db.users.values() if 'bank_account' in user])
        total_loans = sum([sum([loan['remaining'] for loan in user['bank_account']['loans']]) 
                          for user in self.db.users.values() if 'bank_account' in user])
        
        embed = create_embed(
            "📊 آمار اقتصادی اسرائیل",
            f"**تولید ناخالص داخلی:** ${self.economic_stats['gdp']:,}\n"
            f"**نرخ تورم:** {self.economic_stats['inflation']}%\n"
            f"**نرخ بیکاری:** {self.economic_stats['unemployment']}%\n"
            f"**نرخ بهره:** {self.economic_stats['interest_rate']}%\n"
            f"**بدهی ملی:** ${self.economic_stats['national_debt']:,}\n"
            f"**کسری بودجه:** ${self.economic_stats['budget_deficit']:,}",
            EMBED_COLORS['primary']
        )
        
        embed.add_field(
            name="آمار بانکی",
            value=f"**تعداد حساب‌ها:** {total_accounts:,}\n"
                  f"**مجموع پول:** {total_money:,} شکل\n"
                  f"**مجموع وام‌ها:** {total_loans:,} شکل",
            inline=False
        )
        
        embed.add_field(
            name="بودجه دولتی",
            value=f"**دفاع:** {self.government_budget['defense']:,} شکل\n"
                  f"**آموزش:** {self.government_budget['education']:,} شکل\n"
                  f"**بهداشت:** {self.government_budget['health']:,} شکل\n"
                  f"**زیرساخت:** {self.government_budget['infrastructure']:,} شکل\n"
                  f"**رفاه:** {self.government_budget['social']:,} شکل\n"
                  f"**مجموع:** {self.government_budget['total']:,} شکل",
            inline=False
        )
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830807.png")
        await ctx.send(embed=embed)

    @commands.command(name='تخصیص_بودجه')
    @has_role(['وزیر', 'نخست‌وزیر'])
    async def allocate_budget(self, ctx, sector: str, amount: int):
        """تخصیص بودجه به بخش‌های مختلف"""
        valid_sectors = ['defense', 'education', 'health', 'infrastructure', 'social']
        
        if sector not in valid_sectors:
            embed = create_embed(
                "خطا ❌",
                f"بخش نامعتبر! بخش‌های موجود:\n{', '.join(valid_sectors)}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if amount <= 0:
            embed = create_embed(
                "خطا ❌",
                "مبلغ باید مثبت باشد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        if amount > self.government_budget['total']:
            embed = create_embed(
                "بودجه ناکافی ❌",
                f"بودجه کل دولت: {self.government_budget['total']:,} شکل\n"
                f"مبلغ درخواستی: {amount:,} شکل",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # تخصیص بودجه
        self.government_budget[sector] += amount
        self.government_budget['total'] -= amount
        
        sector_names = {
            'defense': 'دفاع',
            'education': 'آموزش',
            'health': 'بهداشت',
            'infrastructure': 'زیرساخت',
            'social': 'رفاه اجتماعی'
        }
        
        embed = create_embed(
            "تخصیص بودجه ✅",
            f"**بخش:** {sector_names[sector]}\n"
            f"**مبلغ:** {amount:,} شکل\n"
            f"**بودجه جدید بخش:** {self.government_budget[sector]:,} شکل\n"
            f"**بودجه باقیمانده:** {self.government_budget['total']:,} شکل",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"تخصیص داده شده توسط: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    def add_to_government_budget(self, amount: int):
        """اضافه کردن پول به بودجه دولت"""
        self.government_budget['total'] += amount

    @tasks.loop(hours=24)
    async def daily_salary(self):
        """پرداخت حقوق روزانه"""
        try:
            guild = self.get_guild(GUILD_ID)
            if not guild:
                return
            
            total_paid = 0
            total_tax = 0
            
            for member in guild.members:
                if member.bot:
                    continue
                
                user_id = str(member.id)
                account = self.db.get_user_data(user_id, 'bank_account')
                
                if not account:
                    continue
                
                # محاسبه حقوق
                user_roles = [role.name for role in member.roles]
                daily_salary = 0
                
                for role, salary in self.base_salary.items():
                    if role in user_roles:
                        daily_salary = max(daily_salary, salary)
                
                if daily_salary == 0:
                    continue
                
                # محاسبه مالیات
                tax = int(daily_salary * self.tax_rates['income'])
                net_salary = daily_salary - tax
                
                # پرداخت حقوق
                account['balance'] += net_salary
                total_paid += net_salary
                total_tax += tax
                
                # ثبت تراکنش
                transaction = {
                    'id': f"SAL{random.randint(100000, 999999)}",
                    'type': 'salary',
                    'amount': net_salary,
                    'tax': -tax,
                    'description': 'حقوق روزانه',
                    'timestamp': datetime.now().isoformat()
                }
                account['transactions'].append(transaction)
                
                # ذخیره تغییرات
                self.db.set_user_data(user_id, 'bank_account', account)
            
            # اضافه کردن مالیات به بودجه
            self.add_to_government_budget(total_tax)
            
            # اعلان در کانال اقتصاد
            channel = discord.utils.get(guild.channels, name='اقتصاد')
            if channel:
                embed = create_embed(
                    "💰 پرداخت حقوق روزانه",
                    f"**مجموع پرداختی:** {total_paid:,} شکل\n"
                    f"**مجموع مالیات:** {total_tax:,} شکل\n"
                    f"**بودجه دولت:** {self.government_budget['total']:,} شکل",
                    EMBED_COLORS['success']
                )
                await channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"خطا در پرداخت حقوق روزانه: {e}")

    @tasks.loop(hours=6)
    async def economic_update(self):
        """به‌روزرسانی آمار اقتصادی"""
        try:
            # تغییرات تصادفی در آمار
            self.economic_stats['gdp'] += random.randint(-10000, 50000)
            self.economic_stats['inflation'] += random.uniform(-0.1, 0.2)
            self.economic_stats['unemployment'] += random.uniform(-0.2, 0.1)
            self.economic_stats['interest_rate'] += random.uniform(-0.1, 0.1)
            
            # اطمینان از محدوده منطقی
            self.economic_stats['inflation'] = max(0, min(10, self.economic_stats['inflation']))
            self.economic_stats['unemployment'] = max(0, min(15, self.economic_stats['unemployment']))
            self.economic_stats['interest_rate'] = max(0, min(10, self.economic_stats['interest_rate']))
            
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی اقتصادی: {e}")

    @tasks.loop(hours=12)
    async def budget_management(self):
        """مدیریت خودکار بودجه"""
        try:
            # کاهش خودکار بودجه بخش‌ها (هزینه‌های عملیاتی)
            operational_costs = {
                'defense': 0.02,
                'education': 0.01,
                'health': 0.015,
                'infrastructure': 0.01,
                'social': 0.01
            }
            
            for sector, cost_rate in operational_costs.items():
                cost = int(self.government_budget[sector] * cost_rate)
                self.government_budget[sector] = max(0, self.government_budget[sector] - cost)
            
        except Exception as e:
            logger.error(f"خطا در مدیریت بودجه: {e}")

# ======================= ربات صنایع نظامی =======================

class MilitaryIndustriesBot(commands.Bot):
    """
    ربات صنایع نظامی
    مسئول تولید تجهیزات نظامی، تحقیق و توسعه، صادرات نظامی
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!صنایع_',
            intents=intents,
            help_command=None,
            description="صنایع نظامی اسرائیل - تولید و توسعه تجهیزات"
        )
        
        self.db = DatabaseManager()
        
        # تجهیزات قابل تولید
        self.equipment_catalog = {
            'iron_dome_missile': {
                'name': 'موشک گنبد آهنین',
                'cost': 50000,
                'materials': {'steel': 10, 'electronics': 5, 'explosive': 3},
                'production_time': 2,  # ساعت
                'tech_level': 1
            },
            'david_sling_missile': {
                'name': 'موشک فلاخن داوود',
                'cost': 150000,
                'materials': {'steel': 25, 'electronics': 15, 'explosive': 10},
                'production_time': 6,
                'tech_level': 2
            },
            'arrow_missile': {
                'name': 'موشک خِتس',
                'cost': 500000,
                'materials': {'steel': 50, 'electronics': 30, 'explosive': 20},
                'production_time': 24,
                'tech_level': 3
            },
            'merkava_tank': {
                'name': 'تانک مرکاوا',
                'cost': 2000000,
                'materials': {'steel': 200, 'electronics': 50, 'engine': 1},
                'production_time': 168,  # یک هفته
                'tech_level': 2
            },
            'f35_fighter': {
                'name': 'جنگنده F-35',
                'cost': 80000000,
                'materials': {'steel': 500, 'electronics': 200, 'engine': 2},
                'production_time': 720,  # یک ماه
                'tech_level': 4
            }
        }
        
        # منابع موجود
        self.materials_inventory = {
            'steel': 1000,
            'electronics': 500,
            'explosive': 200,
            'engine': 50
        }
        
        # درخت فناوری
        self.tech_tree = {
            1: {'name': 'فناوری پایه', 'unlocked': True, 'cost': 0},
            2: {'name': 'فناوری پیشرفته', 'unlocked': False, 'cost': 1000000},
            3: {'name': 'فناوری فوق پیشرفته', 'unlocked': False, 'cost': 5000000},
            4: {'name': 'فناوری نسل آینده', 'unlocked': False, 'cost': 20000000}
        }
        
        # سفارشات در حال تولید
        self.production_queue = []
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - صنایع نظامی اسرائیل آماده است!')
        
        if not self.production_cycle.is_running():
            self.production_cycle.start()
        if not self.resource_generation.is_running():
            self.resource_generation.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="خط تولید نظامی 🏭"
            )
        )

    @commands.command(name='کاتالوگ')
    async def equipment_catalog_cmd(self, ctx):
        """نمایش کاتالوگ تجهیزات"""
        embed = create_embed(
            "🏭 کاتالوگ تجهیزات نظامی",
            "لیست تجهیزات قابل تولید:",
            EMBED_COLORS['primary']
        )
        
        for eq_id, equipment in self.equipment_catalog.items():
            # بررسی دسترسی فناوری
            tech_available = self.tech_tree[equipment['tech_level']]['unlocked']
            status = "✅ قابل تولید" if tech_available else "🔒 نیاز به تحقیق"
            
            materials_text = ", ".join([f"{mat}: {qty}" for mat, qty in equipment['materials'].items()])
            
            embed.add_field(
                name=f"{equipment['name']} {status}",
                value=f"**هزینه:** {equipment['cost']:,} شکل\n"
                      f"**مواد:** {materials_text}\n"
                      f"**زمان تولید:** {equipment['production_time']} ساعت\n"
                      f"**سطح فناوری:** {equipment['tech_level']}",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='موجودی_مواد')
    @has_role(['وزیر', 'مهندس', 'مدیر'])
    async def materials_inventory_cmd(self, ctx):
        """نمایش موجودی مواد اولیه"""
        embed = create_embed(
            "📦 موجودی مواد اولیه",
            "",
            EMBED_COLORS['primary']
        )
        
        for material, quantity in self.materials_inventory.items():
            material_names = {
                'steel': 'فولاد',
                'electronics': 'الکترونیک',
                'explosive': 'مواد منفجره',
                'engine': 'موتور'
            }
            
            embed.add_field(
                name=material_names.get(material, material),
                value=f"{quantity:,} واحد",
                inline=True
            )
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2830/2830411.png")
        await ctx.send(embed=embed)

    @commands.command(name='سفارش_تولید')
    @has_role(['وزیر', 'فرمانده', 'مدیر'])
    async def production_order(self, ctx, equipment_id: str, quantity: int = 1):
        """سفارش تولید تجهیزات"""
        if equipment_id not in self.equipment_catalog:
            embed = create_embed(
                "خطا ❌",
                "تجهیزات مورد نظر یافت نشد!\nبرای مشاهده لیست: `!صنایع_کاتالوگ`",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        equipment = self.equipment_catalog[equipment_id]
        
        # بررسی دسترسی فناوری
        if not self.tech_tree[equipment['tech_level']]['unlocked']:
            embed = create_embed(
                "فناوری نامناسب ❌",
                f"برای تولید {equipment['name']} نیاز به سطح فناوری {equipment['tech_level']} دارید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی مواد اولیه
        for material, needed in equipment['materials'].items():
            total_needed = needed * quantity
            if self.materials_inventory.get(material, 0) < total_needed:
                embed = create_embed(
                    "مواد ناکافی ❌",
                    f"برای تولید {quantity} عدد {equipment['name']} نیاز دارید:\n"
                    f"{material}: {total_needed} (موجود: {self.materials_inventory.get(material, 0)})",
                    EMBED_COLORS['error']
                )
                await ctx.send(embed=embed)
                return
        
        # محاسبه هزینه کل
        total_cost = equipment['cost'] * quantity
        
        # کسر مواد از انبار
        for material, needed in equipment['materials'].items():
            self.materials_inventory[material] -= needed * quantity
        
        # اضافه کردن به صف تولید
        production_id = f"PROD{random.randint(100000, 999999)}"
        production_order = {
            'id': production_id,
            'equipment_id': equipment_id,
            'equipment_name': equipment['name'],
            'quantity': quantity,
            'cost': total_cost,
            'start_time': datetime.now(),
            'completion_time': datetime.now() + timedelta(hours=equipment['production_time']),
            'ordered_by': ctx.author.display_name,
            'status': 'in_progress'
        }
        
        self.production_queue.append(production_order)
        
        embed = create_embed(
            "سفارش تولید ثبت شد ✅",
            f"**تجهیزات:** {equipment['name']}\n"
            f"**تعداد:** {quantity:,} عدد\n"
            f"**هزینه کل:** {total_cost:,} شکل\n"
            f"**زمان تکمیل:** {production_order['completion_time'].strftime('%Y/%m/%d %H:%M')}\n"
            f"**شماره سفارش:** `{production_id}`",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"سفارش داده شده توسط: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name='وضعیت_تولید')
    async def production_status(self, ctx):
        """نمایش وضعیت تولید"""
        if not self.production_queue:
            embed = create_embed(
                "صف تولید خالی",
                "در حال حاضر هیچ سفارشی در حال تولید نیست.",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            "🏭 وضعیت خط تولید",
            f"تعداد سفارشات در صف: {len(self.production_queue)}",
            EMBED_COLORS['primary']
        )
        
        for order in self.production_queue[:5]:  # نمایش 5 سفارش اول
            time_left = order['completion_time'] - datetime.now()
            if time_left.total_seconds() > 0:
                hours_left = int(time_left.total_seconds() / 3600)
                status = f"⏳ {hours_left} ساعت باقیمانده"
            else:
                status = "✅ آماده تحویل"
            
            embed.add_field(
                name=f"{order['equipment_name']} (x{order['quantity']})",
                value=f"**شماره:** {order['id']}\n"
                      f"**وضعیت:** {status}\n"
                      f"**سفارش‌دهنده:** {order['ordered_by']}",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='تحقیق')
    @has_role(['وزیر', 'دانشمند', 'مدیر'])
    async def research_technology(self, ctx, tech_level: int):
        """تحقیق فناوری جدید"""
        if tech_level not in self.tech_tree:
            embed = create_embed(
                "خطا ❌",
                f"سطح فناوری نامعتبر! سطوح موجود: {list(self.tech_tree.keys())}",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        tech = self.tech_tree[tech_level]
        
        if tech['unlocked']:
            embed = create_embed(
                "فناوری موجود ❌",
                f"فناوری سطح {tech_level} قبلاً باز شده است!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی پیش‌نیاز
        if tech_level > 1 and not self.tech_tree[tech_level - 1]['unlocked']:
            embed = create_embed(
                "پیش‌نیاز موجود نیست ❌",
                f"برای تحقیق سطح {tech_level} ابتدا باید سطح {tech_level - 1} را باز کنید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # شبیه‌سازی تحقیق (در اینجا فوری انجام می‌شود)
        tech['unlocked'] = True
        
        embed = create_embed(
            "تحقیق موفق ✅",
            f"**فناوری:** {tech['name']}\n"
            f"**سطح:** {tech_level}\n"
            f"**هزینه:** {tech['cost']:,} شکل\n\n"
            "تجهیزات جدیدی اکنون قابل تولید هستند!",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"تحقیق انجام شده توسط: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name='صادرات')
    @has_role(['وزیر', 'مدیر'])
    async def export_equipment(self, ctx, equipment_id: str, quantity: int, buyer_country: str):
        """صادرات تجهیزات نظامی"""
        # این قسمت برای صادرات به سرورهای دیگر است
        # در اینجا فقط شبیه‌سازی می‌کنیم
        
        if equipment_id not in self.equipment_catalog:
            embed = create_embed(
                "خطا ❌",
                "تجهیزات مورد نظر یافت نشد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        equipment = self.equipment_catalog[equipment_id]
        total_value = equipment['cost'] * quantity
        
        embed = create_embed(
            "صادرات تجهیزات ✅",
            f"**تجهیزات:** {equipment['name']}\n"
            f"**تعداد:** {quantity:,} عدد\n"
            f"**خریدار:** {buyer_country}\n"
            f"**ارزش کل:** ${total_value:,}\n"
            f"**درآمد ارزی:** ${int(total_value * 0.8):,}",
            EMBED_COLORS['success']
        )
        embed.set_footer(text=f"صادرات انجام شده توسط: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @tasks.loop(hours=1)
    async def production_cycle(self):
        """چرخه تولید - بررسی تکمیل سفارشات"""
        try:
            completed_orders = []
            current_time = datetime.now()
            
            for order in self.production_queue:
                if current_time >= order['completion_time']:
                    completed_orders.append(order)
            
            # حذف سفارشات تکمیل شده از صف
            for order in completed_orders:
                self.production_queue.remove(order)
            
            # اطلاع‌رسانی تکمیل سفارشات
            if completed_orders:
                guild = self.get_guild(GUILD_ID)
                if guild:
                    channel = discord.utils.get(guild.channels, name='صنایع-نظامی')
                    if channel:
                        for order in completed_orders:
                            embed = create_embed(
                                "تولید تکمیل شد ✅",
                                f"**تجهیزات:** {order['equipment_name']}\n"
                                f"**تعداد:** {order['quantity']:,} عدد\n"
                                f"**شماره سفارش:** `{order['id']}`\n"
                                f"**سفارش‌دهنده:** {order['ordered_by']}",
                                EMBED_COLORS['success']
                            )
                            await channel.send(embed=embed)
                            
        except Exception as e:
            logger.error(f"خطا در چرخه تولید: {e}")

    @tasks.loop(hours=8)
    async def resource_generation(self):
        """تولید خودکار مواد اولیه"""
        try:
            # تولید مواد اولیه با نرخ ثابت
            generation_rates = {
                'steel': random.randint(50, 100),
                'electronics': random.randint(20, 40),
                'explosive': random.randint(10, 20),
                'engine': random.randint(2, 5)
            }
            
            for material, amount in generation_rates.items():
                self.materials_inventory[material] += amount
            
            # اطلاع‌رسانی
            guild = self.get_guild(GUILD_ID)
            if guild:
                channel = discord.utils.get(guild.channels, name='صنایع-نظامی')
                if channel:
                    embed = create_embed(
                        "📦 تولید مواد اولیه",
                        "مواد اولیه جدید تولید شد:",
                        EMBED_COLORS['primary']
                    )
                    
                    for material, amount in generation_rates.items():
                        material_names = {
                            'steel': 'فولاد',
                            'electronics': 'الکترونیک',
                            'explosive': 'مواد منفجره',
                            'engine': 'موتور'
                        }
                        embed.add_field(
                            name=material_names.get(material, material),
                            value=f"+{amount} واحد",
                            inline=True
                        )
                    
                    await channel.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"خطا در تولید مواد اولیه: {e}")

# ======================= ربات بورس تل‌آویو =======================

class TelAvivStockExchangeBot(commands.Bot):
    """
    ربات بورس تل‌آویو
    مسئول مدیریت بازار سهام، شرکت‌ها و معاملات
    """
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!بورس_',
            intents=intents,
            help_command=None,
            description="بورس تل‌آویو - بازار سرمایه اسرائیل"
        )
        
        self.db = DatabaseManager()
        
        # شرکت‌های بورسی
        self.companies = {
            'TEVA': {
                'name': 'Teva Pharmaceutical',
                'sector': 'دارو',
                'price': 1000,
                'shares': 1000000,
                'available_shares': 500000,
                'dividend_yield': 3.5,
                'last_change': 0
            },
            'CHKP': {
                'name': 'Check Point Software',
                'sector': 'فناوری',
                'price': 1500,
                'shares': 800000,
                'available_shares': 300000,
                'dividend_yield': 2.8,
                'last_change': 0
            },
            'ELBIT': {
                'name': 'Elbit Systems',
                'sector': 'دفاع',
                'price': 2000,
                'shares': 500000,
                'available_shares': 200000,
                'dividend_yield': 4.2,
                'last_change': 0
            }
        }
        
        # شاخص کل بورس
        self.market_index = 1000
        
    async def on_ready(self):
        """وقتی ربات آماده شد"""
        print(f'{self.user} - بورس تل‌آویو آماده است!')
        
        if not self.market_update.is_running():
            self.market_update.start()
        if not self.dividend_payment.is_running():
            self.dividend_payment.start()
            
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="بازار سهام 📈"
            )
        )

    @commands.command(name='نمادها')
    async def list_companies(self, ctx):
        """لیست شرکت‌های بورسی"""
        embed = create_embed(
            "📊 شرکت‌های بورس تل‌آویو",
            f"شاخص کل: {self.market_index:.2f}",
            EMBED_COLORS['primary']
        )
        
        for symbol, company in self.companies.items():
            change_emoji = "📈" if company['last_change'] > 0 else "📉" if company['last_change'] < 0 else "➡️"
            change_text = f"{company['last_change']:+.2f}%" if company['last_change'] != 0 else "0.00%"
            
            embed.add_field(
                name=f"{symbol} {change_emoji}",
                value=f"**{company['name']}**\n"
                      f"بخش: {company['sector']}\n"
                      f"قیمت: {company['price']:,} شکل\n"
                      f"تغییر: {change_text}\n"
                      f"سود سهام: {company['dividend_yield']}%",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='خرید')
    async def buy_stock(self, ctx, symbol: str, quantity: int):
        """خرید سهام"""
        symbol = symbol.upper()
        user_id = str(ctx.author.id)
        
        if symbol not in self.companies:
            embed = create_embed(
                "خطا ❌",
                f"نماد {symbol} یافت نشد!\nبرای مشاهده لیست: `!بورس_نمادها`",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        company = self.companies[symbol]
        
        # بررسی موجودی سهام
        if quantity > company['available_shares']:
            embed = create_embed(
                "سهام ناکافی ❌",
                f"تنها {company['available_shares']:,} سهم از {symbol} موجود است!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # محاسبه هزینه کل
        total_cost = company['price'] * quantity
        commission = int(total_cost * 0.01)  # کارمزد 1%
        final_cost = total_cost + commission
        
        # بررسی موجودی حساب
        # (اینجا باید با ربات بانک ارتباط برقرار کنیم)
        
        # انجام معامله
        company['available_shares'] -= quantity
        
        # ثبت در پرتفوی کاربر
        portfolio = self.db.get_user_data(user_id, 'stock_portfolio') or {}
        if symbol in portfolio:
            # محاسبه میانگین قیمت
            old_quantity = portfolio[symbol]['quantity']
            old_avg_price = portfolio[symbol]['avg_price']
            new_avg_price = ((old_quantity * old_avg_price) + total_cost) / (old_quantity + quantity)
            
            portfolio[symbol]['quantity'] += quantity
            portfolio[symbol]['avg_price'] = new_avg_price
        else:
            portfolio[symbol] = {
                'quantity': quantity,
                'avg_price': company['price'],
                'company_name': company['name']
            }
        
        self.db.set_user_data(user_id, 'stock_portfolio', portfolio)
        
        embed = create_embed(
            "خرید موفق ✅",
            f"**نماد:** {symbol}\n"
            f"**تعداد:** {quantity:,} سهم\n"
            f"**قیمت واحد:** {company['price']:,} شکل\n"
            f"**هزینه کل:** {total_cost:,} شکل\n"
            f"**کارمزد:** {commission:,} شکل\n"
            f"**مجموع پرداختی:** {final_cost:,} شکل",
            EMBED_COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name='فروش')
    async def sell_stock(self, ctx, symbol: str, quantity: int):
        """فروش سهام"""
        symbol = symbol.upper()
        user_id = str(ctx.author.id)
        
        if symbol not in self.companies:
            embed = create_embed(
                "خطا ❌",
                f"نماد {symbol} یافت نشد!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # بررسی پرتفوی کاربر
        portfolio = self.db.get_user_data(user_id, 'stock_portfolio') or {}
        
        if symbol not in portfolio or portfolio[symbol]['quantity'] < quantity:
            owned = portfolio.get(symbol, {}).get('quantity', 0)
            embed = create_embed(
                "سهام ناکافی ❌",
                f"شما تنها {owned:,} سهم از {symbol} دارید!",
                EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        company = self.companies[symbol]
        
        # محاسبه فروش
        total_income = company['price'] * quantity
        commission = int(total_income * 0.01)  # کارمزد 1%
        final_income = total_income - commission
        
        # محاسبه سود/زیان
        avg_price = portfolio[symbol]['avg_price']
        profit_loss = (company['price'] - avg_price) * quantity
        profit_loss_percent = ((company['price'] - avg_price) / avg_price) * 100
        
        # به‌روزرسانی پرتفوی
        portfolio[symbol]['quantity'] -= quantity
        if portfolio[symbol]['quantity'] == 0:
            del portfolio[symbol]
        
        self.db.set_user_data(user_id, 'stock_portfolio', portfolio)
        
        # بازگرداندن سهام به بازار
        company['available_shares'] += quantity
        
        profit_emoji = "📈" if profit_loss > 0 else "📉" if profit_loss < 0 else "➡️"
        
        embed = create_embed(
            "فروش موفق ✅",
            f"**نماد:** {symbol}\n"
            f"**تعداد:** {quantity:,} سهم\n"
            f"**قیمت واحد:** {company['price']:,} شکل\n"
            f"**درآمد کل:** {total_income:,} شکل\n"
            f"**کارمزد:** {commission:,} شکل\n"
            f"**مجموع دریافتی:** {final_income:,} شکل\n\n"
            f"{profit_emoji} **سود/زیان:** {profit_loss:+,} شکل ({profit_loss_percent:+.2f}%)",
            EMBED_COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name='پرتفوی')
    async def show_portfolio(self, ctx, member: discord.Member = None):
        """نمایش پرتفوی سهام"""
        if member is None:
            member = ctx.author
            
        user_id = str(member.id)
        portfolio = self.db.get_user_data(user_id, 'stock_portfolio') or {}
        
        if not portfolio:
            embed = create_embed(
                "پرتفوی خالی",
                f"{member.mention} هیچ سهمی ندارد!",
                EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
        
        embed = create_embed(
            f"📊 پرتفوی {member.display_name}",
            "",
            EMBED_COLORS['primary']
        )
        
        total_value = 0
        total_investment = 0
        
        for symbol, holding in portfolio.items():
            current_price = self.companies[symbol]['price']
            current_value = current_price * holding['quantity']
            investment = holding['avg_price'] * holding['quantity']
            profit_loss = current_value - investment
            profit_loss_percent = (profit_loss / investment) * 100
            
            total_value += current_value
            total_investment += investment
            
            profit_emoji = "📈" if profit_loss > 0 else "📉" if profit_loss < 0 else "➡️"
            
            embed.add_field(
                name=f"{symbol} {profit_emoji}",
                value=f"**تعداد:** {holding['quantity']:,} سهم\n"
                      f"**قیمت میانگین:** {holding['avg_price']:,} شکل\n"
                      f"**قیمت فعلی:** {current_price:,} شکل\n"
                      f"**ارزش:** {current_value:,} شکل\n"
                      f"**سود/زیان:** {profit_loss:+,} شکل ({profit_loss_percent:+.2f}%)",
                inline=True
            )
        
        total_profit_loss = total_value - total_investment
        total_profit_loss_percent = (total_profit_loss / total_investment) * 100
        
        embed.add_field(
            name="📊 خلاصه پرتفوی",
            value=f"**ارزش کل:** {total_value:,} شکل\n"
                  f"**سرمایه اولیه:** {total_investment:,} شکل\n"
                  f"**سود/زیان کل:** {total_profit_loss:+,} شکل ({total_profit_loss_percent:+.2f}%)",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @tasks.loop(minutes=30)
    async def market_update(self):
        """به‌روزرسانی قیمت‌های بازار"""
        try:
            total_change = 0
            
            for symbol, company in self.companies.items():
                # تغییرات تصادفی قیمت
                change_percent = random.uniform(-5, 5)  # تغییر تا 5 درصد
                new_price = int(company['price'] * (1 + change_percent / 100))
                new_price = max(100, new_price)  # حداقل قیمت 100 شکل
                
                company['last_change'] = change_percent
                company['price'] = new_price
                total_change += change_percent
            
            # به‌روزرسانی شاخص کل
            index_change = total_change / len(self.companies)
            self.market_index *= (1 + index_change / 100)
            
            # اطلاع‌رسانی تغییرات مهم
            guild = self.get_guild(GUILD_ID)
            if guild:
                channel = discord.utils.get(guild.channels, name='بورس-اوراق-بهادار')
                if channel and abs(index_change) > 2:  # تغییر بیش از 2 درصد
                    trend_emoji = "📈" if index_change > 0 else "📉"
                    embed = create_embed(
                        f"{trend_emoji} تغییرات بازار",
                        f"شاخص کل: {self.market_index:.2f} ({index_change:+.2f}%)",
                        EMBED_COLORS['primary']
                    )
                    await channel.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی بازار: {e}")

    @tasks.loop(hours=168)  # هفتگی
    async def dividend_payment(self):
        """پرداخت سود سهام"""
        try:
            guild = self.get_guild(GUILD_ID)
            if not guild:
                return
            
            total_dividends = 0
            
            # پرداخت سود برای همه سهامداران
            for user_id, user_data in self.db.users.items():
                portfolio = user_data.get('stock_portfolio', {})
                if not portfolio:
                    continue
                
                user_dividends = 0
                for symbol, holding in portfolio.items():
                    company = self.companies[symbol]
                    dividend_per_share = (company['price'] * company['dividend_yield'] / 100) / 52  # هفتگی
                    dividend = int(dividend_per_share * holding['quantity'])
                    user_dividends += dividend
                
                if user_dividends > 0:
                    # اضافه کردن به حساب کاربر (باید با ربات بانک ارتباط برقرار کنیم)
                    total_dividends += user_dividends
            
            # اطلاع‌رسانی
            channel = discord.utils.get(guild.channels, name='بورس-اوراق-بهادار')
            if channel:
                embed = create_embed(
                    "💰 پرداخت سود سهام",
                    f"مجموع سود پرداخت شده: {total_dividends:,} شکل",
                    EMBED_COLORS['success']
                )
                await channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"خطا در پرداخت سود سهام: {e}")

# ======================= اجرای ربات‌های اقتصادی =======================

async def run_central_bank():
    """اجرای ربات بانک مرکزی"""
    bot = CentralBankBot()
    await bot.start(DISCORD_BOT_TOKEN_CENTRAL_BANK)

async def run_military_industries():
    """اجرای ربات صنایع نظامی"""
    bot = MilitaryIndustriesBot()
    await bot.start(DISCORD_BOT_TOKEN_MILITARY_INDUSTRIES)

async def run_stock_exchange():
    """اجرای ربات بورس"""
    bot = TelAvivStockExchangeBot()
    await bot.start(DISCORD_BOT_TOKEN_STOCK_EXCHANGE)

if __name__ == "__main__":
    """
    راهنمای اجرا:
    
    1. نصب وابستگی‌ها:
       pip install -r requirements.txt
    
    2. تنظیم متغیرهای محیطی در فایل .env:
       DISCORD_BOT_TOKEN_CENTRAL_BANK=توکن_ربات_بانک_مرکزی
       DISCORD_BOT_TOKEN_MILITARY_INDUSTRIES=توکن_ربات_صنایع_نظامی
       DISCORD_BOT_TOKEN_STOCK_EXCHANGE=توکن_ربات_بورس
       GEMINI_API_KEY=کلید_API_جمنای
    
    3. اجرای ربات‌ها:
       python economic_bots.py
    
    دستورات اصلی:
    
    بانک مرکزی:
    - !بانک_ایجاد_حساب : ایجاد حساب بانکی
    - !بانک_موجودی : چک موجودی
    - !بانک_انتقال @کاربر مبلغ : انتقال پول
    - !بانک_درخواست_وام مبلغ : درخواست وام
    - !بانک_آمار_اقتصادی : آمار کلی اقتصاد
    
    صنایع نظامی:
    - !صنایع_کاتالوگ : لیست تجهیزات
    - !صنایع_سفارش_تولید نام_تجهیزات تعداد : سفارش تولید
    - !صنایع_وضعیت_تولید : وضعیت خط تولید
    - !صنایع_تحقیق سطح_فناوری : تحقیق فناوری جدید
    
    بورس اوراق بهادار:
    - !بورس_نمادها : لیست شرکت‌ها
    - !بورس_خرید نماد تعداد : خرید سهام
    - !بورس_فروش نماد تعداد : فروش سهام
    - !بورس_پرتفوی : نمایش پرتفوی
    """
    
    import asyncio
    
    async def main():
        # اجرای همزمان تمام ربات‌های اقتصادی
        await asyncio.gather(
            run_central_bank(),
            run_military_industries(),
            run_stock_exchange()
        )
    
    asyncio.run(main())