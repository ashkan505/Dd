"""
ماژول اطلاعاتی - یگان ۸۲۰۰
Intelligence Module - Unit 8200 Cyber Ops
"""

import discord
from discord.ext import commands
import asyncio
import logging
import json
import datetime
import random
from typing import Dict, List, Optional, Any

from config import config
from models import db_manager, Military
from gemini_integration import gemini_ai

logger = logging.getLogger(__name__)

WAR_ROOM_CHANNEL_NAME = "اتاق_جنگ"

class IntelligenceCog(commands.Cog):
    """ماژول اطلاعاتی برای عملیات سایبری یگان ۸۲۰۰"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager = db_manager
        self.military = Military(self.db_manager)
        self.gemini_ai = gemini_ai
        logger.info("Intelligence Cog initialized")

    def _get_war_room(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        return discord.utils.get(guild.channels, name=WAR_ROOM_CHANNEL_NAME)

    # ------------------------
    # Scans and Risk Assessment
    # ------------------------
    @commands.command(name="scan_user")
    @commands.has_permissions(manage_guild=True)
    async def scan_user(self, ctx: commands.Context, member: discord.Member):
        """اسکن سریع ریسک کاربر (پروفایل تازه، بدون عکس، سرورهای مشترک کم)"""
        risk = 0
        reasons = []
        account_age_days = (datetime.datetime.now(datetime.timezone.utc) - member.created_at).days
        if account_age_days < 14:
            risk += 30
            reasons.append("حساب تازه ایجاد شده")
        if member.avatar is None:
            risk += 20
            reasons.append("فاقد آواتار")
        if len(member.mutual_guilds) < 2:
            risk += 10
            reasons.append("سرورهای مشترک کم")
        risk = min(100, risk)
        embed = discord.Embed(title="🕵️ نتیجه اسکن کاربر", color=config.COLORS["intelligence"], timestamp=datetime.datetime.now())
        embed.add_field(name="کاربر", value=f"{member.mention}", inline=True)
        embed.add_field(name="ریسک", value=f"{risk}/100", inline=True)
        if reasons:
            embed.add_field(name="دلایل", value="\n".join([f"• {r}" for r in reasons]), inline=False)
        await ctx.send(embed=embed)
        war_room = self._get_war_room(ctx.guild)
        if war_room:
            await war_room.send(embed=embed)

    # ------------------------
    # Cyber Ops Simulations (Safe)
    # ------------------------
    @commands.group(name="cyber", invoke_without_command=True)
    async def cyber_group(self, ctx: commands.Context):
        """عملیات سایبری شبیه‌سازی‌شده (آموزشی)"""
        embed = discord.Embed(title="💻 عملیات سایبری - یگان ۸۲۰۰", description="دستورات: recon, ddos_sim, espionage_sim, defend", color=config.COLORS["intelligence"], timestamp=datetime.datetime.now())
        await ctx.send(embed=embed)

    @cyber_group.command(name="recon")
    async def cyber_recon(self, ctx: commands.Context, target: str):
        prompt = f"شبیه‌سازی شناسایی سایبری هدف: {target}. گزارشی آموزشی و ایمن تولید کن."
        report = await self.gemini_ai.generate_response(prompt)
        embed = discord.Embed(title="🔎 شناسایی سایبری (Recon)", description=report[:1800], color=config.COLORS["intelligence"], timestamp=datetime.datetime.now())
        await ctx.send(embed=embed)
        war_room = self._get_war_room(ctx.guild)
        if war_room:
            await war_room.send(embed=embed)

    @cyber_group.command(name="ddos_sim")
    @commands.has_permissions(manage_guild=True)
    async def cyber_ddos(self, ctx: commands.Context, target: str, intensity: int = 1):
        if intensity < 1 or intensity > 5:
            await ctx.send(embed=discord.Embed(title="⚠️ شدت نامعتبر", description="شدت باید بین 1 تا 5 باشد.", color=config.COLORS["warning"]))
            return
        desc = (
            f"شبیه‌سازی ترافیک بالا علیه هدف '{target}' با شدت {intensity}.\n"
            "این یک شبیه‌سازی آموزشی است و هیچ اقدام واقعی انجام نمی‌شود."
        )
        embed = discord.Embed(title="🌐 شبیه‌سازی DDoS", description=desc, color=config.COLORS["warning"], timestamp=datetime.datetime.now())
        await ctx.send(embed=embed)
        war_room = self._get_war_room(ctx.guild)
        if war_room:
            await war_room.send(embed=embed)

    @cyber_group.command(name="espionage_sim")
    @commands.has_permissions(manage_guild=True)
    async def cyber_espionage(self, ctx: commands.Context, target: str):
        prompt = f"سناریوی آموزشی جاسوسی سایبری علیه '{target}' را به‌صورت امن و اخلاقی شبیه‌سازی کن."
        plan = await self.gemini_ai.generate_response(prompt)
        embed = discord.Embed(title="🕶️ شبیه‌سازی جاسوسی", description=plan[:1800], color=config.COLORS["intelligence"], timestamp=datetime.datetime.now())
        await ctx.send(embed=embed)
        war_room = self._get_war_room(ctx.guild)
        if war_room:
            await war_room.send(embed=embed)

    @cyber_group.command(name="defend")
    async def cyber_defend(self, ctx: commands.Context):
        steps = ["فعال‌سازی فایروال مجازی", "سخت‌سازی تنظیمات", "آموزش اعضا", "نظارت پیوسته"]
        embed = discord.Embed(title="🛡️ دفاع سایبری", description="\n".join([f"• {s}" for s in steps]), color=config.COLORS["success"], timestamp=datetime.datetime.now())
        await ctx.send(embed=embed)
        war_room = self._get_war_room(ctx.guild)
        if war_room:
            await war_room.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(IntelligenceCog(bot))