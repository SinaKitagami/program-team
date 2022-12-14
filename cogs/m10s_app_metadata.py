# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from dateutil.relativedelta import relativedelta as rdelta
import traceback
import m10s_util as ut
import textwrap

import config
import aiohttp

from discord import app_commands

class m10s_app_metadata(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    @ut.runnable_check()
    async def update_role_metadata(self, ctx):
        json_body = [
            {
                "key":"isadmin",
                "name":"チーム☆思惟奈ちゃん",
                "description":"思惟奈ちゃん運営である",
                "type":7
            },
            {
                "key":"isdonate",
                "name":"思惟奈ちゃんプレミアム会員",
                "description":"思惟奈ちゃんに寄付を行った、プレミアム会員である",
                "type":7
            },
            {
                "key":"isverified",
                "name":"思惟奈ちゃん認証済みアカウント",
                "description":"思惟奈ちゃん上で、アカウントが認証されている",
                "type":7
            },
            {
                "key":"gamepoint",
                "name":"ゲームポイント",
                "description":"一部ゲームでたまる思惟奈ちゃんゲームポイントを、指定値以上所有している",
                "type":2
            }
        ]
        headers = {
            "Authorization": f"Bot {config.BOT_TOKEN}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.put(url=f"https://discord.com/api/v10/applications/{config.DISCORD_CLIENT_ID}/role-connections/metadata", json=json_body, headers=headers) as resp:
                resp.raise_for_status()
        await ctx.send("> 設定しました。")

    @commands.hybrid_command(description="あなたの接続されているアプリメタデータを更新します。")
    async def sync_metadata(self, ctx:commands.Context):
        upf = await self.bot.cursor.fetchone("select oauth_ref_token from users where id=%s", (ctx.author.id,))
        if upf["oauth_ref_token"]:
            try:
                await self.bot.update_connect_metadata(ctx.author.id, upf["oauth_ref_token"], True)
            except:
                await ctx.send("失敗しました。\n一度連携を外し、再度連携させてください。", ephemeral=True)
            else:
                await ctx.send("完了しました。", ephemeral=True)
        else:
            await ctx.send("失敗しました。\nまだアプリ連携が行われていません。linked-rolesメニューから、思惟奈ちゃんの連携が有効なロールを探して連携してください。", ephemeral=True)


async def setup(bot):
    await bot.add_cog(m10s_app_metadata(bot))