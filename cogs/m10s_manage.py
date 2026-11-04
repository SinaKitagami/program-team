# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import traceback
import json

from discord import app_commands

import m10s_util as ut


class manage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @ut.runnable_check()
    async def cemojiorole(self, ctx, name, *rlis):
        ig = await ctx.message.attachments[0].read()
        await ctx.guild.create_custom_emoji(name=name, image=ig, roles=[ctx.guild.get_role(int(i)) for i in rlis])
        await ctx.send(await ctx._("created-text"))


    @commands.hybrid_command(aliases=["メッセージ一括削除", "次の件数分、メッセージを消して"], description="メッセージ一括削除を行います。")
    @app_commands.describe(msgcount="削除する件数")
    @commands.cooldown(1, 15, type=commands.BucketType.guild)
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id))
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def delmsgs(self, ctx:commands.Context, msgcount:int):
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages and (ctx.channel.permissions_for(ctx.author).manage_messages or ctx.author.id == 404243934210949120):
            await ctx.defer(ephemeral=True)
            async with ctx.message.channel.typing():
                if not ctx.interaction:
                    dmc = ctx.message
                    await dmc.delete()
                dr = await ctx.channel.purge(limit=int(msgcount))
            await ctx.send(await ctx._("delmsgs-del", len(dr)), ephemeral=True, delete_after=15)
        else:
            await ctx.send("> メッセージ一括削除\n　あなたか私に権限がありません！", ephemeral=True)


async def setup(bot):
    await bot.add_cog(manage(bot))
