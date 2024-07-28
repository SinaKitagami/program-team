# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import time
from typing import Optional
from discord import app_commands
import asyncio

import m10s_util as ut


class games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(description="ゲーム関連コマンド")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def game(self, ctx):pass

    @game.command(name="hit_target", description="1から100までの数当てゲームです。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def game2(self, ctx):
        answer = random.randint(1, 100)
        await ctx.send(await ctx._("game2-ready"))
        i = 0
        while True:
            try:
                msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
            except:
                await ctx.send(await ctx._("game2-timeout", answer))
                return
            try:
                i = i + 1
                ur = int(msg.content)
            except:
                await ctx.send(f"{ctx.author.mention}\n{await ctx._('game2-notint')}")
                continue
            if ur > answer:
                await ctx.send(f'{ctx.author.mention}\n{await ctx._("game2-high")}')
            elif ur < answer:
                await ctx.send(f'{ctx.author.mention}\n{await ctx._("game2-low")}')
            else:
                await ctx.send(f'{ctx.author.mention}\n{await ctx._("game2-clear", i)}')
                break

    @game.command(name="near21", description="ブラックジャック風ゲームです。21に近づけた方の勝ちです。1or2人プレイ")
    @commands.bot_has_permissions(manage_messages=True, embed_links=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True, embed_links=True)
    @app_commands.describe(user2="2player-gameを遊ぶ相手(自分自身を選ぶことで誰でも参加可能な形で募集)")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def game1(self, ctx, user2: Optional[discord.Member]):

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages is True:
            if user2 is None:
                embed = discord.Embed(title="game1", description=await ctx._(
                    "game1-dis"), color=self.bot.ec)
                embed.add_field(name=await ctx._("game1-guide1"),
                                value=await ctx._("game1-guide2"))
                embed.add_field(name=await ctx._("game1-now"), value="0")
                guide = await ctx.send(embed=embed)
                g1 = await guide.add_reaction(self.bot.create_emoji_str("s_card_d",653161517927366658))
                g2 = await guide.add_reaction(self.bot.create_emoji_str('s_card_pass',653161518334214144))
                uint = 0
                tmint = 0
                while(True):

                    reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in [str(self.bot.create_emoji_str("s_card_d",653161517927366658)), str(self.bot.create_emoji_str('s_card_pass',653161518334214144))] and r.message.id == guide.id and u == ctx.message.author)

                    await guide.remove_reaction(reaction, user)
                    if str(reaction.emoji) == str(self.bot.create_emoji_str("s_card_d",653161517927366658)):
                        dr = random.randint(1, 11)
                        uint = uint + dr
                        embed = discord.Embed(title="game1", description=await ctx._(
                            "game1-dis"), color=self.bot.ec)
                        embed.add_field(name=await ctx._("game1-guide1"),
                                        value=await ctx._("game1-guide2"), inline=False)
                        embed.add_field(name=await ctx._("game1-now"),
                                        value=str(uint)+"(+"+str(dr)+")")
                        if tmint < random.randint(10, 21):
                            tmdr = random.randint(1, 11)
                            tmint = tmint + tmdr
                            embed.add_field(name=await ctx._(
                                "game1-cpun"), value=await ctx._("game1-cpud"))
                        else:
                            embed.add_field(name=await ctx._(
                                "game1-cpun"), value=await ctx._("game1-cpup"))
                        await guide.edit(embed=embed)
                    elif str(reaction.emoji) == str(self.bot.create_emoji_str('s_card_pass',653161518334214144)):
                        break
                    else:
                        await ctx.send(await ctx._("game1-notr"))
                tmfin = 21 - tmint
                ufin = 21 - uint
                u = str(uint)
                sn = str(tmint)
                if 21 >= uint and tmfin > ufin or 21 < tmint and 21 >= uint:
                    win = await ctx._("game1-yourwin")
                elif 21 >= tmint and tmfin < ufin or 21 < uint and 21 >= tmint:
                    win = await ctx._("game1-sinawin")
                else:
                    win = await ctx._("game1-dr")
                embed = discord.Embed(title=await ctx._(
                    "game1-fin1", win), description=await ctx._("game1-fin2", u, sn), color=self.bot.ec)
                await guide.edit(embed=embed)
            else:
                if user2.bot:
                    await ctx.send(await ctx._("game1-vsbot"))
                    return
                if user2 == ctx.author:
                    join = await ctx.send(await ctx._("game1-join-anyone"))
                    await join.add_reaction(self.bot.create_emoji_str("s_gp_join",653161519206629386))
                    await join.add_reaction(self.bot.create_emoji_str('s_gp_not',653161518833074178))
                    try:
                        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in [str(self.bot.create_emoji_str("s_gp_join",653161519206629386)), str(self.bot.create_emoji_str('s_gp_not',653161518833074178))] and r.message.id == join.id and u.bot is False, timeout=60)
                    except:
                        await ctx.send(await ctx._("game1-timeouted"))
                        return
                else:
                    join = await ctx.send(await ctx._("game1-join", user2.mention))
                    await join.add_reaction(self.bot.create_emoji_str("s_gp_join",653161519206629386))
                    await join.add_reaction(self.bot.create_emoji_str('s_gp_not',653161518833074178))
                    try:
                        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in [str(self.bot.create_emoji_str("s_gp_join",653161519206629386)), str(self.bot.create_emoji_str('s_gp_not',653161518833074178))] and r.message.id == join.id and u == user2, timeout=60)
                    except:
                        await ctx.send(await ctx._("game1-timeouted"))
                        return
                if str(r.emoji) == str(self.bot.create_emoji_str("s_gp_join",653161519206629386)):
                    u1 = ctx.message.author
                    u1_dm = await ut.opendm(u1)
                    u1_card = 0
                    u1_pass = False
                    u2 = u
                    u2_dm = await ut.opendm(u2)
                    u2_card = 0
                    u2_pass = False
                    e1 = discord.Embed(title=await ctx._(
                        "game1-vs-et"), description=await ctx._("game1-vs-ed", str(u1), str(u2)), color=self.bot.ec)
                    e2 = discord.Embed(title=await ctx.l10n(u2, "game1-vs-et"), description=await ctx.l10n(
                        u2, "game1-vs-ed", str(u1), str(u2)), color=self.bot.ec)
                    await u1_dm.send(embed=e1)
                    await u2_dm.send(embed=e2)
                    while not(u1_pass and u2_pass):
                        u1_pass = False
                        u2_pass = False
                        u1_msg = await u1_dm.send(await ctx._("game1-vs-yourturn", u1_card))
                        await u1_msg.add_reaction(self.bot.create_emoji_str("s_card_d",653161517927366658))
                        await u1_msg.add_reaction(self.bot.create_emoji_str('s_card_pass',653161518334214144))
                        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in [str(self.bot.create_emoji_str("s_card_d",653161517927366658)), str(self.bot.create_emoji_str('s_card_pass',653161518334214144))] and r.message.id == u1_msg.id and u == u1)
                        if str(r.emoji) == str(self.bot.create_emoji_str("s_card_d",653161517927366658)):
                            u1_card = u1_card + random.randint(1, 11)
                            await u1_msg.edit(content=await ctx._("game1-vs-dr", u1_card))
                        elif str(r.emoji) == str(self.bot.create_emoji_str('s_card_pass',653161518334214144)):
                            u1_pass = True
                            await u1_msg.edit(content=await ctx._("game1-vs-pass", u1_card))
                        u2_msg = await u2_dm.send(await ctx._("game1-vs-yourturn", u2_card))
                        await u2_msg.add_reaction(self.bot.create_emoji_str("s_card_d",653161517927366658))
                        await u2_msg.add_reaction(str(self.bot.create_emoji_str('s_card_pass',653161518334214144)))
                        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in [str(self.bot.create_emoji_str("s_card_d",653161517927366658)), str(self.bot.create_emoji_str('s_card_pass',653161518334214144))] and r.message.id == u2_msg.id and u == u2)
                        if str(r.emoji) == str(self.bot.create_emoji_str("s_card_d",653161517927366658)):
                            u2_card = u2_card + random.randint(1, 11)
                            await u2_msg.edit(content=await ctx._("game1-vs-dr", u2_card))
                        elif str(r.emoji) == str(self.bot.create_emoji_str('s_card_pass',653161518334214144)):
                            u2_pass = True
                            await u2_msg.edit(content=await ctx._("game1-vs-pass", u2_card))
                    u1_fin = 21 - u1_card
                    u2_fin = 21 - u2_card
                    if 21 >= u1_card and u2_fin > u1_fin or 21 < u2_card and 21 >= u1_card:
                        await ctx.send(await ctx._("game1-vs-fin-win", u1.mention))
                    elif 21 >= u2_card and u2_fin < u1_fin or 21 < u1_card and 21 >= u2_card:
                        await ctx.send(await ctx._("game1-vs-fin-win", u2.mention))
                    else:
                        await ctx.send(await ctx._("game1-vs-fin-draw"))
                    await ctx.send(await ctx._("game1-vs-res", u1.mention, u1_card, u2.mention, u2_card))
                else:
                    await ctx.send(await ctx._("game1-cancel", ctx.author.mention))
        else:
            try:
                await ctx.send(embed=discord.Embed(title=await ctx._("dhaveper"), description=await ctx._("per-manamsg")))
            except:
                await ctx.send(f'{await ctx._("dhaveper")}\n{await ctx._("per-manamsg")}')

    @game.command(name="fish",description="魚釣りです。")
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    @app_commands.checks.cooldown(1, 5)
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def fishany(self, ctx: commands.Context):
        lt = ["🦑", "🦐", "🐙", "🦀", "🐡", "🐠", "🐟"] + \
            [i.id for i in ctx.guild.emojis]
        fs = random.choice(lt)
        if str(type(fs)) == "<class 'int'>":
            fs = str(self.bot.get_emoji(fs))
        gp = random.randint(1, 3)
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        await self.bot.cursor.execute(
            "UPDATE users SET gpoint = %s WHERE id = %s", (upf["gpoint"]+gp, ctx.author.id))
        await ctx.send(embed=ut.getEmbed("fish", await ctx._("fish-get", fs, gp)), ephemeral=True)


async def setup(bot):
    await bot.add_cog(games(bot))
