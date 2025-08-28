"""
ماژول نظامی - نیروی زمینی و نیروی دریایی
Military Module - Ground Forces and Navy
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

class MilitaryCog(commands.Cog):
    """ماژول نظامی برای مدیریت نیروی زمینی و دریایی"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager = db_manager
        self.military = Military(self.db_manager)
        self.gemini_ai = gemini_ai
        logger.info("Military Cog initialized")

    # ------------------------
    # DEFCON
    # ------------------------
    @commands.command(name="defcon")
    @commands.has_permissions(administrator=True)
    async def set_defcon(self, ctx: commands.Context, level: int):
        """تغییر سطح DEFCON: 1-5"""
        if level < 1 or level > 5:
            embed = discord.Embed(
                title="⚠️ مقدار نامعتبر",
                description="سطح DEFCON باید بین 1 تا 5 باشد.",
                color=config.COLORS["warning"]
            )
            await ctx.send(embed=embed)
            return
        self.military.change_defcon_level(level)
        embed = discord.Embed(
            title="🛡️ تغییر سطح DEFCON",
            description=f"سطح DEFCON به {level} تغییر یافت.",
            color=config.COLORS["war"],
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)

    # ------------------------
    # Inventory management
    # ------------------------
    @commands.group(name="inventory", invoke_without_command=True)
    async def inventory_group(self, ctx: commands.Context):
        """مدیریت موجودی تجهیزات نظامی"""
        inv = self.military.equipment or {}
        if not inv:
            desc = "هیچ تجهیزاتی ثبت نشده است."
        else:
            lines = [f"• {k}: {v}" for k, v in inv.items()]
            desc = "\n".join(lines)
        embed = discord.Embed(
            title="📦 موجودی تجهیزات نظامی",
            description=desc,
            color=config.COLORS["military"],
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)

    @inventory_group.command(name="add")
    @commands.has_permissions(administrator=True)
    async def inventory_add(self, ctx: commands.Context, item: str, amount: int):
        if amount <= 0:
            await ctx.send(embed=discord.Embed(title="⚠️ مقدار نامعتبر", description="مقدار باید بزرگتر از صفر باشد.", color=config.COLORS["warning"]))
            return
        self.military.add_equipment(item, amount)
        await ctx.send(embed=discord.Embed(title="✅ ثبت شد", description=f"{amount} عدد '{item}' به موجودی افزوده شد.", color=config.COLORS["success"]))

    @inventory_group.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def inventory_remove(self, ctx: commands.Context, item: str, amount: int):
        if amount <= 0:
            await ctx.send(embed=discord.Embed(title="⚠️ مقدار نامعتبر", description="مقدار باید بزرگتر از صفر باشد.", color=config.COLORS["warning"]))
            return
        self.military.remove_equipment(item, amount)
        await ctx.send(embed=discord.Embed(title="✅ به‌روزرسانی", description=f"{amount} عدد '{item}' از موجودی کم شد.", color=config.COLORS["success"]))

    # ------------------------
    # Forces management
    # ------------------------
    @commands.group(name="forces", invoke_without_command=True)
    async def forces_group(self, ctx: commands.Context):
        """نمایش وضعیت نیروها"""
        m = self.military
        desc = (
            f"کل نیرو: {m.total_forces:,}\n"
            f"هوایی: {m.air_force:,}\n"
            f"زمینی: {m.ground_forces:,}\n"
            f"دریایی: {m.navy:,}\n"
            f"اطلاعاتی: {m.intelligence_units:,}"
        )
        embed = discord.Embed(title="🪖 وضعیت نیروها", description=desc, color=config.COLORS["military"], timestamp=datetime.datetime.now())
        await ctx.send(embed=embed)

    @forces_group.command(name="add")
    @commands.has_permissions(administrator=True)
    async def forces_add(self, ctx: commands.Context, force_type: str, amount: int):
        if amount <= 0:
            await ctx.send(embed=discord.Embed(title="⚠️ مقدار نامعتبر", description="مقدار باید > 0 باشد.", color=config.COLORS["warning"]))
            return
        if force_type not in ["air_force", "ground_forces", "navy", "intelligence_units"]:
            await ctx.send(embed=discord.Embed(title="⚠️ نوع نامعتبر", description="انواع مجاز: air_force, ground_forces, navy, intelligence_units", color=config.COLORS["warning"]))
            return
        self.military.add_forces(force_type, amount)
        await ctx.send(embed=discord.Embed(title="✅ ثبت شد", description=f"{amount} به {force_type} افزوده شد.", color=config.COLORS["success"]))

    @forces_group.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def forces_remove(self, ctx: commands.Context, force_type: str, amount: int):
        if amount <= 0:
            await ctx.send(embed=discord.Embed(title="⚠️ مقدار نامعتبر", description="مقدار باید > 0 باشد.", color=config.COLORS["warning"]))
            return
        if force_type not in ["air_force", "ground_forces", "navy", "intelligence_units"]:
            await ctx.send(embed=discord.Embed(title="⚠️ نوع نامعتبر", description="انواع مجاز: air_force, ground_forces, navy, intelligence_units", color=config.COLORS["warning"]))
            return
        self.military.remove_forces(force_type, amount)
        await ctx.send(embed=discord.Embed(title="✅ به‌روزرسانی", description=f"{amount} از {force_type} کم شد.", color=config.COLORS["success"]))

    # ------------------------
    # Missions
    # ------------------------
    @commands.group(name="mission", invoke_without_command=True)
    async def mission_group(self, ctx: commands.Context):
        """مدیریت مأموریت‌های نظامی"""
        rows = self.db_manager.execute_query("SELECT id, mission_name, mission_type, difficulty, mission_status FROM missions ORDER BY id DESC LIMIT 10")
        if not rows:
            desc = "هیچ مأموریتی ثبت نشده است."
        else:
            lines = [f"#{r[0]} • {r[1]} • {r[2]} • {r[3]} • {r[4]}" for r in rows]
            desc = "\n".join(lines)
        embed = discord.Embed(title="📜 مأموریت‌ها", description=desc, color=config.COLORS["military"], timestamp=datetime.datetime.now())
        await ctx.send(embed=embed)

    @mission_group.command(name="create")
    @commands.has_permissions(manage_guild=True)
    async def mission_create(self, ctx: commands.Context, mission_type: str, difficulty: str = "medium"):
        if mission_type not in ["naval_patrol", "sea_blockade", "ground_patrol", "armor_drill", "amphibious", "resupply"]:
            await ctx.send(embed=discord.Embed(title="⚠️ نوع نامعتبر", description="انواع مجاز: naval_patrol, sea_blockade, ground_patrol, armor_drill, amphibious, resupply", color=config.COLORS["warning"]))
            return
        brief = await self.gemini_ai.generate_mission_briefing(mission_type, difficulty)
        name = brief.get("mission_name", f"ماموریت {mission_type}")
        code = brief.get("mission_code", f"{mission_type[:3].upper()}-{random.randint(100,999)}")
        req_forces = brief.get("required_forces", {"air":0, "ground":0, "navy":0, "intelligence":0})
        rewards = brief.get("rewards", {"experience": 200, "money": 500})
        mission_data = json.dumps(brief)
        self.db_manager.execute_update(
            "INSERT INTO missions (mission_name, mission_type, mission_description, mission_requirements, mission_rewards, mission_status, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"{name} ({code})", mission_type, json.dumps(brief.get("objectives", {})), json.dumps(req_forces), json.dumps(rewards), "active", difficulty)
        )
        embed = discord.Embed(title="🗺️ مأموریت جدید", description=f"{name} ({code})", color=config.COLORS["military"], timestamp=datetime.datetime.now())
        embed.add_field(name="نوع", value=mission_type, inline=True)
        embed.add_field(name="دشواری", value=difficulty, inline=True)
        embed.add_field(name="نیروهای موردنیاز", value=f"Air:{req_forces.get('air',0)} Ground:{req_forces.get('ground',0)} Navy:{req_forces.get('navy',0)} Intel:{req_forces.get('intelligence',0)}", inline=False)
        await ctx.send(embed=embed)

    @mission_group.command(name="assign")
    @commands.has_permissions(manage_guild=True)
    async def mission_assign(self, ctx: commands.Context, mission_id: int, *members: discord.Member):
        row = self.db_manager.execute_query("SELECT id FROM missions WHERE id = ?", (mission_id,))
        if not row:
            await ctx.send(embed=discord.Embed(title="❌ یافت نشد", description="شناسه مأموریت نامعتبر است.", color=config.COLORS["error"]))
            return
        ids = [str(m.id) for m in members]
        self.db_manager.execute_update("UPDATE missions SET assigned_users = ? WHERE id = ?", (json.dumps(ids), mission_id))
        await ctx.send(embed=discord.Embed(title="✅ تخصیص شد", description=f"{len(ids)} کاربر به مأموریت #{mission_id} اختصاص یافتند.", color=config.COLORS["success"]))

    @mission_group.command(name="complete")
    @commands.has_permissions(manage_guild=True)
    async def mission_complete(self, ctx: commands.Context, mission_id: int, success: bool = True):
        row = self.db_manager.execute_query("SELECT mission_rewards FROM missions WHERE id = ?", (mission_id,))
        if not row:
            await ctx.send(embed=discord.Embed(title="❌ یافت نشد", description="شناسه مأموریت نامعتبر است.", color=config.COLORS["error"]))
            return
        self.db_manager.execute_update("UPDATE missions SET mission_status = ?, end_time = ? WHERE id = ?", ("completed" if success else "failed", datetime.datetime.now().isoformat(), mission_id))
        await ctx.send(embed=discord.Embed(title=("🏁 مأموریت تکمیل شد" if success else "⚠️ مأموریت شکست خورد"), color=(config.COLORS["success"] if success else config.COLORS["warning"])) )

    # ------------------------
    # Navy-specific quick commands
    # ------------------------
    @commands.command(name="navy_patrol")
    async def navy_patrol(self, ctx: commands.Context, area: str):
        text = f"پاترول دریایی در منطقه {area} آغاز شد."
        await ctx.send(embed=discord.Embed(title="⚓ عملیات دریایی", description=text, color=config.COLORS["military"]))

    @commands.command(name="ground_drill")
    async def ground_drill(self, ctx: commands.Context, base: str):
        text = f"تمرین رزمی در پایگاه {base} آغاز شد."
        await ctx.send(embed=discord.Embed(title="🪖 عملیات زمینی", description=text, color=config.COLORS["military"]))

async def setup(bot: commands.Bot):
    await bot.add_cog(MilitaryCog(bot))