# -*- coding: utf-8 -*-

import asyncio
import json
import time
import discord
from discord.ext import commands

# from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL

from googleapiclient.discovery import build

from typing import Optional

from discord import app_commands

import os
import shutil
import re
import random

import m10s_util as ut

import mutagen

"""
上のモジュールをインストールすること！

m10s_music.py
制作:mii-10#3110(Discord)
"""

ytdlopts = {
    'proxy': 'http://proxy1.d1.rspsrv.jp:26020/',
    'format': 'bestaudio/best',
    'outtmpl': 'musicfile/%(id)s',
    'restrictfilenames': True,
    # 'dump_single_json' :  True,
    # 'extract_flat' : True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}


class m10s_music(commands.Cog):
    """music in discord.py"""

    def __init__(self, bot):
        self.bot = bot
        self.youtube = build('youtube', 'v3', developerKey=bot.GAPI_TOKEN)
        self.ytdl = YoutubeDL(ytdlopts)
        if not ("qu" in dir(bot) and "lp" in dir(bot) and "mp" in dir(bot) and "am" in dir(bot)):
            self.bot.qu = {}
            self.bot.lp = {}
            self.bot.mp = {}
            self.bot.am = []
        self.bot.music_panel_update = self.panel_update
        self.bot.music_jump = self.jump_music
        self.bot.add_music_queue = self.add_music_queue

    async def gvinfo(self, url:str, mid=None, dl=False):
        if url.endswith(".mp3"):
            return {
                "id":mid or int(time.time()),
                "webpage_url":url,
                "title":url.split("/")[-1],
                "thumbnail":"",
                "uploader":"None",
                "uploader_url":"",
                "uploader_id":"",
                "extractor":"URL_Stream"
            }
        else:
            loop = self.bot.loop or asyncio.get_event_loop()
            dt = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=dl))
            return dt

    async def gpdate(self, url, mid, requestor, dl=True):
        v = await self.gvinfo(url, mid, dl)
        if v["extractor"] == "URL_Stream":
            async with self.bot.session.get(v["webpage_url"]) as resp:
                resp.raise_for_status()
                with open(f"musicfile/{v['id']}","wb") as f:
                    try:
                        bt = await resp.read()
                        await self.bot.loop.run_in_executor(None, lambda:f.write(bt))
                    finally:
                        resp.close()
            with open(f"musicfile/{v['id']}","rb") as mf:
                f:mutagen.FileType = mutagen.File(mf)
                music_len = getattr(getattr(f,"info",None), "length", -1)
            if not dl:
                loop = self.bot.loop or asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: os.remove(f"musicfile/{v['id']}"))
            return {
                "type": "download" if dl else "stream",
                "stream_url":v["webpage_url"],
                "video_id": v['id'],
                "video_url": v['webpage_url'],
                "video_title": v['title'],
                "video_thumbnail": v['thumbnail'],
                "video_up_name": v["uploader"],
                "video_up_url": v["uploader_id"],
                "video_source": "URL_Stream",
                "duration":music_len,
                "now_position":0,
                "requestor":requestor.id
            }
        else:
            return {
                "type": "download" if dl else "stream",
                "stream_url":v["url"],
                "video_id": v.get('id',""),
                "video_url": v['webpage_url'],
                "video_title": v['title'],
                "video_thumbnail": v.get('thumbnail',""),
                "video_up_name": v.get("uploader",""),
                "video_up_url": v.get("uploader_url",""),
                "video_source": v["extractor"],
                "duration":v.get("duration",-1),
                "now_position":0,
                "requestor":requestor.id
            }

    @commands.hybrid_group(name="music", description="音楽機能です。")
    @ut.runnable_check()
    async def music_group(self, ctx):pass

    @music_group.command(name="join", aliases=["invc"], description="あなたが参加しているVCに接続します。")
    @ut.runnable_check()
    async def join_(self, ctx):
        if ctx.author.voice:
            if ctx.voice_client:
                chname = getattr(ctx.guild.voice_client.channel, "name", "(None)")
                await ctx.send(f"すでに{chname}に接続しています。", ephemeral=True)
            else:
                try:
                    if ctx.author.voice.channel:
                        await ctx.author.voice.channel.connect()
                    else:
                        return await ctx.send("> 接続先のVCを検出できません。", ephemeral=True)
                except asyncio.TimeoutError:
                    await ctx.send("接続のタイムアウト！")
                else:
                    await ctx.send(f"{ctx.voice_client.channel.name}に接続しました。", ephemeral=True)
                    e = discord.Embed(title="思惟奈ちゃんミュージックアクティビティビューアーをお試しください。", description="1年越しにこのアプリケーションが復活しました！\n思惟奈ちゃんの音楽機能を、もっと使いやすく。\nキューの確認や音楽コントロール、RPCへの表示をこれ一つで。\nダウンロードは[こちら](https://support.sina-chan.com/mav-download/ )から。\n※Ver 2.\*.\*のみ動作します。旧バージョン(～v1.\*.\*)をお使いの方は更新をお願いします。")
                    e.set_image(url="https://cdn.discordapp.com/attachments/667351221106901042/997827447858942042/unknown.png")
                    await ctx.channel.send(embed=e)
        else:
            await ctx.send("あなたがこのサーバーでボイスチャンネルに接続していません！",ephemeral=True)

    @music_group.command(name="stop", aliases=["leave"], description="再生をやめ、VCから切断します。")
    @ut.runnable_check()
    async def stop_(self, ctx):
        minfo = ut.get_vmusic(self.bot, ctx.author)
        if ctx.voice_client and ctx.author.voice:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                try:
                    await self.bot.mp[str(ctx.guild.id)].delete()
                except:
                    pass
                try:
                    del self.bot.qu[str(ctx.guild.id)]
                    del self.bot.mp[str(ctx.guild.id)]
                    del self.bot.lp[str(ctx.guild.id)]
                except:
                    pass
                await ctx.voice_client.disconnect()
                await ctx.send("切断しました。", ephemeral=True)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！",ephemeral=True)
        elif minfo and ctx.interaction:
            ch = self.bot.mp[str(minfo["guild"].id)].channel
            try:
                await self.bot.mp[str(minfo["guild"].id)].delete()
            except:
                pass
            try:
                del self.bot.qu[str(minfo["guild"].id)]
                del self.bot.mp[str(minfo["guild"].id)]
                del self.bot.lp[str(minfo["guild"].id)]
            except:
                pass
            await minfo["guild"].voice_client.disconnect()
            try:
                await ch.send(f"> リモート切断\n　{ctx.author}が、他のサーバーから切断しました。", delete_after=5)
            except:
                pass
            await ctx.send(f"> リモート切断\n　{minfo['guild']}のVCから、切断しました。",ephemeral=True)

    @music_group.command(name="pause", description="再生中の曲を一時停止します。")
    @ut.runnable_check()
    async def pause_(self, ctx):
        minfo = ut.get_vmusic(self.bot, ctx.author)
        if ctx.voice_client and ctx.author.voice:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                ctx.voice_client.pause()
                await ctx.send("一時停止しました。ボイスチャットを出ても構いません。")
                await self.panel_update(ctx.guild.id, ctx.voice_client)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！",ephemeral=True)
        elif minfo and ctx.interaction:
            minfo["guild"].voice_client.pause()
            try:
                await self.bot.mp[str(minfo["guild"].id)].channel.send(f"> リモート一時停止\n　{ctx.author}が、他のサーバーから一時停止しました。", delete_after=5)
            except:
                pass
            await ctx.send(f"> リモート一時停止\n　{minfo['guild'].name}で再生中の音楽を一時停止しました。",ephemeral=True)
            await self.panel_update(minfo['guild'].id, minfo['guild'].voice_client)



    @music_group.command(name="play", aliases=["p"], description="楽曲を再生します。")
    @ut.runnable_check()
    @app_commands.describe(text = "楽曲を特定するためのもの(検索ワード/URL/memo:[メモ名]/list:[リスト名]/activity:[ユーザーID] ([]は省略))")
    async def play_(self, ctx:commands.Context, *, text: Optional[str]="", file:Optional[discord.Attachment]=None):
        async with ctx.typing():
            if not ctx.voice_client:
                await ctx.invoke(self.join_)
                if not ctx.voice_client:
                    return
            if ctx.voice_client.is_paused():
                await ctx.send("再生を再開しました。")
                ctx.voice_client.resume()
                await self.panel_update(ctx.guild.id, ctx.voice_client)
                return
            if not file and text == "":
                try:
                    await ctx.send("検索するワード/URLを入力してください")
                    m = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send("タイムアウトしました。")
                    return
                else:
                    text = m.content
            if ctx.interaction:
                await ctx.send("> 処理を開始します。", ephemeral=True)
            await self.add_music_queue(ctx.author, ctx.guild, ctx.channel, ctx.voice_client, ctx.message, text, file)
    
    async def add_music_queue(self, requestor, guild, sender, voice_client, message=None, text="", file=None):
        # try:
        vurls = [] #処理するURL
        vdl = False #ビデオダウンロードを行うかどうか
        c_info = False #再生時の表示情報をカスタム作成するかどうか
        if (text.startswith("<http://") and text.endswith(">")) or (text.startswith("<https://") and text.endswith(">")):
            vurls = [text[1:-1]]
        elif text.startswith("http://") or text.startswith("https://"):
            vurls = [text]
        elif text.startswith("dl:http://") or text.startswith("dl:https://"):
            vdl = True
            vurls = [text[3:]]
        elif text.startswith("list:"):
            pf = await self.bot.cursor.fetchone(
                "select * from users where id=%s", (requestor.id,))
            listname = text[5:]
            playlist = json.loads(pf["music_list"]).get(listname, None)
            vurls = []
            if playlist:
                for i in playlist:
                    if (i.startswith("<http://") and i.endswith(">")) or (i.startswith("<https://") and i.endswith(">")):
                        vurls.append(i[1:-1])
                    elif i.startswith("http://") or i.startswith("https://"):
                        vurls.append(i)
            else:
                await sender.send("> 音楽再生\n　該当名称のプレイリストが見つかりません。\n　`/music playlist_manager`で管理できます。")
                return
        elif text.startswith("memo:"):
            pf = await self.bot.cursor.fetchone(
                "select * from users where id=%s", (requestor.id,))
            mn = text[5:]
            memos = json.loads(pf["memo"])
            vurls = []
            if memos is not None and memos.get(mn,None) is not None:
                for i in memos[mn].split("\n"):
                    if (i.startswith("<http://") and i.endswith(">")) or (i.startswith("<https://") and i.endswith(">")):
                        vurls.append(i[1:-1])
                    elif i.startswith("http://") or i.startswith("https://"):
                        vurls.append(i)
            else:
                await sender.send("> 音楽再生\n　該当名称のメモが見つかりません。")
                return
        elif text.startswith("activity:"):
            tar = guild.get_member(int(text[9:])) or guild.get_member(requestor.id)
            spac = [i for i in tar.activities if i.name == "Spotify"]

            if spac:
                title = getattr(spac[0], "title", None) or spac[0].details
                artist = getattr(spac[0], "artist", None) or spac[0].state
                search_response = self.youtube.search().list(
                    part='id',
                    q=f"{title} {artist}",
                    type='video'
                ).execute()
                vid = search_response['items'][0]['id']['videoId']
                if vid:
                    vurls = [f"https://www.youtube.com/watch?v={vid}"]
                else:
                    return await sender.send("動画が見つかりませんでした。")
            else:
                return await sender.send("プレイ中のActivityがSpotifyではありません。")
        elif file:
            vid = getattr(message,"id", int(time.time()))
            c_info = True
            await file.save(f"musicfile/{vid}")
            with open(f"musicfile/{vid}","rb") as mf:
                f:mutagen.FileType = mutagen.File(mf)
                music_len = getattr(getattr(f,"info",None), "length", -1)
            vinfo = {
                "type": "download",
                "stream_url":str(file.url),
                "video_id": vid,
                "video_url": "",
                "video_title": file.filename,
                "video_thumbnail": "",
                "video_up_name": f"{requestor}({requestor.id})",
                "video_up_url": f"https://discord.com/users/{requestor.id}",
                "video_source": "Direct Upload",
                "duration": music_len,
                "now_position": 0,
                "requestor":requestor.id
            }
        else:
            try:
                search_response = self.youtube.search().list(
                    part='id',
                    q=text,
                    type='video'
                ).execute()
                vid = search_response['items'][0]['id']['videoId']
                if vid:
                    vurls = [f"https://www.youtube.com/watch?v={vid}"]
                else:
                    return await sender.send("動画が見つかりませんでした。")
            except:
                return await sender.send("> 検索エラー\n　現在検索ワードを用いた検索ができません。URLをお試しください。")
        if not c_info:
            if vurls == []:
                await sender.send("再生できる楽曲がありません。処理を中止します。")
                return
            sended = False
            for vurl in vurls:
                vinfo = await self.gvinfo(vurl, getattr(message, "id", None), False)
                if vinfo["extractor"] in ["youtube"]:
                    if not("unlock_ytmusic" in self.bot.features[0]):
                        await sender.send("この動画ソースは、Discordの規約変更の影響でサポートが終了しました。\n各個人でダウンロード→ファイルアップロードを経由して再生することは可能ですが、自己責任となります。")
                        return
                        # await sender.send("この動画ソースは、Discordの規約変更の影響で近日中にサポートが打ち切られます。")
                if vinfo.get("_type", "") == "playlist":
                    tks = []
                    for c in vinfo["entries"]:
                        self.bot.am.append(c["id"])
                        tks.append(self.gpdate(
                            c["webpage_url"], getattr(message,"id", None), requestor, False if c["id"] in self.bot.am else vdl))
                    iqlt = [i for i in await asyncio.gather(*tks) if i]
                    if self.bot.qu.get(str(guild.id), None):
                        if not sended:
                            await sender.send(f"キューにプレイリスト内の動画{len(iqlt)}本を追加します。")
                            sended = True
                        self.bot.qu[str(guild.id)] = self.bot.qu[str(
                            guild.id)] + iqlt
                        await self.panel_update(guild.id, voice_client)
                    else:
                        if not sended:
                            await sender.send(f"プレイリストより、{len(iqlt)}本の再生を開始します。")
                            sended = True
                        self.bot.qu[str(guild.id)] = iqlt
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(guild, sender))
                else:
                    self.bot.am.append(vinfo["id"])
                    iqim = await self.gpdate(vurl, getattr(message,"id", None), requestor, vdl)
                    if self.bot.qu.get(str(guild.id), None):
                        if not sended:
                            await sender.send(f"`{iqim['video_title']}`をキューに追加します。")
                            sended = True
                        self.bot.qu[str(sender.guild.id)] = self.bot.qu[str(
                            sender.guild.id)] + [iqim]
                        await self.panel_update(guild.id, voice_client)
                    else:
                        if not sended:
                            await sender.send(f"`{iqim['video_title']}`の再生を開始します。")
                            sended = True
                        self.bot.qu[str(guild.id)] = [iqim]
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(guild, sender))
        else:
            sended = False
            self.bot.am.append(vinfo["video_id"])
            if self.bot.qu.get(str(guild.id), None):
                if not sended:
                    await sender.send(f"`{vinfo['video_title']}`をキューに追加します。")
                    sended = True
                self.bot.qu[str(guild.id)] = self.bot.qu[str(
                    guild.id)] + [vinfo]
                await self.panel_update(guild.id, voice_client)
            else:
                if not sended:
                    await sender.send(f"`{vinfo['video_title']}`の再生を開始します。")
                    sended = True
                self.bot.qu[str(guild.id)] = [vinfo]
                await asyncio.sleep(0.3)
                self.bot.loop.create_task(self.mplay(guild,sender))
        #except:
            #import traceback
            #await sender.send(f"> traceback\n```{traceback.format_exc(2)}```")

    async def mplay(self, guild, sender, vl=0.5):
        v = None
        if not self.bot.lp.get(str(guild.id), None):
            self.bot.lp[str(guild.id)] = False
        if not self.bot.mp.get(str(guild.id), None):
            ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル", color=self.bot.ec)
            ebd.add_field(name="再生中の曲:", value="未読み込み")
            ebd.add_field(name="次の曲:", value="未読み込み")
            ebd.add_field(name="ループ:", value="未読み込み")
            ebd.add_field(name="ボリューム:", value="未読み込み")
            m = await sender.send(embed=ebd)
            self.bot.mp[str(guild.id)] = m
            await m.add_reaction("▶")
            await m.add_reaction("⏸")
            await m.add_reaction("⏹")
            await m.add_reaction("⏭")
            await m.add_reaction("🔁")
            await m.add_reaction("🔀")
            await m.add_reaction("🔼")
            await m.add_reaction("🔽")
            await m.add_reaction("⬇")
            try:
                await m.pin()
            except:
                pass
        if isinstance(guild.me.voice.channel, discord.StageChannel):
            try:
                await guild.me.edit(suppress=False)
                await sender.send("> ステージチャンネルのため、自動的にスピーカーに移動しました。")
            except:
                await sender.send("> ステージチャンネルのため、音楽を再生するためにはスピーカーに移動させる必要があります。")
        while self.bot.qu.get(str(guild.id), None):
            self.bot.qu[str(guild.id)][0]["now_position"] = 0
            if not guild.voice_client.is_connected():
                reconnect_ch = guild.voice_client.channel
                await guild.voice_client.cleanup()
                await reconnect_ch.connect()
            if self.bot.qu[str(guild.id)][0]["type"] == "download":
                guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                f'musicfile/{self.bot.qu[str(guild.id)][0]["video_id"]}'), volume=v or vl))
            else:
                guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                self.bot.qu[str(guild.id)][0]["stream_url"], before_options="-reconnect 1"), volume=v or vl))
            await self.panel_update(guild.id, guild.voice_client)
            try:
                while guild.voice_client and guild.voice_client.is_playing() or guild.voice_client.is_paused():
                    await asyncio.sleep(1)
                    if guild.voice_client.is_playing():
                        try:
                            self.bot.qu[str(guild.id)][0]["now_position"] += 1
                        except:
                            pass
                    v = guild.voice_client.source.volume
            except AttributeError:
                pass
            can_delete = True
            if self.bot.lp.get(str(guild.id),None):
                can_delete = False
                self.bot.qu[str(guild.id)].append(self.bot.qu[str(guild.id)][0])
            else:
                self.bot.am.remove(self.bot.qu[str(guild.id)][0]["video_id"])
            poped_item = self.bot.qu[str(guild.id)].pop(0)
            if can_delete and (not poped_item["video_id"] in self.bot.am) and poped_item["type"] == "download":
                loop = self.bot.loop or asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: os.remove(f'musicfile/{poped_item["video_id"]}'))
        try:
            await self.bot.mp[str(guild.id)].delete()
        except:
            pass
        try:
            del self.bot.qu[str(guild.id)]
            del self.bot.mp[str(guild.id)]
            del self.bot.lp[str(guild.id)]
        except:
            pass
        await guild.voice_client.disconnect()
        await sender.send("キューが空になったため、退出しました。")

    @music_group.command(description="曲をスキップします。")
    @ut.runnable_check()
    async def skip(self, ctx:commands.Context, index:Optional[int]=1):
        minfo = ut.get_vmusic(self.bot, ctx.author)
        if ctx.author.voice and ctx.voice_client and ctx.voice_client.is_playing():
            if ctx.voice_client.channel == ctx.author.voice.channel:
                await self.jump_music(index, ctx.guild.id, ctx.voice_client)
                await ctx.send("曲をスキップしました。",
                ephemeral = True)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！",ephemeral=True)
        elif minfo and ctx.interaction:
            await self.jump_music(index, str(minfo["guild"].id), minfo["guild"].voice_client)
            try:
                await self.bot.mp[str(minfo["guild"].id)].channel.send(f"> リモートスキップ\n　{ctx.author}が、他のサーバーからスキップしました。", delete_after=5)
            except:
                pass
            await ctx.send(f"> リモートスキップ\n　{minfo['guild']}のVCの曲をスキップしました。", ephemeral=True)

    @music_group.command(name="volume",aliases=["chvol","vol"], description="ボリュームを変更します。")
    @ut.runnable_check()
    @app_commands.describe(vol="調整する音量(%)")
    async def chvol(self, ctx, vol: float):
        minfo = ut.get_vmusic(self.bot, ctx.author)
        if ctx.author.voice and ctx.voice_client and ctx.voice_client.is_playing():
            if ctx.voice_client.channel == ctx.author.voice.channel:
                ctx.voice_client.source.volume = vol/100.0
                await ctx.send("ボリュームを調節しました。",ephemeral = True)
                await self.panel_update(ctx.guild.id, ctx.voice_client)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！", ephemeral=True)
        elif minfo and ctx.interaction:
            minfo["guild"].voice_client.source.volume = vol/100.0
            try:
                await self.bot.mp[str(minfo["guild"].id)].channel.send(f"> リモート音量調整\n　{ctx.author}が、他のサーバーから音量調整しました。", delete_after=5)
            except:
                pass
            await ctx.send(f"> リモート音量調整\n　{minfo['guild']}のVCの音量を変更しました。", ephemeral=True)

    @music_group.command(aliases=["np"], description="再生中楽曲について表示します。")
    @ut.runnable_check()
    async def playingmusic(self, ctx):
        minfo = ut.get_vmusic(self.bot, ctx.author)
        if ctx.author.voice and ctx.voice_client and ctx.voice_client.is_playing():
            if ctx.voice_client.channel == ctx.author.voice.channel:
                e = discord.Embed(
                    title="再生中の曲", description=f'[{self.bot.qu[str(ctx.guild.id)][0]["video_title"]}]({self.bot.qu[str(ctx.guild.id)][0]["video_url"]})\nアップロードチャンネル:[{self.bot.qu[str(ctx.guild.id)][0]["video_up_name"]}]({self.bot.qu[str(ctx.guild.id)][0]["video_up_url"]})\nソース:{self.bot.qu[str(ctx.guild.id)][0]["video_source"]}')
                e.set_thumbnail(
                    url=self.bot.qu[str(ctx.guild.id)][0]["video_thumbnail"])
                await ctx.send("> このサーバーで現在再生している楽曲", embed=e, ephemeral=True)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！",ephemeral=True)
        elif minfo and ctx.interaction and minfo["guild"].voice_client and minfo["guild"].voice_client.is_playing():
            e = discord.Embed(
                title="再生中の曲", description=f'[{self.bot.qu[str(minfo["guild"].id)][0]["video_title"]}]({self.bot.qu[str(minfo["guild"].id)][0]["video_url"]})\nアップロードチャンネル:[{self.bot.qu[str(minfo["guild"].id)][0]["video_up_name"]}]({self.bot.qu[str(minfo["guild"].id)][0]["video_up_url"]})\nソース:{self.bot.qu[str(minfo["guild"].id)][0]["video_source"]}')
            e.set_thumbnail(
                url=self.bot.qu[str(minfo["guild"].id)][0]["video_thumbnail"])
            await ctx.send(f"> リモート確認\n> {minfo['guild'].name}で現在再生している楽曲", embed=e, ephemeral=True)
        else:
            await ctx.send("再生中の曲はありません。", ephemeral = True)

    @music_group.command(aliases=["plist", "view_q"], description="楽曲キューを表示します。")
    @ut.runnable_check()
    @app_commands.describe(pg="始めに表示するページ(1ページ当たり5項目)")
    async def queue(self, ctx, pg:Optional[int]=1):
        if ctx.voice_client is None:
            return await ctx.send("ボイスチャンネルに参加していません。")
        elif self.bot.qu.get(str(ctx.guild.id),[]):
            if ctx.voice_client.channel == ctx.author.voice.channel:
                page = pg-1
                pls = [self.bot.qu[str(ctx.guild.id)][5*i:5*(i+1)]
                    for i in range(int(len(self.bot.qu[str(ctx.guild.id)])/5)+1)]
                e = discord.Embed(
                    title="キューの中身", description=f"全{len(self.bot.qu[str(ctx.guild.id)])}曲")
                for i in pls[page]:
                    e.add_field(
                        name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}/{i["type"]}\n追加メンバー:{self.bot.get_user(i["requestor"]).mention}')
                e.set_footer(text=f"page:{page+1}/{len(pls)}")
                msg = await ctx.send(embed=e)
                await msg.add_reaction(self.bot.create_emoji_str("s_move_left",653161518195671041))  # ←
                await msg.add_reaction(self.bot.create_emoji_str('s_move_right',653161518170505216))  # →
                while True:
                    try:
                        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
                    except:
                        break
                    try:
                        await msg.remove_reaction(r, u)
                    except:
                        pass
                    if str(r) == str(self.bot.create_emoji_str('s_move_right',653161518170505216)):  # →
                        if page == len(pls)-1:
                            page = 0
                        else:
                            page += 1
                    elif str(r) == str(self.bot.create_emoji_str("s_move_left",653161518195671041)):  # ←
                        if page == 0:
                            page = len(pls)-1
                        else:
                            page -= 1
                    e = discord.Embed(
                        title="キューの中身", description=f"全{len(self.bot.qu[str(ctx.guild.id)])}曲")
                    for i in pls[page]:
                        e.add_field(
                            name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}/{i["type"]}\n追加メンバー:{self.bot.get_user(i["requestor"]).mention}')
                    e.set_footer(text=f"page:{page+1}/{len(pls)}")
                    await msg.edit(embed=e)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！",ephemeral=True)
        else:
            await ctx.send("現在キューには何もありません。")

    @music_group.command(aliases=["loop", "repeat"], description="ループ状況の確認や変更ができます。")
    @ut.runnable_check()
    @app_commands.describe(is_enable="ループを有効にするかどうか")
    async def loop_q(self, ctx, is_enable:Optional[bool]=None):
        minfo = ut.get_vmusic(self.bot, ctx.author)
        torf = is_enable
        if ctx.voice_client and ctx.author.voice:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                if torf is None:
                    await ctx.send(f"今のキューのループ状態:{self.bot.lp[str(ctx.guild.id)]}",ephemeral=True)
                else:
                    self.bot.lp[str(ctx.guild.id)] = torf
                    await ctx.send(f"きりかえました。\n今のキューのループ状態:{self.bot.lp[str(ctx.guild.id)]}",ephemeral=True)
                    await self.panel_update(ctx.guild.id, ctx.voice_client)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！",ephemeral=True)
        elif minfo and ctx.interaction:
            if torf is None:
                await ctx.send(f"今のキューのループ状態:{self.bot.lp[str(minfo['guild'].id)]}",ephemeral=True)
            else:
                self.bot.lp[str(minfo["guild"].id)] = torf
                await self.panel_update(minfo["guild"].id, minfo["guild"].voice_client)
                try:
                    await self.bot.mp[str(minfo["guild"].id)].channel.send(f"> リモートループ切替\n　{ctx.author}が、他のサーバーからループ状況を切替しました。", delete_after=5)
                except:
                    pass
                await ctx.send(f"> リモートループ切替\n　{minfo['guild'].name}でループ状況を切替しました。",ephemeral=True)

    @music_group.command(name="panel_update", aliases=["pupdate"], description="楽曲パネルの更新/再生成を行います。")
    @ut.runnable_check()
    async def pupdate(self, ctx):
        await self.panel_update(ctx.guild.id, ctx.voice_client, True)
        await ctx.send("パネルを強制的に更新しました。", )

    async def panel_update(self, guild_id, voice_client, regene=False):
        ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル",
                            description=f"キューの曲数:{len(self.bot.qu[str(guild_id)])}曲", color=self.bot.ec)
        ebd.set_footer(text="⬇:パネルを下に持ってくる")
        if voice_client.is_paused():
            ebd.add_field(name="現在一時停止中",
                          value="再開には`s-play`か▶リアクション", inline=False)
        ebd.add_field(
            name="再生中の曲:", value=f"[{self.bot.qu[str(guild_id)][0]['video_title']}]({self.bot.qu[str(guild_id)][0]['video_url']})", inline=False)
        if len(self.bot.qu[str(guild_id)]) > 1:
            ebd.add_field(
                name="次の曲:", value=f"[{self.bot.qu[str(guild_id)][1]['video_title']}]({self.bot.qu[str(guild_id)][1]['video_url']})", inline=False)
        elif self.bot.lp[str(guild_id)]:
            ebd.add_field(
                name="次の曲:", value=f"[{self.bot.qu[str(guild_id)][0]['video_title']}]({self.bot.qu[str(guild_id)][0]['video_url']})", inline=False)
        else:
            ebd.add_field(name="次の曲:", value=f"再生終了", inline=False)
        ebd.add_field(name="ループ:", value=self.bot.lp[str(guild_id)])
        try:
            ebd.add_field(name="ボリューム:", value=int(
               voice_client.source.volume*100))
        except:
            ebd.add_field(name="ボリューム:", value="現在アクセス不可")
        ebd.set_thumbnail(
            url=self.bot.qu[str(guild_id)][0]["video_thumbnail"])
        try:
            await self.bot.mp[str(guild_id)].edit(embed=ebd)
        except discord.NotFound:
            if regene:
                self.bot.mp[str(guild_id)] = await self.bot.mp[str(guild_id)].channel.send(embed=ebd)
        except AttributeError:
            # パネルメッセージが、まだない状態の可能性があるため
            pass


    @music_group.command(name="shuffle", description="キューの中身をシャッフルします。")
    @ut.runnable_check()
    async def shuffle_(self, ctx):
        minfo = ut.get_vmusic(self.bot, ctx.author)
        if ctx.voice_client and ctx.author.voice:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                if self.bot.qu.get(str(ctx.guild.id), None) is not None and len(self.bot.qu[str(ctx.guild.id)]) > 2:
                    tmplist = self.bot.qu[str(ctx.guild.id)][1:]
                    random.shuffle(tmplist)
                    self.bot.qu[str(ctx.guild.id)] = [self.bot.qu[str(ctx.guild.id)][0]] + tmplist
                    await self.panel_update(ctx.guild.id, ctx.voice_client)
                    await ctx.send("> シャッフル\n　シャッフルしました。再生パネルや`s-view_q`でご確認ください。",ephemeral=True)
                else:
                    await ctx.send("> シャッフルエラー\n　シャッフルに必要要件を満たしていません。(VCで音楽再生中で、3曲以上キューに入っている)",ephemeral=True)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！", ephemeral=True)
        elif minfo and ctx.interaction:
            if self.bot.qu.get(str(minfo["guild"].id), None) is not None and len(self.bot.qu[str(minfo["guild"].id)]) > 2:
                tmplist = self.bot.qu[str(minfo["guild"].id)][1:]
                random.shuffle(tmplist)
                self.bot.qu[str(minfo["guild"].id)] = [self.bot.qu[str(minfo["guild"].id)][0]] + tmplist
                await self.panel_update(minfo["guild"].id, minfo["guild"].voice_client)
                try:
                    await self.bot.mp[str(minfo["guild"].id)].channel.send(f"> リモートシャッフル\n　{ctx.author}が、他のサーバーからキューをシャッフルしました。", delete_after=5)
                except:
                    pass
                await ctx.send(f"> リモートシャッフル\n　{minfo['guild'].name}でキューをシャッフルしました。", ephemeral=True)
            else:
                await ctx.send(f"> リモートシャッフルエラー\n　{minfo['guild'].name}で、シャッフルに必要要件を満たしていません。(VCで音楽再生中で、3曲以上キューに入っている)", ephemeral=True)

    @music_group.command(name="move_panel", description="音楽パネルをほかのチャンネルに移動させます。")
    @ut.runnable_check()
    @app_commands.describe(move_to="移動先チャンネル")
    async def move_panel(self, ctx, move_to:discord.TextChannel):
        ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル", color=self.bot.ec)
        ebd.add_field(name="再生中の曲:", value="未読み込み")
        ebd.add_field(name="次の曲:", value="未読み込み")
        ebd.add_field(name="ループ:", value="未読み込み")
        ebd.add_field(name="ボリューム:", value="未読み込み")
        m = await move_to.send(embed=ebd)
        await self.bot.mp[str(ctx.guild.id)].delete()
        self.bot.mp[str(ctx.guild.id)] = m
        await m.add_reaction("▶")
        await m.add_reaction("⏸")
        await m.add_reaction("⏹")
        await m.add_reaction("⏭")
        await m.add_reaction("🔁")
        await m.add_reaction("🔀")
        await m.add_reaction("🔼")
        await m.add_reaction("🔽")
        await m.add_reaction("⬇")
        try:
            await m.pin()
        except:
            pass
        await self.panel_update(ctx.guild.id, ctx.voice_client)
        await ctx.send(f"> 音楽再生パネルの移動\n　{move_to.mention}に移動しました。")
    
    @music_group.command(name="remove", description="キューの特定番目から項目を取り除きます。")
    @ut.runnable_check()
    @app_commands.describe(index="取り除く番目")
    async def _remove(self, ctx, index:int):
        minfo = ut.get_vmusic(self.bot, ctx.author)
        if ctx.voice_client and ctx.author.voice:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                if index > 1 and index <= len(self.bot.qu.get(str(ctx.guild.id),[])):
                    self.bot.qu[str(ctx.guild.id)].pop(index-1)
                    await ctx.send(f"> キューの{index}番目の項目を取り除きました！", ephemeral=True)
                    await self.panel_update(ctx.guild.id, ctx.voice_client)
                else:
                    await ctx.send(f"> エラー\n　その項目は取り除くことができません！", ephemeral=True)
            else:
                await ctx.send("現在再生中のVCは、あなたが参加しているVCではありません！", ephemeral=True)
        elif minfo and ctx.interaction:
            if index > 1 and index <= len(self.bot.qu.get(str(minfo["guild"].id), [])):
                self.bot.qu[str(minfo["guild"].id)].pop(index-1)
                await self.panel_update(minfo["guild"].id, minfo["guild"].voice_client)
                try:
                    await self.bot.mp[str(minfo["guild"].id)].channel.send(f"> リモートremove\n　{ctx.author}が、他のサーバーから項目を取り除きました。", delete_after=5)
                except:
                    pass
                await ctx.send(f">リモートremove\n　キューの{index}番目の項目を取り除きました！", ephemeral=True)
            else:
                await ctx.send(f"> エラー\n　その項目は取り除くことができません！", ephemeral=True)

    async def jump_music(self, move_at:int, guild_id:int, voice_client:discord.VoiceClient):
        if move_at < 0:
            for _ in range(move_at + 1):
                item = self.bot.qu.get(str(guild_id),[]).pop()
                self.bot.qu.get(str(guild_id),[]).insert(0,item)
        elif move_at > 0:
            for _ in range(move_at - 1):
                item = self.bot.qu.get(str(guild_id),[]).pop(0)
                self.bot.qu.get(str(guild_id),[]).append(item)
        voice_client.stop()


    @music_group.group(name="playlist_manager", description="音楽再生リストを管理できます。")
    @ut.runnable_check()
    async def plist(self, ctx:commands.Context):
        pass

    @plist.command(name="check", description="すべてのプレイリストや、その中身を確認できます。")
    @ut.runnable_check()
    @app_commands.describe(name="プレイリスト名")
    async def check_list(self, ctx:commands.Context, name:Optional[str]):
        pf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        lists:dict = json.loads(pf["music_list"])
        if name:
            if lists.get(name,None):
                rt = '\n'
                await ctx.send(f"> プレイリスト`{name}`:\n```\n{rt.join(lists[name])}```", ephemeral = True)
            else:
                await ctx.send(f"> その名前のリストは存在しません。", ephemeral = True)
        else:
            await ctx.send(f"> プレイリスト一覧:\n```\n{','.join([k for k in lists.keys()])}```", ephemeral = True)

    @plist.command(name="add", description="指定されたプレイリスト(存在しない場合は作成されます。)に、URLを追加できます。")
    @ut.runnable_check()
    @app_commands.describe(name="プレイリスト名")
    @app_commands.describe(url="追加するURL")
    async def add_list(self, ctx:commands.Context, name:str, url:str):
        URL = url
        pf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        lists:dict = json.loads(pf["music_list"])
        if lists.get(name,None):
            lists[name].append(URL)
            await self.bot.cursor.execute("UPDATE users SET music_list = %s WHERE id = %s", (json.dumps(lists), ctx.author.id))
            await ctx.send(f"> プレイリスト`{name}`に、`{URL}`を追加しました！", ephemeral = True)
        else:
            lists[name] = [URL]
            await self.bot.cursor.execute("UPDATE users SET music_list = %s WHERE id = %s", (json.dumps(lists), ctx.author.id))
            await ctx.send(f"> プレイリスト`{name}`を作成し、`{URL}`を追加しました！\n　再生時には、`/music play list:{name}`と指定してください。", ephemeral = True)

    @plist.command(name="remove", description="指定されたプレイリストから、項目を取り除きます。")
    @ut.runnable_check()
    @app_commands.describe(name="プレイリスト名")
    @app_commands.describe(index="削除する項目の番目")
    async def remove_list(self, ctx:commands.Context, name:str, index:int):
        pf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        lists:dict = json.loads(pf["music_list"])
        if lists.get(name,None):
            lists[name].pop(index-1)
            await self.bot.cursor.execute("UPDATE users SET music_list = %s WHERE id = %s", (json.dumps(lists), ctx.author.id))
            await ctx.send(f"> プレイリスト`{name}`の、`{index}`番目を削除しました。", ephemeral = True)
            
        else:
            await ctx.send(f"> プレイリスト`{name}`は、存在しません。", ephemeral = True)

    @plist.command(name="delete", description="指定されたプレイリストを削除します。")
    @ut.runnable_check()
    @app_commands.describe(name="プレイリスト名")
    async def delete_list(self, ctx:commands.Context, name:str):
        pf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        lists:dict = json.loads(pf["music_list"])
        if lists.get(name,None):
            del lists[name]
            await self.bot.cursor.execute("UPDATE users SET music_list = %s WHERE id = %s", (json.dumps(lists), ctx.author.id))
            await ctx.send(f"> プレイリスト`{name}`を削除しました。", ephemeral = True)
        else:
            await ctx.send(f"> プレイリスト`{name}`は、存在しません。", ephemeral = True)

    @plist.command(name="get_queue", description="現在の再生キューを、そのまま新しいプレイリストにできます。")
    @ut.runnable_check()
    @app_commands.describe(name="プレイリスト名")
    async def add_queue_to_list(self, ctx:commands.Context, name:str):
        if ctx.author.voice and self.bot.qu.get(str(ctx.guild.id),None):
            pf = await self.bot.cursor.fetchone(
                "select * from users where id=%s", (ctx.author.id,))
            lists:dict = json.loads(pf["music_list"])
            lists[name] = [i["video_url"] for i in self.bot.qu[str(ctx.guild.id)]]
            await self.bot.cursor.execute("UPDATE users SET music_list = %s WHERE id = %s", (json.dumps(lists), ctx.author.id))
            await ctx.send(f"> 現在のキューをもとに、プレイリスト`{name}`を作成しました。\n　再生時には、`/music play list:{name}`と指定してください。", ephemeral = True)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, pr):
        if self.bot.mp.get(str(pr.member.guild.id), None) is None:
            return
        if pr.user_id != pr.member.guild.me.id and self.bot.mp[str(pr.guild_id)].id == pr.message_id:
            ch = self.bot.get_channel(pr.channel_id)
            msg = await ch.fetch_message(pr.message_id)
            try:
                await msg.remove_reaction(pr.emoji, pr.member)
            except:
                pass
            if not pr.member.voice:
                return
            msg.author = pr.member
            ctx = await self.bot.get_context(msg)
            r = pr
            u = pr.member
            if str(r.emoji) == "▶":
                await ctx.invoke(self.play_)
            elif str(r.emoji) == "⏸":
                await ctx.invoke(self.pause_)
            elif str(r.emoji) == "⏹":
                await ctx.invoke(self.stop_)
            elif str(r.emoji) == "⏭":
                await ctx.invoke(self.skip)
            elif str(r.emoji) == "🔁":
                if self.bot.lp[str(u.guild.id)]:
                    await ctx.invoke(self.loop_q, False)
                else:
                    await ctx.invoke(self.loop_q, True)
            elif str(r.emoji) == "🔀":
                await ctx.invoke(self.shuffle_)
            elif str(r.emoji) == "🔼":
                await ctx.invoke(self.chvol, int(ctx.voice_client.source.volume*100+10))
            elif str(r.emoji) == "🔽":
                await ctx.invoke(self.chvol, int(ctx.voice_client.source.volume*100-10))
            elif str(r.emoji) == "⬇":
                op = self.bot.mp[str(u.guild.id)]
                self.bot.mp[str(u.guild.id)] = await msg.channel.send(embed=self.bot.mp[str(u.guild.id)].embeds[0])
                await op.delete()
                m = self.bot.mp[str(u.guild.id)]
                await m.add_reaction("▶")
                await m.add_reaction("⏸")
                await m.add_reaction("⏹")
                await m.add_reaction("⏭")
                await m.add_reaction("🔁")
                await m.add_reaction("🔀")
                await m.add_reaction("🔼")
                await m.add_reaction("🔽")
                await m.add_reaction("⬇")
                try:
                    await m.pin()
                except:
                    pass
                await self.panel_update(u.guild.id, u.guild.voice_client)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.me.voice and [i for i in member.guild.me.voice.channel.members if not i.bot] == []:
            try:
                if member.guild.voice_client.is_paused():
                    return
            except:
                pass
            await member.guild.voice_client.disconnect()
            try:
                await self.bot.mp[str(member.guild.id)].channel.send("参加者がいなくなったため、自動退出を行いました。")
                try:
                    await self.bot.mp[str(member.guild.id)].delete()
                except:
                    await self.bot.mp[str(member.guild.id)].channel.send("操作パネルを削除できませんでした。")
                del self.bot.qu[str(member.guild.id)]
                del self.bot.mp[str(member.guild.id)]
                del self.bot.lp[str(member.guild.id)]
            except:
                pass
        try:
            if self.bot.voice_clients == []:
                shutil.rmtree("musicfile/")
                os.makedirs('musicfile/', exist_ok=True)
        except:
            pass


async def setup(bot):
    await bot.add_cog(m10s_music(bot))
