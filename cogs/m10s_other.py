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
import psutil

from operator import itemgetter

import m10s_util as ut


class other(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="sina-guild",aliases=["思惟奈ちゃん公式サーバー","思惟奈ちゃんのサーバーに行きたい"])
    async def sinaguild(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        await ctx.send("https://discord.gg/vtn2V3v")

    @commands.command()
    async def mas(self,ctx,*,text):
        st=""
        for i in text:
            st = st+f"\|\|{i}\|\|"
        await ctx.send(st)

    @commands.command(aliases=["r","返信","引用"])
    async def reply(self,ctx,id:int,*,text):

        m = await ctx.channel.fetch_message(id)
        e = discord.Embed(description=text,color=self.bot.ec)
        e.add_field(name=f"引用投稿(引用された投稿の送信者:{m.author.display_name})",value=f"{m.content}\n[{self.bot.get_emoji(653161518451392512)} この投稿に飛ぶ]({m.jump_url})")
        e.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def rq(self,ctx):

        await ctx.send(f"{ctx.author.mention}"+ut.textto("IllQ",ctx.author)+f'\n{random.choice(ut.textto("comqest",ctx.author))}')

    @commands.command(name="Af")
    async def a_01(self,ctx):
        if not ut.textto("language",ctx.author)=="ja":
            await ctx.send(ut.textto("cannot-run",ctx.author))
            return

        await ctx.send(ctx.author.mention,embed=ut.getEmbed("",f'あなたは「{random.choice(ctx.guild.members).display_name.replace(ctx.guild.me.display_name,"私").replace(ctx.author.display_name,"あなた自身")}」のこと、好きかな？'))

    @commands.command(aliases=["アンケート","次のアンケートを開いて"])
    async def q(self,ctx,title=None,*ctt):

        if title == None or ctt == []:
            await ctx.send(ut.textto("q-not",ctx.message.author))
        else:
            ky=None
            dct = {}
            for tmp in ctt:
                if ky==None:
                    ky = tmp
                else:
                    dct[ky]=tmp
                    ky = None
            itm = ""
            for k,v in dct.items():
                if itm == "":
                    itm = f"{k}:{v}"
                else:
                    itm = itm + f"\n{k}:{v}"
            embed = discord.Embed(title=title,description=itm)
            qes = await ctx.send(embed=embed)

            for k in ctt[::2]:
                try:
                    await qes.add_reaction(k)
                except Exception as e:
                    try:
                        eid = re.match("<:[a-zA-Z0-9_-]+:([0-9]+)>",k).group(1)
                        ej = self.bot.get_emoji(int(eid))
                        await qes.add_reaction(ej)
                    except:
                        await qes.delete()
                        await ctx.send(ut.textto("q-error",ctx.author))

    @commands.command(aliases=["クレジット","クレジットを見せて"])
    async def credit(self,ctx):
        await ctx.send(ut.textto("credit",ctx.message.author))

    @commands.command()
    async def allonline(self,ctx,mus=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if mus == None:
            info = ctx.message.author
        else:
            if ctx.message.mentions:
                info = ctx.message.mentions[0]
            else:
                info = ctx.guild.get_member(int(mus))
        await ctx.send(f"Status:{str(info.status)}(PC:{str(info.desktop_status)},Mobile:{str(info.mobile_status)},Web:{str(info.web_status)})")

    @commands.command(aliases=["フィードバック","開発者にフィードバックを送って"])
    async def feedback(self,ctx,ttl,ctt=None):
        embed = discord.Embed(title=ttl, description=ctt, color=self.bot.ec)
        fbc = self.bot.get_channel(667361484283707393)
        embed.set_author(name=f"{str(ctx.message.author)}", icon_url=ctx.message.author.avatar_url_as(static_format='png'))
        await fbc.send(embed=embed)
        await ctx.send(ut.textto("feedback-sended",ctx.message.author))

    @commands.command(aliases=["レポート","報告","通報","お知らせ"])
    async def report(self,ctx,ttl,*,ctt=None):
        embed = discord.Embed(title=ttl, description=ctt, color=self.bot.ec)
        fbc = self.bot.get_channel(667361501924950036)
        embed.set_author(name=f"{str(ctx.message.author)}", icon_url=ctx.message.author.avatar_url_as(static_format='png'))
        await fbc.send(embed=embed)
        await ctx.send(ut.textto("thanks-report",ctx.author))

    @commands.command(aliases=["ステータス","あなたの情報を教えて"])
    async def botinfo(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        mem = psutil.virtual_memory()
        allmem=str(mem.total/1000000000)[0:3]
        used=str(mem.used/1000000000)[0:3]
        ava=str(mem.available/1000000000)[0:3]
        memparcent=mem.percent
        embed = discord.Embed(title=ut.textto("status-inserver",ctx.message.author), description=f"{len(self.bot.guilds)}", color=self.bot.ec)
        embed.add_field(name=ut.textto("status-prefix",ctx.message.author), value="s-")
        embed.add_field(name=ut.textto("status-starttime",ctx.message.author), value=self.bot.StartTime.strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
        embed.add_field(name=ut.textto("status-ver",ctx.message.author), value=platform.python_version())
        embed.add_field(name=ut.textto("status-pros",ctx.message.author), value=platform.processor())
        embed.add_field(name=ut.textto("status-os",ctx.message.author), value=f"{platform.system()} {platform.release()}({platform.version()})")
        embed.add_field(name="メモリ", value=f"全てのメモリ容量:{allmem}GB\n使用量:{used}GB({memparcent}%)\n空き容量{ava}GB({100-memparcent}%)")
        embed.add_field(name="全ユーザー数",value=len(self.bot.users))
        embed.add_field(name="全チャンネル",value=len([i for i in self.bot.get_all_channels()]))
        embed.add_field(name="思惟奈ちゃんをほかのサーバーに！",value="https://discordapp.com/api/oauth2/authorize?client_id=462885760043843584&permissions=8&scope=bot")
        await ctx.send(embed=embed)

    @commands.command(aliases=["rt"])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def rettext(self,ctx,*,te):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.clean_content )
        await ctx.send(te.replace("@everyone","everyone").replace("@here","here"))
        await ctx.message.delete()

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def eatit(self,ctx,it):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if ut.textto("language",ctx.author)=="ja":
            if ut.textto(f"eat-{it}",ctx.message.author).startswith("Not found key:"):
                await ctx.send(ut.textto("eat-?",ctx.message.author))
            else:
                await ctx.send(ut.textto(f"eat-{it}",ctx.message.author))
        else:
            await ctx.send(ut.textto("cannot-run",ctx.author))

    @commands.command()
    async def QandA(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        quest = len(ctx.message.content.replace("s-QandA ","")) % 5
        if quest == 0:
            await ctx.send("yes")
        elif quest == 1:
            await ctx.send("no")
        elif quest == 2:
            await ctx.send("no")
        elif quest == 3:
            await ctx.send("yes")
        elif quest == 4:
            await ctx.send("?")

    @commands.command(aliases=["scratchwikiのurl", "次のページのScratchwikiのURL教えて"])
    async def jscrawiki(self,ctx, un:str):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        await ctx.send(ut.textto("jscrawiki-return",ctx.message.author).format(un.replace("@","@ ")))

    @commands.command(aliases=["scratchのユーザーurl", "次のScratchユーザーのURL教えて"])
    async def scrauser(self,ctx, un:str):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        await ctx.send(ut.textto("scrauser-return",ctx.message.author).format(un.replace("@","@ ")))

    @commands.command(name="randomint",liases=["randint", "乱数","次の条件で乱数を作って"])
    async def randomint(self,ctx,*args):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if len(args)==1:
            s=1
            e=6
            c=int(args[0])
        elif len(args)==2:
            s=int(args[0])
            e=int(args[1])
            c=1
        elif len(args)==3:
            s=int(args[0])
            e=int(args[1])
            c=int(args[2])
        else:
            await ctx.send(ut.textto("randomint-arg-error",ctx.message.author))
        #try:
        intcount = []
        rnd = 0
        for i in range(c):
            if s <= e:
                tmp =  random.randint(s, e)
                intcount = intcount + [tmp]
                rnd= rnd + tmp
            else:
                tmp =  random.randint(e, s)
                intcount = intcount + [tmp]
                rnd= rnd + tmp
        await ctx.send(ut.textto("randomint-return1",ctx.message.author).format(str(s),str(e),str(c),str(rnd),str(intcount)))
        #except:
            #await ctx.send(ut.textto("randomint-return2",ctx.message.author))

    @commands.command(name="fortune",aliases=["おみくじ", "今日のおみくじをひく"])
    async def fortune(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        rnd = random.randint(0, 6)
        await ctx.send(ut.textto("omikuzi-return",ctx.message.author).format(ut.textto("omikuzi-"+str(rnd),ctx.message.author)))

    @commands.command()
    async def memo(self,ctx,mode="a",mn="def",*,ctt=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        mmj = self.bot.cursor.fetchone()
        if mode == "r":
            if not mmj["memo"] == None:
                if mmj["memo"].get(mn) == None:
                    await ctx.send(ut.textto("memo-r-notfound1",ctx.message.author))
                else:
                    await ctx.send(mmj["memo"][mn].replace("@everyone","everyone").replace("@here","here"))
            else:
                await ctx.send(ut.textto("memo-r-notfound2",ctx.message.author))
        elif mode == "w":
            if ctt == None:
                mmj["memo"][mn] = None
            else:
                mmj["memo"][mn] = ctt
            self.bot.cursor.execute("UPDATE users SET memo = ? WHERE id = ?", (mmj["memo"],ctx.author.id))

            await ctx.send(ut.textto("memo-w-write",ctx.message.author).format(str(mn).replace("@everyone","everyone").replace("@here","here")))
        elif mode == "a":
            if mmj["memo"] == {}:
                await ctx.send(ut.textto("memo-a-notfound",ctx.message.author))
            else:
                await ctx.send(str(mmj["memo"].keys()).replace("dict_keys(",ut.textto("memo-a-list",ctx.message.author)).replace(")",""))
        else:
            await ctx.send(ut.textto("memo-except",ctx.message.author))

    @commands.command(name="textlocker")
    async def textlocker(self,ctx):
        if not ut.textto("language",ctx.author) == "ja":
            await ctx.send(ut.textto("cannot-run",ctx.author))
            return

        tl=self.bot.tl
        dc = await ut.opendm(ctx.author)
        askmd=await dc.send(embed=ut.getEmbed("テキスト暗号・複合","暗号化する場合は🔒を、復号する場合は🔓を押してください。"))
        await askmd.add_reaction('🔒')
        await askmd.add_reaction('🔓')
        try:
            r,u= await self.bot.wait_for("reaction_add", check=lambda r,u: str(r.emoji) in ["🔒","🔓"] and r.message.id==askmd.id and u.bot==False,timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("タイムアウトしました。初めからやり直してください。")
            return
        if str(r.emoji) == "🔒":
            setting={}
            rtxt = await ut.wait_message_return(ctx,"暗号化する文を送ってください。",dc)
            setting["text"] = rtxt.content.lower()
            rtxt = await ut.wait_message_return(ctx,"始めのずらしを送ってください。",dc)
            setting["zs"] = int(rtxt.content)
            rtxt = await ut.wait_message_return(ctx,"パターンを変えるまでの数を送ってください。",dc)
            setting["cp"] = int(rtxt.content)
            rtxt = await ut.wait_message_return(ctx,"変えるときのずらす数を送ってください。",dc)
            setting["cpt"] = int(rtxt.content)
            rtext = ""
            tcount = 0
            zcount = 0
            uzs = setting["zs"]
            while tcount <= len(setting["text"])-1:
                zcount = zcount + 1
                ztmp = tl.find(setting["text"][tcount])
                if not ztmp == -1:
                    if ztmp+uzs >= len(tl):
                        rtext = f"{rtext}{tl[ztmp+uzs-len(tl)]}"
                    else:
                        rtext = f"{rtext}{tl[ztmp+uzs]}"
                    if zcount == setting["cp"]:
                        uzs = uzs + setting["cpt"]
                        zcount = 0
                else:
                    rtext = f"{rtext}☒"
                tcount = tcount + 1
            await dc.send(f"`{rtext}`になりました。")
        elif str(r.emoji) == "🔓":
            setting={}
            rtxt = await ut.wait_message_return(ctx,"復号する文を送ってください。",dc)
            setting["text"] = rtxt.content
            rtxt = await ut.wait_message_return(ctx,"始めのずらしを送ってください。",dc)
            setting["zs"] = int(rtxt.content)
            rtxt = await ut.wait_message_return(ctx,"パターンを変えるまでの数を送ってください。",dc)
            setting["cp"] = int(rtxt.content)
            rtxt = await ut.wait_message_return(ctx,"変えるときのずらす数を送ってください。",dc)
            setting["cpt"] = int(rtxt.content)
            rtext = ""
            tcount = 0
            zcount = 0
            uzs = setting["zs"]
            while tcount <= len(setting["text"])-1:
                zcount = zcount + 1
                ztmp = tl.find(setting["text"][tcount])
                if not ztmp == -1:
                    if ztmp+uzs < 0:
                        rtext = f"{rtext}{tl[ztmp-uzs+len(tl)]}"
                    else:
                        rtext = f"{rtext}{tl[ztmp-uzs]}"
                    if zcount == setting["cp"]:
                        uzs = uzs + setting["cpt"]
                        zcount = 0
                else:
                    rtext = f"{rtext}☒"
                tcount = tcount + 1
            await dc.send(f"`{rtext}`になりました。")
        else:
            await ctx.send("絵文字が違います。")

    @commands.command()
    async def rg(self,ctx,cou:int,role:commands.RoleConverter=None):

        if role is None:
            role = ctx.guild.default_role
        if cou >= 1:
            ml = [m.mention for m in role.members if not m.bot]
            ogl = []
            gl = []
            tmp = "hoge"
            while len(ml) >= cou:
                for i in range(cou):
                    tmp = random.choice(ml)
                    ogl.append(tmp)
                    ml.remove(tmp)
                gl.append(ogl)
                ogl=[]
                tmp = "hoge"
            gtxt = "\n".join([f"{'、'.join(m)}" for m in gl])
            ng = ",".join(ml)
            await ctx.send(embed=discord.Embed(title=ut.textto("rg-title",ctx.author),description=ut.textto("rg-desc",ctx.author).format(gtxt,ng), color=self.bot.ec))
        else:
            await ctx.send(ut.textto("rg-block",ctx.author))

    @commands.command(aliases=["一定時間削除"])
    async def timemsg(self,ctx,sec:float):
        await asyncio.sleep(sec)
        await ctx.message.delete()

    @commands.command()
    async def ping(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        startt = time.time()
        mes = await ctx.send("please wait")
        await mes.edit(content=str(round(time.time()-startt,3)*1000)+"ms")



def setup(bot):
    bot.add_cog(other(bot))