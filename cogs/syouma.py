# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio

import m10s_util as ut
from bs4 import BeautifulSoup
import random
import requests
import time
import datetime
"""↑様々な便利コマンド詰め合わせ
ut.textto("キー",Member)
    ユーザーの言語設定に基づいてキーのテキストを返す。
ut.ondevicon(Member)
    オンライン状況に基づくデバイスアイコンテキストを返す。
ut.getEmbed(title,description,color,(name,value)...)
    Embedのお手軽生成。これ使ったのがあるから消そうにも消せない。
await ut.opendm(Member/User)
    DMチャンネルを返します。DMチャンネルが存在しないなんてことでは困らせません。
await wait_message_return(ctx,質問するテキスト,←の送信先,待つ時間):
    入力待ちの簡略化。タイムアウトの例外キャッチを忘れずに
"""


class syouma(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tenki")
    async def tenki(self, msg, address):
        color = random.randint(0x000000, 0xffffff)
        Url = "https://tenki.jp"
        Req = requests.get(Url + "/search/?keyword=" + address)
        Soup = BeautifulSoup(Req.text, 'lxml')
        Sed = Soup.find_all(class_="search-entry-data")
        HrfUrl = None
        for val in Sed:
            if val.find(class_="address").text.find("以下に掲載がない場合"):
                HrfUrl = val.a.get("href")
            # print(HrfUrl)
    #myDict = {}
    # 住所からhrefを取得
    # if not(HrfUrl is None):
        await asyncio.sleep(1)  # 一回requestを投げているので1秒待つ
        Req = requests.get(Url + HrfUrl)
    # print(Req)
        bsObj = BeautifulSoup(Req.content, "html.parser")
        today = bsObj.find(class_="today-weather")
        weather = today.p.string
        temp = today.div.find(class_="date-value-wrap")
        temp = temp.find_all("dd")
        temp_max = temp[0].span.string  # 最高気温
        temp_max_diff = temp[1].string  # 最高気温の前日比
        temp_min = temp[2].span.string  # 最低気温
        temp_min_diff = temp[3].string  # 最低気温の前日比
        todayni = bsObj.find(class_="tomorrow-weather")
        weatherni = todayni.p.string
        tempni = todayni.div.find(class_="date-value-wrap")
        tempni = tempni.find_all("dd")
        temp_maxni = tempni[0].span.string  # 最高気温
        temp_max_diffni = tempni[1].string  # 最高気温の前日比
        temp_minni = tempni[2].span.string  # 最低気温
        temp_min_diffni = tempni[3].string  # 最低気温の前日比
        await msg.send(embed=discord.Embed(title=f"{address}の今日の天気:{weather}\n明日の天気:{weatherni}", description=f"今日の最高気温:{temp_max} {temp_max_diff}\n今日の最低気温:{temp_min} {temp_min_diff}\n明日の最高気温:{temp_maxni} {temp_max_diffni}\n明日の最低気温:{temp_minni} {temp_min_diffni}", color=color))

    @commands.Cog.listener()
    async def event(self, args):
        pass


def setup(bot):
    bot.add_cog(syouma(bot))
