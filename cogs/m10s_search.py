# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json
import random
from googleapiclient.discovery import build
import wikipedia
import time
import asyncio
from dateutil.relativedelta import relativedelta as rdelta

from discord import app_commands

import m10s_util as ut

import config as cf

import traceback

class search(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @ut.runnable_check()
    async def getby(self, ctx, k: str):
        await ctx.send(embed=ut.getEmbed("", await ctx._(k)))

    @commands.hybrid_group(name="search", description="検索系コマンド")
    @ut.runnable_check()
    async def search_commands(self,ctx):
        pass

    @search_commands.command(aliases=["twisearch", "twitterで検索して"], description="Twitter検索")
    @app_commands.describe(word="検索文字列")
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    @ut.runnable_check()
    async def twitter(self, ctx, *, word: str):
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
                embed.add_field(name=await ctx._(
                    "twi-see"), value=f'{self.bot.get_emoji(653161518451392512)} https://twitter.com/{tweet["user"]["screen_name"]}/status/{tweet["id"]}')
            await ctx.send(embed=embed)
        except:
            await ctx.send(await ctx._("twi-error"))
            # await ctx.send(embed=ut.getEmbed("traceback",traceback.format_exc(3)))

    @search_commands.command(aliases=["jwp", "次の言葉でwikipedia調べて"],description="wikipedia検索")
    @app_commands.describe(word="検索文字列")
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @ut.runnable_check()
    async def wikipedia(self, ctx, *, word:str):
        try:
            async with ctx.message.channel.typing():
                wd = word
                sw = wikipedia.search(wd, results=1)
                sw1 = sw[0].replace(" ", "_")
                sr = wikipedia.page(sw1)
                embed = discord.Embed(
                    title=sw1, description=sr.summary, color=self.bot.ec)
                embed.add_field(name=await ctx._("jwp-seemore"),
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
                        await ctx.send(await ctx._("jwp-found", wd, sw1))
            except:
                await ctx.send(await ctx._("jwp-notfound"))

    # @search_commands.command(aliases=["jpwt", "天気", "今日の天気は"],description="日本の天気予報図を表示します。")
    # @commands.cooldown(1, 15, type=commands.BucketType.user) -> 形式変更で動かなくなっていましたよ
    async def weather_in_japan(self, ctx):

        if ctx.channel.permissions_for(ctx.guild.me).attach_files is True:
            try:
                async with ctx.message.channel.typing():
                    content = await self.bot.apple_util.get_as_binary("http://www.jma.go.jp/jp/yoho/images/000_telop_today.png")
                    with open("imgs/weather.png", 'wb') as f:
                        f.write(content)
                    await ctx.send(file=discord.File("imgs/weather.png"))
                    await ctx.send(await ctx._("jpwt-credit"))
            except:
                await ctx.send(await ctx._("jpwt-error"))
        else:
            try:
                await ctx.send(embed=discord.Embed(title=await ctx._("dhaveper"), description=await ctx._("per-sendfile")))
            except:
                await ctx.send(f"{await ctx._('dhaveper')}\n{await ctx._('per-sendfile')}")

    @search_commands.command(aliases=["ニュース", "ニュースを見せて"],description="newsapi経由でニュースを表示します。")
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    @ut.runnable_check()
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



    @search_commands.command(aliases=["次の言葉でyoutube調べて"], description="YouTube検索")
    @app_commands.describe(word="検索文字列")
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @ut.runnable_check()
    async def youtube(self, ctx, *, word:str):
        #try:
        async with ctx.message.channel.typing():
            with build('youtube', 'v3', developerKey=self.bot.GAPI_TOKEN) as youtube:
                search_response = youtube.search().list(
                    part="id",
                    q=word,
                    type='video'
                ).execute()
            id = search_response['items'][0]['id']['videoId']
            await ctx.send(await ctx._("youtube-found", id))
        #except:
            #await ctx.send(await ctx._("youtube-notfound"))


async def setup(bot):
    await bot.add_cog(search(bot))
