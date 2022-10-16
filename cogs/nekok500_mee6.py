import discord
import aiohttp
from discord.ext import commands

from typing import Optional

from discord import app_commands

import m10s_util as ut


class MEE6(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="「mee6のレベルランキング」を一覧表示します。")
    @ut.runnable_check()
    @commands.guild_only()
    @app_commands.describe(start="最高順位")
    @app_commands.describe(end="最低順位")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def levels(self, ctx, start:Optional[int]=1, end:Optional[int]=10):
        start -= 1
        async with self.bot.session.get("https://mee6.xyz/api/plugins/levels/leaderboard/{0}".format(ctx.guild.id)) as resp:
            js = await resp.json()
            if "status_code" in js:
                if js["status_code"] == 404:
                    await ctx.send(embed=discord.Embed(title=await ctx._("cmd-error-t"), description=await ctx._("mee6-notfound")))
                    return

            else:
                l = []
                for row in js["players"][start:end]:
                    l.append("{0}: {1}Lv {2}/{3}exp".format(ctx.guild.get_member(row["id"]).name if not ctx.guild.get_member(row["id"]) is None else (
                        row["username"] + "#" + row["discriminator"]), row["level"], row["detailed_xp"][0], row["detailed_xp"][1]))
                await ctx.send(embed=discord.Embed(title="MEE6 LeaderBoard", description="\n".join(l), color=0x05FF05))


async def setup(bot):
    await bot.add_cog(MEE6(bot))
