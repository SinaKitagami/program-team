# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import asyncio

from operator import itemgetter
import json

import m10s_util as ut


class levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ranklev(self, ctx, start=1, end=10):
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #gs = await self.bot.cursor.fetchone()
        async with ctx.channel.typing():
            le = json.loads(gs["levels"])
            lrs = [(int(k), v["level"], v["exp"])
                   for k, v in le.items() if v["dlu"]]
            text = ""
            lranks = [(ind, i) for ind, i in enumerate(
                sorted(lrs, key=itemgetter(1, 2), reverse=True))]
            for ind, i in lranks[start-1:end]:
                un = ctx.guild.get_member(i[0])
                if un is None:
                    un = await self.bot.fetch_user(i[0])
                    if un is None:
                        un = f"id:`{i[0]}`"
                    else:
                        un = str(un)+f"({await ctx._('ranklev-outsideg')})"
                else:
                    un = un.mention
                if len(text+f"> {ind+1}.{un}\n　level:{i[1]},exp:{i[2]}\n") <= 2036:
                    text = text + f"> {ind+1}.{un}\n　level:{i[1]},exp:{i[2]}\n"
                else:
                    text = text+f"({await ctx._('ranklev-lenover')})"
                    break
            e = discord.Embed(title=await ctx._("ranklev-title"),
                              description=text, color=self.bot.ec)
        await ctx.send(embed=e)

    @commands.command(aliases=["レベルカード切替", "次の番号のカードにレベルカードを切り替えて"])
    async def switchlevelcard(self, ctx, number: int=None):
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        cn = ["kazuta123-a", "kazuta123-b", "m@ji☆",
              "tomohiro0405", "氷河", "雪銀　翔", "kazuta123-c"]
        if number is None:
            await ctx.send(await ctx._("slc-your", upf["levcard"].replace("-a", "").replace("-b", "").replace("-c", "")))
        else:
            if 1 <= number <= 6:
                await ctx.send(await ctx._("slc-set", number, cn[number-1].replace("-a", "").replace("-b", "").replace("-c", "")))
                await self.bot.cursor.execute(
                    "UPDATE users SET levcard = %s WHERE id = %s", (cn[number-1], ctx.author.id))
            else:
                await ctx.send(await ctx._("slc-numb"))

    @commands.command(name="level", aliases=["レベルカード", "レベルを見せて"])
    @commands.cooldown(1, 20, type=commands.BucketType.user)
    @commands.bot_has_permissions(attach_files=True)
    async def level(self, ctx, tu: commands.MemberConverter=None):
        if tu:
            u = tu
        else:
            u = ctx.author
        LEVEL_FONT = "meiryo.ttc"

        headers = {
            "User-Agent": "DiscordBot (sina-chan with discord.py)",
            "Authorization": f"Bot {self.bot.http.token}"
        }
        async with self.bot.session.get(f"https://discord.com/api/v9/users/{u.id}", headers=headers) as resp:
            resp.raise_for_status()
            ucb = await resp.json()

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if ctx.channel.permissions_for(ctx.guild.me).attach_files is True:
            gs = await self.bot.cursor.fetchone(
                "select * from guilds where id=%s", (ctx.guild.id,))
            #gs = await self.bot.cursor.fetchone()
            level = json.loads(gs["levels"])
            if level.get(str(u.id), None) is None:
                await ctx.send(await ctx._("level-notcount"))
            else:
                async with ctx.message.channel.typing():
                    nowl = level[str(u.id)]['level']
                    exp = level[str(u.id)]['exp']
                    nextl = nowl ** 3 + 20
                    tonextexp = nextl - exp
                    nextl = str(nextl)
                    tonextexp = str(tonextexp)
                    try:
                        await u.avatar_url_as(static_format="png").save("imgs/usericon.png")
                        dlicon = Image.open('imgs/usericon.png', 'r')
                    except:
                        dlicon = Image.open('imgs/noimg.png', 'r')
                    dlicon = dlicon.resize((100, 100))
                    cv = None
                    if ucb["banner"]:
                        cb = "banner"
                        banner_url = f'https://cdn.discordapp.com/banners/{u.id}/{ucb["banner"]}.png?size=640'
                        async with self.bot.session.get(banner_url, headers=headers) as resp:
                            resp.raise_for_status()
                            bt = await resp.read()
                            with open(f"imgs/custom_banner_{u.id}.png", mode="wb")as f:
                                f.write(bt)
                        cv = Image.open(f"imgs/custom_banner_{u.id}.png", 'r')
                    else:
                        c = await self.bot.cursor.fetchone(
                            "select * from users where id=%s", (u.id,))
                        #c = await self.bot.cursor.fetchone()
                        cb = c["levcard"] or "m@ji☆"
                        cv = Image.open('imgs/'+cb+'.png', 'r')
                    cv.paste(dlicon, (200, 10))
                    dt = ImageDraw.Draw(cv)
                    fonta = ImageFont.truetype(LEVEL_FONT, 30)
                    fontb = ImageFont.truetype(LEVEL_FONT, 42)
                    fontc = ImageFont.truetype(LEVEL_FONT, 20)
                    if len(u.display_name) > 11:
                        etc = "…"
                    else:
                        etc = ""
                    if cb == "kazuta123-a" or cb == "kazuta123-b" or cb == "kazuta123-c" or cb == "tomohiro0405":
                        dt.text(
                            (300, 60), u.display_name[0:10] + etc, font=fonta, fill='#ffffff')

                        dt.text((50, 110), await ctx.l10n(
                            u, "lc-level")+str(level[str(u.id)]['level']), font=fontb, fill='#ffffff')

                        dt.text((50, 170), await ctx.l10n(
                            u, "lc-exp") + str(level[str(u.id)]['exp'])+"/"+nextl, font=fonta, fill='#ffffff')

                        dt.text((50, 210), await ctx.l10n(u, "lc-next") +
                                tonextexp, font=fontc, fill='#ffffff')
                        
                        if cb != "banner":
                            dt.text((50, 300), await ctx.l10n(u, "lc-createdby", cb.replace("m@ji☆", "おあず").replace("kazuta123", "kazuta246").replace("-a", "").replace("-b", "").replace("-c", "")), font=fontc, fill='#ffffff')
                    else:
                        dt.text(
                            (300, 60), u.display_name[0:10] + etc, font=fonta, fill='#000000')

                        dt.text((50, 110), await ctx.l10n(
                            u, "lc-level")+str(level[str(u.id)]['level']), font=fontb, fill='#000000')

                        dt.text((50, 170), await ctx.l10n(
                            u, "lc-exp") + str(level[str(u.id)]['exp'])+"/"+nextl, font=fonta, fill='#000000')

                        dt.text((50, 210), await ctx.l10n(u, "lc-next") +
                                tonextexp, font=fontc, fill='#000000')

                        if cb != "banner":
                            dt.text((50, 300), await ctx.l10n(u, "lc-createdby", cb.replace("m@ji☆", "おあず").replace("kazuta123", "kazuta246").replace("-a", "").replace("-b", "").replace("-c", "")), font=fontc, fill='#000000')

                    cv.save("imgs/sina'slevelcard.png", 'PNG')
                await ctx.send(file=discord.File("imgs/sina'slevelcard.png"))
        else:
            try:
                await ctx.send(embed=discord.Embed(title=await ctx._("dhaveper"), description=await ctx._("per-sendfile")))
            except:
                await ctx.send(f"{await ctx._('dhaveper')}\n{await ctx._('per-sendfile')}")


def setup(bot):
    bot.add_cog(levels(bot))
