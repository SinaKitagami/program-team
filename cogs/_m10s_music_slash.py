# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext import commands

from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash
from discord_slash.utils.manage_commands import create_choice, create_option

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

target_guilds = []

class music_slash(commands.Cog):
    """music in discord.py with slash_command"""

    def __init__(self, bot):
        self.bot = bot
        self.youtube = build('youtube', 'v3', developerKey=bot.GAPI_TOKEN)
        self.ytdl = YoutubeDL(ytdlopts)
        if not ("qu" in dir(bot) and "lp" in dir(bot) and "mp" in dir(bot)):
            self.bot.qu = {}
            self.bot.lp = {}
            self.bot.mp = {}

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

    @cog_slash(name="join", description="ボイスチャンネルに参加します。",guild_ids=target_guilds)
    async def join_(self, ctx:SlashContext):
        await ctx.defer(hidden=True)
        if ctx.author.voice:
            if ctx.guild.voice_client:
                await ctx.send(f"すでに{ctx.guild.voice_client.channel.name}に接続しています。",hidden=True)
            else:
                try:
                    await ctx.author.voice.channel.connect()
                    await ctx.send(f"{ctx.guild.voice_client.channel.name}に接続しました。",hidden=True)
                except asyncio.TimeoutError:
                    await ctx.send("接続のタイムアウト！",hidden=True)
        else:
            await ctx.send("あなたがボイスチャンネルに接続していません！",hidden=True)

    @cog_slash(name="stop", description="ボイスチャンネルから切断します。",guild_ids=target_guilds)
    async def stop_(self, ctx:SlashContext):
        await ctx.defer(hidden=True)
        if ctx.guild.voice_client and ctx.author.voice:
            if ctx.guild.voice_client.channel == ctx.author.voice.channel:
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
                await ctx.guild.voice_client.disconnect()
                await ctx.send("切断しました。",hidden=True)

    @cog_slash(name="pause",description="再生中の楽曲を一時停止します。",guild_ids=target_guilds)
    async def pause_(self, ctx:SlashContext):
        await ctx.defer(hidden=True)
        if ctx.guild.voice_client and ctx.author.voice:
            ctx.guild.voice_client.pause()
            await ctx.send("一時停止しました。ボイスチャットを出ても構いません。",hidden=True)
            await self.panel_update(ctx)

    @cog_slash(name="play", description="引数に入れたものをもとに曲を再生します。/一時停止した音楽を再生します。" ,guild_ids=target_guilds,
        options=[
            create_option(name="URL",description="これを指定した場合、指定したURLから読み込みます。(優先度1)",option_type=3,required=False),
            create_option(name="word",description="これを指定した場合、指定した言葉で検索を行います。(優先度2)",option_type=3,required=False),
            create_option(name="memo",description="これを指定した場合、そのメモに書かれたURLから読み込みます。(優先度3)",option_type=3,required=False),
            create_option(name="user",description="これを指定した場合、このユーザーのSpotifyアクティビティに基づいて再生します。(優先度4)",option_type=6,required=False)
            ]
    )
    async def play_(self, ctx:SlashContext, **kargs):
        await ctx.defer(hidden=True)
        if not ctx.guild.voice_client:
            if ctx.author.voice:
                if ctx.guild.voice_client:
                    await ctx.send(f"{ctx.guild.voice_client.channel.name}に接続しました。",hidden=True)
                else:
                    try:
                        await ctx.author.voice.channel.connect()
                    except asyncio.TimeoutError:
                        await ctx.send("接続のタイムアウト！",hidden=True)
            else:
                await ctx.send("あなたがボイスチャンネルに接続していません！",hidden=True)
            if not ctx.guild.voice_client:
                return
        if ctx.guild.voice_client.is_paused():
            await ctx.send("再生を再開しました。",hidden=True)
            ctx.guild.voice_client.resume()
            await self.panel_update(ctx)
            return
        if not kargs:
            try:
                m = await ut.wait_message_return(ctx, "再生するURLを送信してください。", ctx.channel)
            except asyncio.TimeoutError:
                await ctx.send("タイムアウトしました。")
                return
            else:
                vurls = [m.content]
        async with ctx.channel.typing():
            vurls = [] #処理するURL
            vdl = True #ビデオダウンロードを行うかどうか
            if kargs.get("URL",None):
                text = kargs["URL"]
                if text.startswith("stream:http://") or text.startswith("stream:https://"):
                    vdl = False
                    vurls = [text[7:]]
                else:
                    vurls = [text]
            elif kargs.get("word",None):
                search_response = self.youtube.search().list(
                    part='snippet',
                    q=kargs["word"],
                    type='video'
                ).execute()
                vid = search_response['items'][0]['id']['videoId']
                if vid:
                    vurls = [f"https://www.youtube.com/watch?v={vid}"]
                else:
                    return await ctx.send("動画が見つかりませんでした。",hidden=True)
            elif kargs.get("memo's_name",None):
                self.bot.cursor.execute(
                    "select * from users where id=?", (ctx.author.id,))
                pf = self.bot.cursor.fetchone()
                mn = kargs["memo"]
                if pf["memo"] is not None and pf["memo"].get(mn,None) is not None:
                    for i in pf["memo"][mn].split("\n"):
                        if (i.startswith("<http://") and i.endswith(">")) or (i.startswith("<https://") and i.endswith(">")):
                            vurls = [i[1:-1]]
                        elif i.startswith("http://") or i.startswith("https://"):
                            vurls = [i]
                else:
                    await ctx.send("> 音楽再生\n　該当名称のメモが見つかりません。",hidden=True)
                    return
            elif kargs.get("user",None):
                tar = kargs["user"]
                spac = [i for i in tar.activities if i.name == "Spotify"]

                if spac:
                    title = getattr(spac[0], "title",None) or spac[0].details
                    artist = getattr(spac[0], "artist",None) or spac[0].state
                    search_response = self.youtube.search().list(
                        part='snippet',
                        q=f"{title} {artist}",
                        type='video'
                    ).execute()
                    vid = search_response['items'][0]['id']['videoId']
                    if vid:
                        vurls = [f"https://www.youtube.com/watch?v={vid}"]
                    else:
                        return await ctx.send("動画が見つかりませんでした。",hidden=True)
                else:
                    return await ctx.send("プレイ中のActivityがSpotifyではありません。",hidden=True)
            if vurls == []:
                return
            for vurl in vurls:
                vinfo = await self.gvinfo(ctx, vurl, False)
                if vinfo.get("extractor", "").startswith("youtube"):
                    if vinfo.get("_type", None) == "playlist":
                        tks = []
                        for c in vinfo["entries"]:
                            tks.append(self.gpdate(
                                f"https://www.youtube.com/watch?v={c['id']}", ctx, vdl))
                        iqlt = [i for i in await asyncio.gather(*tks) if i]
                        if self.bot.qu.get(str(ctx.guild.id), None):
                            await ctx.send(f"キューにプレイリスト内の動画{len(iqlt)}本を追加します。",hidden=True)
                            self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                ctx.guild.id)] + iqlt
                            await self.panel_update(ctx)
                        else:
                            await ctx.send(f"プレイリストより、{len(iqlt)}本の再生を開始します。",hidden=True)
                            self.bot.qu[str(ctx.guild.id)] = iqlt
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(ctx))
                    else:
                        iqim = await self.gpdate(vurl, ctx, vdl)
                        if self.bot.qu.get(str(ctx.guild.id), None):
                            await ctx.send(f"`{iqim['video_title']}`をキューに追加します。",hidden=True)
                            self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                ctx.guild.id)] + [iqim]
                            await self.panel_update(ctx)
                        else:
                            await ctx.send(f"`{iqim['video_title']}`の再生を開始します。",hidden=True)
                            self.bot.qu[str(ctx.guild.id)] = [iqim]
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(ctx))
                elif vinfo.get("extractor", "") == "niconico":
                    iqim = await self.gpdate(vurl, ctx, vdl, "niconico")
                    if self.bot.qu.get(str(ctx.guild.id), None):
                        await ctx.send(f"`{iqim['video_title']}`をキューに追加します。",hidden=True)
                        self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                            ctx.guild.id)] + [iqim]
                        await self.panel_update(ctx)
                    else:
                        await ctx.send(f"`{iqim['video_title']}`の再生を開始します。",hidden=True)
                        self.bot.qu[str(ctx.guild.id)] = [iqim]
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(ctx))
                elif vinfo.get("extractor", "").startswith("soundcloud"):
                    if vinfo.get("_type", None) == "playlist":

                        tks = []
                        for c in vinfo["entries"]:
                            tks.append(self.gpdate(c["url"], ctx, vdl, "soundcloud"))
                        iqlt = [i for i in await asyncio.gather(*tks) if i]
                        if self.bot.qu.get(str(ctx.guild.id), None):
                            await ctx.send(f"キューにプレイリスト内の動画{len(iqlt)}本を追加します。",hidden=True)
                            self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                ctx.guild.id)] + iqlt
                            await self.panel_update(ctx)
                        else:
                            await ctx.send(f"プレイリストより、{len(iqlt)}本の再生を開始します。",hidden=True)
                            self.bot.qu[str(ctx.guild.id)] = iqlt
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(ctx))

                    else:
                        iqim = await self.gpdate(vurl, ctx, vdl, "soundcloud")
                        if self.bot.qu.get(str(ctx.guild.id), None):
                            await ctx.send(f"`{iqim['video_title']}`をキューに追加します。",hidden=True)
                            self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                                ctx.guild.id)] + [iqim]
                            await self.panel_update(ctx)
                        else:
                            await ctx.send(f"`{iqim['video_title']}`の再生を開始します。",hidden=True)
                            self.bot.qu[str(ctx.guild.id)] = [iqim]
                            await asyncio.sleep(0.3)
                            self.bot.loop.create_task(self.mplay(ctx))
                elif vinfo.get("extractor", "").startswith("URL_Stream"):
                    iqim = await self.gpdate(vurl, ctx, vdl, "URL_Stream")
                    if self.bot.qu.get(str(ctx.guild.id), None):
                        await ctx.send(f"`{iqim['video_title']}`をキューに追加します。")
                        self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                            ctx.guild.id)] + [iqim]
                        await self.panel_update(ctx)
                    else:
                        await ctx.send(f"`{iqim['video_title']}`の再生を開始します。")
                        self.bot.qu[str(ctx.guild.id)] = [iqim]
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(ctx))
                else:
                    await ctx.send("now,the video can't play the bot",hidden=True)


    async def mplay(self, ctx:SlashContext, vl=0.5):
        v = None
        if not self.bot.lp.get(str(ctx.guild.id), None):
            self.bot.lp[str(ctx.guild.id)] = False
        if not self.bot.mp.get(str(ctx.guild.id), None):
            ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル", color=self.bot.ec)
            ebd.add_field(name="再生中の曲:", value="未読み込み")
            ebd.add_field(name="次の曲:", value="未読み込み")
            ebd.add_field(name="ループ:", value="未読み込み")
            ebd.add_field(name="ボリューム:", value="未読み込み")
            m = await ctx.channel.send(embed=ebd)
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
                await ctx.channel.send("> ステージチャンネルのため、自動的にスピーカーに移動しました。")
            except:
                await ctx.channel.send("> ステージチャンネルのため、音楽を再生するためにはスピーカーに移動させる必要があります。")
        while self.bot.qu[str(ctx.guild.id)]:
            if self.bot.qu[str(ctx.guild.id)][0]["type"] == "download":
                ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                f'musicfile/{self.bot.qu[str(ctx.guild.id)][0]["video_id"]}'), volume=v or vl))
            else:
                ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                self.bot.qu[str(ctx.guild.id)][0]["stream_url"]), volume=v or vl))
            await self.panel_update(ctx)
            try:
                while ctx.guild.voice_client.is_playing() or ctx.guild.voice_client.is_paused():
                    await asyncio.sleep(1)
                    v = ctx.guild.voice_client.source.volume
            except AttributeError:
                pass
            if self.bot.lp[str(ctx.guild.id)]:
                self.bot.qu[str(ctx.guild.id)].append(self.bot.qu[str(ctx.guild.id)][0])
            self.bot.qu[str(ctx.guild.id)].pop(0)
        await ctx.invoke(self.bot.get_command("stop"))

    @cog_slash(name="skip",description="現在再生中の曲をスキップします。",guild_ids=target_guilds)
    async def skip(self, ctx:SlashContext):
        await ctx.defer(hidden=True)
        if ctx.author.voice and ctx.guild.voice_client.is_playing():
            lp = self.bot.lp[str(ctx.guild.id)]
            self.bot.lp[str(ctx.guild.id)] = False
            ctx.guild.voice_client.stop()
            self.bot.lp[str(ctx.guild.id)] = lp
            await ctx.send("曲をスキップしました。",hidden=True)

    @cog_slash(name="volume",description="設定した値にボリュームを調節します。",guild_ids=target_guilds,
        options=[create_option(name="音量",description="設定する音量(0~100)",option_type=4,required=True)]
    )
    async def chvol(self, ctx:SlashContext, **kargs):
        await ctx.defer(hidden=True)
        if ctx.author.voice and ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.source.volume = float(kargs.get("音量"))/100.0
            await ctx.send(f"ボリュームを{ctx.guild.voice_client.source.volume*100.0}に調節しました。",hidden=True)
            await self.panel_update(ctx)

    @cog_slash(name="now_playing",description="現在再生中の音楽について表示します。",guild_ids=target_guilds)
    async def playingmusic(self, ctx:SlashContext):
        await ctx.defer(hidden=True)
        if ctx.guild.voice_client is None:
            return await ctx.send("ボイスチャンネルに参加していません。",hidden=True)
        if ctx.guild.voice_client.is_playing():
            e = discord.Embed(
                title="再生中の曲", description=f'[{self.bot.qu[str(ctx.guild.id)][0]["video_title"]}]({self.bot.qu[str(ctx.guild.id)][0]["video_url"]})\nアップロードチャンネル:[{self.bot.qu[str(ctx.guild.id)][0]["video_up_name"]}]({self.bot.qu[str(ctx.guild.id)][0]["video_up_url"]})\nソース:{self.bot.qu[str(ctx.guild.id)][0]["video_source"]}')
            e.set_thumbnail(
                url=self.bot.qu[str(ctx.guild.id)][0]["video_thumbnail"])
            await ctx.send(embed=e)
        else:
            await ctx.send("再生中の曲はありません。",hidden=True)

    @cog_slash(name="queue",description="再生キューに入っている曲を表示します。",guild_ids=target_guilds)
    async def view_q(self, ctx:SlashContext):
        await ctx.defer(hidden=True)
        if ctx.guild.voice_client is None:
            return await ctx.send("ボイスチャンネルに参加していません。",hidden=True)
        if ctx.guild.voice_client.is_playing():
            page = 0
            pls = [self.bot.qu[str(ctx.guild.id)][5*i:5*(i+1)]
                   for i in range(int(len(self.bot.qu[str(ctx.guild.id)])/5)+1)]
            e = discord.Embed(
                title="キューの中身", description=f"全{len(self.bot.qu[str(ctx.guild.id)])}曲")
            for i in pls[page]:
                e.add_field(
                    name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}')
            e.set_footer(text=f"page:{page+1}/{len(pls)}")
            msg = await ctx.channel.send(embed=e)
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
                        name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}')
                e.set_footer(text=f"page:{page+1}/{len(pls)}")
                await msg.edit(embed=e)
        else:
            await ctx.send("現在キューには何もありません。")

    @cog_slash(name="loop",description="再生キューをループするかどうかを設定します。",guild_ids=target_guilds,
        options=[create_option(name="有効にするかどうか",description="Trueで有効に、Falseで無効にします。(入力しなければ現在の状態を表示します。)",option_type=5,required=False)]
    )
    async def loop_q(self, ctx:SlashContext, **kargs):
        torf = kargs.get("有効にするかどうか",None)
        await ctx.defer(hidden=True)
        if ctx.author.voice:
            if torf is None:
                await ctx.send(f"今のキューのループ状態:{self.bot.lp[str(ctx.guild.id)]}",hidden=True)
            else:
                self.bot.lp[str(ctx.guild.id)] = torf
                await ctx.send(f"きりかえました。\n今のキューのループ状態:{self.bot.lp[str(ctx.guild.id)]}",hidden=True)
                await self.panel_update(ctx)

    @cog_slash(name="panel_update",description="再生パネルを強制的に更新します。",guild_ids=target_guilds)
    async def pupdate(self, ctx):
        await ctx.defer(hidden=True)
        await self.panel_update(ctx)

    async def panel_update(self, ctx):
        ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル",
                            description=f"キューの曲数:{len(self.bot.qu[str(ctx.guild.id)])}曲\nリアクションで操作でき、そのたびに操作パネルが更新されます。\n▶:(一時停止中)再生の再開,⏸:(再生中)一時停止,⏹:ストップ,⏭:スキップ,🔁:ループ切替,🔀次以降の曲のシャッフル,🔼:ボリュームを上げる,🔽:ボリュームを下げる,⬇:パネルを下に持ってくる", color=self.bot.ec)
        if ctx.guild.voice_client.is_paused():
            ebd.add_field(name="現在一時停止中",
                          value="再開には`s-play`か▶リアクション", inline=False)
        ebd.add_field(
            name="再生中の曲:", value=f"[{self.bot.qu[str(ctx.guild.id)][0]['video_title']}]({self.bot.qu[str(ctx.guild.id)][0]['video_url']})(from {self.bot.qu[str(ctx.guild.id)][0]['video_source']})")
        if len(self.bot.qu[str(ctx.guild.id)]) > 1:
            ebd.add_field(
                name="次の曲:", value=f"[{self.bot.qu[str(ctx.guild.id)][1]['video_title']}]({self.bot.qu[str(ctx.guild.id)][0]['video_url']})(from {self.bot.qu[str(ctx.guild.id)][1]['video_source']})")
        elif self.bot.lp[str(ctx.guild.id)]:
            ebd.add_field(
                name="次の曲:", value=f"[{self.bot.qu[str(ctx.guild.id)][0]['video_title']}]({self.bot.qu[str(ctx.guild.id)][0]['video_url']})(from {self.bot.qu[str(ctx.guild.id)][0]['video_source']})(スキップでキューから削除され、再生が止まります。)")
        else:
            ebd.add_field(name="次の曲:", value=f"再生終了")
        ebd.add_field(name="ループ:", value=self.bot.lp[str(ctx.guild.id)])
        try:
            ebd.add_field(name="ボリューム:", value=int(
                ctx.guild.voice_client.source.volume*100))
        except:
            ebd.add_field(name="ボリューム:", value="現在アクセス不可")
        ebd.set_thumbnail(
            url=self.bot.qu[str(ctx.guild.id)][0]["video_thumbnail"])
        try:
            await self.bot.mp[str(ctx.guild.id)].edit(embed=ebd)
        except AttributeError:
            # パネルメッセージが、まだない状態の可能性があるため
            pass


    @cog_slash(name="shuffle",description="再生キューをシャッフルします。",guild_ids=target_guilds)
    async def shuffle_(self, ctx):
        await ctx.defer(hidden=True)
        if self.bot.qu.get(str(ctx.guild.id), None) is not None and len(self.bot.qu[str(ctx.guild.id)]) > 2:
            tmplist = self.bot.qu[str(ctx.guild.id)][1:]
            random.shuffle(tmplist)
            self.bot.qu[str(ctx.guild.id)] = [self.bot.qu[str(ctx.guild.id)][0]] + tmplist
            await ctx.send("> シャッフル\n　シャッフルしました。再生パネルや`s-view_q`,`/queue`でご確認ください。",hidden=True)
        else:
            await ctx.send("> シャッフルエラー\n　シャッフルに必要要件を満たしていません。(VCで音楽再生中で、3曲以上キューに入っている)",hidden=True)


    @cog_slash(name="move_panel",description="他のチャンネルにミュージック操作パネルを移動します。",guild_ids=target_guilds,
        options=[create_option(name="移動先チャンネル",description="音楽再生パネルを移動させたいテキストチャンネルを指定してください。",option_type=7,required=True)]
    )
    async def move_panel(self, ctx:SlashContext, **kargs):
        move_to = kargs.get("移動先チャンネル")
        await ctx.defer(hidden=True)
        if move_to.type == discord.ChannelType.text:
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
            await self.panel_update(ctx)
            await ctx.send(f"> 音楽再生パネルの移動\n　{move_to.mention}に移動しました。",hidden=True)
        else:
            await ctx.send("> 音楽操作パネルの移動\n　不適切なチャンネルタイプ(テキストチャンネルではないもの)が指定されました。",hidden=True)

    @commands.Cog.listener()
    async def on_slash_command(self, ctx:SlashContext):
        ch = self.bot.get_channel(693048961107230811)
        e = discord.Embed(title=f"スラッシュコマンド:{ctx.command}の実行", color=self.bot.ec)
        e.set_author(name=f"実行者:{str(ctx.author)}({ctx.author.id})",
                    icon_url=ctx.author.avatar_url_as(static_format="png"))
        e.set_footer(text=f"実行サーバー:{ctx.guild.name}({ctx.guild.id})",
                    icon_url=ctx.guild.icon_url_as(static_format="png"))
        e.add_field(name="実行チャンネル", value=ctx.channel.name)
        await ch.send(embed=e)
        
    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx:SlashContext, error):
            ch = self.bot.get_channel(652127085598474242)
            await ch.send(embed=ut.getEmbed("エラーログ", f"コマンド:`{ctx.command}`\n```{str(error)}```", self.bot.ec, f"サーバー", ctx.guild.name, "実行メンバー", ctx.author.name))


def setup(bot):
    bot.add_cog(music_slash(bot))
