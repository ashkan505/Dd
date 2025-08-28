"""
ربات اقتصاد ملی - مدیریت بودجه، حساب‌های شهروندان و سیستم‌های اقتصادی
National Economy Bot - Managing Budget, Citizen Accounts and Economic Systems
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import logging
import datetime
from typing import Dict, List, Optional, Any
import os
import sys
import random

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BOT_TOKENS, SERVER_CONFIG, ECONOMY_CONFIG
from utils.embed_helper import EmbedHelper

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/economy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ایجاد دایرکتوری لاگ‌ها
os.makedirs('logs', exist_ok=True)

class EconomyBot(commands.Bot):
    """ربات اقتصاد ملی - مدیریت سیستم اقتصادی اسرائیل"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # راه‌اندازی کمک‌کننده‌ها
        self.embed_helper = EmbedHelper()
        
        # وضعیت اقتصادی
        self.economy_status = {
            "national_budget": 1000000,      # بودجه ملی (شِکِل)
            "tax_revenue": 0,                # درآمد مالیاتی
            "citizen_count": 0,              # تعداد شهروندان
            "daily_income_distributed": 0,   # درآمد روزانه توزیع شده
            "last_daily_distribution": None, # آخرین توزیع درآمد
            "inflation_rate": 0.02,          # نرخ تورم (2%)
            "economic_growth": 0.05          # نرخ رشد اقتصادی (5%)
        }
        
        # حساب‌های شهروندان
        self.citizen_accounts = {}
        
        # تراکنش‌ها
        self.transactions = []
        
        # بازار بورس
        self.stock_market = {
            "companies": {},
            "stock_prices": {},
            "market_cap": 0
        }
        
        # داده‌های ذخیره‌شده
        self.data_file = "data/economy_data.json"
        self.load_data()
        
        # راه‌اندازی وظایف خودکار
        self.setup_tasks()
        
        logger.info("💰 ربات اقتصاد ملی راه‌اندازی شد")
    
    async def setup_hook(self):
        """راه‌اندازی اولیه ربات"""
        await self.add_cog(EconomyCommands(self))
        await self.add_cog(CitizenCommands(self))
        await self.add_cog(StockMarketCommands(self))
        await self.add_cog(TaxCommands(self))
        
        logger.info("✅ تمام کامندها با موفقیت بارگذاری شدند")
    
    def setup_tasks(self):
        """راه‌اندازی وظایف خودکار"""
        self.daily_income_distribution.start()
        self.economic_simulation.start()
        self.stock_market_update.start()
        
        logger.info("✅ وظایف خودکار راه‌اندازی شدند")
    
    def load_data(self):
        """بارگذاری داده‌های ذخیره‌شده"""
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.economy_status.update(data.get('economy_status', {}))
                    self.citizen_accounts.update(data.get('citizen_accounts', {}))
                    self.stock_market.update(data.get('stock_market', {}))
                    logger.info("✅ داده‌های اقتصادی بارگذاری شدند")
            else:
                self.save_data()
                logger.info("✅ فایل داده‌های جدید ایجاد شد")
        except Exception as e:
            logger.error(f"❌ خطا در بارگذاری داده‌ها: {e}")
    
    def save_data(self):
        """ذخیره داده‌های اقتصادی"""
        try:
            data = {
                'economy_status': self.economy_status,
                'citizen_accounts': self.citizen_accounts,
                'stock_market': self.stock_market,
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("✅ داده‌های اقتصادی ذخیره شدند")
        except Exception as e:
            logger.error(f"❌ خطا در ذخیره داده‌ها: {e}")
    
    async def on_ready(self):
        """رویداد آماده شدن ربات"""
        logger.info(f"💰 ربات اقتصاد ملی آماده شد: {self.user}")
        
        # تنظیم وضعیت ربات
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="اقتصاد اسرائیل 💰"
            )
        )
    
    async def on_member_join(self, member):
        """رویداد عضویت کاربر جدید"""
        await self.create_citizen_account(member)
    
    async def create_citizen_account(self, member):
        """ایجاد حساب برای شهروند جدید"""
        try:
            user_id = str(member.id)
            
            if user_id not in self.citizen_accounts:
                self.citizen_accounts[user_id] = {
                    "user_id": user_id,
                    "username": member.display_name,
                    "balance": ECONOMY_CONFIG["initial_balance"],
                    "daily_income": ECONOMY_CONFIG["daily_income"],
                    "total_income": 0,
                    "total_expenses": 0,
                    "join_date": datetime.datetime.now().isoformat(),
                    "last_daily_income": None,
                    "properties": [],
                    "investments": [],
                    "tax_paid": 0
                }
                
                self.economy_status["citizen_count"] += 1
                self.save_data()
                
                logger.info(f"✅ حساب اقتصادی برای {member.display_name} ایجاد شد")
                
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد حساب اقتصادی: {e}")
    
    @tasks.loop(hours=24)
    async def daily_income_distribution(self):
        """توزیع درآمد روزانه برای شهروندان"""
        try:
            current_time = datetime.datetime.now()
            
            # بررسی اینکه آیا امروز درآمد توزیع شده یا نه
            if (self.economy_status["last_daily_distribution"] and 
                datetime.datetime.fromisoformat(self.economy_status["last_daily_distribution"]).date() == current_time.date()):
                return
            
            total_distributed = 0
            
            for user_id, account in self.citizen_accounts.items():
                # اعطای درآمد روزانه
                account["balance"] += account["daily_income"]
                account["total_income"] += account["daily_income"]
                account["last_daily_income"] = current_time.isoformat()
                total_distributed += account["daily_income"]
            
            self.economy_status["daily_income_distributed"] = total_distributed
            self.economy_status["last_daily_distribution"] = current_time.isoformat()
            
            # ارسال اعلان
            await self.broadcast_daily_income()
            
            self.save_data()
            logger.info(f"✅ درآمد روزانه {total_distributed} شِکِل توزیع شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در توزیع درآمد روزانه: {e}")
    
    @tasks.loop(hours=6)
    async def economic_simulation(self):
        """شبیه‌سازی اقتصادی"""
        try:
            # محاسبه تورم
            inflation_effect = random.uniform(-0.01, 0.03)  # -1% تا +3%
            self.economy_status["inflation_rate"] = max(0, self.economy_status["inflation_rate"] + inflation_effect)
            
            # محاسبه رشد اقتصادی
            growth_effect = random.uniform(-0.02, 0.04)  # -2% تا +4%
            self.economy_status["economic_growth"] = max(0, self.economy_status["economic_growth"] + growth_effect)
            
            # تأثیر بر بودجه ملی
            growth_multiplier = 1 + self.economy_status["economic_growth"]
            self.economy_status["national_budget"] = int(self.economy_status["national_budget"] * growth_multiplier)
            
            # به‌روزرسانی قیمت‌های بورس
            await self.update_stock_prices()
            
            self.save_data()
            
        except Exception as e:
            logger.error(f"❌ خطا در شبیه‌سازی اقتصادی: {e}")
    
    @tasks.loop(hours=2)
    async def stock_market_update(self):
        """به‌روزرسانی بازار بورس"""
        try:
            await self.update_stock_prices()
            self.save_data()
        except Exception as e:
            logger.error(f"❌ خطا در به‌روزرسانی بازار بورس: {e}")
    
    async def update_stock_prices(self):
        """به‌روزرسانی قیمت‌های سهام"""
        try:
            for company_id, company in self.stock_market["companies"].items():
                # تغییر تصادفی قیمت سهام
                price_change = random.uniform(-0.1, 0.1)  # -10% تا +10%
                current_price = company.get("stock_price", 100)
                new_price = max(1, current_price * (1 + price_change))
                
                company["stock_price"] = round(new_price, 2)
                company["last_update"] = datetime.datetime.now().isoformat()
            
            # محاسبه ارزش کل بازار
            total_market_cap = sum(
                company.get("stock_price", 0) * company.get("shares_outstanding", 1000)
                for company in self.stock_market["companies"].values()
            )
            self.stock_market["market_cap"] = total_market_cap
            
        except Exception as e:
            logger.error(f"❌ خطا در به‌روزرسانی قیمت‌های سهام: {e}")
    
    async def broadcast_daily_income(self):
        """اعلان توزیع درآمد روزانه"""
        try:
            guild = self.get_guild(SERVER_CONFIG["guild_id"])
            if not guild:
                return
            
            news_channel = discord.utils.get(guild.channels, name="اخبار-ملی")
            if not news_channel:
                return
            
            embed = self.embed_helper.create_economy_embed(
                title="💰 توزیع درآمد روزانه",
                description="درآمد روزانه برای تمام شهروندان توزیع شد!",
                fields=[
                    {"name": "💰 مبلغ توزیع شده", "value": f"{self.economy_status['daily_income_distributed']:,} شِکِل", "inline": True},
                    {"name": "👥 تعداد شهروندان", "value": f"{self.economy_status['citizen_count']}", "inline": True},
                    {"name": "📅 تاریخ", "value": datetime.datetime.now().strftime("%Y/%m/%d"), "inline": True}
                ]
            )
            
            await news_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ خطا در اعلان درآمد روزانه: {e}")
    
    async def transfer_money(self, from_user_id: str, to_user_id: str, amount: int):
        """انتقال پول بین کاربران"""
        try:
            if from_user_id not in self.citizen_accounts or to_user_id not in self.citizen_accounts:
                return False, "یکی از کاربران حساب اقتصادی ندارد"
            
            from_account = self.citizen_accounts[from_user_id]
            to_account = self.citizen_accounts[to_user_id]
            
            if from_account["balance"] < amount:
                return False, "موجودی کافی نیست"
            
            if amount <= 0:
                return False, "مبلغ باید مثبت باشد"
            
            # انجام تراکنش
            from_account["balance"] -= amount
            from_account["total_expenses"] += amount
            
            to_account["balance"] += amount
            to_account["total_income"] += amount
            
            # ثبت تراکنش
            transaction = {
                "from_user": from_user_id,
                "to_user": to_user_id,
                "amount": amount,
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "transfer"
            }
            self.transactions.append(transaction)
            
            # محاسبه مالیات
            tax_amount = int(amount * ECONOMY_CONFIG["tax_rate"])
            if tax_amount > 0:
                self.economy_status["tax_revenue"] += tax_amount
                self.economy_status["national_budget"] += tax_amount
                
                # کسر مالیات از حساب گیرنده
                to_account["balance"] -= tax_amount
                to_account["tax_paid"] += tax_amount
            
            self.save_data()
            return True, "تراکنش با موفقیت انجام شد"
            
        except Exception as e:
            logger.error(f"❌ خطا در انتقال پول: {e}")
            return False, f"خطا در انتقال پول: {str(e)}"
    
    async def get_citizen_balance(self, user_id: str) -> Optional[int]:
        """دریافت موجودی کاربر"""
        try:
            if user_id in self.citizen_accounts:
                return self.citizen_accounts[user_id]["balance"]
            return None
        except Exception as e:
            logger.error(f"❌ خطا در دریافت موجودی: {e}")
            return None

# کلاس کامندهای اقتصادی
class EconomyCommands(commands.Cog):
    """کامندهای مربوط به اقتصاد و مدیریت"""
    
    def __init__(self, bot: EconomyBot):
        self.bot = bot
    
    @commands.command(name="economy_status")
    @commands.has_permissions(administrator=True)
    async def economy_status(self, ctx):
        """نمایش وضعیت اقتصادی کشور"""
        try:
            embed = self.bot.embed_helper.create_economy_embed(
                title="💰 وضعیت اقتصادی اسرائیل",
                description="وضعیت لحظه‌ای اقتصاد ملی",
                fields=[
                    {"name": "🏦 بودجه ملی", "value": f"{self.bot.economy_status['national_budget']:,} شِکِل", "inline": True},
                    {"name": "💰 درآمد مالیاتی", "value": f"{self.bot.economy_status['tax_revenue']:,} شِکِل", "inline": True},
                    {"name": "👥 تعداد شهروندان", "value": f"{self.bot.economy_status['citizen_count']}", "inline": True},
                    {"name": "📊 درآمد روزانه توزیع شده", "value": f"{self.bot.economy_status['daily_income_distributed']:,} شِکِل", "inline": True},
                    {"name": "📈 نرخ تورم", "value": f"{self.bot.economy_status['inflation_rate']:.2%}", "inline": True},
                    {"name": "🚀 نرخ رشد اقتصادی", "value": f"{self.bot.economy_status['economic_growth']:.2%}", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش وضعیت اقتصادی",
                description=f"خطا در نمایش وضعیت اقتصادی: {str(e)}",
                error_code="ECON_001"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش وضعیت اقتصادی: {e}")
    
    @commands.command(name="add_budget")
    @commands.has_permissions(administrator=True)
    async def add_budget(self, ctx, amount: int):
        """افزودن بودجه به خزانه ملی"""
        try:
            if amount <= 0:
                embed = self.bot.embed_helper.create_error_embed(
                    title="مبلغ نامعتبر",
                    description="مبلغ باید مثبت باشد.",
                    error_code="ECON_002"
                )
                await ctx.send(embed=embed)
                return
            
            old_budget = self.bot.economy_status["national_budget"]
            self.bot.economy_status["national_budget"] += amount
            
            embed = self.bot.embed_helper.create_success_embed(
                title="✅ بودجه اضافه شد",
                description=f"{amount:,} شِکِل به بودجه ملی اضافه شد.",
                fields=[
                    {"name": "بودجه قبلی", "value": f"{old_budget:,} شِکِل", "inline": True},
                    {"name": "بودجه جدید", "value": f"{self.bot.economy_status['national_budget']:,} شِکِل", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            self.bot.save_data()
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در افزودن بودجه",
                description=f"خطا در افزودن بودجه: {str(e)}",
                error_code="ECON_003"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در افزودن بودجه: {e}")

# کلاس کامندهای شهروندان
class CitizenCommands(commands.Cog):
    """کامندهای مربوط به شهروندان و حساب‌های شخصی"""
    
    def __init__(self, bot: EconomyBot):
        self.bot = bot
    
    @commands.command(name="balance")
    async def check_balance(self, ctx, user: discord.Member = None):
        """بررسی موجودی حساب"""
        try:
            target_user = user or ctx.author
            user_id = str(target_user.id)
            
            if user_id not in self.bot.citizen_accounts:
                embed = self.bot.embed_helper.create_error_embed(
                    title="حساب یافت نشد",
                    description="این کاربر حساب اقتصادی ندارد."
                )
                await ctx.send(embed=embed)
                return
            
            account = self.bot.citizen_accounts[user_id]
            
            embed = self.bot.embed_helper.create_economy_embed(
                title="💰 موجودی حساب",
                description=f"وضعیت حساب {target_user.display_name}",
                fields=[
                    {"name": "💰 موجودی فعلی", "value": f"{account['balance']:,} شِکِل", "inline": True},
                    {"name": "📈 درآمد کل", "value": f"{account['total_income']:,} شِکِل", "inline": True},
                    {"name": "📉 هزینه کل", "value": f"{account['total_expenses']:,} شِکِل", "inline": True},
                    {"name": "💸 مالیات پرداخت شده", "value": f"{account['tax_paid']:,} شِکِل", "inline": True},
                    {"name": "📅 تاریخ عضویت", "value": datetime.datetime.fromisoformat(account['join_date']).strftime("%Y/%m/%d"), "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در بررسی موجودی",
                description=f"خطا در بررسی موجودی: {str(e)}",
                error_code="ECON_004"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در بررسی موجودی: {e}")
    
    @commands.command(name="transfer")
    async def transfer_money(self, ctx, user: discord.Member, amount: int):
        """انتقال پول به کاربر دیگر"""
        try:
            if amount <= 0:
                embed = self.bot.embed_helper.create_error_embed(
                    title="مبلغ نامعتبر",
                    description="مبلغ باید مثبت باشد.",
                    error_code="ECON_005"
                )
                await ctx.send(embed=embed)
                return
            
            from_user_id = str(ctx.author.id)
            to_user_id = str(user.id)
            
            success, message = await self.bot.transfer_money(from_user_id, to_user_id, amount)
            
            if success:
                embed = self.bot.embed_helper.create_success_embed(
                    title="✅ انتقال موفق",
                    description=f"{amount:,} شِکِل به {user.display_name} منتقل شد.",
                    fields=[
                        {"name": "از", "value": ctx.author.display_name, "inline": True},
                        {"name": "به", "value": user.display_name, "inline": True},
                        {"name": "مبلغ", "value": f"{amount:,} شِکِل", "inline": True}
                    ]
                )
            else:
                embed = self.bot.embed_helper.create_error_embed(
                    title="❌ انتقال ناموفق",
                    description=message,
                    error_code="ECON_006"
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در انتقال پول",
                description=f"خطا در انتقال پول: {str(e)}",
                error_code="ECON_007"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در انتقال پول: {e}")

# کلاس کامندهای بازار بورس
class StockMarketCommands(commands.Cog):
    """کامندهای مربوط به بازار بورس"""
    
    def __init__(self, bot: EconomyBot):
        self.bot = bot
    
    @commands.command(name="stock_market")
    async def show_stock_market(self, ctx):
        """نمایش وضعیت بازار بورس"""
        try:
            if not self.bot.stock_market["companies"]:
                embed = self.bot.embed_helper.create_info_embed(
                    title="📈 بازار بورس",
                    description="هنوز شرکتی در بازار بورس ثبت نشده است."
                )
                await ctx.send(embed=embed)
                return
            
            # نمایش شرکت‌های موجود
            companies_text = ""
            for company_id, company in self.bot.stock_market["companies"].items():
                companies_text += f"**{company['name']}**\n"
                companies_text += f"   قیمت: {company.get('stock_price', 0):.2f} شِکِل\n"
                companies_text += f"   سهام موجود: {company.get('shares_outstanding', 0):,}\n"
                companies_text += f"   ارزش: {company.get('stock_price', 0) * company.get('shares_outstanding', 0):,} شِکِل\n\n"
            
            embed = self.bot.embed_helper.create_economy_embed(
                title="📈 بازار بورس تل‌آویو",
                description="وضعیت فعلی بازار بورس",
                fields=[
                    {"name": "🏢 تعداد شرکت‌ها", "value": f"{len(self.bot.stock_market['companies'])}", "inline": True},
                    {"name": "💰 ارزش کل بازار", "value": f"{self.bot.stock_market['market_cap']:,} شِکِل", "inline": True},
                    {"name": "📊 شرکت‌ها", "value": companies_text, "inline": False}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش بازار بورس",
                description=f"خطا در نمایش بازار بورس: {str(e)}",
                error_code="ECON_008"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش بازار بورس: {e}")

# کلاس کامندهای مالیاتی
class TaxCommands(commands.Cog):
    """کامندهای مربوط به مالیات"""
    
    def __init__(self, bot: EconomyBot):
        self.bot = bot
    
    @commands.command(name="tax_info")
    async def tax_info(self, ctx):
        """نمایش اطلاعات مالیاتی"""
        try:
            embed = self.bot.embed_helper.create_economy_embed(
                title="💸 اطلاعات مالیاتی",
                description="اطلاعات مربوط به سیستم مالیاتی",
                fields=[
                    {"name": "📊 نرخ مالیات", "value": f"{ECONOMY_CONFIG['tax_rate']:.1%}", "inline": True},
                    {"name": "💰 درآمد مالیاتی کل", "value": f"{self.bot.economy_status['tax_revenue']:,} شِکِل", "inline": True},
                    {"name": "🏦 بودجه ملی", "value": f"{self.bot.economy_status['national_budget']:,} شِکِل", "inline": True}
                ]
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_embed = self.bot.embed_helper.create_error_embed(
                title="خطا در نمایش اطلاعات مالیاتی",
                description=f"خطا در نمایش اطلاعات مالیاتی: {str(e)}",
                error_code="ECON_009"
            )
            await ctx.send(embed=error_embed)
            logger.error(f"❌ خطا در نمایش اطلاعات مالیاتی: {e}")

# راه‌اندازی ربات
async def main():
    """تابع اصلی راه‌اندازی ربات"""
    bot = EconomyBot()
    
    try:
        await bot.start(BOT_TOKENS["economy"])
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # اجرای ربات
    asyncio.run(main())