# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json
import random
from apiclient.discovery import build
import wikipedia
import time
import asyncio
from dateutil.relativedelta import relativedelta as rdelta

import m10s_util as ut

import config as cf

import traceback

class search(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getby(self, ctx, k: str):
        await ctx.send(embed=ut.getEmbed("", ctx._(k)))

    @commands.command(name="checkscrauname")
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def scrauname(self, ctx, un: str):
        if not ctx.user_lang() == "ja":
            await ctx.send(ctx._("cannot-run"))
            return

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        try:
            async with ctx.message.channel.typing():
                url = f'https://scratch.mit.edu/accounts/check_username/{un}'
                content = await self.bot.apple_util.get_as_json(url)
                print(content)
            await ctx.send(embed=discord.Embed(title=f"Scratchでのユーザー名:\'{content[0]['username']}\'の使用可能状態", description=f"{content[0]['msg']}({content[0]['msg'].replace('username exists','存在するため使用不可').replace('bad username','検閲により使用不可').replace('invalid username','無効なユーザー名').replace('valid username','使用可能')})"))
        except:
            await ctx.send("何らかの例外が発生しました。")

    @commands.command(aliases=["twitter", "twitterで検索して"])
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    async def twisearch(self, ctx, *, word: str):
        try:
            async with ctx.message.channel.typing():
                ret = self.bot.twi.search.tweets(
                    q=word, result_type="recent", lang="ja", count=1)
                tweet = ret["statuses"][0]
                embed = discord.Embed(description=tweet["text"], color=int(
                    tweet["user"]["profile_background_color"], 16))
                embed.set_author(name=f'{tweet["user"]["name"]}(@{tweet["user"]["screen_name"]})',
                                 url=f'https://twitter.com/{tweet["user"]["screen_name"]}', icon_url=tweet["user"]["profile_image_url_https"])
                try:
                    embed.set_image(
                        url=tweet["entities"]["media"][0]["media_url_https"])
                except:
                    pass
                embed.add_field(name=ctx._(
                    "twi-see"), value=f'{self.bot.get_emoji(653161518451392512)} https://twitter.com/{tweet["user"]["screen_name"]}/status/{tweet["id"]}')
            await ctx.send(embed=embed)
        except:
            await ctx.send(ctx._("twi-error"))
            # await ctx.send(embed=ut.getEmbed("traceback",traceback.format_exc(3)))

    @commands.command(aliases=["wikipedia", "次の言葉でwikipedia調べて"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def jwp(self, ctx):
        try:
            async with ctx.message.channel.typing():
                wd = ctx.message.content.replace("s-jwp ", "")
                sw = wikipedia.search(wd, results=1)
                sw1 = sw[0].replace(" ", "_")
                sr = wikipedia.page(sw1)
                embed = discord.Embed(
                    title=sw1, description=sr.summary, color=self.bot.ec)
                embed.add_field(name=ctx._("jwp-seemore"),
                                value=f"https://ja.wikipedia.org/wiki/{sw1}")
                try:
                    embed.set_image(url=sr.images[0])
                except:
                    pass
            await ctx.send(embed=embed)
        except:
            try:
                async with ctx.message.channel.typing():
                    if not sw is None:
                        await ctx.send(ctx._("jwp-found", wd, sw1))
            except:
                await ctx.send(ctx._("jwp-notfound"))

    @commands.command(aliases=["天気", "今日の天気は"])
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    async def jpwt(self, ctx):

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if ctx.channel.permissions_for(ctx.guild.me).attach_files is True:
            try:
                async with ctx.message.channel.typing():
                    content = await self.bot.apple_util.get_as_binary("http://www.jma.go.jp/jp/yoho/images/000_telop_today.png")
                    with open("imgs/weather.png", 'wb') as f:
                        f.write(content)
                    await ctx.send(file=discord.File("imgs/weather.png"))
                    await ctx.send(ctx._("jpwt-credit"))
            except:
                await ctx.send(ctx._("jpwt-error"))
        else:
            try:
                await ctx.send(embed=discord.Embed(title=ctx._("dhaveper"), description=ctx._("per-sendfile")))
            except:
                await ctx.send(f"{ctx._('dhaveper')}\n{ctx._('per-sendfile')}")

    @commands.command(aliases=["ニュース", "ニュースを見せて"])
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    async def news(self, ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        content = await self.bot.apple_util.get_as_json('https://newsapi.org/v2/top-headlines?country=jp&pagesize=5&apiKey='+self.bot.NAPI_TOKEN)
        embeds=[]
        for i in content['articles']:
            e=discord.Embed(title=i["title"],description=i["description"],color=self.bot.ec)
            e.add_field(name="もっと見る",value=i["url"])
            e.set_author(name=i["author"])
            e.set_footer(text=f"{i['content']}·using `https://newsapi.org/`")
            e.set_image(url=i["urlToImage"])
            embeds.append(e)
        page=0
        msg = await ctx.send(embed=embeds[0])
        await msg.add_reaction(self.bot.get_emoji(653161518195671041))
        await msg.add_reaction(self.bot.get_emoji(653161518170505216))
        while True:
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
            except:
                break
            try:
                await msg.remove_reaction(r, u)
            except:
                pass
            if str(r) == str(self.bot.get_emoji(653161518170505216)):
                if page == 4:
                    page = 0
                else:
                    page = page + 1
            elif str(r) == str(self.bot.get_emoji(653161518195671041)):
                if page == 0:
                    page = 4
                else:
                    page = page - 1
            await msg.edit(embed=embeds[page])

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def gwd(self, ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        try:
            async with ctx.message.channel.typing():
                str1 = ctx.message.content.replace("s-gwd ", "")
                sjson = await self.bot.apple_util.get_as_json("https://www.wikidata.org/w/api.php?action=wbsearchentities&search="+str1+"&language=en&format=json")
                sid = sjson["search"][0]["id"]
                purjson = await self.bot.apple_util.get_as_json("https://www.wikidata.org/w/api.php?action=wbsearchentities&search="+str1+"&language=en&format=json")
                purl = purjson["search"][0]["concepturi"]
                sret = self.bot.mwc.get(
                    sid, load=True).attributes["claims"]["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
                vsd = sret.replace("+", "")
                vsd = vsd.replace("-", "/")
                vsd = vsd.replace("T00:00:00Z", "")
            await ctx.send(ctx._("gwd-return1", str1, vsd, purl))
        except:
            await ctx.send(ctx._("gwd-return2"))

    @commands.command()
    @commands.cooldown(1, 80)
    async def gupd(self, ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        content = await self.bot.apple_util.get_as_json('https://ja.scratch-wiki.info/w/api.php?action=query&list=recentchanges&rcprop=title|timestamp|user|comment|flags|sizes&format=json')
        await ctx.send(ctx._("gupd-send"))
        for i in range(5):
            try:
                embed = discord.Embed(title=ctx._(
                    "gupd-page"), description=content["query"]['recentchanges'][i]["title"], color=self.bot.ec)
                embed.add_field(name=ctx._("gupd-editor"),
                                value=content["query"]['recentchanges'][i]["user"])
                embed.add_field(name=ctx._("gupd-size"), value=str(content["query"]['recentchanges'][i]["oldlen"])+"→"+str(
                    content["query"]['recentchanges'][i]["newlen"])+"("+str(content["query"]['recentchanges'][i]["newlen"]-content["query"]['recentchanges'][i]["oldlen"])+")")
                embed.add_field(name=ctx._(
                    "gupd-type"), value=content["query"]['recentchanges'][i]["type"])
                if not content["query"]['recentchanges'][i]["comment"] == "":
                    embed.add_field(name=ctx._(
                        "gupd-comment"), value=content["query"]['recentchanges'][i]["comment"])
                else:
                    embed.add_field(name=ctx._("gupd-comment"),
                                    value=ctx._("gupd-notcomment"))
                embed.add_field(name=ctx._("gupd-time"), value=content["query"]['recentchanges'][i]["timestamp"].replace(
                    "T", " ").replace("Z", "").replace("-", "/"))
                await ctx.send(embed=embed)
            except:
                eembed = discord.Embed(title=ctx._(
                    "gupd-unknown"), description=ctx._("gupd-url"), color=self.bot.ec)
                await ctx.send(embed=eembed)

    @commands.command(aliases=["次の言葉でyoutube調べて"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def youtube(self, ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        try:
            async with ctx.message.channel.typing():
                wd = ctx.message.content.replace("s-youtube ", "")
                youtube = build('youtube', 'v3',
                                developerKey=self.bot.GAPI_TOKEN)
                search_response = youtube.search().list(
                    part='snippet',
                    q=wd,
                    type='video'
                ).execute()
                id = search_response['items'][0]['id']['videoId']
                await ctx.send(ctx._("youtube-found", id))
        except:
            await ctx.send(ctx._("youtube-notfound"))

    @commands.command(name="scranotif", aliases=["snotify", "Scratchの通知", "Scratchの通知を調べて"])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def scranotif(self, ctx, un: str):

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        try:
            async with ctx.message.channel.typing():
                url = 'https://api.scratch.mit.edu/users/'+un+'/messages/count'
                content = await self.bot.apple_util.get_as_json(url)
                await ctx.send(ctx._("scranotif-notify", un, str(content['count'])))
        except:
            await ctx.send(ctx._("scranotif-badrequest"))

    @commands.command()
    @commands.cooldown(2, 10, type=commands.BucketType.user)
    async def wid(self, ctx, inid):
        if not ctx.user_lang() == "ja":
            await ctx.send(ctx._("cannot-run"))
            return

        async with ctx.message.channel.typing():
            st = time.time()
            try:
                id = int(inid)
            except:
                id = None
            idis = self.bot.get_channel(id)
            if idis:
                if isinstance(idis, discord.DMChannel):
                    await ctx.send(embed=ut.getEmbed("DMチャンネル", f"相手:{idis.recipient}"))
                elif isinstance(idis, discord.GroupChannel):
                    await ctx.send(embed=ut.getEmbed("グループDMチャンネル", f"メンバー:{','.join(idis.recipients)},\n名前:{idis.name},"))
                elif isinstance(idis, discord.abc.GuildChannel):
                    await ctx.send(embed=ut.getEmbed("サーバーチャンネル", f"名前:{idis.name}\nサーバー:{idis.guild}"))
                else:
                    await ctx.send(embed=ut.getEmbed("その他チャンネル", f"名前:{idis.name}"))
                return
            idis = self.bot.get_guild(id)
            if idis:
                self.bot.cursor.execute("select * from guilds where id = ?",(ctx.guild.id,))
                gp = self.bot.cursor.fetchone()
                if gp["verified"]:
                    ptn = f'{ctx._("sina_verified_guild")}:'
                else:
                    ptn = ""
                if "PARTNER" in ctx.guild.features:
                    ptn = ptn+f'{ctx._("discord_partner_guild")}:'
                await ctx.send(embed=ut.getEmbed("サーバー", f"{ptn}\n名前:{idis.name}\nid:{idis.id}"))
                return
            try:
                idis = await self.bot.fetch_user(id)
                u = idis
                info = ""
                if u.id in self.bot.team_sina:
                    info = f',({ctx._("team_sina-chan")})'
                if u.id in cf.partner_ids:
                        info = info+f"、(🔗{ctx._('sina_parnter_bot')})"
                e = discord.Embed(title="ユーザー", description=info, color=self.bot.ec)
                if u.system:
                    e.add_field(
                        name="✅システムアカウント", value="このアカウントは、Discordのシステムアカウントであり、安全です。", inline=False)
                e.add_field(name="名前", value=u.name)
                e.add_field(name="id", value=u.id)
                e.add_field(name="ディスクリミネータ", value=u.discriminator)
                e.add_field(name="botかどうか", value=u.bot)

                e.set_thumbnail(url=u.avatar_url)
                e.set_footer(
                    text=f"アカウント作成日時(そのままの値:{(u.created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')},タイムスタンプ化:")
                e.timestamp = u.created_at
                await ctx.send(embed=e)
                return
            except:
                pass
            idis = self.bot.get_emoji(id)
            if idis:
                await ctx.send(embed=ut.getEmbed("絵文字", f"名前:{str(idis)}\nid:{idis.id}"))
                return
            try:
                idis = await self.bot.fetch_invite(inid)
                await ctx.send(embed=ut.getEmbed("サーバー招待", f"名前:{str(idis.guild.name)}\nチャンネル:{idis.channel.name}\nmember_count:{idis.approximate_member_count}\npresence_count:{idis.approximate_presence_count}\n[参加]({idis.url})"))
                return
            except:
                pass
            try:
                idis = await self.bot.fetch_webhook(id)
                await ctx.send(embed=ut.getEmbed("webhook", f"デフォルトネーム:{idis.name}\nサーバーid:{idis.guild_id}"))
                return
            except:
                pass
            try:
                idis = await self.bot.fetch_widget(inid)
                await ctx.send(embed=ut.getEmbed("サーバーウィジェット", f"名前:{idis.name}\n招待:{idis.invite_url}"))
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
            await ctx.send(embed=ut.getEmbed("そのidでは見つかりませんでした。", "(現在メッセージidの検索は無効化されています。)"))


def setup(bot):
    bot.add_cog(search(bot))
