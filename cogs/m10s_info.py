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

class info(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def anyuserinfo(self,ctx,*,uid:int=None):
        if uid:
            self.bot.cursor.execute("select * from users where id=?",(uid,))
            upf = self.bot.cursor.fetchone()
            if upf:
                isva=upf["sinapartner"]
            else:
                isva=0
            try:
                u=await self.bot.fetch_user(uid)
            except discord.NotFound:
                await ctx.send(ut.textto("aui-nf",ctx.author))
            except discord.HTTPException:
                await ctx.send(ut.textto("aui-he",ctx.author))
            except:
                await ctx.send(ut.textto("aui-othere",ctx.author).format(traceback.format_exc()))
            else:
                ptn=""
                if u.id in self.bot.team_sina:
                    ptn=f',({ut.textto("team_sina-chan",ctx.author)})'
                if u.id in [i[1] for i in self.bot.partnerg]:
                    ptn=ptn+f',({ut.textto("partner_guild_o",ctx.author)})'
                if isva:
                    ptn=ptn+f"、(💠{'認証済みアカウント'})"
                e = discord.Embed(title=f"{ut.textto('aui-uinfo',ctx.author)}{ptn}",color=self.bot.ec)
                if u.system:
                    e.add_field(name="✅システムアカウント",value="このアカウントは、Discordのシステムアカウントであり、安全です。",inline=False)
                e.add_field(name=ut.textto("aui-name",ctx.author),value=u.name)
                e.add_field(name=ut.textto("aui-id",ctx.author),value=u.id)
                e.add_field(name=ut.textto("aui-dr",ctx.author),value=u.discriminator)
                e.add_field(name=ut.textto("aui-isbot",ctx.author),value=u.bot)
                e.set_thumbnail(url=u.avatar_url)
                tm=(u.created_at + rdelta(hours=9)).strftime("%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}").format(*"年月日時分秒")
                e.set_footer(text=ut.textto("aui-created",ctx.author).format(tm))
                e.timestamp = u.created_at
            await ctx.send(embed=e)
        else:
            await ctx.send(ut.textto("aui-nid",ctx.author))

    @commands.command(aliases=["ui","ユーザー情報","ユーザーの情報を教えて"])
    async def userinfo(self,ctx, mus:commands.MemberConverter=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if mus == None:
            info = ctx.message.author
        else:
            info = mus
        self.bot.cursor.execute("select * from users where id=?",(info.id,))
        upf = self.bot.cursor.fetchone()
        if upf:
            isva=upf["sinapartner"]
        else:
            isva=0
        async with ctx.message.channel.typing(): 
            ptn=""
            if info.id in self.bot.team_sina:
                ptn=f',({ut.textto("team_sina-chan",ctx.author)})'
            if info.id in [i[1] for i in self.bot.partnerg]:
                ptn=ptn+f',({ut.textto("partner_guild_o",ctx.author)})'
            if isva:
                ptn=ptn+f"、(💠{'認証済みアカウント'})"
            if ctx.guild.owner == info:
                embed = discord.Embed(title=ut.textto("uinfo-title",ctx.author), description=f"{ptn} - {ut.textto('userinfo-owner',ctx.message.author)}", color=info.color)
            else:
                embed = discord.Embed(title=ut.textto("uinfo-title",ctx.author), description=ptn, color=info.color)
            if info.system:
                embed.add_field(name="✅システムアカウント",value="このアカウントは、Discordのシステムアカウントであり、安全です。",inline=False)
            embed.add_field(name=ut.textto("userinfo-name",ctx.message.author),value=f"{info.name} - {ut.ondevicon(info)}")
            try:
                if not info.premium_since is None:
                    embed.add_field(name=ut.textto("userinfo-guildbooster",ctx.message.author), value=f"since {info.premium_since}")
            except:
                pass
            embed.add_field(name=ut.textto("userinfo-joindiscord",ctx.message.author), value=(info.created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            embed.add_field(name=ut.textto("userinfo-id",ctx.message.author), value=info.id)
            embed.add_field(name=ut.textto("userinfo-online",ctx.message.author), value=f"{str(info.status)}")
            embed.add_field(name=ut.textto("userinfo-isbot",ctx.message.author), value=str(info.bot))
            embed.add_field(name=ut.textto("userinfo-displayname",ctx.message.author), value=info.display_name)
            embed.add_field(name=ut.textto("userinfo-joinserver",ctx.message.author), value=(info.joined_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            if not info.activity == None:
                try:
                    if info.activity.type == discord.ActivityType.custom:
                        embed.add_field(name=ut.textto("userinfo-nowplaying",ctx.message.author), value=info.activity)
                    else:
                        embed.add_field(name=ut.textto("userinfo-nowplaying",ctx.message.author), value=f'{info.activity.name}')
                except:
                    embed.add_field(name=ut.textto("userinfo-nowplaying",ctx.message.author), value=info.activity)
            hasroles = ""
            for r in info.roles:
                hasroles = hasroles + f"{r.mention},"
            embed.add_field(name=ut.textto("userinfo-roles",ctx.message.author), value=hasroles)
            embed.add_field(name=ut.textto("userinfo-guildper",ctx.author),value=f"`{'`,`'.join([ut.textto(f'p-{i[0]}',ctx.author) for i in list(info.guild_permissions) if i[1]])}`")
            if not info.avatar_url == None:
                embed.set_thumbnail(url=info.avatar_url_as(static_format='png'))
                embed.add_field(name=ut.textto("userinfo-iconurl",ctx.message.author),value=info.avatar_url_as(static_format='png'))
            else:
                embed.set_image(url=info.default_avatar_url_as(static_format='png'))
            lmsc=ut.get_vmusic(self.bot,info)
            if lmsc:
                embed.add_field(name=f"思惟奈ちゃんを使って[{lmsc['name']}]({lmsc['url']} )を聴いています。",value=f"サーバー:{lmsc['guild'].name}")
        await ctx.send(embed=embed)


    @commands.command()
    async def cinvite(self,ctx,ivt:str):
        i = await self.bot.fetch_invite(ivt)
        e=discord.Embed(title=ut.textto("cinvite-title",ctx.author),description=ut.textto("cinvite-from",ctx.author).format(str(i.inviter)),color=self.bot.ec)
        e.set_author(name=f'{i.guild.name}({i.guild.id})',icon_url=i.guild.icon_url_as(format="png"))
        e.add_field(name=ut.textto("cinvite-memcount",ctx.author),value=f'{i.approximate_member_count}\n({ut.textto("cinvite-onmemcount",ctx.author)}{i.approximate_presence_count})')
        e.add_field(name=ut.textto("cinvite-ch",ctx.author),value=f"{i.channel.name}({i.channel.type})")
        e.add_field(name=ut.textto("cinvite-tmp",ctx.author),value=str(i.temporary))
        e.add_field(name=ut.textto("cinvite-deleted",ctx.author),value=str(i.revoked))
        e.add_field(name=ut.textto("cinvite-link",ctx.author),value=i.url,inline=False)
        e.set_footer(text=ut.textto("cinvite-createdat",ctx.author))
        e.timestamp = i.created_at or discord.Embed.Empty
        await ctx.send(embed=e)

    @commands.command()
    async def emojiinfo(self,ctx,*,emj:commands.EmojiConverter=None):

        if emj==None:
            await ctx.send(ut.textto("einfo-needarg",ctx.author))
        else:
            embed = discord.Embed(title=emj.name, description=f"id:{emj.id}",color=self.bot.ec)
            embed.add_field(name=ut.textto("einfo-animated",ctx.author), value=emj.animated)
            embed.add_field(name=ut.textto("einfo-manageout",ctx.author), value=emj.managed)
            if emj.user:
                embed.add_field(name=ut.textto("einfo-adduser",ctx.author), value=str(emj.user))
            embed.add_field(name="url", value=emj.url)
            embed.set_footer(text=ut.textto("einfo-addday",ctx.author))
            embed.timestamp = emj.created_at
            await ctx.send(embed=embed)

    @commands.command(name="dguild")
    async def serverinfo(self,ctx,sid=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if not sid == None:
            sevinfo = self.bot.get_guild(int(str(sid)))
        else:
            sevinfo = ctx.message.guild
        if sevinfo.id in [i[0] for i in self.bot.partnerg]:
            ptn=f'{ut.textto("partner_guild",ctx.author)}:'
        else:
            ptn=""
        try:
            embed = discord.Embed(title=ut.textto("serverinfo-name",ctx.message.author), description=sevinfo.name, color=self.bot.ec)
            if not sevinfo.icon_url == None:
                embed.set_thumbnail(url=sevinfo.icon_url_as(static_format='png'))
            embed.add_field(name=ut.textto("serverinfo-role",ctx.message.author), value=len(sevinfo.roles))
            embed.add_field(name=ut.textto("serverinfo-emoji",ctx.message.author), value=len(sevinfo.emojis))
            embed.add_field(name=ut.textto("serverinfo-country",ctx.message.author), value=str(sevinfo.region))
            bm = 0
            ubm = 0
            for m in sevinfo.members:
                if m.bot:
                    bm = bm + 1
                else:
                    ubm = ubm + 1
            embed.add_field(name=ut.textto("serverinfo-member",ctx.message.author), value=f"{len(sevinfo.members)}(bot:{bm}/user:{ubm})")
            embed.add_field(name=ut.textto("serverinfo-channel",ctx.message.author), value=f'{ut.textto("serverinfo-text",ctx.message.author)}:{len(sevinfo.text_channels)}\n{ut.textto("serverinfo-voice",ctx.message.author)}:{len(sevinfo.voice_channels)}')
            embed.add_field(name=ut.textto("serverinfo-id",ctx.message.author), value=sevinfo.id)
            embed.add_field(name=ut.textto("serverinfo-owner",ctx.message.author), value=sevinfo.owner.name)
            embed.add_field(name=ut.textto("serverinfo-create",ctx.message.author), value=(sevinfo.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            rlist = ",".join([i.name for i in sevinfo.roles])
            if len(rlist) <= 1000:
                embed.add_field(name=ut.textto("serverinfo-roles",ctx.message.author),value=rlist)
            try:
                embed.add_field(name=ut.textto("serverinfo-nitroboost",ctx.message.author),value=ut.textto("serverinfo-nitroboost-val",ctx.message.author).format(sevinfo.premium_tier))
                embed.add_field(name=ut.textto("serverinfo-nitroboost-can-title",ctx.message.author),value=ut.textto(f"serverinfo-nitroboost-can-{sevinfo.premium_tier}",ctx.message.author).format(sevinfo.premium_tier,sevinfo.premium_subscription_count))
            except:
                pass
            
            if sevinfo.system_channel:
                embed.add_field(name=ut.textto("serverinfo-sysch",ctx.message.author),value=sevinfo.system_channel)
                try:
                    embed.add_field(name=ut.textto("serverinfo-sysch-welcome",ctx.message.author),value=sevinfo.system_channel_flags.join_notifications)
                    embed.add_field(name=ut.textto("serverinfo-sysch-boost",ctx.message.author),value=sevinfo.system_channel_flags.premium_subscriptions)
                except:
                    pass
            if sevinfo.afk_channel:
                embed.add_field(name=ut.textto("serverinfo-afkch",ctx.message.author),value=sevinfo.afk_channel.name)
                embed.add_field(name=ut.textto("serverinfo-afktimeout",ctx.message.author),value=str(sevinfo.afk_timeout/60))
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
            #await ctx.send(ut.textto("serverinfo-except",ctx.message.author))

    @commands.command()
    async def cprofile(self,ctx,usid=None):
        uid = usid or ctx.author.id
        self.bot.cursor.execute("select * from users where id=?",(uid,))
        pf = self.bot.cursor.fetchone()
        e = discord.Embed(title=ut.textto("cpro-title",ctx.author),description=f"id:{uid}")
        e.add_field(name="prefix",value=pf["prefix"])
        e.add_field(name=ut.textto("cpro-gpoint",ctx.author),value=pf["gpoint"])
        e.add_field(name=ut.textto("cpro-levelcard",ctx.author),value=pf["levcard"])
        e.add_field(name=ut.textto("cpro-renotif",ctx.author),value=pf["onnotif"])
        e.add_field(name=ut.textto("cpro-lang",ctx.author),value=pf["lang"])
        e.add_field(name="認証済みかどうか", value=pf["sinapartner"])
        await ctx.send(embed=e)

    @commands.command()
    async def checkmember(self,ctx,member:commands.MemberConverter):
        if not ut.textto("language",ctx.author)=="ja":
            await ctx.send(ut.textto("cannot-run",ctx.author))
            return
        bunotif = 0
        for g in self.bot.guilds:
            try:
                tmp = await g.bans()
            except:
                continue
            banulist = [i.user.id for i in tmp]
            if member.id in banulist:
                bunotif = bunotif + 1
        if bunotif == 0:
            await ctx.send(embed=discord.Embed(title=ut.textto("ucheck-title",ctx.author).format(member),description=ut.textto("ucheck-not_ban",ctx.author)))
        else:
            await ctx.send(embed=discord.Embed(title=ut.textto("ucheck-title",ctx.author).format(member),description=ut.textto("ucheck-not_ban",ctx.author).format(bunotif)))

    @commands.command(aliases=["次のボイスチャンネルのURLを教えて"])
    async def vcurl(self,ctx,vch:commands.VoiceChannelConverter=None):
        if vch is None and (not ctx.author.voice == None):
            ch = ctx.author.voice.channel
        else:
            ch = vch
        await ctx.send(embed=ut.getEmbed(ch.name,f"https://discordapp.com/channels/{ctx.guild.id}/{ch.id}"))

    @commands.command(name="chinfo",aliases=["チャンネル情報","次のチャンネルについて教えて"])
    async def channelinfo(self,ctx,cid:int=None):

        if cid is None:
            ch = ctx.message.channel
        else:
            ch = ctx.guild.get_channel(cid)
        if isinstance(ch,discord.TextChannel):

            embed = discord.Embed(title=ch.name, description=f"id:{ch.id}", color=ctx.author.colour)

            embed.add_field(name=ut.textto("ci-type",ctx.message.author),value=ut.textto("ci-text",ctx.message.author))

            embed.add_field(name=ut.textto("ci-topic",ctx.message.author),value=ch.topic or ut.textto("topic-is-none",ctx.author))

            embed.add_field(name=ut.textto("ci-slow",ctx.message.author),value=str(ch.slowmode_delay).replace("0",ut.textto("ci-None",ctx.message.author)))

            embed.add_field(name=ut.textto("ci-nsfw",ctx.message.author),value=ch.is_nsfw())

            embed.add_field(name=ut.textto("ci-cate",ctx.message.author),value=ch.category)

            embed.add_field(name=ut.textto("ci-created",ctx.message.author),value=(ch.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

            embed.add_field(name=ut.textto("ci-invitec",ctx.message.author),value=str(len(await ch.invites())).replace("0",ut.textto("ci-None",ctx.message.author)))

            embed.add_field(name=ut.textto("ci-pinc",ctx.message.author),value=str(len(await ch.pins())).replace("0",ut.textto("ci-None",ctx.message.author)))

            embed.add_field(name=ut.textto("ci-whc",ctx.message.author),value=str(len(await ch.webhooks())).replace("0",ut.textto("ci-None",ctx.message.author)))

            embed.add_field(name=ut.textto("ci-url",ctx.message.author),value=f"[{ut.textto('ci-click',ctx.message.author)}](https://discordapp.com/channels/{ctx.guild.id}/{ch.id})")

            await ctx.send(embed=embed)

        elif isinstance(ch,discord.VoiceChannel):
            embed = discord.Embed(title=ch.name, description=f"id:{ch.id}", color=ctx.author.colour)

            embed.add_field(name=ut.textto("ci-type",ctx.message.author),value=ut.textto("ci-voice",ctx.message.author))

            embed.add_field(name=ut.textto("ci-bit",ctx.message.author),value=ch.bitrate)

            embed.add_field(name=ut.textto("ci-limituser",ctx.message.author),value=str(ch.user_limit).replace("0",ut.textto("ci-None",ctx.message.author)))

            embed.add_field(name=ut.textto("ci-cate",ctx.message.author),value=ch.category)

            embed.add_field(name=ut.textto("ci-created",ctx.message.author),value=(ch.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

            embed.add_field(name=ut.textto("ci-invitec",ctx.message.author),value=str(len(await ch.invites())).replace("0",ut.textto("ci-None",ctx.message.author)))

            embed.add_field(name=ut.textto("ci-url",ctx.message.author),value=f"[{ut.textto('ci-click',ctx.message.author)}](https://discordapp.com/channels/{ctx.guild.id}/{ch.id})")

            await ctx.send(embed=embed)

        elif isinstance(ch,discord.CategoryChannel):
            
            embed = discord.Embed(title=ch.name, description=f"id:{ch.id}", color=ctx.author.colour)

            embed.add_field(name=ut.textto("ci-type",ctx.message.author),value=ut.textto("ci-cate",ctx.message.author))

            embed.add_field(name=ut.textto("ci-nsfw",ctx.message.author),value=ch.is_nsfw())

            ic = ""

            for c in ch.channels:
                ic = ic + c.mention + ","

            embed.add_field(name=ut.textto("ci-inch",ctx.message.author),value=ic)

            embed.add_field(name=ut.textto("ci-created",ctx.message.author),value=(ch.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

            embed.add_field(name=ut.textto("ci-url",ctx.message.author),value=f"[{ut.textto('ci-click',ctx.message.author)}](https://discordapp.com/channels/{ctx.guild.id}/{ch.id})")

            await ctx.send(embed=embed)
        else:
            await ctx.send(ut.textto("ci-notfound",ctx.message.author))

    @commands.command(aliases=["ボイス情報","音声情報を教えて"])
    async def voiceinfo(self,ctx,mus:commands.MemberConverter=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if mus == None:
            info = ctx.message.author
        else:
            info = mus
        try:
            embed = discord.Embed(title=info.display_name, description=f"{info.voice.channel.guild.name} - {info.voice.channel.name}", color=info.colour)
            vste=""
            if info.voice.deaf:
                #サバスピーカーミュート
                vste=vste+str(self.bot.get_emoji(653161518057127937))
            else:
                #サバスピーカーオン
                vste=vste+str(self.bot.get_emoji(653161518082293770))
            if info.voice.mute:
                #サバマイクミュート
                vste=vste+str(self.bot.get_emoji(653161518086619137))
            else:
                #サバマイクオン
                vste=vste+str(self.bot.get_emoji(653161518086619137))
            if info.voice.self_deaf:
                #スピーカーミュート
                vste=vste+str(self.bot.get_emoji(653161518258585620))
            else:
                #スピーカーオン
                vste=vste+str(self.bot.get_emoji(653161517881098272))
            if info.voice.self_mute:
                #マイクミュート
                vste=vste+str(self.bot.get_emoji(653161519143714816))
            else:
                #マイクオン
                vste=vste+str(self.bot.get_emoji(653161518224900096))
            if info.voice.self_video:
                #画面共有
                vste=vste+str(self.bot.get_emoji(653161517960658945))
            elif info.voice.self_stream:
                #GoLive
                vste=vste+str(self.bot.get_emoji(653161518250196992))
            embed.add_field(name="ステータス(status)",value=vste)
        except AttributeError:
            await ctx.send(ut.textto("vi-nfch",ctx.message.author))
        finally:
            lmusic=ut.get_vmusic(self.bot,info)
            if lmusic:
                if lmusic["guild"].id == ctx.guild.id and info.id in [i.id for i in ctx.voice_client.channel.members]:
                    embed.add_field(name="ボイスチャットで思惟奈ちゃんを使って音楽を聞いています。",value=f"[{lmusic['name']}]({lmusic['url']} )")
            await ctx.send(embed=embed)

    @commands.command(aliases=["役職情報","次の役職について教えて"])
    async def roleinfo(self,ctx,*,role:commands.RoleConverter=None):

        if role==None:
            await ctx.send(ut.textto("roleinfo-howto",ctx.message.author))
        elif role.guild == ctx.guild:
            embed = discord.Embed(title=role.name, description=f"id:{role.id}", color=role.colour)
            embed.add_field(name=ut.textto("roleinfo-hoist",ctx.message.author), value=role.hoist)
            embed.add_field(name=ut.textto("roleinfo-mention",ctx.message.author), value=role.mentionable)
            hasmember=""
            for m in role.members:
                hasmember = hasmember + f"{m.mention},"
            if not hasmember == "":
                embed.add_field(name=ut.textto("roleinfo-hasmember",ctx.message.author), value=hasmember)
            else:
                embed.add_field(name=ut.textto("roleinfo-hasmember",ctx.message.author), value="(None)")
            hasper = ""
            for pn,bl in iter(role.permissions):
                if bl:
                    hasper = hasper + f"`{ut.textto(f'p-{pn}',ctx.author)}`,"
            embed.add_field(name=ut.textto("roleinfo-hasper",ctx.message.author), value=hasper)
            embed.add_field(name=ut.textto("roleinfo-created",ctx.message.author), value=(role.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

            await ctx.send(embed=embed)
        else:
            await ctx.send(ut.textto("roleinfo-other",ctx.message.author))

    @commands.command(name="activity",aliases=["アクティビティ","なにしてるか見せて"])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def infoactivity(self,ctx, mus:commands.MemberConverter=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        try:
            await self.bot.request_offline_members(ctx.guild)
        except:
            pass
        if mus is None:
            info = ctx.message.author
        else:
            info = mus
        lmsc=ut.get_vmusic(self.bot,info)
        if lmsc:
            embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=f"{lmsc['guild'].name}で、思惟奈ちゃんを使って[{lmsc['name']}]({lmsc['url']} )を聞いています", color=info.color)
            await ctx.send(embed=embed)
        if info.activity is None:
            if str(info.status) == "offline":
                embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=ut.textto("playinginfo-offline",ctx.message.author), color=info.color)
            else:
                sete =False
                try:
                    if info.voice.self_stream:
                        embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=str(self.bot.get_emoji(653161518250196992))+ut.textto("playinginfo-GoLive",ctx.message.author), color=info.color)
                        sete=True
                    elif info.voice.self_video:
                        embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=str(self.bot.get_emoji(653161517960658945))+ut.textto("playinginfo-screenshare",ctx.message.author), color=info.color)
                        sete=True
                    elif info.voice:
                        embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=str(self.bot.get_emoji(653161518082293770))+ut.textto("playinginfo-invc",ctx.message.author), color=info.color)
                        sete=True
                except:
                    pass
                if not sete:
                    if info.bot:
                        embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=ut.textto("playinginfo-bot",ctx.message.author), color=info.color)
                    elif "🌐"==ut.ondevicon(info):
                        embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=ut.textto("playinginfo-onlyWeb",ctx.message.author), color=info.color)
                    elif "📱"==ut.ondevicon(info):
                        embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=ut.textto("playinginfo-onlyPhone",ctx.message.author), color=info.color)
                    else:
                        embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=ut.textto("playinginfo-noActivity",ctx.message.author), color=info.color)
            activ=info.activity
            embed.set_author(name=info.display_name, icon_url=info.avatar_url_as(static_format='png'))
            await ctx.send(embed=embed)
        else:
            for anactivity in info.activities:
                if anactivity.type == discord.ActivityType.playing:
                    activName=ut.textto("playinginfo-playing",ctx.message.author)+anactivity.name
                elif anactivity.type == discord.ActivityType.watching:
                    activName=ut.textto("playinginfo-watching",ctx.message.author)+anactivity.name
                elif anactivity.type == discord.ActivityType.listening:
                    activName=ut.textto("playinginfo-listening",ctx.message.author).format(anactivity.name)
                elif anactivity.type ==  discord.ActivityType.streaming:
                    activName=ut.textto("playinginfo-streaming",ctx.message.author)+anactivity.name
                elif anactivity.type ==  discord.ActivityType.custom:
                    activName=ut.textto("playinginfo-custom_status",ctx.message.author)
                else:
                    activName=ut.textto("playinginfo-unknown",ctx.message.author)+anactivity.name
                embed = discord.Embed(title=ut.textto("playinginfo-doing",ctx.message.author), description=activName, color=info.color)
                activ=anactivity
                embed.set_author(name=info.display_name, icon_url=info.avatar_url_as(static_format='png'))
                if anactivity.name == "Spotify":
                    try:
                        embed.add_field(name=ut.textto("playinginfo-title",ctx.message.author), value=activ.title)
                        embed.add_field(name=ut.textto("playinginfo-artist",ctx.message.author), value=activ.artist)
                        embed.add_field(name=ut.textto("playinginfo-album",ctx.message.author), value=activ.album)
                        embed.add_field(name="URL", value=f"https://open.spotify.com/track/{activ.track_id}")
                        tmp=str(int((datetime.datetime.utcnow() - activ.start).seconds%60))
                        pnow=f"{int((datetime.datetime.utcnow() - activ.start).seconds/60)}:{tmp if len(tmp)==2 else f'0{tmp}'}"
                        tmp=str(int(activ.duration.seconds%60))
                        pml=f"{int(activ.duration.seconds/60)}:{tmp if len(tmp)==2 else f'0{tmp}'}"
                        embed.add_field(name="経過時間", value=f"{pnow}/{pml}")
                        embed.set_thumbnail(url=activ.album_cover_url)
                    except AttributeError:
                        embed.add_field(name=ut.textto("spotify-local",ctx.author), value=ut.textto("spotify-cantlisten-wu",ctx.author))
                        embed.add_field(name=ut.textto("playinginfo-title",ctx.message.author), value=activ.details)
                        embed.add_field(name=ut.textto("playinginfo-artist",ctx.message.author), value=activ.state)
                elif anactivity.type==discord.ActivityType.streaming:
                    try:
                        embed.add_field(name=ut.textto("playinginfo-streampage",ctx.message.author), value=activ.url)
                    except:
                        pass
                    try:
                        embed.add_field(name=ut.textto("playinginfo-do",ctx.message.author), value=activ.datails)
                    except:
                        pass
                elif anactivity.type==discord.ActivityType.custom:
                    embed.add_field(name=ut.textto("playinginfo-det",ctx.message.author), value=str(anactivity))
                else:
                    try:
                        vl = ""
                        if activ.details:
                            vl = f"{activ.details}\n"
                        if activ.state:
                            vl = f"{vl}{activ.state}\n"
                        if vl == "":
                            vl = "なし"
                        embed.add_field(name=ut.textto("playinginfo-det",ctx.message.author), value=vl)
                    except:
                        pass
                try:
                    if anactivity.created_at:
                        embed.set_footer(text=f"started the activity at")
                        embed.timestamp=anactivity.created_at
                except:
                    pass
                await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def ginfo(self,ctx):
        if ctx.guild.id in [i[0] for i in self.bot.partnerg]:
            ptn=f'{ut.textto("partner_guild",ctx.author)}:'
        else:
            ptn=""
        pmax= 12 if "PUBLIC" in ctx.guild.features else 11
        page = 0
        e =discord.Embed(title=ut.textto("ginfo-ov-title",ctx.author),color=self.bot.ec)
        e.set_author(name=f"{ptn}{ctx.guild.name}",icon_url=ctx.guild.icon_url_as(static_format='png'))
        e.add_field(name=ut.textto("ginfo-region",ctx.author),value=ctx.guild.region)
        e.add_field(name=ut.textto("ginfo-afkch",ctx.author),value=ctx.guild.afk_channel)
        if ctx.guild.afk_channel:
            e.add_field(name=ut.textto("ginfo-afktout",ctx.author),value=f"{ctx.guild.afk_timeout/60}min")
        else:
            e.add_field(name=ut.textto("ginfo-afktout",ctx.author),value=ut.textto("ginfo-afknone",ctx.author))
        e.add_field(name=ut.textto("ginfo-sysch",ctx.author),value=ctx.guild.system_channel)
        e.add_field(name=ut.textto("ginfo-memjoinnotif",ctx.author),value=ctx.guild.system_channel_flags.join_notifications)
        e.add_field(name=ut.textto("ginfo-serverboostnotif",ctx.author),value=ctx.guild.system_channel_flags.premium_subscriptions)
        if ctx.guild.default_notifications == discord.NotificationLevel.all_messages:
            e.add_field(name=ut.textto("ginfo-defnotif",ctx.author),value=ut.textto("ginfo-allmsg",ctx.author))
        else:
            e.add_field(name=ut.textto("ginfo-defnotif",ctx.author),value=ut.textto("ginfo-omention",ctx.author))
        if "INVITE_SPLASH" in ctx.guild.features:
            e.add_field(name=ut.textto("ginfo-invitesp",ctx.author),value=ut.textto("ginfo-invitesp-pos",ctx.author))
            e.set_image(url=ctx.guild.splash_url_as(format="png"))
        if "BANNER" in ctx.guild.features:
            e.add_field(name=ut.textto("ginfo-banner",ctx.author),value=ut.textto("ginfo-banner-pos",ctx.author))
            e.set_thumbnail(url=ctx.guild.banner_url_as(format="png"))
        mp = await ctx.send(embed=e)
        await mp.add_reaction(self.bot.get_emoji(653161518195671041))
        await mp.add_reaction(self.bot.get_emoji(653161518170505216))
        while True:
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r,u: r.message.id==mp.id and u.id == ctx.message.author.id,timeout=30)
            except:
                break
            try:
                await mp.remove_reaction(r,u)
            except:
                pass
            if str(r) == str(self.bot.get_emoji(653161518170505216)):
                if page == pmax:
                    page = 0
                else:
                    page = page + 1
            elif str(r) == str(self.bot.get_emoji(653161518195671041)):
                if page == 0:
                    page = pmax
                else:
                    page = page - 1
            try:
                if page == 0:
                    #概要
                    e =discord.Embed(title=ut.textto("ginfo-ov-title",ctx.author),color=self.bot.ec)
                    e.set_author(name=f"{ptn}{ctx.guild.name}",icon_url=ctx.guild.icon_url_as(static_format='png'))
                    e.add_field(name=ut.textto("ginfo-region",ctx.author),value=ctx.guild.region)
                    e.add_field(name=ut.textto("ginfo-afkch",ctx.author),value=ctx.guild.afk_channel)
                    if ctx.guild.afk_channel:
                        e.add_field(name=ut.textto("ginfo-afktout",ctx.author),value=f"{ctx.guild.afk_timeout/60}min")
                    else:
                        e.add_field(name=ut.textto("ginfo-afktout",ctx.author),value=ut.textto("ginfo-afknone",ctx.author))
                    e.add_field(name=ut.textto("ginfo-sysch",ctx.author),value=ctx.guild.system_channel)
                    e.add_field(name=ut.textto("ginfo-memjoinnotif",ctx.author),value=ctx.guild.system_channel_flags.join_notifications)
                    e.add_field(name=ut.textto("ginfo-serverboostnotif",ctx.author),value=ctx.guild.system_channel_flags.premium_subscriptions)
                    if ctx.guild.default_notifications == discord.NotificationLevel.all_messages:
                        e.add_field(name=ut.textto("ginfo-defnotif",ctx.author),value=ut.textto("ginfo-allmsg",ctx.author))
                    else:
                        e.add_field(name=ut.textto("ginfo-defnotif",ctx.author),value=ut.textto("ginfo-omention",ctx.author))
                    if "INVITE_SPLASH" in ctx.guild.features:
                        e.add_field(name=ut.textto("ginfo-invitesp",ctx.author),value=ut.textto("ginfo-invitesp-pos",ctx.author))
                        e.set_image(url=ctx.guild.splash_url_as(format="png"))
                    if "BANNER" in ctx.guild.features:
                        e.add_field(name=ut.textto("ginfo-banner",ctx.author),value=ut.textto("ginfo-banner-pos",ctx.author))
                        e.set_thumbnail(url=ctx.guild.banner_url_as(format="png"))
                    await mp.edit(embed=e)
                elif page == 1:
                    #管理
                    e = discord.Embed(title=ut.textto("ginfo-manage",ctx.author),color=self.bot.ec)
                    if ctx.guild.verification_level == discord.VerificationLevel.none:
                        e.add_field(name=ut.textto("ginfo-vlevel",ctx.author),value=ut.textto("ginfo-vlnone",ctx.author))
                    elif ctx.guild.verification_level == discord.VerificationLevel.low:
                        e.add_field(name=ut.textto("ginfo-vlevel",ctx.author),value=ut.textto("ginfo-vl1",ctx.author))
                    elif ctx.guild.verification_level == discord.VerificationLevel.medium:
                        e.add_field(name=ut.textto("ginfo-vlevel",ctx.author),value=ut.textto("ginfo-vl2",ctx.author))
                    elif ctx.guild.verification_level == discord.VerificationLevel.high:
                        e.add_field(name=ut.textto("ginfo-vlevel",ctx.author),value=ut.textto("ginfo-vl3",ctx.author))
                    elif ctx.guild.verification_level == discord.VerificationLevel.extreme:
                        e.add_field(name=ut.textto("ginfo-vlevel",ctx.author),value=ut.textto("ginfo-vl4",ctx.author))
                    if ctx.guild.explicit_content_filter == discord.ContentFilter.disabled:
                        e.add_field(name=ut.textto("ginfo-filter",ctx.author),value=ut.textto("ginfo-fnone",ctx.author))
                    elif ctx.guild.explicit_content_filter == discord.ContentFilter.no_role:
                        e.add_field(name=ut.textto("ginfo-filter",ctx.author),value=ut.textto("ginfo-f1",ctx.author))
                    elif ctx.guild.explicit_content_filter == discord.ContentFilter.all_members:
                        e.add_field(name=ut.textto("ginfo-filter",ctx.author),value=ut.textto("ginfo-f2",ctx.author))
                    await mp.edit(embed=e)
                elif page == 2:
                    #roles
                    if ctx.author.guild_permissions.manage_roles or ctx.author.id == 404243934210949120:
                        rl = ctx.guild.roles[::-1]
                        rls = ""
                        for r in rl:
                            if len(f"{rls}\n{r.name}")>=1998:
                                rls=rls+"\n…"
                                break
                            else:
                                rls=f"{rls}\n{r.name}"
                        await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-roles",ctx.author),description=rls,color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-roles",ctx.author),description=ut.textto("ginfo-cantview",ctx.author),color=self.bot.ec))
                elif page == 3:
                    #emoji
                    ejs=""
                    for i in ctx.guild.emojis:
                        if len( ejs + "," + str(i) ) >=1998:
                            ejs=ejs+"など"
                            break
                        else:
                            ejs=ejs + "," + str(i)
                    await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-emoji",ctx.author),description=ejs,color=self.bot.ec))
                elif page == 4:
                    #webhooks
                    if ctx.author.guild_permissions.manage_webhooks or ctx.author.id == 404243934210949120:
                        await mp.edit(embed=discord.Embed(title="webhooks",description="\n".join([f"{i.name},[link]({i.url}),created by {i.user}" for i in await ctx.guild.webhooks()]),color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title="webhooks",description=ut.textto("ginfo-cantview",ctx.author),color=self.bot.ec))
                elif page == 5:
                    #ウィジェット
                    if ctx.author.guild_permissions.manage_guild or ctx.author.id == 404243934210949120:
                        try:
                            wdt = await ctx.guild.widget()
                            await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-widget",ctx.author),description=f"URL: {wdt.json_url}",color=self.bot.ec))
                        except:
                            await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-widget",ctx.author),description=ut.textto("ginfo-ctuw",ctx.author),color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-widget",ctx.author),description=ut.textto("ginfo-cantview",ctx.author),color=self.bot.ec))
                elif page == 6:
                    #Nitro server boost
                    e = discord.Embed(title=str(self.bot.get_emoji(653161518971617281))+"Nitro Server Boost",description=f"Level:{ctx.guild.premium_tier}\n({ctx.guild.premium_subscription_count})",color=self.bot.ec)
                    e.add_field(name=ut.textto("ginfo-bst-add",ctx.author),value=ut.textto(f"ginfo-blev{ctx.guild.premium_tier}",ctx.author))
                    await mp.edit(embed=e)
                elif page == 7:
                    #member
                    vml=ut.textto("ginfo-strlenover",ctx.author)
                    if len("\n".join([f"{str(i)}" for i in ctx.guild.members])) <= 1024:
                        vml = "\n".join([f"{str(i)}" for i in ctx.guild.members]).replace(str(ctx.guild.owner),f"👑{str(ctx.guild.owner)}")
                    await mp.edit(embed=discord.Embed(title="member",description=f"member count:{len(ctx.guild.members)}\n```"+vml+"```"),color=self.bot.ec)
                elif page == 8:
                    if ctx.author.guild_permissions.manage_guild or ctx.author.id == 404243934210949120:
                        try:
                            vi = await ctx.guild.vanity_invite()
                            vi = vi.code
                        except:
                            vi = "NF_VInvite"
                        #invites
                        vil = ut.textto("ginfo-strlenover",ctx.author)
                        if len("\n".join([f'{i.code},{ut.textto("ginfo-use-invite",ctx.author)}:{i.uses}/{i.max_uses},{ut.textto("ginfo-created-invite",ctx.author)}:{i.inviter}' for i in await ctx.guild.invites()])) <= 1023:
                            vil = "\n".join([f'{i.code},{ut.textto("ginfo-use-invite",ctx.author)}:{i.uses}/{i.max_uses},{ut.textto("ginfo-created-invite",ctx.author)}:{i.inviter}' for i in await ctx.guild.invites()]).replace(vi,f"{self.bot.get_emoji(653161518103265291)}{vi}")
                        await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-invites",ctx.author),description=vil,color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-invites",ctx.author),description=ut.textto("ginfo-cantview",ctx.author),color=self.bot.ec))
                elif page == 9:
                    if ctx.author.guild_permissions.ban_members or ctx.author.id == 404243934210949120:
                        #ban_user 
                        vbl=ut.textto("ginfo-strlenover",ctx.author)
                        bl = []
                        for i in await ctx.guild.bans():
                            bl.append(f"{i.user},reason:{i.reason}")
                        if len("\n".join(bl)) <= 1024:
                            vbl = "\n".join(bl)
                        await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-banneduser",ctx.author),description=vbl),color=self.bot.ec)
                    else:
                        await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-banneduser",ctx.author),description=ut.textto("ginfo-cantview",ctx.author),color=self.bot.ec))
                elif page == 10:
                    #サーバーのチャンネル
                    e =discord.Embed(title=ut.textto("ginfo-chlist",ctx.author),color=self.bot.ec)
                    for mct,mch in ctx.guild.by_category():
                        chs="\n".join([i.name for i in mch])
                        e.add_field(name=str(mct).replace("None",ut.textto("ginfo-nocate",ctx.author)),value=f"```{chs}```",inline=True)
                    await mp.edit(embed=e)
                elif page == 11:
                    self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
                    gs = self.bot.cursor.fetchone()
                    e =discord.Embed(title="other",color=self.bot.ec)
                    e.add_field(name="owner",value=ctx.guild.owner.mention)
                    e.add_field(name="features",value=f"```{','.join(ctx.guild.features)}```")
                    e.add_field(name=ut.textto("ginfo-sinagprofile",ctx.author),value=ut.textto("ginfo-gprodesc",ctx.author).format(gs["reward"],gs["sendlog"],gs["prefix"],gs["lang"],))
                    await mp.edit(embed=e)
                elif page == 12:
                    e=discord.Embed(title="公開サーバー設定",description=ctx.guild.description or "概要なし",color=self.bot.ec)
                    e.add_field(name="優先言語",value=ctx.guild.preferred_locale)
                    e.add_field(name="ルールチャンネル",value=ctx.guild.rules_channel.mention)
                    await mp.edit(embed=e)
            except:
                await mp.edit(embed=discord.Embed(title=ut.textto("ginfo-anyerror-title",ctx.author),description=ut.textto("ginfo-anyerror-desc",ctx.author).format(traceback.format_exc(0)),color=self.bot.ec))

    @commands.command(name="team_sina-chan")
    async def view_teammember(self,ctx):
        await ctx.send(embed=ut.getEmbed(ut.textto("team_sina-chan",ctx.author),"\n".join([self.bot.get_user(i).name for i in self.bot.team_sina])))

    @commands.command()
    async def vusers(self,ctx):
        self.bot.cursor.execute("select * from users")
        pf = self.bot.cursor.fetchall()
        async with ctx.message.channel.typing():
            vlist = []
            for i in pf:
                if i["sinapartner"] == True:
                    bu = await self.bot.fetch_user(i["id"])
                    vlist.append(f"ユーザー名:{bu},id:{i['id']}")
            embed=discord.Embed(title=f"認証済みアカウント一覧({len(vlist)}名)",description="```{0}```".format('\n'.join(vlist)),color=self.bot.ec)
        await ctx.send(embed=embed)

    @commands.command()
    async def mutual_guilds(self,ctx,uid=None):
        try:
            user=await self.bot.fetch_user(int(uid))
        except:
            user = ctx.author
        mg=[]
        for g in self.bot.guilds:
            if g.get_member(user.id):
                mg+=[f"{g.name}({g.id})"]
        if mg!=[]:
            t="\n".join(mg)
            e=discord.Embed(description=f"```{t}```",color=self.bot.ec)
            e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
            await ctx.send(embed=e)
        else:
            e=discord.Embed(description="なし",color=self.bot.ec)
            e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
            await ctx.send(embed=e)

    @commands.command()
    async def features(self,ctx):
        await ctx.author.send(embed=ut.getEmbed("あなたのfeatures","```{}```".format(",".join(self.bot.features.get(ctx.author.id,["(なし)"])))))

def setup(bot):
    bot.add_cog(info(bot))