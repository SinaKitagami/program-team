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


class manage(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def backup(self,ctx,gid:int):
        if not ctx.guild.me.guild_permissions.administrator:
            await ctx.send("このサーバーで、わたしが管理者権限を持ってないので使用できません。")
            return
        try:
            g = self.bot.get_guild(gid)
            if ctx.author.permissions_in(ctx.channel).administrator == True or ctx.author.id == 404243934210949120:
                pgs=await ctx.send(f"役職\n進行度:0/{len(g.roles)}")
                tk=0
                rlid={}
                async with ctx.channel.typing():
                    #役職。rlid(dict)に旧id(str)で参照すれば新idが返ってくる
                    for r in g.roles[1:][::-1]:
                        rl=await ctx.guild.create_role(name=r.name,permissions=r.permissions,colour=r.colour,hoist=r.hoist,mentionable=r.mentionable,reason=f"{g.name}より。役職転送コマンド実行による。")
                        await asyncio.sleep(2)
                        rlid[str(r.id)]=rl.id
                        tk=tk+1
                        await pgs.edit(content=f"役職\n進行度:{tk}/{len(g.roles)}")
                    await ctx.guild.default_role.edit(permissions=g.default_role.permissions)
                    rlid[str(g.default_role.id)]=ctx.guild.default_role.id
                    await pgs.edit(content=f"チャンネル\n進行度:0/{len(g.channels)}")
                    tk=0
                    #チャンネル。
                    chlt={}
                    for mct,mch in g.by_category():
                        await asyncio.sleep(2)
                        try:
                            ovwt={}
                            await asyncio.sleep(2)
                            for k,v in mct.overwrites.items():
                                try:
                                    rl=ctx.guild.get_role(rlid[str(k.id)])
                                    ovwt[rl]=v
                                except:
                                    pass
                            ct = await ctx.guild.create_category_channel(name=mct.name,overwrites=ovwt)
                            chlt[str(mct.id)]=ct.id
                            tk=tk+1
                            await pgs.edit(content=f"チャンネル\n進行度:{tk}/{len(g.channels)}")
                        except AttributeError:
                            ct = None
                        for c in mch:
                            ovwt={}
                            await asyncio.sleep(2)
                            for k,v in c.overwrites.items():
                                try:
                                    rl=ctx.guild.get_role(rlid[k])
                                    ovwt[rl]=v
                                except:
                                    pass
                            if isinstance(c,discord.TextChannel):
                                cch=await ctx.guild.create_text_channel(name=c.name,category=ct,topic=c.topic,slowmode_delay=c.slowmode_delay,nsfw=c.is_nsfw(),overwrites=ovwt)
                            elif isinstance(c,discord.VoiceChannel):
                                if ctx.guild.bitrate_limit >= c.bitrate:
                                    cch=await ctx.guild.create_voice_channel(name=c.name,category=ct,bitrate=c.bitrate,user_limit=c.user_limit,overwrites=ovwt)
                                else:
                                    cch=await ctx.guild.create_voice_channel(name=c.name,category=ct,bitrate=ctx.guild.bitrate_limit,user_limit=c.user_limit,overwrites=ovwt)
                            else:
                                pass
                            try:
                                chlt[str(c.id)]=cch.id
                                tk=tk+1
                                await pgs.edit(content=f"チャンネル\n進行度:{tk}/{len(g.channels)}")
                            except:
                                pass
                    await pgs.edit(content="チャンネル完了\nnext:絵文字")
                    #絵文字
                    tk=0
                    for e in g.emojis:
                        if len(ctx.guild.emojis)>=ctx.guild.emoji_limit:
                            break
                        print("looping")
                        try:
                            ei = await e.url.read()
                            await ctx.guild.create_custom_emoji(name=e.name,image=ei)
                            await asyncio.sleep(5)
                            print("done")
                        except:
                            await ctx.send(f"```{traceback.format_exc(3)}```")
                    await pgs.edit(content="絵文字完了\nnext:ユーザーのban状況")
                    #ユーザーのban
                    bm = await g.bans()
                    tk=0
                    for i in bm:
                        await g.ban(user=i.user,reason=i.reason)
                        await asyncio.sleep(2)
                        tk=tk+1
                        await pgs.edit(content=f"ban状況確認\n進行度:{tk}/{len(bm)}")

                    await pgs.edit(content="ban状況完了\nnext:サーバー設定")
                    #サーバー設定
                    icn = await g.icon_url_as(static_format="png").read()
                    await ctx.guild.edit(name=g.name,icon=icn,region=g.region,verification_level=g.verification_level,default_notifications=g.default_notifications,explicit_content_filter=g.explicit_content_filter)
                    #afk
                    if g.afk_channel:
                        await ctx.guild.edit(afk_channel=ctx.guild.get_channel(chlt[str(g.afk_channel.id)]),afk_timeout=g.afk_timeout)
                    #システムチャンネル
                    if g.system_channel:
                        await ctx.guild.edit(system_channel=ctx.guild.get_channel(chlt[str(g.system_channel.id)]),system_channel_flags=g.system_channel_flags)
                    #サーバー招待スプラッシュ
                    if str(g.splash_url) and ("INVITE_SPLASH" in ctx.guild.features):
                        sp = await g.splash_url.read()
                        await ctx.guild.edit(splash=sp)
                    #サーバーバナー
                    if str(g.banner_url) and ("BANNER" in ctx.guild.features):
                        bn = await g.banner_url.read()
                        await ctx.guild.edit(banner=bn)
                    await ctx.send("完了しました。")
            else:
                await ctx.send("このサーバーの管理者である必要があります。")
        except:
            await ctx.send(embed=ut.getEmbed("エラー",f"詳細:```{traceback.format_exc(0)}```"))


    @commands.command()
    async def lrewardupd(self,ctx):
        async with ctx.channel.typing():
            self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
            gs=self.bot.cursor.fetchone()
            rslt={}
            for uk,uv in gs["levels"].items():
                u = ctx.guild.get_member(int(uk))
                for k,v in gs["reward"].items():
                    if int(k)<=uv["level"]:
                        try:
                            rl = ctx.message.guild.get_role(v)
                            await u.add_roles(rl)
                            if rslt[k]:
                                rslt[k].append(u.display_name)
                            else:
                                rslt[k] = [u.display_name]
                            await asyncio.sleep(0.2)
                        except:
                            pass
        await ctx.send("完了しました。",embed=ut.getEmbed("追加者一覧",f"```{','.join([f'レベル{k}:{v}'] for k,v in rslt.items())}```"))

    @commands.command()
    async def cemojiorole(self,ctx,name,*rlis):
        ig = await ctx.message.attachments[0].read()
        await ctx.guild.create_custom_emoji(name=name,image=ig,roles=[ctx.guild.get_role(int(i)) for i in rlis])
        await ctx.send(ut.textto("created-text",ctx.author))

    @commands.command()
    async def delm(self,ctx, ctxid):
        if ctx.message.author.permissions_in(ctx.message.channel).manage_messages == True or ctx.author.id == 404243934210949120:
            print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
            dctx = await ctx.message.channel.fetch_message(ctxid)
            print(f'{ctx.message.author.name}さんのコマンド実行で、{ctx.message.guild.name}でメッセージ"{dctx.content}"が削除されました。')
            await dctx.delete()
            await ctx.message.delete()

    @commands.command(aliases=["バン","次のメンバーをこのサーバーからbanして"])
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def memban(self,ctx,mem:int,dmd:int=0,rs=None):

        user_per = ctx.channel.permissions_for(ctx.author).ban_members
        bot_per = ctx.channel.permissions_for(ctx.guild.me).ban_members
        if user_per and bot_per or ctx.author.id == 404243934210949120:
            try:
                bmem = await self.bot.fetch_user(mem)
                await ctx.guild.ban(bmem,delete_message_days=dmd,reason=rs)
            except:
                await ctx.send(ut.textto("mem-up",ctx.message.author))
            else:
                await ctx.send(ut.textto("mem-banned",ctx.message.author))
        else:
            await ctx.send(ut.textto("mem-don'thasper",ctx.message.author))



    @commands.command(aliases=["キック","次のメンバーをこのサーバーから追い出して"])
    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    async def memkick(self,ctx,mem:commands.MemberConverter):

        user_per = ctx.channel.permissions_for(ctx.author).kick_members
        bot_per = ctx.channel.permissions_for(ctx.guild.me).kick_members
        if user_per and bot_per or ctx.author.id == 404243934210949120:
            try:
                await mem.kick()
            except:
                await ctx.send(ut.textto("mem-up",ctx.message.author))
            else:
                await ctx.send(ut.textto("mem-kicked",ctx.message.author))
        else:
            await ctx.send(ut.textto("mem-don'thasper",ctx.message.author))

    @commands.command(aliases=["ピン留め切替","次のメッセージをピン留めして"])
    async def pin(self,ctx,mid:int):
        msg = await ctx.message.channel.fetch_message(mid)
        if msg.pinned:
            await msg.unpin()
            await ctx.send(ut.textto("pin-unpinned",ctx.message.author))
        else:
            await msg.pin()
            await ctx.send(ut.textto("pin-pinned",ctx.message.author))

    @commands.command(aliases=["メッセージ一括削除","次の件数分、メッセージを消して"])
    @commands.cooldown(1, 15, type=commands.BucketType.guild)
    async def delmsgs(self,ctx,msgcount):
        if ctx.message.author.permissions_in(ctx.message.channel).manage_messages == True or ctx.author.id == 404243934210949120:
            async with ctx.message.channel.typing():
                print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
                dmc = ctx.message
                await dmc.delete()
                dr=await dmc.channel.purge(limit=int(msgcount))
                await ctx.send(ut.textto("delmsgs-del",ctx.message.author).format(len(dr)))

    @commands.command()
    async def Wecall(self,ctx, us=None, name=None):

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if not us == None and not name == None:
            if not ctx.message.mentions[0].id == ctx.author.id:
                if ctx.message.mentions[0].bot == False:
                    ok = await ctx.send(ut.textto("Wecall-areyouok",ctx.message.author).format(ctx.message.mentions[0].mention,ctx.message.author.mention,name))
                    await ok.add_reaction('⭕')
                    await ok.add_reaction('❌')
                    reaction, user = await self.bot.wait_for("reaction_add", check=lambda r,u: r.message.id==ok.id and u.id == ctx.message.mentions[0].id)
                    if str(reaction.emoji) == "⭕":
                        try:
                            await ctx.message.mentions[0].edit(nick=name)
                            await ctx.send(ut.textto("Wecall-changed",ctx.message.author))
                        except:
                            await ctx.send(ut.textto("Wecall-notchanged1",ctx.message.author))
                    else:
                        await ctx.send(ut.textto("Wecall-notchanged2",ctx.message.author))
                else:
                    await ctx.send(ut.textto("Wecall-bot",ctx.message.author))
            else:
                await ctx.send(ut.textto("Wecall-not",ctx.message.author))


def setup(bot):
    bot.add_cog(manage(bot))