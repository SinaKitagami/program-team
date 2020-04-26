# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import random

import m10s_util as ut
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
ut.get_vmusic(bot,member)
    思惟奈ちゃんの音楽再生機能でそのメンバーがきいている曲を返します。
"""

class m10s_bmail(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="b-mail",aliases=["bm"])
    async def b_mail(self,ctx):
        dch = await ut.opendm(ctx.author)
        schs = [i for i in self.bot.get_all_channels() if i.name.startswith("sbm-")]
        bmaillog=self.bot.get_channel(701747896621596693)
        try:
            msg = await ut.wait_message_return(ctx,"あなたの思いをここにのせて…",dch,30)
            sch=random.choice(schs)
            try:
                smg=await sch.send(embed=ut.getEmbed("誰かの手紙が流れ着いた…",msg.clean_content,self.bot.ec,"もし迷惑ユーザーを見かけたら","メッセージIDを添えて`s-report`コマンドでお知らせください。"))
                e=ut.getEmbed("ボトルメールログ",msg.clean_content,self.bot.ec,"チャンネル",msg.channel.name,"メッセージID",str(smg.id))
                e.set_author(name=f"{msg.author}({msg.author.id})",icon_url=msg.author.icon_url_as(static_format="png"))
                await bmaillog.send(embed=e)
            except:
                pass
        except asyncio.TimeoutError:
            await dch.send("手紙とボトルはどこかへ消えてしまった…")

def setup(bot):
    bot.add_cog(m10s_bmail(bot))