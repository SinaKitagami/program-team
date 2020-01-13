# -*- coding: utf-8 -*-

import discord
from discord.ext import commands,tasks
import json
from collections import OrderedDict
import random
import requests
import urllib.request
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import wikipedia
import wikidata.client
from PIL import Image, ImageDraw, ImageFont
import time
import asyncio
import dropbox
import datetime
import pickle
import sys
import platform
import re
from twitter import *
from dateutil.relativedelta import relativedelta as rdelta
import traceback
import threading
import os
import shutil
import pytz
import sqlite3

from operator import itemgetter

import m10s_util as ut


class levels(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def ranklev(self,ctx):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        async with ctx.channel.typing():
            le = gs["levels"]
            lrs = [(int(k),v["level"],v["exp"]) for k,v in le.items() if v["dlu"]]
            text=""
            for ind,i in enumerate(sorted(lrs, key=itemgetter(1,2), reverse=True)):
                un = ctx.guild.get_member(i[0])
                if un is None:
                    un = await self.bot.fetch_user(i[0])
                    if un is None:
                        un=f"id:`{i[0]}`"
                    else:
                        un = str(un)+f"({ut.textto('ranklev-outsideg',ctx.author)})"
                else:
                    un = un.mention
                if len(text+f"> {ind+1}.{un}\n　level:{i[1]},exp:{i[2]}\n") <= 2036:
                    text = text + f"> {ind+1}.{un}\n　level:{i[1]},exp:{i[2]}\n"
                else:
                    text = text+f"({ut.textto('ranklev-lenover',ctx.author)})"
                    break
            e = discord.Embed(title=ut.textto("ranklev-title",ctx.author),description=text,color=self.bot.ec)
        await ctx.send(embed=e)

    @commands.command(aliases=["レベルカード切替","次の番号のカードにレベルカードを切り替えて"])
    async def switchlevelcard(self,ctx,number:int=None):
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        cn=["kazuta123-a","kazuta123-b","m@ji☆","tomohiro0405","氷河","雪銀　翔","kazuta123-c"]
        if number==None:
            await ctx.send(ut.textto("slc-your",ctx.message.author).format(upf["levcard"].replace("-a","").replace("-b","").replace("-c","")))
        else:
            if 1 <= number <= 6:
                await ctx.send(ut.textto("slc-set",ctx.message.author).format(number,cn[number-1].replace("-a","").replace("-b","").replace("-c","")))
                self.bot.cursor.execute("UPDATE users SET levcard = ? WHERE id = ?", (cn[number-1],ctx.author.id))
            else:
                await ctx.send(ut.textto("slc-numb",ctx.message.author))

    @commands.command(name="level",aliases=["レベルカード", "レベルを見せて"])
    @commands.cooldown(1, 20, type=commands.BucketType.user)
    async def level(self,ctx, tu:commands.MemberConverter=None):
        if tu:
            u = tu
        else:
            u = ctx.author
        LEVEL_FONT = "meiryo.ttc"
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if ctx.channel.permissions_for(ctx.guild.me).attach_files == True:
            self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
            gs=self.bot.cursor.fetchone()
            level=gs["levels"]
            if level.get(str(u.id),None) is None:
                await ctx.send(ut.textto("level-notcount",ctx.author))
            else:
                async with ctx.message.channel.typing():
                    nowl = level[str(u.id)]['level']
                    exp = level[str(u.id)]['exp']
                    nextl = nowl ** 3 + 20
                    tonextexp = nextl - exp
                    nextl = str(nextl)
                    tonextexp = str(tonextexp)
                    try:
                        r = requests.get(u.avatar_url_as(static_format="png"), stream=True)
                        if r.status_code == 200:
                            with open("imgs/usericon.png", 'wb') as f:
                                f.write(r.content)
                        dlicon = Image.open('imgs/usericon.png', 'r')
                    except:
                        dlicon = Image.open('imgs/noimg.png', 'r')
                    dlicon = dlicon.resize((100, 100))
                    self.bot.cursor.execute("select * from users where id=?",(u.id,))
                    c = self.bot.cursor.fetchone()
                    cb=c["levcard"] or "m@ji☆"
                    cv = Image.open('imgs/'+cb+'.png','r')
                    cv.paste(dlicon, (200, 10))
                    dt = ImageDraw.Draw(cv)
                    fonta = ImageFont.truetype(LEVEL_FONT, 30)
                    fontb = ImageFont.truetype(LEVEL_FONT, 42)
                    fontc = ImageFont.truetype(LEVEL_FONT, 20)
                    if len(u.display_name) > 11:
                        etc = "…"
                    else:
                        etc = ""
                    if cb=="kazuta123-a" or cb=="kazuta123-b" or cb=="kazuta123-c" or cb=="tomohiro0405":
                        dt.text((300, 60), u.display_name[0:10] +etc, font=fonta, fill='#ffffff')

                        dt.text((50, 110), ut.textto("lc-level",u)+str(level[str(u.id)]['level']) , font=fontb, fill='#ffffff')

                        dt.text((50, 170), ut.textto("lc-exp",u) + str(level[str(u.id)]['exp'])+"/"+nextl , font=fonta, fill='#ffffff')

                        dt.text((50, 210), ut.textto("lc-next",u)+tonextexp , font=fontc, fill='#ffffff')

                        dt.text((50, 300), ut.textto("lc-createdby",u).format(cb.replace("m@ji☆","おあず").replace("kazuta123","kazuta246").replace("-a","").replace("-b","").replace("-c","")) , font=fontc, fill='#ffffff')
                    else:
                        dt.text((300, 60), u.display_name[0:10] +etc, font=fonta, fill='#000000')

                        dt.text((50, 110), ut.textto("lc-level",u)+str(level[str(u.id)]['level']) , font=fontb, fill='#000000')

                        dt.text((50, 170), ut.textto("lc-exp",u) + str(level[str(u.id)]['exp'])+"/"+nextl , font=fonta, fill='#000000')

                        dt.text((50, 210), ut.textto("lc-next",u)+tonextexp , font=fontc, fill='#000000')

                        dt.text((50, 300), ut.textto("lc-createdby",u).format(cb.replace("m@ji☆","おあず").replace("kazuta123","kazuta246").replace("-a","").replace("-b","").replace("-c","")) , font=fontc, fill='#000000')

                    cv.save("imgs/sina'slevelcard.png", 'PNG') 
                await ctx.send(file=discord.File("imgs/sina'slevelcard.png"))
        else:
            try:
                await ctx.send(embed=discord.Embed(title=ut.textto("dhaveper",ctx.author),description=ut.textto("per-sendfile",ctx.author)))
            except:
                await ctx.send(f"{ut.textto('dhaveper',ctx.author)}\n{ut.textto('per-sendfile',ctx.author)}")           




def setup(bot):
    bot.add_cog(levels(bot))