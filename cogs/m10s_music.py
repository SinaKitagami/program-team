# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

from apiclient.discovery import build

import os
import shutil
import re

"""
上のモジュールをインストールすること！

m10s_music.py
制作:mii-10#3110(Discord)
"""

ytdlopts = {
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
        self.bot.qu = {}
        self.bot.lp = {}
        self.bot.mp = {}

    async def gvinfo(self, url, dl=False):
        loop = self.bot.loop or asyncio.get_event_loop()
        dt = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=dl))
        return dt

    async def gpdate(self, url, dl=True, utype="Youtube"):
        v = await self.gvinfo(url, dl)
        if utype == "Youtube":
            return {
                "type": "download" if dl else "stream",
                "video_id": v['id'],
                "video_url": v['webpage_url'],
                "video_title": v['title'],
                "video_thumbnail": v['thumbnail'],
                "video_up_name": v["uploader"],
                "video_up_url": v["uploader_url"],
                "video_source": "Youtube"
            }
        elif utype == "niconico":
            return {
                "type": "download" if dl else "stream",
                "video_id": v['id'],
                "video_url": v['webpage_url'],
                "video_title": v['title'],
                "video_thumbnail": v['thumbnail'],
                "video_up_name": v["uploader"],
                "video_up_url": "https://www.nicovideo.jp/user/"+v["uploader_id"],
                "video_source": "niconico"
            }
        elif utype == "soundcloud":
            return {
                "video_id": v['id'],
                "video_url": v['webpage_url'],
                "video_title": v['title'],
                "video_thumbnail": v['thumbnail'],
                "video_up_name": v["uploader"],
                "video_up_url": re.match(r"(https://soundcloud\.com/.+?/)", v['webpage_url']).group(0),
                "video_source": "SoundCloud"
            }

    @commands.command(name="join", aliases=["invc"])
    async def join_(self, ctx):
        if ctx.author.voice:
            if ctx.voice_client:
                await ctx.send(f"{ctx.voice_client.channel.name}に接続しました。")
            else:
                try:
                    await ctx.author.voice.channel.connect()
                except asyncio.TimeoutError:
                    await ctx.send("接続のタイムアウト！")
        else:
            await ctx.send("あなたがボイスチャンネルに接続していません！")

    @commands.command(name="stop", aliases=["leave"])
    async def stop_(self, ctx):
        if ctx.voice_client and ctx.author.voice:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                try:
                    await self.bot.mp[str(ctx.guild.id)].delete()
                except:
                    await ctx.send("操作パネルを削除できませんでした。")
                self.bot.qu[str(ctx.guild.id)] = None
                self.bot.mp[str(ctx.guild.id)] = None
                self.bot.lp[str(ctx.guild.id)] = None
                await ctx.voice_client.disconnect()
                await ctx.send("切断しました。")

    @commands.command(name="pause")
    async def pause_(self, ctx):
        if ctx.voice_client and ctx.author.voice:
            ctx.voice_client.pause()
            await ctx.send("一時停止しました。ボイスチャットを出ても構いません。")
            await self.panel_update(ctx)

    @commands.command(name="play", aliases=["p"])
    async def play_(self, ctx, *, text: str=""):
        if not ctx.voice_client:
            await ctx.invoke(self.bot.get_command("join"))
            if not ctx.voice_client:
                return
        if ctx.voice_client.is_paused():
            await ctx.send("再生を再開しました。")
            ctx.voice_client.resume()
            await self.panel_update(ctx)
            return
        if text == "":
            await ctx.send("URL/曲名が未指定です。また、現在リアクションからの追加はできません。")
            return
        async with ctx.typing():
            if text.startswith("http://") or text.startswith("https://"):
                vurl = text
            else:
                search_response = self.youtube.search().list(
                    part='snippet',
                    q=text,
                    type='video'
                ).execute()
                vid = search_response['items'][0]['id']['videoId']
                if vid:
                    vurl = f"https://www.youtube.com/watch?v={vid}"
                else:
                    return await ctx.send("動画が見つかりませんでした。")
            if not vurl:
                return
            vinfo = await self.gvinfo(vurl, False)
            if vinfo.get("extractor", "").startswith("youtube"):
                if vinfo.get("_type", None) == "playlist":
                    tks = []
                    for c in vinfo["entries"]:
                        tks.append(self.gpdate(
                            f"https://www.youtube.com/watch?v={c['id']}", True))
                    iqlt = [i for i in await asyncio.gather(*tks) if i]
                    if self.bot.qu.get(str(ctx.guild.id), None):
                        await ctx.send("キューにプレイリスト内の動画を追加します。")
                        self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                            ctx.guild.id)] + iqlt
                        await self.panel_update(ctx)
                    else:
                        await ctx.send("プレイリストより、再生を開始します。")
                        self.bot.qu[str(ctx.guild.id)] = iqlt
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(ctx))
                else:
                    iqim = await self.gpdate(vurl, True)
                    if self.bot.qu.get(str(ctx.guild.id), None):
                        await ctx.send("キューに追加します。")
                        self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                            ctx.guild.id)] + [iqim]
                        await self.panel_update(ctx)
                    else:
                        await ctx.send("再生を開始します。")
                        self.bot.qu[str(ctx.guild.id)] = [iqim]
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(ctx))
            elif vinfo.get("extractor", "") == "niconico":
                iqim = await self.gpdate(vurl, True, "niconico")
                if self.bot.qu.get(str(ctx.guild.id), None):
                    await ctx.send("キューに追加します。")
                    self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                        ctx.guild.id)] + [iqim]
                    await self.panel_update(ctx)
                else:
                    await ctx.send("再生を開始します。")
                    self.bot.qu[str(ctx.guild.id)] = [iqim]
                    await asyncio.sleep(0.3)
                    self.bot.loop.create_task(self.mplay(ctx))
            elif vinfo.get("extractor", "").startswith("soundcloud"):
                if vinfo.get("_type", None) == "playlist":

                    tks = []
                    for c in vinfo["entries"]:
                        tks.append(self.gpdate(c["url"], True, "soundcloud"))
                    iqlt = [i for i in await asyncio.gather(*tks) if i]
                    if self.bot.qu.get(str(ctx.guild.id), None):
                        await ctx.send("キューにプレイリスト内の動画を追加します。")
                        self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                            ctx.guild.id)] + iqlt
                        await self.panel_update(ctx)
                    else:
                        await ctx.send("プレイリストより、再生を開始します。")
                        self.bot.qu[str(ctx.guild.id)] = iqlt
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(ctx))

                else:
                    iqim = await self.gpdate(vurl, True, "soundcloud")
                    if self.bot.qu.get(str(ctx.guild.id), None):
                        await ctx.send("キューに追加します。")
                        self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                            ctx.guild.id)] + [iqim]
                        await self.panel_update(ctx)
                    else:
                        await ctx.send("再生を開始します。")
                        self.bot.qu[str(ctx.guild.id)] = [iqim]
                        await asyncio.sleep(0.3)
                        self.bot.loop.create_task(self.mplay(ctx))
            else:
                await ctx.send("now,the video can't play the bot")

    async def mplay(self, ctx, vl=0.5, lp=False):
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
            await m.add_reaction("▶")
            await m.add_reaction("⏸")
            await m.add_reaction("⏹")
            await m.add_reaction("⏭")
            await m.add_reaction("🔁")
            await m.add_reaction("🔼")
            await m.add_reaction("🔽")
            await m.add_reaction("⬇")
            self.bot.mp[str(ctx.guild.id)] = m
            try:
                await m.pin()
            except:
                pass
        while self.bot.qu[str(ctx.guild.id)]:
            if v:
                ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                    f'musicfile/{self.bot.qu[str(ctx.guild.id)][0]["video_id"]}'), volume=v))
            else:
                ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                    f'musicfile/{self.bot.qu[str(ctx.guild.id)][0]["video_id"]}'), volume=vl))
            await self.panel_update(ctx)
            try:
                while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                    await asyncio.sleep(1)
                    v = ctx.voice_client.source.volume
            except AttributeError:
                break
            if self.bot.lp[str(ctx.guild.id)]:
                self.bot.qu[str(ctx.guild.id)] = self.bot.qu[str(
                    ctx.guild.id)] + [self.bot.qu[str(ctx.guild.id)][0]]
            self.bot.qu[str(ctx.guild.id)].pop(0)
        await ctx.invoke(self.bot.get_command("stop"))

    @commands.command()
    async def skip(self, ctx):
        if ctx.author.voice and ctx.voice_client.is_playing():
            v = ctx.voice_client.source.volume
            lp = self.bot.lp[str(ctx.guild.id)]
            self.bot.lp[str(ctx.guild.id)] = False
            ctx.voice_client.stop()
            self.bot.lp[str(ctx.guild.id)] = lp
            await ctx.send("曲をスキップしました。")

    @commands.command(aliases=["vol"])
    async def chvol(self, ctx, vol: float):
        if ctx.author.voice and ctx.voice_client.is_playing():
            ctx.voice_client.source.volume = vol/100.0
            await ctx.send("ボリュームを調節しました。")
            await self.panel_update(ctx)

    @commands.command(aliases=["np"])
    async def playingmusic(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("ボイスチャンネルに参加していません。")
        if ctx.voice_client.is_playing():
            e = discord.Embed(
                title="再生中の曲", description=f'[{self.bot.qu[str(ctx.guild.id)][0]["video_title"]}]({self.bot.qu[str(ctx.guild.id)][0]["video_url"]})\nアップロードチャンネル:[{self.bot.qu[str(ctx.guild.id)][0]["video_up_name"]}]({self.bot.qu[str(ctx.guild.id)][0]["video_up_url"]})\nソース:{self.bot.qu[str(ctx.guild.id)][0]["video_source"]}')
            e.set_thumbnail(
                url=self.bot.qu[str(ctx.guild.id)][0]["video_thumbnail"])
            await ctx.send(embed=e)
        else:
            await ctx.send("再生中の曲はありません。")

    @commands.command(aliases=["plist", "queue"])
    async def view_q(self, ctx, pg=1):
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
                    name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}')
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
                        name=i["video_title"], value=f'[動画]({i["video_url"]})/[アップロードチャンネル]({i["video_up_url"]})\nソース:{i["video_source"]}')
                e.set_footer(text=f"page:{page+1}/{len(pls)}")
                await msg.edit(embed=e)
        else:
            await ctx.send("現在キューには何もありません。")

    @commands.command(aliases=["loop", "repeat"])
    async def loop_q(self, ctx, torf: bool=None):
        if ctx.author.voice:
            if torf is None:
                await ctx.send(f"今のキューのループ状態:{self.bot.lp[str(ctx.guild.id)]}")
            else:
                self.bot.lp[str(ctx.guild.id)] = torf
                await ctx.send(f"きりかえました。\n今のキューのループ状態:{self.bot.lp[str(ctx.guild.id)]}")
                await self.panel_update(ctx)

    @commands.command()
    async def pupdate(self, ctx):
        await self.panel_update(ctx)

    async def panel_update(self, ctx):
        ebd = discord.Embed(title="思惟奈ちゃん-ミュージック操作パネル",
                            description=f"キューの曲数:{len(self.bot.qu[str(ctx.guild.id)])}曲\nリアクションで操作でき、そのたびに操作パネルが更新されます。\n▶:(一時停止中)再生の再開,⏸:(再生中)一時停止,⏹:ストップ,⏭:スキップ,🔁:ループ切替,🔼:ボリュームを上げる,🔽:ボリュームを下げる,⬇:パネルを下に持ってくる", color=self.bot.ec)
        if ctx.voice_client.is_paused():
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
                ctx.voice_client.source.volume*100))
        except:
            ebd.add_field(name="ボリューム:", value="現在アクセス不可")
        ebd.set_thumbnail(
            url=self.bot.qu[str(ctx.guild.id)][0]["video_thumbnail"])
        await self.bot.mp[str(ctx.guild.id)].edit(embed=ebd)

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
            msg.author = pr.member
            ctx = await self.bot.get_context(msg)
            r = pr
            u = pr.member
            if str(r.emoji) == "▶":
                await ctx.invoke(self.bot.get_command("play"))
            elif str(r.emoji) == "⏸":
                await ctx.invoke(self.bot.get_command("pause"))
            elif str(r.emoji) == "⏹":
                await ctx.invoke(self.bot.get_command("stop"))
            elif str(r.emoji) == "⏭":
                await ctx.invoke(self.bot.get_command("skip"))
            elif str(r.emoji) == "🔁":
                if self.bot.lp[str(u.guild.id)]:
                    await ctx.invoke(self.bot.get_command("loop"), False)
                else:
                    await ctx.invoke(self.bot.get_command("loop"), True)
            elif str(r.emoji) == "🔼":
                await ctx.invoke(self.bot.get_command("chvol"), int(ctx.voice_client.source.volume*100+10))
            elif str(r.emoji) == "🔽":
                await ctx.invoke(self.bot.get_command("chvol"), int(ctx.voice_client.source.volume*100-10))
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
                await m.add_reaction("🔼")
                await m.add_reaction("🔽")
                await m.add_reaction("⬇")
                try:
                    await m.pin()
                except:
                    pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            if not member.guild.voice_client.is_paused() and [i for i in member.guild.me.voice.channel.members if not i.bot] == []:
                try:
                    await self.bot.mp[str(member.guild.id)].delete()
                except:
                    await self.bot.mp[str(member.guild.id)].channel.send("操作パネルを削除できませんでした。")
                self.bot.qu[str(member.guild.id)] = None
                self.bot.mp[str(member.guild.id)] = None
                self.bot.lp[str(member.guild.id)] = None
                await member.guild.voice_client.disconnect()
        except:
            pass
        try:
            if self.bot.voice_clients == []:
                shutil.rmtree("musicfile/")
                os.makedirs('musicfile/', exist_ok=True)
        except:
            pass


def setup(bot):
    bot.add_cog(music(bot))
