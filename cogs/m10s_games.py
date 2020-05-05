# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import time
import asyncio

import m10s_util as ut


class games(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def game2(self,ctx):
        answer = random.randint(1,100)
        await ctx.send(ctx._("game2-ready"))
        i=0
        while True:
            try:
                msg = await self.bot.wait_for('message', check=lambda m: m.author==ctx.author and m.channel==ctx.channel,timeout=60)
            except:
                await ctx.send(ctx._("game2-timeout", answer))
                return
            try:
                i = i + 1
                ur = int(msg.content)
            except:
                await ctx.send(f"{ctx.author.mention}\n{ctx._('game2-notint')}")
                continue
            if ur>answer:
                await ctx.send(f'{ctx.author.mention}\n{ctx._("game2-high")}')
            elif ur<answer:
                await ctx.send(f'{ctx.author.mention}\n{ctx._("game2-low")}')
            else:
                await ctx.send(f'{ctx.author.mention}\n{ctx._("game2-clear", i)}')
                break




    @commands.command(name="near21")
    async def game1(self,ctx,user2:commands.MemberConverter=None):

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content)
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages == True:
            if user2 == None:
                embed = discord.Embed(title="game1", description=ctx._($1), color=self.bot.ec)
                embed.add_field(name=ctx._($1), value=ctx._($1))
                embed.add_field(name=ctx._($1), value="0")
                guide = await ctx.send(embed=embed)
                g1=await guide.add_reaction(self.bot.get_emoji(653161517927366658))
                g2=await guide.add_reaction(self.bot.get_emoji(653161518334214144))
                uint = 0
                tmint= 0
                while(True):

                    reaction, user = await self.bot.wait_for("reaction_add", check=lambda r,u: str(r.emoji) in [str(self.bot.get_emoji(653161517927366658)),str(self.bot.get_emoji(653161518334214144))] and r.message.id==guide.id and u == ctx.message.author)

                    await guide.remove_reaction(reaction,user)
                    if str(reaction.emoji) == str(self.bot.get_emoji(653161517927366658)):
                        dr = random.randint(1,11)
                        uint = uint + dr
                        embed = discord.Embed(title="game1", description=ctx._($1), color=self.bot.ec)
                        embed.add_field(name=ctx._($1), value=ctx._($1), inline=False)
                        embed.add_field(name=ctx._($1), value=str(uint)+"(+"+str(dr)+")")
                        if tmint < random.randint(10,21):
                            tmdr = random.randint(1,11)
                            tmint = tmint + tmdr
                            embed.add_field(name=ctx._($1), value=ctx._($1))
                        else:
                            embed.add_field(name=ctx._($1), value=ctx._($1))
                        await guide.edit(embed=embed)
                    elif str(reaction.emoji) == str(self.bot.get_emoji(653161518334214144)):
                        break
                    else:
                        await ctx.send(ctx._($1))
                tmfin = 21 - tmint
                ufin = 21 - uint
                u = str(uint)
                sn=str(tmint)
                if 21 >= uint and tmfin > ufin or 21 < tmint and 21 >= uint:
                    win=ctx._($1)
                elif 21 >= tmint and tmfin < ufin or 21 < uint and 21>= tmint:
                    win=ctx._($1)
                else:
                    win=ctx._($1)
                embed = discord.Embed(title=ctx._($1).format(win), description=ctx._($1).format(u,sn), color=self.bot.ec)
                await guide.edit(embed=embed)
            else:
                if user2.bot:
                    await ctx.send(ctx._($1))
                    return
                if user2 == ctx.author:
                    join=await ctx.send(ctx._($1))
                    await join.add_reaction(self.bot.get_emoji(653161519206629386))
                    await join.add_reaction(self.bot.get_emoji(653161518833074178))
                    try:
                        r,u= await self.bot.wait_for("reaction_add", check=lambda r,u: str(r.emoji) in [str(self.bot.get_emoji(653161519206629386)),str(self.bot.get_emoji(653161518833074178))] and r.message.id==join.id and u.bot==False,timeout=60)
                    except:
                        await ctx.send(ctx._($1))
                        return
                else:
                    join=await ctx.send(ctx._($1).format(user2.mention))
                    await join.add_reaction(self.bot.get_emoji(653161519206629386))
                    await join.add_reaction(self.bot.get_emoji(653161518833074178))
                    try:
                        r,u= await self.bot.wait_for("reaction_add", check=lambda r,u: str(r.emoji) in [str(self.bot.get_emoji(653161519206629386)),str(self.bot.get_emoji(653161518833074178))] and r.message.id==join.id and u == user2,timeout=60)
                    except:
                        await ctx.send(ctx._($1))
                        return
                if str(r.emoji)==str(self.bot.get_emoji(653161519206629386)):
                    u1 = ctx.message.author
                    u1_dm = await ut.opendm(u1)
                    u1_card = 0
                    u1_pass = False
                    u2 = u
                    u2_dm = await ut.opendm(u2)
                    u2_card = 0
                    u2_pass = False
                    e1 = discord.Embed(title=ctx._("game1-vs-et"),description=ctx._("game1-vs-ed",str(u1),str(u2)),color=self.bot.ec)
                    e2 = discord.Embed(title=ctx.l10n(u2,"game1-vs-et"),description=ctx.l10n(u2,"game1-vs-ed",str(u1),str(u2)),color=self.bot.ec)
                    await u1_dm.send(embed=e1)
                    await u2_dm.send(embed=e2)
                    while not(u1_pass and u2_pass):
                        u1_pass = False
                        u2_pass = False
                        u1_msg = await u1_dm.send(ctx._($1).format(u1_card))
                        await u1_msg.add_reaction(self.bot.get_emoji(653161517927366658))
                        await u1_msg.add_reaction(self.bot.get_emoji(653161518334214144))
                        r,u=await self.bot.wait_for("reaction_add", check=lambda r,u: str(r.emoji) in [str(self.bot.get_emoji(653161517927366658)),str(self.bot.get_emoji(653161518334214144))] and r.message.id==u1_msg.id and u == u1)
                        if str(r.emoji)==str(self.bot.get_emoji(653161517927366658)):
                            u1_card  = u1_card + random.randint(1,11)
                            await u1_msg.edit(content=ctx._($1).format(u1_card))
                        elif str(r.emoji)==str(self.bot.get_emoji(653161518334214144)):
                            u1_pass=True
                            await u1_msg.edit(content=ctx._($1).format(u1_card))
                        u2_msg = await u2_dm.send(ctx._($1).format(u2_card))
                        await u2_msg.add_reaction(self.bot.get_emoji(653161517927366658))
                        await u2_msg.add_reaction(str(self.bot.get_emoji(653161518334214144)))
                        r,u=await self.bot.wait_for("reaction_add", check=lambda r,u: str(r.emoji) in [str(self.bot.get_emoji(653161517927366658)),str(self.bot.get_emoji(653161518334214144))] and r.message.id==u2_msg.id and u == u2)
                        if str(r.emoji)==str(self.bot.get_emoji(653161517927366658)):
                            u2_card  = u2_card + random.randint(1,11)
                            await u2_msg.edit(content=ctx._($1).format(u2_card))
                        elif str(r.emoji)==str(self.bot.get_emoji(653161518334214144)):
                            u2_pass=True
                            await u2_msg.edit(content=ctx._($1).format(u2_card))
                    u1_fin = 21 - u1_card
                    u2_fin = 21 - u2_card
                    if 21 >= u1_card and u2_fin > u1_fin or 21 < u2_card and 21 >= u1_card:
                        await ctx.send(ctx._($1).format(u1.mention))
                    elif 21 >= u2_card and u2_fin < u1_fin or 21 < u1_card and 21>= u2_card:
                        await ctx.send(ctx._($1).format(u2.mention))
                    else:
                        await ctx.send(ctx._($1))
                    await ctx.send(ctx._($1).format(u1.mention,u1_card,u2.mention,u2_card))
                else:
                    await ctx.send(ctx._($1).format(ctx.author.mention))
        else:
            try:
                await ctx.send(embed=discord.Embed(title=ctx._($1),description=ctx._($1)))
            except:
                await ctx.send(f'{ctx._($1)}\n{ctx._($1)}')

    @commands.command(name="fish")
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def fishany(self,ctx):
        lt=["🦑","🦐","🐙","🦀","🐡","🐠","🐟"] + [i.id for i in ctx.guild.emojis]
        fs = random.choice(lt)
        if str(type(fs)) == "<class 'int'>":
            fs = str(self.bot.get_emoji(fs))
        gp = random.randint(1,3)
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        self.bot.cursor.execute("UPDATE users SET gpoint = ? WHERE id = ?", (upf["gpoint"]+gp,ctx.author.id))
        await ctx.send(embed=ut.getEmbed("fish",ctx._($1).format(fs,gp)))



def setup(bot):
    bot.add_cog(games(bot))
