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


class search(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def getby(self,ctx,k:str):
        await ctx.send(embed=ut.getEmbed("",ut.textto(k,ctx.author)))


    @commands.command(name="checkscrauname")
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def scrauname(self, ctx, un:str):
        if not ut.textto("language",ctx.author)=="ja":
            await ctx.send(ut.textto("cannot-run",ctx.author))
            return

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        try:
            async with ctx.message.channel.typing():
                url = f'https://scratch.mit.edu/accounts/check_username/{un}'
                response = urllib.request.urlopen(url)
                content = json.loads(response.read().decode('utf8'))
                print(content)
            await ctx.send(embed=discord.Embed(title=f"Scratchでのユーザー名:\'{content[0]['username']}\'の使用可能状態",description=f"{content[0]['msg']}({content[0]['msg'].replace('username exists','存在するため使用不可').replace('bad username','検閲により使用不可').replace('invalid username','無効なユーザー名').replace('valid username','使用可能')})"))
        except:
            await ctx.send("何らかの例外が発生しました。")

    @commands.command(aliases=["twitter検索","twitterで検索して"])
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    async def twisearch(self,ctx,*,word:str):
        try:
            async with ctx.message.channel.typing():
                ret = self.bot.twi.search.tweets(q=word,result_type="recent", lang="ja", count=2)
                tweet = ret["statuses"][0]
                embed = discord.Embed(description=tweet["text"], color=int(tweet["user"]["profile_background_color"],16))
                embed.set_author(name=f'{tweet["user"]["name"]}(@{tweet["user"]["screen_name"]})',url=f'https://twitter.com/{tweet["user"]["screen_name"]}', icon_url=tweet["user"]["profile_image_url_https"])
                try:
                    embed.set_image(url=tweet["entities"]["media"][0]["media_url_https"])
                except:
                    pass
                embed.add_field(name=ut.textto("twi-see",ctx.message.author),value=f'{self.bot.get_emoji(653161518451392512)} https://twitter.com/{tweet["user"]["screen_name"]}/status/{tweet["id"]}')
            await ctx.send(embed=embed)
        except:
            await ctx.send(ut.textto("twi-error",ctx.message.author))
            #await ctx.send(embed=ut.getEmbed("traceback",traceback.format_exc(3)))

    @commands.command(aliases=["wikipedia","次の言葉でwikipedia調べて"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def jwp(self,ctx):
        try:
            async with ctx.message.channel.typing():
                wd = ctx.message.content.replace("s-jwp ", "")  
                sw = wikipedia.search(wd, results=1)
                sw1 = sw[0].replace(" ", "_")
                sr = wikipedia.page(sw1)
                embed = discord.Embed(title=sw1, description=sr.summary, color=self.bot.ec)
                embed.add_field(name=ut.textto("jwp-seemore",ctx.message.author), value=f"https://ja.wikipedia.org/wiki/{sw1}")
                try:
                    embed.set_image(url=sr.images[0])
                except:
                    pass
            await ctx.send(embed=embed)
        except:
            try:
                async with ctx.message.channel.typing():
                    if not sw == None:
                        await ctx.send(ut.textto("jwp-found",ctx.message.author).format(wd,sw1))
            except:
                await ctx.send(ut.textto("jwp-notfound",ctx.message.author))

    @commands.command(aliases=["天気","今日の天気は"])
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    async def jpwt(self,ctx):

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if ctx.channel.permissions_for(ctx.guild.me).attach_files == True:
            try:
                async with ctx.message.channel.typing():
                    r = requests.get("http://www.jma.go.jp/jp/yoho/images/000_telop_today.png", stream=True)
                    if r.status_code == 200:
                        with open("imgs/weather.png", 'wb') as f:
                            f.write(r.content)
                        await ctx.send(file=discord.File("imgs/weather.png"))
                        await ctx.send(ut.textto("jpwt-credit",ctx.message.author))
            except:
                await ctx.send(ut.textto("jpwt-error",ctx.message.author))
        else:
            try:
                await ctx.send(embed=discord.Embed(title=ut.textto("dhaveper",ctx.message.author),description=ut.textto("per-sendfile",ctx.message.author)))
            except:
                    await ctx.send(f"{ut.textto('dhaveper',ctx.message.author)}\n{ut.textto('per-sendfile',ctx.message.author)}")           


    @commands.command(aliases=["ニュース","ニュースを見せて"])
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    async def news(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        content = requests.get('https://newsapi.org/v2/top-headlines?country=jp&pagesize=5&apiKey='+self.bot.NAPI_TOKEN).json()
        for i in range(int(content["totalResults"]) - 1):
            await ctx.send(content['articles'][i]["url"])



    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def gwd(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        try:
            async with ctx.message.channel.typing():
                str1 = ctx.message.content.replace("s-gwd ", "")
                sid = requests.get("https://www.wikidata.org/w/api.php?action=wbsearchentities&search="+str1+"&language=en&format=json").json()["search"][0]["id"]
                purl = requests.get("https://www.wikidata.org/w/api.php?action=wbsearchentities&search="+str1+"&language=en&format=json").json()["search"][0]["concepturi"]
                sret = self.bot.mwc.get(sid, load=True).attributes["claims"]["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
                vsd = sret.replace("+","")
                vsd = vsd.replace("-","/")
                vsd = vsd.replace("T00:00:00Z","")
            await ctx.send(ut.textto("gwd-return1",ctx.message.author).format(str1,vsd,purl))
        except:
            await ctx.send(ut.textto("gwd-return2",ctx.message.author))

    @commands.command()
    @commands.cooldown(1, 80)
    async def gupd(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        content = requests.get('https://ja.scratch-wiki.info/w/api.php?action=query&list=recentchanges&rcprop=title|timestamp|user|comment|flags|sizes&format=json').json()
        await ctx.send(ut.textto("gupd-send",ctx.message.author))
        for i in range(5):
            try:
                embed = discord.Embed(title=ut.textto("gupd-page",ctx.message.author), description=content["query"]['recentchanges'][i]["title"], color=self.bot.ec)
                embed.add_field(name=ut.textto("gupd-editor",ctx.message.author), value=content["query"]['recentchanges'][i]["user"])
                embed.add_field(name=ut.textto("gupd-size",ctx.message.author), value=str(content["query"]['recentchanges'][i]["oldlen"])+"→"+str(content["query"]['recentchanges'][i]["newlen"])+"("+str(content["query"]['recentchanges'][i]["newlen"]-content["query"]['recentchanges'][i]["oldlen"])+")")
                embed.add_field(name=ut.textto("gupd-type",ctx.message.author), value=content["query"]['recentchanges'][i]["type"])
                if not content["query"]['recentchanges'][i]["comment"] == "":
                    embed.add_field(name=ut.textto("gupd-comment",ctx.message.author), value=content["query"]['recentchanges'][i]["comment"])
                else:
                    embed.add_field(name=ut.textto("gupd-comment",ctx.message.author), value=ut.textto("gupd-notcomment",ctx.message.author))
                embed.add_field(name=ut.textto("gupd-time",ctx.message.author), value=content["query"]['recentchanges'][i]["timestamp"].replace("T"," ").replace("Z","").replace("-","/"))
                await ctx.send(embed=embed)
            except:
                eembed = discord.Embed(title=ut.textto("gupd-unknown",ctx.message.author), description=ut.textto("gupd-url",ctx.message.author), color=self.bot.ec)
                await ctx.send(embed=eembed)

    @commands.command(aliases=["次の言葉でyoutube調べて"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def youtube(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        try:
            async with ctx.message.channel.typing():
                wd = ctx.message.content.replace("s-youtube ", "")
                youtube = build('youtube', 'v3', developerKey=self.bot.GAPI_TOKEN)
                search_response = youtube.search().list(
                part='snippet',
                q=wd,
                type='video'
                ).execute()
                id = search_response['items'][0]['id']['videoId']
                await ctx.send(ut.textto("youtube-found",ctx.message.author).format(id))        
        except:
            await ctx.send(ut.textto("youtube-notfound",ctx.message.author))  

    @commands.command(name="scranotif",aliases=["snotify", "Scratchの通知","Scratchの通知を調べて"])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def scranotif(self,ctx, un:str):

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        try:
            async with ctx.message.channel.typing():
                url = 'https://api.scratch.mit.edu/users/'+un+'/messages/count'
                response = urllib.request.urlopen(url)
                content = json.loads(response.read().decode('utf8'))
                await ctx.send(ut.textto("scranotif-notify",ctx.message.author).format(un,str(content['count'])))
        except:
            await ctx.send(ut.textto("scranotif-badrequest",ctx.message.author))

    @commands.command()
    @commands.cooldown(2, 10, type=commands.BucketType.user)
    async def wid(self,ctx,inid):
        if not ut.textto("language",ctx.author) == "ja":
            await ctx.send(ut.textto("cannot-run",ctx.author))
            return

        async with ctx.message.channel.typing():
            st = time.time()
            try:
                id = int(inid)
            except:
                id = None
            idis = self.bot.get_channel(id)
            if idis:
                if isinstance(idis,discord.DMChannel):
                    await ctx.send(embed=ut.getEmbed("DMチャンネル",f"相手:{idis.recipient}"))
                elif isinstance(idis,discord.GroupChannel):
                    await ctx.send(embed=ut.getEmbed("グループDMチャンネル",f"メンバー:{','.join(idis.recipients)},\n名前:{idis.name},"))
                elif isinstance(idis,discord.abc.GuildChannel):
                    await ctx.send(embed=ut.getEmbed("サーバーチャンネル",f"名前:{idis.name}\nサーバー:{idis.guild}"))
                else:
                    await ctx.send(embed=ut.getEmbed("その他チャンネル",f"名前:{idis.name}"))
                return
            idis = self.bot.get_guild(id)
            if idis:
                if idis.id in [i[0] for i in self.bot.partnerg]:
                    ptn="🔗パートナーサーバー"
                else:
                    ptn=""
                await ctx.send(embed=ut.getEmbed("サーバー",f"{ptn}\n名前:{idis.name}\nid:{idis.id}"))
                return
            try:
                idis = await self.bot.fetch_user(id)
                u=idis
                e = discord.Embed(title="ユーザー",color=self.bot.ec)
                if u.system:
                    e.add_field(name="✅システムアカウント",value="このアカウントは、Discordのシステムアカウントであり、安全です。",inline=False)
                e.add_field(name="名前",value=u.name)
                e.add_field(name="id",value=u.id)
                e.add_field(name="ディスクリミネータ",value=u.discriminator)
                e.add_field(name="botかどうか",value=u.bot)

                e.set_thumbnail(url=u.avatar_url)
                e.set_footer(text=f"アカウント作成日時(そのままの値:{(u.created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')},タイムスタンプ化:")
                e.timestamp = u.created_at
                await ctx.send(embed=e)
                return
            except:
                pass
            idis = self.bot.get_emoji(id)
            if idis:
                await ctx.send(embed=ut.getEmbed("絵文字",f"名前:{str(idis)}\nid:{idis.id}"))
                return
            try:
                idis = await self.bot.fetch_invite(inid)
                await ctx.send(embed=ut.getEmbed("サーバー招待",f"名前:{str(idis.guild.name)}\nチャンネル:{idis.channel.name}\nmember_count:{idis.approximate_member_count}\npresence_count:{idis.approximate_presence_count}\n[参加]({idis.url})"))
                return
            except:
                pass
            try:
                idis = await self.bot.fetch_webhook(id)
                await ctx.send(embed=ut.getEmbed("webhook",f"デフォルトネーム:{idis.name}\nサーバーid:{idis.guild_id}"))
                return
            except:
                pass
            try:
                idis = await self.bot.fetch_widget(inid)
                await ctx.send(embed=ut.getEmbed("サーバーウィジェット",f"名前:{idis.name}\n招待:{idis.invite_url}"))
                return
            except:
                pass
            """try:
                for g in self.bot.guilds:
                    for ch in g.text_channels:
                        try:
                            idis = await ch.fetch_message(id)
                            await ctx.send(embed=ut.getEmbed("メッセージ",f"送信者:{idis.author}\n内容:{idis.content}"))
                            return
                        except:
                            pass
                        finally:
                            await asyncio.sleep(0.5)
            except:
                pass"""
            await ctx.send(embed=ut.getEmbed("そのidでは見つかりませんでした。","(現在メッセージidの検索は無効化されています。)"))





def setup(bot):
    bot.add_cog(search(bot))