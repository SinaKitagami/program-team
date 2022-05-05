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

        @app_commands.context_menu(name="spread spoiler")
        async def spread_spoiler(interaction:discord.Interaction, message:discord.Message):
            await interaction.response.send_message(message.content.replace("||", ""), ephemeral=True)

        bot.tree.add_command(spread_spoiler)

        @app_commands.command(name="shutdown")
        async def bot_exit(interaction:discord.Interaction):
            await interaction.response.send_message("自動的に終了されます…", ephemeral=True)

        bot.tree.add_command(bot_exit, guild=discord.Object(id=582545206017261598))

async def setup(bot):
    await bot.add_cog(mini_features(bot))