# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

import m10s_util as ut
"""↑様々な便利コマンド詰め合わせ
ut.textto("キー",Member)
    ユーザーの言語設定に基づいてキーのテキストを返す。
ut.ondevicon(Member)
    オンライン状況に基づくデバイスアイコンテキストを返す。
"""

class ClassName(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="pass")
    async def command(self,ctx,aegs):
        pass

    @commands.Cog.listener()
    async def event(self, args):
        pass

def setup(bot):
    bot.add_cog(ClassName(bot))