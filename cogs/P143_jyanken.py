# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio


class jyanken(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="jyanken")
    async def command(self, ctx,):
        def win(hand):
            embed = discord.Embed(
                title="ジャンケン", description="ポイ!" + hand + "\nやった、私の勝ちだね。", color=0xffff00)
            return embed

        def lose(hand):
            embed = discord.Embed(
                title="ジャンケン", description="ポイ!" + hand + "\nあれ、負けちゃった。", color=0xffff00)
            return embed

        def aiko(hand):
            embed = discord.Embed(
                title="ジャンケン", description="ポイ!" + hand + "\nあいこで･･･", color=0xffff00)
            return embed
        embed = discord.Embed(
            title="ジャンケン", description="ジャンケンをするよ。\n最初はグー、ジャンケン…", color=0xffff00)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("\N{RAISED FIST}")
        await msg.add_reaction("\N{VICTORY HAND}")
        await msg.add_reaction("\N{RAISED HAND WITH FINGERS SPLAYED}")
        while(True):
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id and (r.emoji == "\N{RAISED FIST}" or r.emoji == "\N{VICTORY HAND}" or r.emoji == "\N{RAISED HAND WITH FINGERS SPLAYED}"), timeout=15)
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="ジャンケン", description="15秒間操作がされなかったのでゲームを終了しました。", color=0xffff00)
                await ctx.send(embed=embed)
                break
            else:
                hand = random.randint(0, 2)
                if reaction.emoji == "\N{RAISED FIST}":
                    if hand == 0:
                        await msg.edit(embed=aiko("\N{RAISED FIST}"))
                        await msg.remove_reaction("\N{RAISED FIST}", ctx.author)
                    elif hand == 1:
                        await msg.edit(embed=lose("\N{VICTORY HAND}"))
                        break
                    elif hand == 2:
                        await msg.edit(embed=win("\N{RAISED HAND WITH FINGERS SPLAYED}"))
                        break
                elif reaction.emoji == "\N{VICTORY HAND}":
                    if hand == 0:
                        await msg.edit(embed=win("\N{RAISED FIST}"))
                        break
                    elif hand == 1:
                        await msg.edit(embed=aiko("\N{VICTORY HAND}"))
                        await msg.remove_reaction("\N{VICTORY HAND}", ctx.author)
                    elif hand == 2:
                        await msg.edit(embed=lose("\N{RAISED HAND WITH FINGERS SPLAYED}"))
                        break
                elif reaction.emoji == "\N{RAISED HAND WITH FINGERS SPLAYED}":
                    if hand == 0:
                        await msg.edit(embed=lose("\N{RAISED FIST}"))
                        break
                    elif hand == 1:
                        await msg.edit(embed=win("\N{VICTORY HAND}"))
                        break
                    elif hand == 2:
                        await msg.edit(embed=aiko("\N{RAISED HAND WITH FINGERS SPLAYED}"))
                        await msg.remove_reaction("\N{RAISED HAND WITH FINGERS SPLAYED}", ctx.author)


async def setup(bot):
    await bot.add_cog(jyanken(bot))
