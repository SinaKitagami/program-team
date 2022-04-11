# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import traceback
import m10s_util as ut

"""
テストコマンドのゴミ箱
"""


class tests(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def testA(self, ctx):
        e = discord.Embed(
            title="テスト", description="リアクションしてどうぞ", color=self.bot.ec)
        msg = await ctx.send(embed=e)
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")
        try:
            r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
            if str(r) == "1️⃣":
                e = discord.Embed(
                    title="項目1", description="ブーストするといいことあるよ", color=self.bot.ec)
            elif str(r) == "2️⃣":
                e = discord.Embed(
                    title="項目2", description="えーっと、書くこと知らないんだってよ", color=self.bot.ec)
            elif str(r) == "3️⃣":
                e = discord.Embed(
                    title="項目3", description="まあ、これ、あくまで例示だしいいよね？", color=self.bot.ec)
            else:
                e = discord.Embed(
                    title="項目?", description="このリアクションには、何もないよ！", color=self.bot.ec)
            await msg.edit(embed=e)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="タイムアウト！", description="もう一度はじめから試してください。"))

    @commands.command()
    async def roletrans(self, ctx, gid: int):
        try:
            g = self.bot.get_guild(gid)
            if ctx.channel.permissions_for(ctx.author).administrator is True or ctx.author.id == 404243934210949120:
                async with ctx.channel.typing():
                    for r in g.roles[1:][::-1]:
                        await ctx.guild.create_role(name=r.name, permissions=r.permissions, colour=r.colour, hoist=r.hoist, mentionable=r.mentionable, reason=f"{g.name}より。役職転送コマンド実行による。")
                        await asyncio.sleep(2)
                await ctx.send("完了しました。")
            else:
                await ctx.send("このサーバーの管理者である必要があります。")
        except:
            await ctx.send(embed=ut.getEmbed("エラー", f"詳細:```{traceback.format_exc(0)}```"))

    @commands.command()
    async def chtrans(self, ctx, gid: int):
        try:
            g = self.bot.get_guild(gid)
            if ctx.channel.permissions_for(ctx.author).administrator is True or ctx.author.id == 404243934210949120:
                async with ctx.channel.typing():
                    # すること
                    for mct, mch in g.by_category():
                        await asyncio.sleep(2)
                        try:
                            ct = await ctx.guild.create_category_channel(name=mct.name)
                        except AttributeError:
                            ct = None
                        for c in mch:
                            await asyncio.sleep(2)
                            if isinstance(c, discord.TextChannel):
                                await ctx.guild.create_text_channel(name=c.name, category=ct, topic=c.topic, slowmode_delay=c.slowmode_delay, nsfw=c.is_nsfw())
                            elif isinstance(c, discord.VoiceChannel):
                                await ctx.guild.create_voice_channel(name=c.name, category=ct, bitrate=c.bitrate, user_limit=c.user_limit)
                            else:
                                pass
                await ctx.send("完了しました。")
            else:
                await ctx.send(await ctx._("need-admin"))
        except:
            await ctx.send(embed=ut.getEmbed(await ctx._("ginfo-anyerror-title"), await ctx._("ginfo-anyerror-title", traceback.format_exc(0))))


async def setup(bot):
    await bot.add_cog(tests(bot))
