# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext import tasks,commands

from youtube_dl import YoutubeDL
import youtube_dl

import threading

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import re

#tokens
import config

"""
上のモジュールをインストールすること！

music.py
制作:mii-10#3110(Discord)
クレジットをお願いします。
不具合は上のDiscordアカウントまで。
予告なく、思惟奈ちゃんで使用しているソースと公開しているソースにずれが生じることがあります。
"""

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'musicfile/%(id)s',
    'restrictfilenames': True,
    'noplaylist': True,
    #'dump_single_json' :  True,
    #'extract_flat' : True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}
setA = {
    'format': 'bestaudio/best',
    'outtmpl': 'musicfile/%(id)s',
    'restrictfilenames': True,
    'noplaylist': True,
    #'dump_single_json' :  True,
    'extract_flat' : True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}
GAPI_TOKEN = config.GAPI_TOKEN
rt = None

def rt1(self,url,short=False):
    global rt
    if short:
        rt = self.sydl.extract_info(url, download=True)
    else:
        rt = self.ytdl.extract_info(url, download=True)

class music(commands.Cog):
    """music in discord.py"""

    def __init__(self,bot):
        self.bot = bot
        self.youtube = build('youtube', 'v3', developerKey=GAPI_TOKEN)
        self.ytdl = YoutubeDL(ytdlopts)
        self.sydl = YoutubeDL(setA)
        self.music_loop = {}
        self.music_q = {}
        self.smusic = False


    @commands.command(name="invc",aliases=["join"])
    async def connectVC(self,ctx):
        if ctx.author.voice:
            try:
                await ctx.author.voice.channel.connect()
                await ctx.send(f"チャンネル:{ctx.author.voice.channel.mention}に参加しました。")
            except discord.ClientException:
                await ctx.send("すでにこのサーバーのほかのVCに参加しています！")
        else:
            await ctx.send("あなたが接続中のVCが見当たらないね。")

    @commands.command(name="stop",aliases=["leave"])
    async def disconnectVC(self,ctx):
        if ctx.author.voice:
            self.smusic = True
            try:
                self.music_loop[str(ctx.guild.id)] = None
                self.music_q[str(ctx.guild.id)].clear()
            except KeyError:
                pass
            finally:
                try:
                    await ctx.voice_client.disconnect()
                except:
                    await ctx.send("VC切断が正常に完了しませんでした。")
        else:
            await ctx.send("あなたが接続中のVCが見当たらないね。")     

    @commands.command(aliases=["p"])
    async def play(self,ctx,*,text):
        try:
            if ctx.voice_client is None:
                await ctx.invoke(self.bot.get_command("invc"))
        except:
            pass
        if text.startswith("https://"):
            url=text
        else:
            search_response = self.youtube.search().list(
            part='snippet',
            q=text,
            type='video'
            ).execute()
            vid = search_response['items'][0]['id']['videoId']
            url=f"https://www.youtube.com/watch?v={vid}"
        if ctx.author.voice:
            async with ctx.message.channel.typing():
                try:
                    t1 = threading.Thread(target=rt1,args=[self,url,True])
                    t1.start()
                    if self.music_loop.get(str(ctx.guild.id),None) is None:
                        self.music_loop[str(ctx.guild.id)] = False
                    t1.join()
                except youtube_dl.utils.ExtractorError:
                    await ctx.send("再生できない曲です。")
                    return
                except youtube_dl.utils.DownloadError:
                    await ctx.send("再生できない曲です。")
                    return
                #print (rt)
                log = rt
            if log["extractor"].startswith("youtube"):
                if log.get("_type",None) == "playlist":
                    m = await ctx.send("プレイリストから曲を読み込みます。しばらくお待ちください…。")
                    plist = log["entries"]
                    in_q = []
                    for ctt in plist:
                        try:
                            await m.add_reaction("🔄")
                            t1 = threading.Thread(target=rt1,args=[self,"https://www.youtube.com/watch?v="+ctt["id"]])
                            t1.start()
                            t1.join()
                            v = rt
                            in_q.append({
                                "video_id":v['id'],
                                "video_url":v['webpage_url'],
                                "video_title":v['title'],
                                "video_thumbnail":v['thumbnail'],
                                "video_up_name":v["uploader"],
                                "video_up_url":v["uploader_url"],
                                "video_source":"Youtube"
                            })
                        except:
                            pass
                        await m.remove_reaction("🔄",self.bot.user)
                        await asyncio.sleep(1)
                    if not ctx.voice_client.is_playing():
                        try:
                            await ctx.send(f"キューに次の項目を追加し、再生を開始します。:`{'`,`'.join([i['video_title'] for i in in_q])}`")
                        except:
                            await ctx.send(f"キューに項目を追加し、再生を開始します。:{in_q[0]['video_title']}など")
                        self.music_q[str(ctx.guild.id)] = in_q
                        self.bot.loop.create_task(self.play_music_q(ctx))
                    else:
                        try:
                            await ctx.send(f"キューに曲を追加しました。:`{'`,`'.join([i['video_title'] for i in in_q])}``")
                        except:
                            await ctx.send(f"キューに曲を追加しました。:{in_q[0]['video_title']}など")
                        self.music_q[str(ctx.guild.id)] = self.music_q[str(ctx.guild.id)]+[in_q]
                else:
                    try:
                        t1 = threading.Thread(target=rt1,args=[self,url])
                        t1.start()
                        t1.join()
                    except youtube_dl.utils.ExtractorError:
                        await ctx.send("再生できない曲です。")
                        return
                    except youtube_dl.utils.DownloadError:
                        await ctx.send("再生できない曲です。")
                        return
                    log = rt
                    in_q = {
                        "video_id":log['id'],
                        "video_url":log['webpage_url'],
                        "video_title":log['title'],
                        "video_thumbnail":log['thumbnail'],
                        "video_up_name":log["uploader"],
                        "video_up_url":log["uploader_url"],
                        "video_source":"Youtube"
                    }
                    if not ctx.voice_client.is_playing():
                        await ctx.send(f"再生を開始します。:{in_q['video_title']}")
                        self.music_q[str(ctx.guild.id)] = [in_q]
                        self.bot.loop.create_task(self.play_music_q(ctx))
                    else:
                        await ctx.send(f"キューに曲を追加しました。:{in_q['video_title']}")
                        self.music_q[str(ctx.guild.id)] = self.music_q[str(ctx.guild.id)]+[in_q]
            elif log["extractor"] == "niconico":
                try:
                    t1 = threading.Thread(target=rt1,args=[self,url])
                    t1.start()
                    t1.join()
                except youtube_dl.utils.ExtractorError:
                    await ctx.send("再生できない曲です。")
                    return
                except youtube_dl.utils.DownloadError:
                    await ctx.send("再生できない曲です。")
                    return
                log = rt
                in_q = {
                    "video_id":log['id'],
                    "video_url":log['webpage_url'],
                    "video_title":log['title'],
                    "video_thumbnail":log['thumbnail'],
                    "video_up_name":log["uploader"],
                    "video_up_url":"https://www.nicovideo.jp/user/"+log["uploader_id"],
                    "video_source":"niconico"
                }
                if not ctx.voice_client.is_playing():
                    await ctx.send(f"再生を開始します。:{in_q['video_title']}")
                    self.music_q[str(ctx.guild.id)] = [in_q]
                    self.bot.loop.create_task(self.play_music_q(ctx))
                else:
                    await ctx.send(f"キューに曲を追加しました。:{in_q['video_title']}")
                    self.music_q[str(ctx.guild.id)] = self.music_q[str(ctx.guild.id)]+[in_q]
            elif log["extractor"].startswith("soundcloud"):
                if log.get("_type",None) == "playlist":
                    m = await ctx.send("プレイリストから曲を読み込みます。しばらくお待ちください…。")
                    plist = log["entries"]
                    in_q = []
                    for ctt in plist:
                        try:
                            await m.add_reaction("🔄")
                            t1 = threading.Thread(target=rt1,args=[self,ctt["url"]])
                            t1.start()
                            t1.join()
                            v = rt
                            in_q.append({
                                "video_id":v['id'],
                                "video_url":v['webpage_url'],
                                "video_title":v['title'],
                                "video_thumbnail":v['thumbnail'],
                                "video_up_name":v["uploader"],
                                "video_up_url":v["webpage_url"],  #re.match("(https://soundcloud\.com/.+?)/.+",v["webpage_url"]).group(0),
                                "video_source":"SoundCloud"
                            })
                        except:
                            pass
                        await m.remove_reaction("🔄",self.bot.user)
                        await asyncio.sleep(1)
                    if not ctx.voice_client.is_playing():
                        try:
                            await ctx.send(f"キューに次の項目を追加し、再生を開始します。:`{'`,`'.join([i['video_title'] for i in in_q])}`")
                        except:
                            await ctx.send(f"キューに項目を追加し、再生を開始します。:{in_q[0]['video_title']}など")
                        self.music_q[str(ctx.guild.id)] = in_q
                        self.bot.loop.create_task(self.play_music_q(ctx))
                    else:
                        try:
                            await ctx.send(f"キューに曲を追加しました。:`{'`,`'.join([i['video_title'] for i in in_q])}``")
                        except:
                            await ctx.send(f"キューに曲を追加しました。:{in_q[0]['video_title']}など")
                        self.music_q[str(ctx.guild.id)] = self.music_q[str(ctx.guild.id)]+[in_q]
                else:
                    try:
                        t1 = threading.Thread(target=rt1,args=[self,url])
                        t1.start()
                        t1.join()
                    except youtube_dl.utils.ExtractorError:
                        await ctx.send("再生できない曲です。")
                        return
                    except youtube_dl.utils.DownloadError:
                        await ctx.send("再生できない曲です。")
                        return
                    log = rt
                    in_q = {
                        "video_id":log['id'],
                        "video_url":log['webpage_url'],
                        "video_title":log['title'],
                        "video_thumbnail":log['thumbnail'],
                        "video_up_name":log["uploader"],
                        "video_up_url":log["webpage_url"],  #re.match("(https://soundcloud\.com/.+?)/.+",log["webpage_url"]).group(0),
                        "video_source":"SoundCloud"
                    }
                    if not ctx.voice_client.is_playing():
                        await ctx.send(f"再生を開始します。:{in_q['video_title']}")
                        self.music_q[str(ctx.guild.id)] = [in_q]
                        self.bot.loop.create_task(self.play_music_q(ctx))
                    else:
                        await ctx.send(f"キューに曲を追加しました。:{in_q['video_title']}")
                        self.music_q[str(ctx.guild.id)] = self.music_q[str(ctx.guild.id)]+[in_q]
        else:
            await ctx.send("あなたが接続中のVCが見当たらないね。")


    @commands.command(aliases=["np"])
    async def playingmusic(self,ctx):
        if ctx.voice_client.is_playing():
            e = discord.Embed(title="再生中の曲",description=f'[{self.music_q[str(ctx.guild.id)][0]["video_title"]}]({self.music_q[str(ctx.guild.id)][0]["video_url"]})\nアップロードチャンネル:[{self.music_q[str(ctx.guild.id)][0]["video_up_name"]}]({self.music_q[str(ctx.guild.id)][0]["video_up_url"]})\nソース:{self.music_q[str(ctx.guild.id)][0]["video_source"]}')
            e.set_thumbnail(url=self.music_q[str(ctx.guild.id)][0]["video_thumbnail"])
            await ctx.send(embed=e)
        else:
            await ctx.send("再生中の曲はありません。")

    @commands.command(aliases=["plist"])
    async def view_q(self,ctx,page=1):
        if ctx.voice_client.is_playing():
            e=discord.Embed(title="キューにある曲:",description=f'{len(self.music_q[str(ctx.guild.id)])}\n{1+(page-1)*5}から{5+(page-1)*5}',color=0x42bcf4)
            for x in range(5):
                try:
                    e.add_field(name=self.music_q[str(ctx.guild.id)][x+(page-1)*5]["video_title"],value=f'[動画]({self.music_q[str(ctx.guild.id)][x+(page-1)*5]["video_url"]})/[アップロードチャンネル]({self.music_q[str(ctx.guild.id)][x+(page-1)*5]["video_up_url"]})\nソース:{self.music_q[str(ctx.guild.id)][0]["video_source"]}')
                except IndexError:
                    break
            await ctx.send(embed=e)
        else:
            await ctx.send("現在キューには何もありません。")

    @commands.command(aliases=["loop","repeat"])
    async def loop_q(self,ctx,torf:bool=None):
        if ctx.author.voice:
            if torf is None:
                await ctx.send(f"今のキューのループ状態:{self.music_loop[str(ctx.guild.id)]}")
            else:
                self.music_loop[str(ctx.guild.id)] = torf
                await ctx.send(f"きりかえました。\n今のキューのループ状態:{self.music_loop[str(ctx.guild.id)]}")

    @commands.command(aliases=["pass"])
    async def skip(self,ctx):
        if ctx.author.voice and ctx.voice_client.is_playing():
            v = ctx.voice_client.source.volume
            self.smusic = True
            tmp_q = self.music_q[str(ctx.guild.id)]
            tmp_q.pop(0)
            self.music_q[str(ctx.guild.id)] = []
            ctx.voice_client.stop()
            await ctx.send("曲をスキップしました。")
            self.music_q[str(ctx.guild.id)] = tmp_q
            self.bot.loop.create_task(self.play_music_q(ctx,v))

    @commands.command(aliases=["vol"])
    async def chvol(self,ctx,vol:float):
        if ctx.author.voice and ctx.voice_client.is_playing():
            ctx.voice_client.source.volume = vol/100.0
            await ctx.send("ボリュームを調節しました。")

    async def play_music_q(self,ctx,vol=1.0):
        self.smusic = False
        while not self.music_q[str(ctx.guild.id)] == []:
            try:
                v = ctx.voice_client.source.volume
            except:
                v=None
            if v:
                ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(f'musicfile/{self.music_q[str(ctx.guild.id)][0]["video_id"]}'),volume=v))
            else:
                try:
                    ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(f'musicfile/{self.music_q[str(ctx.guild.id)][0]["video_id"]}'),volume=vol))
                except AttributeError:
                    ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(f'musicfile/{self.music_q[str(ctx.guild.id)][0]["video_id"]}'),volume=1.0))
            while ctx.voice_client.is_playing():
                await asyncio.sleep(1)
            if self.smusic:
                return
            if self.music_loop[str(ctx.guild.id)]:
                self.music_q[str(ctx.guild.id)] = self.music_q[str(ctx.guild.id)] + [self.music_q[str(ctx.guild.id)][0]]
            self.music_q[str(ctx.guild.id)].pop(0)


def setup(bot):
    bot.add_cog(music(bot))
