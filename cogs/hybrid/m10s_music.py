# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

from apiclient.discovery import build

from typing import Optional

from discord import app_commands

import os
import shutil
import re
import random

import m10s_util as ut

"""
上のモジュールをインストールすること！

m10s_music.py
制作:mii-10#3110(Discord)
"""

ytdlopts = {
    'proxy': 'http://proxy-sve1.d.rspnet.jp:26020/',
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

    async def gvinfo(self, ctx, url:str, dl=False):
        if url.endswith(".mp3"):
            return {
                "id":ctx.message.id,
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

    async def gpdate(self, url, ctx, dl=True, utype="Youtube"):
        v = await self.gvinfo(ctx, url, dl)
        if utype == "Youtube":
            return {
                "type": "download" if dl else "stream",
                "stream_url":v["url"],
                "video_id": v['id'],
                "video_url": v['webpage_url'],
                "video_title": v['title'],
                "video_thumbnail": v['thumbnail'],
                "video_up_name": v["uploader"],
                "video_up_url": v["uploader_url"],
                "video_source": "YouTube",
                "requester":ctx.author.id
            }
        elif utype == "niconico":
            return {
                "type": "download" if dl else "stream",
                "stream_url":v["url"],
                "video_id": v['id'],
                "video_url": v['webpage_url'],
                "video_title": v['title'],
                "video_thumbnail": v['thumbnail'],
                "video_up_name": v["uploader"],
                "video_up_url": "https://www.nicovideo.jp/user/"+v["uploader_id"],
                "video_source": "niconico",
                "requester":ctx.author.id
            }
        elif utype == "soundcloud":
            return {
                "type": "download" if dl else "stream",
                "stream_url":v["url"],
                "video_id": v['id'],
                "video_url": v['webpage_url'],
                "video_title": v['title'],
                "video_thumbnail": v['thumbnail'],
                "video_up_name": v["uploader"],
                "video_up_url": re.match(r"(https://soundcloud\.com/.+?/)", v['webpage_url']).group(0),
                "video_source": "SoundCloud",
                "requester":ctx.author.id
            }
        elif utype == "URL_Stream":
            if dl:
                async with self.bot.session.get(v["webpage_url"]) as resp:
                    resp.raise_for_status()
                    with open(f"musicfile/{v['id']}","wb") as f:
                        try:
                            bt = await resp.read()
                            await self.bot.loop.run_in_executor(None, lambda:f.write(bt))
                        finally:
                            resp.close()
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
                "requester":ctx.author.id
            }

    @commands.hybrid_group(name="music", description="音楽機能です。")
    async def music_group(self, ctx):pass

    @music_group.command(name="join", aliases=["invc"],description="あなたが参加しているVCに接続します。")
    async def join_(self, ctx):
        if ctx.author.voice:
            if ctx.voice_client:
                    await ctx.send(f"すでに{ctx.guild.voice_client.channel.name}に接続しています。", ephemeral=True)
            else:
                try:
                    await ctx.author.voice.channel.connect()
                except asyncio.TimeoutError:
                    await ctx.send("接続のタイムアウト！")
                else:
                    await ctx.send(f"{ctx.voice_client.channel.name}に接続しました。", ephemeral=True)
        else:
            await ctx.send("あなたがボイスチャンネルに接続していません！")

    @music_group.command(name="stop", aliases=["leave"], description="再生をやめ、VCから切断します。")
    async def stop_(self, ctx):
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
                await ctx.send("切断しました。",ephemeral=True)

    @music_group.command(name="pause", description="再生中の曲を一時停止します。")
    async def pause_(self, ctx):
        if ctx.voice_client and ctx.author.voice:
            ctx.voice_client.pause()
            await ctx.send("一時停止しました。ボイスチャットを出ても構いません。")
            await self.panel_update(ctx.guild.id, ctx.voice_client)

    @music_group.command(name="play", aliases=["p"], description="楽曲を再生します。")
    @app_commands.describe(text = "楽曲を特定するためのもの(検索ワード/URL/memo:[メモ名]/activity:[ユーザーID] ([]は省略))")
    async def play_(self, ctx, *, text: Optional[str]=""):
        if not ctx.voice_client:
            await ctx.invoke(self.join_)
            if not ctx.voice_client:
                return
        if ctx.voice_client.is_paused():
            await ctx.send("再生を再開しました。")
            ctx.voice_client.resume()
            await self.panel_update(ctx.guild.id, ctx.voice_client)
            return
        if text == "":
            try:
                m = await ut.wait_message_return(ctx, "検索するワード または 再生するURLを送信してください。", ctx.channel)
            except asyncio.TimeoutError:
                await ctx.send("タイムアウトしました。")
                return
            else:
                text = m.content
        async with ctx.typing():
            #try:
            vurls = [] #処理するURL
            vdl = False #ビデオダウンロードを行うかどうか
            c_info = False #再生時の表示情報をカスタム作成するかどうか
            if (text.startswith("<http://") and text.endswith(">")) or (text.startswith("<https://") and text.endswith(">")):
                vurls = [text[1:-1]]
            elif text.startswith("http://") or text.startswith("https://"):
                vurls = [text]
            elif text.startswith("dl:http://") or text.startswith("dl:https://"):
                vdl = True
                vurls = [text[7:]]
            elif text.startswith("memo:"):
                await self.bot.cursor.execute(
                    "select * from users where id=%s", (ctx.author.id,))
                pf = await self.bot.cursor.fetchone()
                mn = text[5:]
                if pf["memo"] is not None and pf["memo"].get(mn,None) is not None:
                    for i in pf["memo"][mn].split("\n"):
                        if (i.startswith("<http://") and i.endswith(">")) or (i.startswith("<https://") and i.endswith(">")):
                            vurls = [i[1:-1]]
                        elif i.startswith("http://") or i.startswith("https://"):
                            vurls = [i]
                else:
                    await ctx.send("> 音楽再生\n　該当名称のメモが見つかりません。")
                    return
            elif text.startswith("activity:"):
                tar = ctx.guild.get_member(int(text[9:])) or ctx.author
                spac = [i for i in tar.activities if i.name == "Spotify"]

                if spac:
                    title = getattr(spac[0], "title",None) or spac[0].details
                    artist = getattr(spac[0], "artist",None) or spac[0].state
                    search_response = self.youtube.search().list(
                        part='id',
                        q=f"{title} {artist}",
                        type='video'
                    ).execute()
                    vid = search_response['items'][0]['id']['videoId']
                    if vid:
                        vurls = [f"https://www.youtube.com/watch?v={vid}"]
                    else:
                        return await ctx.send("動画が見つかりませんでした。")
                else:
                    return await ctx.send("プレイ中のActivityがSpotifyではありません。")
            elif text.startswith("file:"):
                c_info = True
                await ctx.message.attachments[0].save(f"musicfile/{ctx.message.id}")
                vinfo = {
                        "type": "download",
                        "stream_url":str(ctx.message.attachments[0].url),
                        "video_id": ctx.message.id,
                        "video_url": "",
                        "video_title": ctx.message.attachments[0].filename,
                        "video_thumbnail": "",
                        "video_up_name": f"{ctx.author}({ctx.author.id})",
                        "video_up_url": f"https://discord.com/users/{ctx.author.id}",
                        "video_source": "Direct Upload",
                        "requester":ctx.author.id
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
                        return await ctx.send("動画が見つかりませんでした。")
                except:
                    return await ctx.send("> 検索エラー\n　現在検索ワードを用いた検索ができません。URLをお試しください。")
            if not c_info:
                if vurls == []:
                    return
                for vurl in vurls:
                    vinfo = await self.gvinfo(ctx, vurl, False)
                    if vinfo.get("extractor", "").startswith("youtube"):
                        if vinfo.get("_type", None) == "playlist":
                            tks = []
                            for c in vinfo["entries"]:
                                self.bot.am.append(c["id"])
                                tks.append(self.gpdate(
                                    f"https://www.youtube.com/watch?v={c['id']}", ctx, False if c["id"] in self.bot.am else vdl))
                            iqlt = [i for i in await asyncio.gather(*tks) if i]
                            if self.bot.qu.get(str(ctx.guild.id), None):
                                await ctx.send(f"キューにプレイリスト内の動画{len(iqlt)}本を追加します。")
                                self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                    ctx.guild.id)] + iqlt
                                await self.panel_update(ctx.guild.id, ctx.voice_client)
                            else:
                                await ctx.send(f"プレイリストより、{len(iqlt)}本の再生を開始します。")
                                self.bot.qu[str(ctx.guild.id)] = iqlt
                                await asyncio.sleep(0.3)
                                self.bot.loop.create_task(self.mplay(ctx))
                        else:
                            self.bot.am.append(vinfo["id"])
                            iqim = await self.gpdate(vurl, ctx, vdl)
                            if self.bot.qu.get(str(ctx.guild.id), None):
                                await ctx.send(f"`{iqim['video_title']}`をキューに追加します。")
                                self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                    ctx.guild.id)] + [iqim]
                                await self.panel_update(ctx.guild.id, ctx.voice_client)
                            else:
                                await ctx.send(f"`{iqim['video_title']}`の再生を開始します。")
                                self.bot.qu[str(ctx.guild.id)] = [iqim]
                                await asyncio.sleep(0.3)
                                self.bot.loop.create_task(self.mplay(ctx))
                    elif vinfo.get("extractor", "") == "niconico":
                        self.bot.am.append(vinfo["id"])
                        iqim = await self.gpdate(vurl, ctx, False if vinfo["id"] in self.bot.am else vdl, "niconico")
                        if self.bot.qu.get(str(ctx.guild.id), None):
                            await ctx.send(f"`{iqim['video_title']}`をキューに追加します。")
                            self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                ctx.guild.id)] + [iqim]
                            await self.panel_update(ctx.guild.id, ctx.voice_client)
                        else:
                            await ctx.send(f"`{iqim['video_title']}`の再生を開始します。")
                            self.bot.qu[str(ctx.guild.id)] = [iqim]
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(ctx))
                    elif vinfo.get("extractor", "").startswith("soundcloud"):
                        if vinfo.get("_type", None) == "playlist":

                            tks = []
                            for c in vinfo["entries"]:
                                self.bot.am.append(c["id"])
                                tks.append(self.gpdate(c["url"], ctx, False if c["id"] in self.bot.am else vdl, "soundcloud"))
                            iqlt = [i for i in await asyncio.gather(*tks) if i]
                            if self.bot.qu.get(str(ctx.guild.id), None):
                                await ctx.send(f"キューにプレイリスト内の動画{len(iqlt)}本を追加します。")
                                self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                    ctx.guild.id)] + iqlt
                                await self.panel_update(ctx.guild.id, ctx.voice_client)
                            else:
                                await ctx.send(f"プレイリストより、{len(iqlt)}本の再生を開始します。")
                                self.bot.qu[str(ctx.guild.id)] = iqlt
                                await asyncio.sleep(0.3)
                                self.bot.loop.create_task(self.mplay(ctx))

                        else:
                            self.bot.am.append(vinfo["id"])
                            iqim = await self.gpdate(vurl, ctx, False if vinfo["id"] in self.bot.am else vdl, "soundcloud")
                            if self.bot.qu.get(str(ctx.guild.id), None):
                                await ctx.send(f"`{iqim['video_title']}`をキューに追加します。")
                                self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                    ctx.guild.id)] + [iqim]
                                await self.panel_update(ctx.guild.id, ctx.voice_client)
                            else:
                                await ctx.send(f"`{iqim['video_title']}`の再生を開始します。")
                                self.bot.qu[str(ctx.guild.id)] = [iqim]
                                await asyncio.sleep(0.3)
                                self.bot.loop.create_task(self.mplay(ctx))
                    elif vinfo.get("extractor", "").startswith("URL_Stream"):
                        self.bot.am.append(vinfo["id"])
                        iqim = await self.gpdate(vurl, ctx, False if vinfo["id"] in self.bot.am else vdl, "URL_Stream")
                        if self.bot.qu.get(str(ctx.guild.id), None):
                            await ctx.send(f"`{iqim['video_title']}`をキューに追加します。")
                            self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                ctx.guild.id)] + [iqim]
                            await self.panel_update(ctx.guild.id, ctx.voice_client)
                        else:
                            await ctx.send(f"`{iqim['video_title']}`の再生を開始します。")
                            self.bot.qu[str(ctx.guild.id)] = [iqim]
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(ctx))                        
                    else:
                        await ctx.send("now,the video can't play the bot")
            else:
                self.bot.am.append(vinfo["id"])
                if self.bot.qu.get(str(ctx.guild.id), None):
                    await ctx.send(f"`{vinfo['video_title']}`をキューに追加します。")
                    self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                        ctx.guild.id)] + [vinfo]
                    await self.panel_update(ctx.guild.id, ctx.voice_client)
                else:
                    await ctx.send(f"`{vinfo['video_title']}`の再生を開始します。")
                    self.bot.qu[str(ctx.guild.id)] = [vinfo]
                    await asyncio.sleep(0.3)
                    self.bot.loop.create_task(self.mplay(ctx))
            """except:
                import traceback
                await ctx.send(f"> traceback\n```{traceback.format_exc(2)}```")"""

    async def mplay(self, ctx, vl=0.5):
        v = None
        if not self.bot.lp.get(str(ctx.guild.id), None):
            self.bot.lp[str(ctx.guild.id)] = False
        if not self.bot.mp.get(str(ctx.guild.id), None):
            ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル", color=self.bot.ec)
            ebd.add_field(name="再生中の曲:", value="未読み込み")
            ebd.add_field(name="次の曲:", value="未読み込み")
            ebd.add_field(name="ループ:", value="未読み込み")
            ebd.add_field(name="ボリューム:", value="未読み込み")
            m = await ctx.send(embed=ebd)
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
        if isinstance(ctx.me.voice.channel, discord.StageChannel):
            try:
                await ctx.me.edit(suppress=False)
                await ctx.send("> ステージチャンネルのため、自動的にスピーカーに移動しました。")
            except:
                await ctx.send("> ステージチャンネルのため、音楽を再生するためにはスピーカーに移動させる必要があります。")
        while self.bot.qu.get(str(ctx.guild.id),None):
            if self.bot.qu[str(ctx.guild.id)][0]["type"] == "download":
                ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                f'musicfile/{self.bot.qu[str(ctx.guild.id)][0]["video_id"]}'), volume=v or vl))
            else:
                ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                self.bot.qu[str(ctx.guild.id)][0]["stream_url"], before_options="-reconnect 1"), volume=v or vl))
            await self.panel_update(ctx.guild.id, ctx.voice_client)
            try:
                while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                    await asyncio.sleep(1)
                    v = ctx.voice_client.source.volume
            except AttributeError:
                pass
            can_delete = True
            if self.bot.lp.get(str(ctx.guild.id),None):
                can_delete = False
                self.bot.qu[str(ctx.guild.id)].append(self.bot.qu[str(ctx.guild.id)][0])
            else:
                self.bot.am.remove(self.bot.qu[str(ctx.guild.id)][0]["video_id"])
            poped_item = self.bot.qu[str(ctx.guild.id)].pop(0)
            if can_delete and (not poped_item["video_id"] in self.bot.am) and poped_item["type"] == "download":
                loop = self.bot.loop or asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: os.remove(f'musicfile/{poped_item["video_id"]}'))
        await ctx.invoke(self.bot.get_command("stop"))

    @music_group.command(description="曲をスキップします。")
    async def skip(self, ctx):
        if ctx.author.voice and ctx.voice_client.is_playing():
            lp = self.bot.lp[str(ctx.guild.id)]
            self.bot.lp[str(ctx.guild.id)] = False
            ctx.voice_client.stop()
            self.bot.lp[str(ctx.guild.id)] = lp
            await ctx.send("曲をスキップしました。",ephemeral = True)

    @music_group.command(name="volume",aliases=["chvol","vol"], description="ボリュームを変更します。")
    @app_commands.describe(vol="調整する音量(0-200)")
    async def chvol(self, ctx, vol: float):
        if ctx.author.voice and ctx.voice_client.is_playing():
            ctx.voice_client.source.volume = vol/100.0
            await ctx.send("ボリュームを調節しました。",ephemeral = True)
            await self.panel_update(ctx.guild.id, ctx.voice_client)

    @music_group.command(aliases=["np"], description="再生中楽曲について表示します。")
    async def playingmusic(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("ボイスチャンネルに参加していません。", ephemeral=True)
        if ctx.voice_client.is_playing():
            e = discord.Embed(
                title="再生中の曲", description=f'[{self.bot.qu[str(ctx.guild.id)][0]["video_title"]}]({self.bot.qu[str(ctx.guild.id)][0]["video_url"]})\nアップロードチャンネル:[{self.bot.qu[str(ctx.guild.id)][0]["video_up_name"]}]({self.bot.qu[str(ctx.guild.id)][0]["video_up_url"]})\nソース:{self.bot.qu[str(ctx.guild.id)][0]["video_source"]}')
            e.set_thumbnail(
                url=self.bot.qu[str(ctx.guild.id)][0]["video_thumbnail"])
            await ctx.send(embed=e)
        else:
            await ctx.send("再生中の曲はありません。", ephemeral = True)

    @music_group.command(aliases=["plist", "view_q"], description="楽曲キューを表示します。")
    @app_commands.describe(pg="始めに表示するページ(1ページ当たり5項目)")
    async def queue(self, ctx, pg:Optional[int]=1):
        if ctx.voice_client is None:
            return await ctx.send("ボイスチャンネルに参加していません。")
        if ctx.voice_client.is_playing():
            page = pg-1
            pls = [self.bot.qu[str(ctx.guild.id)][5*i:5*(i+1)]
                   for i in range(int(len(self.bot.qu[str(ctx.guild.id)])/5)+1)]
            e = discord.Embed(
                title="キューの中身", description=f"全{len(self.bot.qu[str(ctx.guild.id)])}曲")
            for i in pls[page]:
                e.add_field(
                    name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}/{i["type"]}\n追加メンバー:{self.bot.get_user(i["requester"]).mention}')
            e.set_footer(text=f"page:{page+1}/{len(pls)}")
            msg = await ctx.send(embed=e)
            await msg.add_reaction(self.bot.get_emoji(653161518195671041))  # ←
            await msg.add_reaction(self.bot.get_emoji(653161518170505216))  # →
            while True:
                try:
                    r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
                except:
                    break
                try:
                    await msg.remove_reaction(r, u)
                except:
                    pass
                if str(r) == str(self.bot.get_emoji(653161518170505216)):  # →
                    if page == len(pls)-1:
                        page = 0
                    else:
                        page += 1
                elif str(r) == str(self.bot.get_emoji(653161518195671041)):  # ←
                    if page == 0:
                        page = len(pls)-1
                    else:
                        page -= 1
                e = discord.Embed(
                    title="キューの中身", description=f"全{len(self.bot.qu[str(ctx.guild.id)])}曲")
                for i in pls[page]:
                    e.add_field(
                        name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}/{i["type"]}\n追加メンバー:{self.bot.get_user(i["requester"]).mention}')
                e.set_footer(text=f"page:{page+1}/{len(pls)}")
                await msg.edit(embed=e)
        else:
            await ctx.send("現在キューには何もありません。")

    @music_group.command(aliases=["loop", "repeat"], description="ループ状況の確認や変更ができます。")
    @app_commands.describe(is_enable="ループを有効にするかどうか")
    async def loop_q(self, ctx, is_enable:Optional[bool]=None):
        torf = is_enable
        if ctx.author.voice:
            if torf is None:
                await ctx.send(f"今のキューのループ状態:{self.bot.lp[str(ctx.guild.id)]}")
            else:
                self.bot.lp[str(ctx.guild.id)] = torf
                await ctx.send(f"きりかえました。\n今のキューのループ状態:{self.bot.lp[str(ctx.guild.id)]}")
                await self.panel_update(ctx.guild.id, ctx.voice_client)

    @music_group.command(name="panel_update", aliases=["pupdate"], description="楽曲パネルの更新を行います。")
    async def pupdate(self, ctx):
        await self.panel_update(ctx.guild.id, ctx.voice_client)

    async def panel_update(self, guild_id, voice_client):
        ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル",
                            description=f"キューの曲数:{len(self.bot.qu[str(guild_id)])}曲", color=self.bot.ec)
        ebd.set_footer("⬇:パネルを下に持ってくる")
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
        except AttributeError:
            # パネルメッセージが、まだない状態の可能性があるため
            pass


    @music_group.command(name="shuffle", description="キューの中身をシャッフルします。")
    async def shuffle_(self, ctx):
        if self.bot.qu.get(str(ctx.guild.id), None) is not None and len(self.bot.qu[str(ctx.guild.id)]) > 2:
            tmplist = self.bot.qu[str(ctx.guild.id)][1:]
            random.shuffle(tmplist)
            self.bot.qu[str(ctx.guild.id)] = [self.bot.qu[str(ctx.guild.id)][0]] + tmplist
            await ctx.send("> シャッフル\n　シャッフルしました。再生パネルや`s-view_q`でご確認ください。")
        else:
            await ctx.send("> シャッフルエラー\n　シャッフルに必要要件を満たしていません。(VCで音楽再生中で、3曲以上キューに入っている)")

    @music_group.command(name="move_panel", description="音楽パネルをほかのサーバーに移動させます。")
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
