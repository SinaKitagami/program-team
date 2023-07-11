# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import datetime
from dateutil.relativedelta import relativedelta as rdelta
import traceback
from typing import Union

import config as cf

import m10s_util as ut

from my_module import dpy_interaction as dpyui

from discord import app_commands


class info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot            

    @commands.command(name="dguild")
    @ut.runnable_check()
    async def serverinfo(self, ctx, sid=None):
        if sid is not None:
            sevinfo: discord.Guild = self.bot.get_guild(int(str(sid)))
        else:
            sevinfo: discord.Guild = ctx.message.guild
        
        if sevinfo is None:
            return await ctx.send("そのサーバーに思惟奈ちゃんがいるかどうか確認してください。")

        try:
            embed = discord.Embed(title=await ctx._(
                "serverinfo-name"), description=sevinfo.name, color=self.bot.ec)
            if sevinfo.icon is not None:
                embed.set_thumbnail(
                    url=sevinfo.icon.replace(static_format='png'))
            embed.add_field(name=await ctx._("serverinfo-role"),
                            value=len(sevinfo.roles))
            embed.add_field(name=await ctx._("serverinfo-emoji"),
                            value=len(sevinfo.emojis))

            bm = 0
            ubm = 0
            for m in sevinfo.members:
                if m.bot:
                    bm = bm + 1
                else:
                    ubm = ubm + 1
            embed.add_field(name=await ctx._("serverinfo-member"),
                            value=f"{len(sevinfo.members)}(bot:{bm}/user:{ubm})")
            embed.add_field(name=await ctx._("serverinfo-channel"),
                            value=f'{await ctx._("serverinfo-text")}:{len(sevinfo.text_channels)}\n{await ctx._("serverinfo-voice")}:{len(sevinfo.voice_channels)}')
            embed.add_field(name=await ctx._("serverinfo-id"), value=sevinfo.id)
            embed.add_field(name=await ctx._("serverinfo-owner"),
                            value=sevinfo.owner.name)
            embed.add_field(name=await ctx._("serverinfo-create"), value=(sevinfo.created_at + rdelta(
                hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            rlist = ",".join([i.name for i in sevinfo.roles])
            if len(rlist) <= 1000:
                embed.add_field(name=await ctx._("serverinfo-roles"), value=rlist)
            try:
                embed.add_field(name=await ctx._("serverinfo-nitroboost"),
                                value=await ctx._("serverinfo-nitroboost-val", sevinfo.premium_tier))
                embed.add_field(name=await ctx._("serverinfo-nitroboost-can-title"), value=await ctx._(
                    f"serverinfo-nitroboost-can-{sevinfo.premium_tier}", sevinfo.premium_tier, sevinfo.premium_subscription_count))
            except:
                pass

            if sevinfo.system_channel:
                embed.add_field(name=await ctx._("serverinfo-sysch"),
                                value=sevinfo.system_channel)
                try:
                    embed.add_field(name=await ctx._("serverinfo-sysch-welcome"),
                                    value=sevinfo.system_channel_flags.join_notifications)
                    embed.add_field(name=await ctx._("serverinfo-sysch-boost"),
                                    value=sevinfo.system_channel_flags.premium_subscriptions)
                except:
                    pass
            if sevinfo.afk_channel:
                embed.add_field(name=await ctx._("serverinfo-afkch"),
                                value=sevinfo.afk_channel.name)
                embed.add_field(name=await ctx._("serverinfo-afktimeout"),
                                value=str(sevinfo.afk_timeout/60))
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
            # await ctx.send(await ctx._("serverinfo-except"))

    #chinfo is 'm10s_chinfo_rewrite' now


    @commands.hybrid_command(name="team_sina-chan", description="チーム☆思惟奈ちゃんメンバーを表示します。")
    @ut.runnable_check()
    async def view_teammember(self, ctx):
        await ctx.send(embed=ut.getEmbed(await ctx._("team_sina-chan"), "\n".join([(await self.bot.fetch_user(i)).name for i in self.bot.team_sina])))

    @commands.command()
    @ut.runnable_check()
    async def mutual_guilds(self, ctx, uid=None):
        if ctx.author.id in self.bot.team_sina:
            try:
                user = await self.bot.fetch_user(int(uid))
            except:
                user = ctx.author
            mg = []
            for g in self.bot.guilds:
                if g.get_member(user.id):
                    mg += [f"{g.name}({g.id})"]
            if mg != []:
                t = "\n".join(mg)
                e = discord.Embed(description=f"```{t}```", color=self.bot.ec)
                e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
                await ctx.send(embed=e)
            else:
                e = discord.Embed(description="なし", color=self.bot.ec)
                e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
                await ctx.send(embed=e)
        else:
            await ctx.reply("> 共通サーバーチェッカー\n　Discord公式の機能でチェックできるようになったため、このコマンドは運営専用になりました。プロフィールから確認してください。")


async def setup(bot):
    await bot.add_cog(info(bot))
