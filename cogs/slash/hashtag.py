import asyncio
from typing import Optional
import discord
from discord.ext import commands

from discord import app_commands

import json

import m10s_util as ut

class hashtag(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(description="ハッシュタグとして使うかどうかの設定を切り替えます。")
    async def hashtag(self, interaction:discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            d = await self.bot.cursor.fetchone(
                "select * from guilds where id=%s", (interaction.guild.id,))
            #d = await self.bot.cursor.fetchone()
            hc = json.loads(d["hash"])
            if hc == None:
                hc = [interaction.channel.id]
                await interaction.response.send_message(await self.bot._(interaction.user, "hash-connect"))
            elif interaction.channel.id in hc:
                hc.remove(interaction.channel.id)
                await interaction.response.send_message(await self.bot._(interaction.user, "hash-disconnect"))
            else:
                hc.append(interaction.channel.id)
                await interaction.response.send_message(await self.bot._(interaction.user, "hash-connect"))
            await self.bot.cursor.execute(
                "UPDATE guilds SET hash = %s WHERE id = %s", (json.dumps(hc), interaction.guild.id))
        else:
            await interaction.response.send_message("> あなたには、このコマンドを実行する権限がありません。\n　サーバー管理者である必要があります。",ephemeral=True)

async def setup(bot):
    await bot.add_cog(hashtag(bot))