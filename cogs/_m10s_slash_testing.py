# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio

from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash

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

target_guilds = [461153681971216384]

class m10s_slash_testing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_slash(name="ping", description="すべてはここから始まった", guild_ids=target_guilds)
    async def _ping(self, ctx:SlashContext):
        await ctx.defer(hidden=False)
        await asyncio.sleep(3)
        await ctx.send("こんにちは！思惟奈だよ！",hidden=True)

    @cog_slash(name="testing_A", description="テストコマンドA", guild_ids=target_guilds)
    async def tsA(self, ctx:SlashContext):
        await ctx.defer(hidden=True)
        await asyncio.sleep(3)
        await ctx.send("こんにちは！思惟奈だよ！",hidden=True)

    @cog_slash(name="testing_B", description="テストコマンドA", guild_ids=target_guilds)
    async def tsB(self, ctx:SlashContext):
        await ctx.defer(hidden=False)
        await asyncio.sleep(3)
        await ctx.send("こんにちは！思惟奈だよ！",hidden=True)

    @cog_slash(name="testing_C", description="テストコマンドA", guild_ids=target_guilds)
    async def tsC(self, ctx:SlashContext):
        await ctx.defer(hidden=True)
        await asyncio.sleep(3)
        await ctx.send("こんにちは！思惟奈だよ！",hidden=False)


async def setup(bot):
    await bot.add_cog(m10s_slash_testing(bot))
