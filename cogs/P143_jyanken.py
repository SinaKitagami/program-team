# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio

class jyanken(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="jyanken")
    async def command(self,ctx,):
        def win(hand):
            embed = discord.Embed(title="ジャンケン" , description= hand + "。\nやった、僕の勝ちだね。" , color=0xffff00)
            return embed
        def lose(hand):
            embed = discord.Embed(title="ジャンケン" , description=hand + "。\nあれ、負けちゃった。" , color=0xffff00)
            return embed
        def aiko(hand):
            embed = discord.Embed(title="ジャンケン" , description=hand + "。\nあいこで･･･" , color=0xffff00)
            return embed
        embed = discord.Embed(title="ジャンケン" , description="最初はグー、ジャンケン…" , color=0xffff00)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('\N{RAISED FIST}')
        await msg.add_reaction('\N{VICTORY HAND}')
        await msg.add_reaction('\N{RAISED HAND WITH FINGERS SPLAYED}')
        while(True):
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=lambda r,u: r.message.id==msg.id and u.id==ctx.author.id, timeout=15)
            except asyncio.TimeoutError:
                embed = discord.Embed(title="ジャンケン" , description="15秒間操作がされなかったのでゲームを終了しました。" , color=0xffff00)
                await ctx.send(embed=embed)
                break
            else:
                hand = random.randint(0,2)
                if reaction.emoji == '\N{RAISED FIST}':
                    if hand == 0:
                        await msg.edit(embed=aiko("グー"))
                        await msg.remove_reaction("\N{RAISED FIST}",ctx.author)
                    elif hand == 1:
                        await msg.edit(embed=lose("チョキ"))
                        break
                    elif hand == 2:
                        await msg.edit(embed=win("パー"))
                        break
                elif reaction.emoji == '\N{VICTORY HAND}':
                    if hand == 0:
                        await msg.edit(embed=win("グー"))
                        break
                    elif hand == 1:
                        await msg.edit(embed=aiko("チョキ"))
                        await msg.remove_reaction('\N{VICTORY HAND}',ctx.author)
                    elif hand == 2:
                        await msg.edit(embed=lose("パー"))
                        break
                elif reaction.emoji == '\N{RAISED HAND WITH FINGERS SPLAYED}':
                    if hand == 0:
                        await msg.edit(embed=lose("グー"))
                        break
                    elif hand == 1:
                        await msg.edit(embed=win("チョキ"))
                        break
                    elif hand == 2:
                        await msg.edit(embed=aiko("パー"))
                        await msg.remove_reaction("\N{RAISED HAND WITH FINGERS SPLAYED}",ctx.author)
                else:
                    embed = discord.Embed(title="ジャンケン" , description="ええっと…これは何を出しているの?" , color=0xffff00)
                    await msg.edit(embed=embed)
                    break

def setup(bot):
    bot.add_cog(jyanken(bot))