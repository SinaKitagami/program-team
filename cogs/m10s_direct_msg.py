# -*- coding: utf-8 -*-

import discord
from discord.ext import commands, tasks
import asyncio
from dateutil.relativedelta import relativedelta as rdelta
import traceback
import m10s_util as ut
import textwrap

import config
import aiohttp

from discord import app_commands

class m10s_direct_msg(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    @ut.runnable_check()
    async def send_dm(self, ctx, target_id:int, *, content:str):
        try:
            user = await self.bot.fetch_user(target_id)
        except discord.NotFound:
            await ctx.author.send("該当ユーザーが見つかりませんでした。")
        except discord.HTTPException:
            await ctx.author.send("ユーザーの取得に失敗しました。")
        else:
            m  = await ctx.author.send(f"`{str(user)}`に```\n{content}```と送信してもよろしいですか？")
            await m.add_reaction("⭕")
            await m.add_reaction("❌")
            try:
                r,u = await self.bot.wait_for("reaction_add", timeout=30, check=lambda r,u:u.id == ctx.author.id and str(r.emoji) in ["⭕","❌"])
            except asyncio.TimeoutError:
                await m.edit(content="タイムアウトしました。再度操作を行ってください。")
                return
            if str(r.emoji) == "⭕":
                try:
                    await user.send(content)
                except:
                    await ctx.author.send("送信に失敗しました。")
                else:
                    await ctx.author.send("送信しました。")
            else:
                await ctx.author.send("キャンセルしました。")
            

async def setup(bot):
    await bot.add_cog(m10s_direct_msg(bot))