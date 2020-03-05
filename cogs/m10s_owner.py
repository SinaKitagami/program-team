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

class owner(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def get_ch_id(self,ctx,cnm:str):
        await ctx.send(embed=ut.getEmbed("一致チャンネル",str([f"{i.name}({i.id})" for i in ctx.guild.channels if i.name==cnm])))

    @commands.command()
    @commands.is_owner()
    async def chlogs(self,ctx,cid:int,count:int):
        ch = self.bot.get_channel(cid)
        async for m in ch.history(limit=count):
            await ctx.author.send(embed=ut.getEmbed("メッセージ",m.clean_content,self.bot.ec,"送信者",str(m.author)))
            await asyncio.sleep(2)

    @commands.command()
    @commands.is_owner()
    async def dcomrun(self,ctx,cname,*,ags):
        c = ctx
        c.args = list(ags)
        try:
            await c.invoke(self.bot.get_command(cname))
        except:
            await ctx.send(embed=discord.Embed(title="dcomrunエラー",description=traceback.format_exc(0)))

    @commands.command()
    @commands.is_owner()
    async def cu(self,ctx):
        await ctx.send("see you...")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def aev(self,ctx,*,cmd):
        try:
            await eval(cmd)
            await ctx.message.add_reaction(self.bot.get_emoji(653161518103265291))
        except:
            await ctx.send(embed=discord.Embed(title="awaitEvalエラー",description=traceback.format_exc(0)))
    
    @commands.command()
    @commands.is_owner()
    async def eval(self,ctx,*,cmd):
            await ctx.message.add_reaction(self.bot.get_emoji(653161518346534912))
            kg="\n"
            txt=f'async def evdf(ctx,bot):{kg}{kg.join([f" {i}" for i in cmd.replace("```py","").replace("```","").split(kg)])}'
            try:
                exec(txt)
                await eval("evdf(ctx,self.bot)")
                await ctx.message.remove_reaction(self.bot.get_emoji(653161518346534912),self.bot.user)
                await ctx.message.add_reaction(self.bot.get_emoji(653161518103265291))
            except:
                await ctx.message.remove_reaction(self.bot.get_emoji(653161518346534912),self.bot.user)
                await ctx.message.add_reaction("❌")
                await ctx.author.send(embed=discord.Embed(title="eval's Error",description=f"```{traceback.format_exc(3)}```",color=self.bot.ec))

    @commands.command()
    @commands.is_owner()
    async def inserver(self,ctx):
        guilds = self.bot.guilds
        gcount = len(guilds)-1
        page=0

        embed=discord.Embed(title="サーバー情報",description=f"{guilds[page].name}(id:`{guilds[page].id}`)",color=self.bot.ec)
        embed.add_field(name="サーバー人数",value=f"{guilds[page].member_count}人")
        embed.add_field(name="ブースト状態",value=f"{guilds[page].premium_tier}レベル({guilds[page].premium_subscription_count}ブースト)")
        embed.add_field(name="チャンネル状況",value=f"テキスト:{len(guilds[page].text_channels)}\nボイス:{len(guilds[page].voice_channels)}\nカテゴリー:{len(guilds[page].categories)}")
        embed.add_field(name="サーバー作成日時",value=f"{guilds[page].created_at.strftime('%Y年%m月%d日 %H時%M分%S秒')}")
        embed.add_field(name="思惟奈ちゃん導入日時",value=f"{guilds[page].me.joined_at.strftime('%Y年%m月%d日 %H時%M分%S秒')}")
        embed.add_field(name="オーナー",value=f"{guilds[page].owner}")
        embed.set_thumbnail(url=guilds[page].icon_url_as(static_format="png"))
        embed.set_footer(text=f"{page+1}/{gcount+1}")

        msg = await ctx.send(embed=embed)
        await msg.add_reaction(self.bot.get_emoji(653161518195671041))
        await msg.add_reaction(self.bot.get_emoji(653161518170505216))
        while True:
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r,u: r.message.id==msg.id and u.id == ctx.message.author.id,timeout=30)
            except:
                break
            try:
                await msg.remove_reaction(r,u)
            except:
                pass
            if str(r) == str(self.bot.get_emoji(653161518170505216)):
                if page == gcount:
                    page = 0
                else:
                    page = page + 1
                
            elif str(r) == str(self.bot.get_emoji(653161518195671041)):
                if page == 0:
                    page = gcount
                else:
                    page = page - 1
            
            embed=discord.Embed(title="サーバー情報",description=f"{guilds[page].name}(id:`{guilds[page].id}`)",color=self.bot.ec)
            embed.add_field(name="サーバー人数",value=f"{guilds[page].member_count}人")
            embed.add_field(name="ブースト状態",value=f"{guilds[page].premium_tier}レベル({guilds[page].premium_subscription_count}ブースト)")
            embed.add_field(name="チャンネル状況",value=f"テキスト:{len(guilds[page].text_channels)}\nボイス:{len(guilds[page].voice_channels)}\nカテゴリー:{len(guilds[page].categories)}")
            embed.add_field(name="サーバー作成日時",value=f"{guilds[page].created_at.strftime('%Y年%m月%d日 %H時%M分%S秒')}")
            embed.add_field(name="思惟奈ちゃん導入日時",value=f"{guilds[page].me.joined_at.strftime('%Y年%m月%d日 %H時%M分%S秒')}")
            embed.add_field(name="オーナー",value=f"{guilds[page].owner}")
            embed.set_thumbnail(url=guilds[page].icon_url_as(static_format="png"))
            embed.set_footer(text=f"{page+1}/{gcount+1}")
            await msg.edit(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def dmember(self,ctx,*,mus=None):
        info=None
        tmp2=None
        if mus == None:
            await ctx.send("メンバーid/名前の指定は必須です。")
        else:
            tmp = None
            try:
                tmp = int(mus)
            except:
                pass
            for guild in self.bot.guilds:
                if tmp:
                    tmp2 = guild.get_member(int(mus))
                else:
                    tmp2 = guild.get_member_named(mus)
                if tmp2:
                    info = tmp2
                    break
        if info:
            async with ctx.message.channel.typing(): 
                if ctx.guild.owner == info:
                    embed = discord.Embed(title=ut.textto("userinfo-name",ctx.message.author), description=f"{info.name} - {ut.ondevicon(info)} - {ut.textto('userinfo-owner',ctx.message.author)}", color=info.color)
                else:
                    embed = discord.Embed(title=ut.textto("userinfo-name",ctx.message.author), description=f"{info.name} - {ut.ondevicon(info)}", color=info.color)
                embed.add_field(name=ut.textto("userinfo-joindiscord",ctx.message.author), value=info.created_at)
                embed.add_field(name=ut.textto("userinfo-id",ctx.message.author), value=info.id)
                embed.add_field(name=ut.textto("userinfo-online",ctx.message.author), value=f"{str(info.status)}")
                embed.add_field(name=ut.textto("userinfo-isbot",ctx.message.author), value=str(info.bot))
                embed.add_field(name=ut.textto("userinfo-displayname",ctx.message.author), value=info.display_name)
                embed.add_field(name=ut.textto("userinfo-joinserver",ctx.message.author), value=info.joined_at)
                embed.set_footer(text=f"サーバー:{info.guild.name}({info.guild.id})")
                if not info.activity == None:
                    try:
                        embed.add_field(name=ut.textto("userinfo-nowplaying",ctx.message.author), value=f'{info.activity.name}')
                    except:
                        embed.add_field(name=ut.textto("userinfo-nowplaying",ctx.message.author), value=info.activity)
                hasroles = ""
                for r in info.roles:
                    hasroles = hasroles + f"{r.mention},"
                embed.add_field(name=ut.textto("userinfo-roles",ctx.message.author), value=hasroles)
                if not info.avatar_url == None:
                    embed.set_thumbnail(url=info.avatar_url_as(static_format='png'))
                    embed.add_field(name=ut.textto("userinfo-iconurl",ctx.message.author),value=info.avatar_url_as(static_format='png'))
                else:
                    embed.set_image(url=info.default_avatar_url_as(static_format='png'))
            await ctx.send(embed=embed)
        else:
            await ctx.send("一致するユーザーが、共通サーバーに見つかりませんでした。")

    @commands.command()
    @commands.is_owner()
    async def cuglobal(self,ctx,*cids):
        self.bot.cursor.execute("select * from globalchs")
        chs = self.bot.cursor.fetchall()
        async with ctx.channel.typing():
            for cid in [int(i) for i in cids]:
                await asyncio.sleep(0.5)
                try:
                    for ch in chs:
                        if cid in ch["ids"]:
                            clt=ch["ids"]
                            clt.remove(cid)
                            self.bot.cursor.execute("UPDATE globalchs SET ids = ? WHERE name = ?", (clt,ch["name"]))
                            break
                except:
                    pass
        await ctx.send("強制切断できてるか確認してねー")


    @commands.command()
    @commands.is_owner()
    async def retfmt(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        try:
            await ctx.send(ctx.message.clean_content.replace("s-retfmt ","").format(ctx,self.bot).replace("第三・十勝チャット Japan(beta)",""))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.is_owner()
    async def changenick(self,ctx, name=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        await ctx.message.guild.me.edit(nick=name)
        if name == None:
            await ctx.send("私のニックネームをデフォルトの名前に変更したよ。")
        else:
            await ctx.send("私のニックネームを"+name+"に変更したよ。")

    @commands.command()
    @commands.is_owner()
    async def guserft(self,ctx,*,nandt):
        lt=[f"{str(m)}({m.id})" for m in self.bot.users if nandt in str(m)]
        if lt:
            t="\n".join(lt)
            await ctx.send(embed=ut.getEmbed(f"{str(nandt)}に一致するユーザー",f"```{t}```"))
        else:
            await ctx.send(embed=ut.getEmbed("","一致ユーザーなし"))

    @commands.command()
    @commands.is_owner()
    async def mutual_guilds(self,ctx,user:commands.converter.UserConverter):
        mg=[]
        for g in self.bot.guilds:
            if g.get_member(user.id):
                mg+=[f"{g.name}({g.id})"]
        if mg:
            t="\n".join(mg)
            e=discord.Embed(description=f"```{t}```",color=self.bot.ec)
            e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
            await ctx.send(embed=e)
        else:
            e=discord.Embed(description="なし",color=self.bot.ec)
            e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
            await ctx.send(embed=e)



def setup(bot):
    bot.add_cog(owner(bot))