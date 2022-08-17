import asyncio
from typing import Optional
import discord
from discord.ext import commands

from discord import app_commands

import json

import m10s_util as ut

class mini_features(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        @app_commands.command(name="shutdown")
        @app_commands.guilds(discord.Object(id=582545206017261598))
        @ut.runnable_check()
        async def bot_exit(interaction:discord.Interaction):
            await interaction.response.send_message("自動的に終了されます…", ephemeral=True)

        bot.tree.add_command(bot_exit, guild=discord.Object(id=582545206017261598))
        
        @app_commands.context_menu(name="spread spoiler")
        @ut.runnable_check()
        async def spread_spoiler(interaction:discord.Interaction, message:discord.Message):
            await interaction.response.send_message(embed=discord.Embed(title="スポイラー展開", description=message.content.replace("||", ""), color=self.bot.ec), ephemeral=True)

        bot.tree.add_command(spread_spoiler)

    @commands.hybrid_command(description="一文字ずつ隠すスポイラーの文面を作成します。")
    @app_commands.describe(text="作成のもとになるテキスト")
    @ut.runnable_check()
    async def mark_as_spoiler_each_char(self, ctx, *, text:str):
        st = ""
        for i in text:
            st = st+f"\|\|{i}\|\|"
        await ctx.send(embed=discord.Embed(title="スポイラー化テキスト",description=f"{st}", color=self.bot.ec), ephemeral=True)

async def setup(bot):
    await bot.add_cog(mini_features(bot))