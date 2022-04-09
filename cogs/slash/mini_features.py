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

async def setup(bot):
    await bot.add_cog(mini_features(bot))