# -*- coding: utf-8 -*-

import asyncio
from typing import Optional
import discord
from discord.ext import commands

from discord import app_commands

from youtube_dl import YoutubeDL

from apiclient.discovery import build

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


class music(commands.Cog):
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
            loop = asyncio.get_event_loop()
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
                "requester":ctx.user.id
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
                "requester":ctx.user.id
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
                "requester":ctx.user.id
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
                "requester":ctx.user.id
            }

    @app_commands.command(name="join", description="ボイスチャンネルに接続します。")
    async def join_(self, interaction:discord.Interaction):
        if interaction.user.voice:
            if interaction.guild.voice_client:
                    await interaction.response.send_message(f"すでに{interaction.guild.voice_client.channel.name}に接続しています。", ephemeral=True)
            else:
                try:
                    await interaction.user.voice.channel.connect()
                except asyncio.TimeoutError:
                    await interaction.response.send_message(f"接続がタイムアウトしました。", ephemeral=True)
                else:
                    await interaction.response.send_message(f"{interaction.user.voice.channel.name}に接続しました。")
        else:
            await interaction.response.send_message(f"あなたがボイスチャンネルに接続していません！", ephemeral=True)

    @app_commands.command(name="stop", description="再生を停止し、ボイスチャンネルから切断します。")
    async def stop_(self, interaction:discord.Interaction):
        if interaction.guild.voice_client and interaction.user.voice:
            if interaction.guild.voice_client.channel == interaction.user.voice.channel:
                try:
                    await self.bot.mp[str(interaction.guild_id)].delete()
                except:
                    pass
                try:
                    del self.bot.qu[str(interaction.guild_id)]
                    del self.bot.mp[str(interaction.guild_id)]
                    del self.bot.lp[str(interaction.guild_id)]
                except:
                    pass
                await interaction.guild.voice_client.disconnect()
                await interaction.response.send_message("> 切断しました。")

    @app_commands.command(name="pause", description="再生を一時的に停止します。")
    async def pause_(self, interaction:discord.Interaction):
        if interaction.guild.voice_client and interaction.user.voice:
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("> 一時停止しました。ボイスチャットを出ても構いません。")
            await self.panel_update(interaction.guild_id, interaction.guild.voice_client)

    @app_commands.command(name="play", description="引数に従って、音楽を再生します。")
    @app_commands.describe(word="検索するワード")
    @app_commands.describe(url="音楽のURL")
    @app_commands.describe(activity="Spotifyアクティビティを持つユーザー")
    @app_commands.describe(attachment="再生する音声ファイル")
    async def play_(self, interaction:discord.Interaction, word:Optional[str], url:Optional[str], activity:Optional[discord.Member], attachment:Optional[discord.Attachment]):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("> 再生を開始する前に、ボイスチャンネルに参加させてください。", ephemeral=True)
        if interaction.guild.voice_client.is_paused():
            await interaction.response.send_message("再生を再開しました。")
            interaction.guild.voice_client.resume()
            await self.panel_update(interaction.guild_id, interaction.guild.voice_client)
            return
        if word == None and url == None and activity == None and attachment == None:
            await interaction.response.send_message("> 引数を指定してください。", ephemeral=True)
        #try:
        vurls = [] #処理するURL
        vdl = False #ビデオダウンロードを行うかどうか
        c_info = False #再生時の表示情報をカスタム作成するかどうか
        if url:
            if url.startswith("http://") or url.startswith("https://"):
                vurls = [url]
            elif url.startswith("dl:http://") or url.startswith("dl:https://"):
                vdl = True
                vurls = [url[3:]]
        elif activity:
            tar = interaction.guild.get_member(activity.id)
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
                    return await interaction.response.send_message("> 見つかりませんでした。", ephemeral=True)
            else:
                return await interaction.response.send_message("> プレイ中のアクティビティにSpotifyがありません。", ephemeral=True)
        elif attachment:
            import time
            c_info = True
            fn = time.time()
            await attachment.save(f"musicfile/{fn}")
            vinfo = {
                    "type": "download",
                    "stream_url":str(attachment.url),
                    "video_id": fn,
                    "video_url": "",
                    "video_title": attachment.filename,
                    "video_thumbnail": "",
                    "video_up_name": f"{interaction.user}({interaction.user.id})",
                    "video_up_url": f"https://discord.com/users/{interaction.user.id}",
                    "video_source": "Direct Upload",
                    "requester":interaction.user.id
                    }
        else:
            try:
                search_response = self.youtube.search().list(
                    part='id',
                    q=word,
                    type='video'
                ).execute()
                vid = search_response['items'][0]['id']['videoId']
                if vid:
                    vurls = [f"https://www.youtube.com/watch?v={vid}"]
                else:
                    return await interaction.response.send_message("> 見つかりませんでした。", ephemeral=True)
            except:
                return await interaction.response.send_message("> 検索エラー\n　現在検索ワードを用いた検索ができません。URLをお試しください。", ephemeral=True)
        if not c_info:
            if vurls == []:
                return
            for vurl in vurls:
                vinfo = await self.gvinfo(interaction, vurl, False)
                if vinfo.get("extractor", "").startswith("youtube"):
                    if vinfo.get("_type", None) == "playlist":
                        tks = []
                        for c in vinfo["entries"]:
                            self.bot.am.append(c["id"])
                            tks.append(self.gpdate(
                                f"https://www.youtube.com/watch?v={c['id']}", interaction, False if c["id"] in self.bot.am else vdl))
                        iqlt = [i for i in await asyncio.gather(*tks) if i]
                        if self.bot.qu.get(str(interaction.guild.id), None):
                            await interaction.response.send_message(f"キューにプレイリスト内の動画{len(iqlt)}本を追加します。")
                            self.bot.qu[str(interaction.guild.id)] = self.bot.qu[str(
                                interaction.guild.id)] + iqlt
                            await self.panel_update(interaction.guild.id, interaction.guild.voice_client)
                        else:
                            await interaction.response.send_message(f"プレイリストより、{len(iqlt)}本の再生を開始します。")
                            self.bot.qu[str(interaction.guild.id)] = iqlt
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(interaction))
                    else:
                        self.bot.am.append(vinfo["id"])
                        iqim = await self.gpdate(vurl, interaction, vdl)
                        if self.bot.qu.get(str(interaction.guild.id), None):
                            await interaction.response.send_message(f"`{iqim['video_title']}`をキューに追加します。")
                            self.bot.qu[str(interaction.guild.id)] = self.bot.qu[str(
                                interaction.guild.id)] + [iqim]
                            await self.panel_update(interaction.guild.id, interaction.guild.voice_client)
                        else:
                            await interaction.response.send_message(f"`{iqim['video_title']}`の再生を開始します。")
                            self.bot.qu[str(interaction.guild.id)] = [iqim]
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(interaction))
                elif vinfo.get("extractor", "") == "niconico":
                    self.bot.am.append(vinfo["id"])
                    iqim = await self.gpdate(vurl, interaction, False if vinfo["id"] in self.bot.am else vdl, "niconico")
                    if self.bot.qu.get(str(interaction.guild.id), None):
                        await interaction.response.send_message(f"`{iqim['video_title']}`をキューに追加します。")
                        self.bot.qu[str(interaction.guild.id)] = self.bot.qu[str(
                            interaction.guild.id)] + [iqim]
                        await self.panel_update(interaction.guild.id, interaction.guild.voice_client)
                    else:
                        await interaction.response.send_message(f"`{iqim['video_title']}`の再生を開始します。")
                        self.bot.qu[str(interaction.guild.id)] = [iqim]
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(interaction))
                elif vinfo.get("extractor", "").startswith("soundcloud"):
                    if vinfo.get("_type", None) == "playlist":

                        tks = []
                        for c in vinfo["entries"]:
                            self.bot.am.append(c["id"])
                            tks.append(self.gpdate(c["url"], interaction, False if c["id"] in self.bot.am else vdl, "soundcloud"))
                        iqlt = [i for i in await asyncio.gather(*tks) if i]
                        if self.bot.qu.get(str(interaction.guild.id), None):
                            await interaction.response.send_message(f"キューにプレイリスト内の動画{len(iqlt)}本を追加します。")
                            self.bot.qu[str(interaction.guild.id)] = self.bot.qu[str(
                                interaction.guild.id)] + iqlt
                            await self.panel_update(interaction.guild.id, interaction.voice_client)
                        else:
                            await interaction.response.send_message(f"プレイリストより、{len(iqlt)}本の再生を開始します。")
                            self.bot.qu[str(interaction.guild.id)] = iqlt
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(interaction))

                    else:
                        self.bot.am.append(vinfo["id"])
                        iqim = await self.gpdate(vurl, interaction, False if vinfo["id"] in self.bot.am else vdl, "soundcloud")
                        if self.bot.qu.get(str(interaction.guild.id), None):
                            await interaction.response.send_message(f"`{iqim['video_title']}`をキューに追加します。")
                            self.bot.qu[str(interaction.guild.id)] = self.bot.qu[str(
                                interaction.guild.id)] + [iqim]
                            await self.panel_update(interaction.guild.id, interaction.guild.voice_client)
                        else:
                            await interaction.response.send_message(f"`{iqim['video_title']}`の再生を開始します。")
                            self.bot.qu[str(interaction.guild.id)] = [iqim]
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(interaction))
                elif vinfo.get("extractor", "").startswith("URL_Stream"):
                    self.bot.am.append(vinfo["id"])
                    iqim = await self.gpdate(vurl, interaction, False if vinfo["id"] in self.bot.am else vdl, "URL_Stream")
                    if self.bot.qu.get(str(interaction.guild.id), None):
                        await interaction.response.send_message(f"`{iqim['video_title']}`をキューに追加します。")
                        self.bot.qu[str(interaction.guild.id)] = self.bot.qu[str(
                            interaction.guild.id)] + [iqim]
                        await self.panel_update(interaction.guild.id, interaction.guild.voice_client)
                    else:
                        await interaction.response.send_message(f"`{iqim['video_title']}`の再生を開始します。")
                        self.bot.qu[str(interaction.guild.id)] = [iqim]
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(interaction))                        
                else:
                    await interaction.response.send_message("now,the video can't play the bot")
        else:
            self.bot.am.append(vinfo["video_id"])
            if self.bot.qu.get(str(interaction.guild.id), None):
                await interaction.response.send_message(f"`{vinfo['video_title']}`をキューに追加します。")
                self.bot.qu[str(interaction.guild.id)] = self.bot.qu[str(
                    interaction.guild.id)] + [vinfo]
                await self.panel_update(interaction.guild.id, interaction.guild.voice_client)
            else:
                await interaction.response.send_message(f"`{vinfo['video_title']}`の再生を開始します。")
                self.bot.qu[str(interaction.guild.id)] = [vinfo]
                await asyncio.sleep(0.3)
                self.bot.loop.create_task(self.mplay(interaction))
        """except:
            import traceback
            await interaction.response.send_message(f"> traceback\n```{traceback.format_exc(2)}```")"""

    async def mplay(self, interaction:discord.Interaction, vl=0.5):
        v = None
        if not self.bot.lp.get(str(interaction.guild.id), None):
            self.bot.lp[str(interaction.guild.id)] = False
        if not self.bot.mp.get(str(interaction.guild.id), None):
            ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル", color=self.bot.ec)
            ebd.add_field(name="再生中の曲:", value="未読み込み")
            ebd.add_field(name="次の曲:", value="未読み込み")
            ebd.add_field(name="ループ:", value="未読み込み")
            ebd.add_field(name="ボリューム:", value="未読み込み")
            m = await interaction.channel.send(embed=ebd)
            self.bot.mp[str(interaction.guild.id)] = m
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
        if isinstance(interaction.guild.me.voice.channel, discord.StageChannel):
            try:
                await interaction.guild.me.edit(suppress=False)
                await interaction.channel.send("> ステージチャンネルのため、自動的にスピーカーに移動しました。")
            except:
                await interaction.channel.send("> ステージチャンネルのため、音楽を再生するためにはスピーカーに移動させる必要があります。")
        while self.bot.qu.get(str(interaction.guild.id),None):
            if self.bot.qu[str(interaction.guild.id)][0]["type"] == "download":
                interaction.guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                f'musicfile/{self.bot.qu[str(interaction.guild.id)][0]["video_id"]}'), volume=v or vl))
            else:
                interaction.guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                self.bot.qu[str(interaction.guild.id)][0]["stream_url"], before_options="-reconnect 1"), volume=v or vl))
            await self.panel_update(interaction.guild.id, interaction.guild.voice_client)
            try:
                while interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
                    await asyncio.sleep(1)
                    v = interaction.guild.voice_client.source.volume
            except AttributeError:
                pass
            can_delete = True
            if self.bot.lp.get(str(interaction.guild.id),None):
                can_delete = False
                self.bot.qu[str(interaction.guild.id)].append(self.bot.qu[str(interaction.guild.id)][0])
            else:
                self.bot.am.remove(self.bot.qu[str(interaction.guild.id)][0]["video_id"])
            poped_item = self.bot.qu[str(interaction.guild.id)].pop(0)
            if can_delete and (not poped_item["video_id"] in self.bot.am) and poped_item["type"] == "download":
                loop = self.bot.loop or asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: os.remove(f'musicfile/{poped_item["video_id"]}'))
        try:
            await self.bot.mp[str(interaction.guild_id)].delete()
        except:
            pass
        try:
            del self.bot.qu[str(interaction.guild_id)]
            del self.bot.mp[str(interaction.guild_id)]
            del self.bot.lp[str(interaction.guild_id)]
        except:
            pass
        await interaction.guild.voice_client.disconnect()

    @app_commands.command(name="skip",description="再生中楽曲をスキップします。")
    async def skip(self, interaction:discord.Interaction):
        if interaction.user.voice and interaction.guild.voice_client.is_playing():
            lp = self.bot.lp[str(interaction.guild.id)]
            self.bot.lp[str(interaction.guild.id)] = False
            interaction.guild.voice_client.stop()
            self.bot.lp[str(interaction.guild.id)] = lp
            await interaction.response.send_message("> 曲をスキップしました。")

    @app_commands.command(name="volume", description="音量を調節します。")
    async def chvol(self, interaction:discord.Interaction, vol: float):
        if interaction.user.voice and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.source.volume = vol/100.0
            await interaction.response.send_message("> ボリュームを調節しました。")
            await self.panel_update(interaction.guild.id, interaction.guild.voice_client)

    @app_commands.command(name="now_playing", description="再生中楽曲を表示します。")
    async def playingmusic(self, interaction:discord.Interaction):
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("> ボイスチャンネルに参加していません。", ephemeral=True)
        if interaction.guild.voice_client.is_playing():
            e = discord.Embed(
                title="再生中の曲", description=f'[{self.bot.qu[str(interaction.guild.id)][0]["video_title"]}]({self.bot.qu[str(interaction.guild.id)][0]["video_url"]})\nアップロードチャンネル:[{self.bot.qu[str(interaction.guild.id)][0]["video_up_name"]}]({self.bot.qu[str(interaction.guild.id)][0]["video_up_url"]})\nソース:{self.bot.qu[str(interaction.guild.id)][0]["video_source"]}')
            e.set_thumbnail(
                url=self.bot.qu[str(interaction.guild.id)][0]["video_thumbnail"])
            await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            await interaction.response.send_message("> 再生中の曲はありません。", ephemeral=True)

    @app_commands.command(name="queue", description="再生キューを表示します。")
    @app_commands.describe(page_number="最初に表示するページ(1ページ当たり5件)")
    async def view_q(self, interaction:discord.Interaction, page_number:Optional[int]):
        pg = page_number
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("> ボイスチャンネルに参加していません。", ephemeral=True)
        if interaction.guild_id.voice_client.is_playing():
            page = pg-1 if pg else 0
            pls = [self.bot.qu[str(interaction.guild.id)][5*i:5*(i+1)]
                   for i in range(int(len(self.bot.qu[str(interaction.guild.id)])/5)+1)]
            e = discord.Embed(
                title="キューの中身", description=f"全{len(self.bot.qu[str(interaction.guild.id)])}曲")
            for i in pls[page]:
                e.add_field(
                    name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}/{i["type"]}\n追加メンバー:{self.bot.get_user(i["requester"]).mention}')
            e.set_footer(text=f"page:{page+1}/{len(pls)}")
            await interaction.response.send_message(embed=e)
            msg = await interaction.original_message()
            await msg.add_reaction(self.bot.get_emoji(653161518195671041))  # ←
            await msg.add_reaction(self.bot.get_emoji(653161518170505216))  # →
            while True:
                try:
                    r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == interaction.user.id, timeout=30)
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
                    title="キューの中身", description=f"全{len(self.bot.qu[str(interaction.guild.id)])}曲")
                for i in pls[page]:
                    e.add_field(
                        name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}/{i["type"]}\n追加メンバー:{self.bot.get_user(i["requester"]).mention}')
                e.set_footer(text=f"page:{page+1}/{len(pls)}")
                await msg.edit(embed=e)
        else:
             await interaction.response.send_message("現在キューには何もありません。", ephemeral=True)

    @app_commands.command(name="loop", description="ループ状態の確認/変更を行います。")
    @app_commands.describe(enable="ループ設定を有効にするかどうか")
    async def loop_q(self, interaction:discord.Interaction, enable: Optional[bool]):
        if interaction.user.voice:
            if enable is None:
                await interaction.response.send_message(f"今のキューのループ状態:{self.bot.lp[str(interaction.guild.id)]}", ephemeral=True)
            else:
                self.bot.lp[str(interaction.guild.id)] = enable
                await interaction.response.send_message(f"きりかえました。\n今のキューのループ状態:{self.bot.lp[str(interaction.guild.id)]}")
                await self.panel_update(interaction.guild.id, interaction.guild.voice_client)

    @app_commands.command(name="panel_update", description="音楽再生パネルの情報を更新します。")
    async def pupdate(self, interaction:discord.Interaction):
        await self.panel_update(interaction.guild.id, interaction.guild.voice_client)

    async def panel_update(self, guild_id, voice_client):
        ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル",
                            #description=f"キューの曲数:{len(self.bot.qu[str(guild_id)])}曲\nリアクションで操作でき、そのたびに操作パネルが更新されます。\n▶:(一時停止中)再生の再開,⏸:(再生中)一時停止,⏹:ストップ,⏭:スキップ,🔁:ループ切替,🔀次以降の曲のシャッフル,🔼:ボリュームを上げる,🔽:ボリュームを下げる,⬇:パネルを下に持ってくる", color=self.bot.ec)
                            description=f"キューの曲数:{len(self.bot.qu[str(guild_id)])}曲", color=self.bot.ec)
        if voice_client.is_paused():
            ebd.add_field(name="現在一時停止中",
                          value="再開には`s-play`か▶リアクション", inline=False)
        ebd.add_field(
            name="再生中の曲:", value=f"[{self.bot.qu[str(guild_id)][0]['video_title']}]({self.bot.qu[str(guild_id)][0]['video_url']})(from {self.bot.qu[str(guild_id)][0]['video_source']})(再生方式:{self.bot.qu[str(guild_id)][0]['type']})(追加者:{self.bot.get_user(self.bot.qu[str(guild_id)][0]['requester']).mention})")
        if len(self.bot.qu[str(guild_id)]) > 1:
            ebd.add_field(
                name="次の曲:", value=f"[{self.bot.qu[str(guild_id)][1]['video_title']}]({self.bot.qu[str(guild_id)][1]['video_url']})(from {self.bot.qu[str(guild_id)][1]['video_source']})(再生方式:{self.bot.qu[str(guild_id)][1]['type']})(追加者:{self.bot.get_user(self.bot.qu[str(guild_id)][1]['requester']).mention})")
        elif self.bot.lp[str(guild_id)]:
            ebd.add_field(
                name="次の曲:", value=f"[{self.bot.qu[str(guild_id)][0]['video_title']}]({self.bot.qu[str(guild_id)][0]['video_url']})(from {self.bot.qu[str(guild_id)][0]['video_source']})(再生方式:{self.bot.qu[str(guild_id)][0]['type']})(追加者:{self.bot.get_user(self.bot.qu[str(guild_id)][0]['requester']).mention})(スキップでキューから削除され、再生が止まります。)")
        else:
            ebd.add_field(name="次の曲:", value=f"再生終了")
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


    @app_commands.command(name="shuffle", description="再生キューをシャッフルします。")
    async def shuffle_(self, interaction:discord.Interaction):
        if self.bot.qu.get(str(interaction.guild.id), None) is not None and len(self.bot.qu[str(interaction.guild.id)]) > 2:
            tmplist = self.bot.qu[str(interaction.guild.id)][1:]
            random.shuffle(tmplist)
            self.bot.qu[str(interaction.guild.id)] = [self.bot.qu[str(interaction.guild.id)][0]] + tmplist
            await interaction.response.send_message("> シャッフル\n　シャッフルしました。再生パネルや`s-view_q`でご確認ください。")
        else:
            await interaction.response.send_message("> シャッフルエラー\n　シャッフルに必要要件を満たしていません。(VCで音楽再生中で、3曲以上キューに入っている)", ephemeral=True)

    @app_commands.command(name="move_panel", description="音楽再生パネルを移動します。")
    @app_commands.describe(move_to="移動先チャンネル")
    async def move_panel(self, interaction:discord.Interaction, move_to:discord.TextChannel):
        ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル", color=self.bot.ec)
        ebd.add_field(name="再生中の曲:", value="未読み込み")
        ebd.add_field(name="次の曲:", value="未読み込み")
        ebd.add_field(name="ループ:", value="未読み込み")
        ebd.add_field(name="ボリューム:", value="未読み込み")
        m = await move_to.send(embed=ebd)
        await self.bot.mp[str(interaction.guild.id)].delete()
        self.bot.mp[str(interaction.guild.id)] = m
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
        await self.panel_update(interaction.guild.id, interaction.guild.voice_client)
        await interaction.response.send_message(f"> 音楽再生パネルの移動\n　{move_to.mention}に移動しました。")


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
    await bot.add_cog(music(bot))
