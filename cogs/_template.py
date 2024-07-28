# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio

import m10s_util as ut
"""↑様々な便利コマンド詰め合わせ
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


class ClassName(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        pass

    @commands.hybrid_command(name="pass", description="")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def command(self, ctx, args):
        pass

    @commands.Cog.listener()
    async def event(self, args):
        pass


async def setup(bot):
    await bot.add_cog(ClassName(bot))
