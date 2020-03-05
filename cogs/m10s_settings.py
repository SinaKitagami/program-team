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


class settings(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def userprefix(self,ctx,mode="view",ipf=""):
        if ipf=="@everyone" or ipf=="@here":
            await ctx.send("その文字列はprefixとして使えません。")
            return
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        if mode=="view":
            await ctx.send(embed=ut.getEmbed("ユーザーのprefix",f'```{",".join(upf["prefix"])}```'))
        elif mode=="set":
            spf = upf["prefix"]+[ipf]
            self.bot.cursor.execute("UPDATE users SET prefix = ? WHERE id = ?", (spf,ctx.author.id))
            await ctx.send(ut.textto("upf-add",ctx.author).format(ipf))
        elif mode=="del":
            spf = upf["prefix"]
            spf.remove(ipf)
            self.bot.cursor.execute("UPDATE users SET prefix = ? WHERE id = ?", (spf,ctx.author.id))
            await ctx.send(f"prefixから{ipf}を削除しました。")
        else:
            await ctx.send(embed=ut.getEmbed("不適切なモード選択","`view`または`set`または`del`を指定してください。"))


    @commands.command(aliases=["switchlevelup"])
    async def switchLevelup(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        dor = self.bot.cursor.fetchone()
        if dor["levels"][str(ctx.author.id)]["dlu"]:
            dor["levels"][str(ctx.author.id)]["dlu"] = False
            await ctx.send(ut.textto("sLu-off",ctx.message.author))
        else:
            dor["levels"][str(ctx.author.id)]["dlu"] = True
            await ctx.send(ut.textto("sLu-on",ctx.message.author))
        self.bot.cursor.execute("UPDATE guilds SET levels = ? WHERE id = ?", (dor["levels"],ctx.guild.id))


    @commands.command()
    async def guildprefix(self,ctx,mode="view",ipf=""):
        if ipf=="@everyone" or ipf=="@here":
            await ctx.send("その文字列はprefixとして使えません。")
            return
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        if mode=="view":
            await ctx.send(embed=ut.getEmbed("ユーザーのprefix",f'```{",".join(gs["prefix"])}```'))
        elif mode=="set":
            spf = gs["prefix"]+[ipf]
            self.bot.cursor.execute("UPDATE guilds SET prefix = ? WHERE id = ?", (spf,ctx.guild.id))
            await ctx.send(ut.textto("upf-add",ctx.author).format(ipf))
        elif mode=="del":
            spf = gs["prefix"]
            spf.remove(ipf)
            self.bot.cursor.execute("UPDATE guilds SET prefix = ? WHERE id = ?", (spf,ctx.guild.id))
            await ctx.send(f"{ipf}を削除しました。")
        else:
            await ctx.send(embed=ut.getEmbed("不適切なモード選択","`view`または`set`または`del`を指定してください。"))

    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    @commands.command()
    async def guildlang(self,ctx,lang):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if ut.textto("language",lang).startswith("Not found language:"):
            await ctx.send(ut.textto("setl-cantuse",ctx.author))
        else:
            self.bot.cursor.execute("UPDATE guilds SET lang = ? WHERE id = ?", (lang,ctx.guild.id))
            await ctx.send(ut.textto("setl-set",ctx.message.author))

    @commands.command()
    async def sendlogto(self,ctx,to=None):
        if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
            self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
            gpf = self.bot.cursor.fetchone()
            if to:
                self.bot.cursor.execute("UPDATE guilds SET sendlog = ? WHERE id = ?", (int(to),ctx.guild.id))
                n=ctx.guild.me.nick
                await ctx.guild.me.edit(nick="ニックネーム変更テスト")
                await asyncio.sleep(1)
                await ctx.guild.me.edit(nick=n)
                await asyncio.sleep(1)
                await ctx.send("変更しました。ニックネーム変更通知が送られているかどうか確認してください。")
            else:
                self.bot.cursor.execute("UPDATE guilds SET sendlog = ? WHERE id = ?", (None,ctx.guild.id))
                await ctx.send("解除しました。")
        else:
            await ctx.send("このコマンドの使用には、管理者権限が必要です。")

    @commands.command(aliases=["言語設定","言語を次の言語に変えて"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def userlang(self,ctx,lang):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if ut.textto("language",lang).startswith("Not found language:"):
            await ctx.send(ut.textto("setl-cantuse",ctx.author))
        else:
            self.bot.cursor.execute("UPDATE users SET lang = ? WHERE id = ?", (lang,ctx.author.id))
            await ctx.send(ut.textto("setl-set",ctx.message.author))

    @commands.command()
    async def comlock(self,ctx,do="view",comname=""):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        if do =="add":
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120):
                await ctx.send(ut.textto("need-admin",ctx.author))
                return
            if not comname in gs["lockcom"]:
                gs["lockcom"].append(comname)
                self.bot.cursor.execute("UPDATE guilds SET lockcom = ? WHERE id = ?", (gs["lockcom"],ctx.guild.id))
            await ctx.send(ut.textto("upf-add",ctx.author).format(comname))
        elif do =="del":
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120):
                await ctx.send(ut.textto("need-admin",ctx.author))
                return
            if comname in gs["lockcom"]:
                gs["lockcom"].remove(comname)
                self.bot.cursor.execute("UPDATE guilds SET lockcom = ? WHERE id = ?", (gs["lockcom"],ctx.guild.id))
            await ctx.send(ut.textto("deleted-text",ctx.author))
        elif do =="view":
            await ctx.send(ut.textto("comlock-view",ctx.author).format(str(gs["lockcom"])))
        else:
            await ctx.send(ut.textto("comlock-unknown",ctx.author))

    @commands.command()
    async def setsysmsg(self,ctx,mode="check",when="welcome",to="sysch",content=None):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        msgs = self.bot.cursor.fetchone()
        sm = msgs["jltasks"]
        if mode == "check":
            embed = discord.Embed(title=ut.textto("ssm-sendcontent",ctx.message.author), description=ctx.guild.name, color=self.bot.ec)
            try:
                embed.add_field(name=ut.textto("ssm-welcome",ctx.message.author), value=f'{sm["welcome"].get("content")}({ut.textto("ssm-sendto",ctx.message.author)}):{sm["welcome"].get("sendto")})')
            except:
                pass
            try:
                embed.add_field(name=ut.textto("ssm-seeyou",ctx.message.author), value=f'{sm["cu"].get("content")}({ut.textto("ssm-sendto",ctx.message.author)}:{sm["cu"].get("sendto")})')
            except:
                pass
            await ctx.send(embed=embed)
        elif mode == "set":
            if ctx.author.permissions_in(ctx.channel).administrator == True or ctx.author.id == 404243934210949120:
                try:
                    msgs["jltasks"][when]={}
                    msgs["jltasks"][when]["content"] = content
                    msgs["jltasks"][when]["sendto"] = to
                    self.bot.cursor.execute("UPDATE guilds SET jltasks = ? WHERE id = ?", (msgs["jltasks"],ctx.guild.id))
                    await ctx.send(ut.textto("ssm-set",ctx.message.author))
                except:
                    await ctx.send(ut.textto("ssm-not",ctx.message.author))
            else:
                await ctx.send(ut.textto("need-admin",ctx.author))


    @commands.command(aliases=["サーバーコマンド","次の条件でサーバーコマンドを開く"])
    async def servercmd(self,ctx,mode="all",name=None):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        mmj = self.bot.cursor.fetchone()
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if mode == "add":
            if not mmj["commands"].get(name,None) is None:
                if not(ctx.author.permissions_in(ctx.channel).manage_guild == True and ctx.author.permissions_in(ctx.channel).manage_roles == True or ctx.author.id == 404243934210949120):
                    await ctx.send(ut.textto("need-manage",ctx.author))
                    return
            dc = ctx.author.dm_channel
            if dc == None:
                await ctx.author.create_dm()
                dc = ctx.author.dm_channel
            
            emojis = ctx.guild.emojis

            se = [] 
            for e in emojis:
                se = se + [str(e)]
            
            await dc.send(ut.textto("scmd-add-guide1",ctx.message.author))
            
            def check(m):
                return m.channel == dc and m.author == ctx.author

            msg = await self.bot.wait_for('message', check=check)
            if msg.content =="one":
                await dc.send(ut.textto("scmd-add-guide2",ctx.message.author))
                mes = await self.bot.wait_for('message', check=check)
                guide=mes.content
                try:
                    await dc.send(ut.textto("scmd-add-guide3-a",ctx.message.author).format(ut.textto("scmd-guide-emoji",ctx.message.author),str(se)))
                except:
                    await dc.send(ut.textto("scmd-add-guide3-a",ctx.message.author).format(ut.textto("scmd-guide-emoji",ctx.message.author),"(絵文字が多すぎて表示できません！)"))
                mg=await self.bot.wait_for('message', check=check)
                rep = mg.clean_content.format(se)
                mmj["commands"][name]={}
                mmj["commands"][name]["mode"]="one"
                mmj["commands"][name]["rep"]=rep
                mmj["commands"][name]["createdBy"]=ctx.author.name
                mmj["commands"][name]["guide"]=guide
            elif msg.content == "random":
                await dc.send(ut.textto("scmd-add-guide2",ctx.message.author))
                mes = await self.bot.wait_for('message', check=check)
                guide=mes.content
                try:
                    await dc.send(ut.textto("scmd-add-guide3-a",ctx.message.author).format(ut.textto("scmd-guide-emoji",ctx.message.author),str(se)))
                except:
                    await dc.send(ut.textto("scmd-add-guide3-a",ctx.message.author).format(ut.textto("scmd-guide-emoji",ctx.message.author),"(絵文字が多すぎて表示できません！)"))
                rep = []
                while True:
                    mg=await self.bot.wait_for('message', check=check)
                    if mg.content=="stop":
                        break
                    else:
                        rep = rep + [mg.clean_content.format(se)]
                        try:
                            await dc.send(ut.textto("scmd-add-guide3-b",ctx.message.author).format(ut.textto("scmd-guide-emoji",ctx.message.author),str(se)))
                        except:
                            await dc.send(ut.textto("scmd-add-guide3-b",ctx.message.author).format(ut.textto("scmd-guide-emoji",ctx.message.author),"(絵文字が多すぎて表示できません！)"))
                mmj["commands"][name]={}
                mmj["commands"][name]["mode"]="random"
                mmj["commands"][name]["rep"]=rep
                mmj["commands"][name]["createdBy"]=ctx.author.name
                mmj["commands"][name]["guide"]=guide
            elif msg.content == "role":
                if ctx.author.permissions_in(ctx.channel).manage_guild == True and ctx.author.permissions_in(ctx.channel).manage_roles == True or ctx.author.id == 404243934210949120:
                    await dc.send(ut.textto("scmd-add-guide2",ctx.message.author))
                    mes = await self.bot.wait_for('message', check=check)
                    guide=mes.content
                    await dc.send(ut.textto("scmd-add-guide3-c",ctx.message.author).format(ut.textto("scmd-guide-emoji",ctx.message.author),str(se)))
                    mg=await self.bot.wait_for('message', check=check)
                    rep = int(mg.clean_content)
                    mmj["commands"][name]={}
                    mmj["commands"][name]["mode"]="role"
                    mmj["commands"][name]["rep"]=rep
                    mmj["commands"][name]["createdBy"]=ctx.author.name
                    mmj["commands"][name]["guide"]=guide
                else:
                    await ctx.send(ut.textto("need-manage",ctx.author))
                    return
            else:
                await dc.send(ut.textto("scmd-add-not",ctx.message.author))
                return
            self.bot.cursor.execute("UPDATE guilds SET commands = ? WHERE id = ?", (mmj["commands"],ctx.guild.id))
            await ctx.send(ut.textto("scmd-add-fin",ctx.message.author))
        elif mode == "help":
            if mmj["commands"] == {}:
                await ctx.send(ut.textto("scmd-all-notfound",ctx.message.author))
            elif mmj["commands"].get(name) is None:
                await ctx.send(ut.textto("scmd-help-notfound",ctx.message.author))
            else:
                await ctx.send(ut.textto("scmd-help-title",ctx.message.author).format(name,mmj["commands"][name]['createdBy'],mmj["commands"][name]['guide']))
        elif mode == "all":
            if mmj["commands"] == []:
                await ctx.send(ut.textto("scmd-all-notfound",ctx.message.author))
            else:
                await ctx.send(str(mmj["commands"].keys()).replace("dict_keys(",ut.textto("scmd-all-list",ctx.message.author)).replace(")",""))
        elif mode == "del":
            if ctx.author.permissions_in(ctx.channel).manage_guild == True and ctx.author.permissions_in(ctx.channel).manage_roles == True or ctx.author.id == 404243934210949120:
                if not mmj["commands"] == None:
                    del mmj["commands"][name]
                await ctx.send(ut.textto("scmd-del",ctx.message.author))
                self.bot.cursor.execute("UPDATE guilds SET commands = ? WHERE id = ?", (mmj["commands"],ctx.guild.id))
            else:
                await ctx.send(ut.textto("need-manage",ctx.author))
        else:
            await ctx.send(ut.textto("scmd-except",ctx.message.author))

    @commands.command()
    async def hash(self,ctx):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        d = self.bot.cursor.fetchone()
        hc = d["hash"]
        if hc == None:
            d["hash"]=[ctx.channel.id]
            await ctx.send(ut.textto("hash-connect",ctx.message.author))
        elif ctx.channel.id in hc:
            d["hash"].remove(ctx.channel.id)
            await ctx.send(ut.textto("hash-disconnect",ctx.message.author))
        else:
            d["hash"].append(ctx.channel.id)
            await ctx.send(ut.textto("hash-connect",ctx.message.author))
        self.bot.cursor.execute("UPDATE guilds SET hash = ? WHERE id = ?", (d["hash"],ctx.guild.id))

    @commands.command(aliases=["オンライン通知"])
    async def onlinenotif(self,ctx,mode,uid:int):
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        if mode=='add':
            upf["onnotif"].append(uid)
            self.bot.cursor.execute("UPDATE users SET onnotif = ? WHERE id = ?", (upf["onnotif"],ctx.author.id))
            await ctx.send(ut.textto("onnotif-set",ctx.message.author))
        elif mode =='del':
            upf["onnotif"].remove(uid)
            self.bot.cursor.execute("UPDATE users SET onnotif = ? WHERE id = ?", (upf["onnotif"],ctx.author.id))
            await ctx.send(ut.textto("onnotif-stop",ctx.message.author))
        else:
            await ctx.send(ut.textto("onnotif-error",ctx.message.author))
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        await ctx.send(f"upf:{upf['onnotif']}")

    @commands.command()
    async def levelupsendto(self,ctx,to):
        if to == "here":
            self.bot.cursor.execute("UPDATE guilds SET levelupsendto = ? WHERE id = ?", ("here",ctx.guild.id))
        else:
            self.bot.cursor.execute("UPDATE guilds SET levelupsendto = ? WHERE id = ?", (int(to),ctx.guild.id))
        await ctx.send(ut.textto("changed",ctx.author))

    @commands.command()
    async def levelreward(self,ctx,lv:int,rl:commands.RoleConverter=None):
        rid = rl.id
        if not(ctx.author.permissions_in(ctx.channel).manage_guild == True and ctx.author.permissions_in(ctx.channel).manage_roles == True or ctx.author.id == 404243934210949120):
            await ctx.send(ut.textto("need-admin",ctx.author))
            return
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        if rid is None:
            del gs["reward"][str(lv)]
        else:
            gs["reward"][str(lv)] = rid
        self.bot.cursor.execute("UPDATE guilds SET reward = ? WHERE id = ?", (gs["reward"],ctx.guild.id))
        await ctx.send(ut.textto("changed",ctx.author))



def setup(bot):
    bot.add_cog(settings(bot))