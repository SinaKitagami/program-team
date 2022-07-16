#codiing:utf-8

import aiohttp
from dateutil.relativedelta import relativedelta as rdelta
import discord
from discord.ext import commands

import asyncio

import m10s_util as ut

from my_module import dpy_interaction as dpyui

class m10s_beta(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot:commands.Bot = bot

    @commands.command()
    async def tsts(self, ctx):
        menu = dpyui.interaction_menu("test_1","選択してください",1,3)
        menu.add_option("りくりく","rikuchan","選択項目1")
        menu.add_option("りっくん","rikkun","選択項目2")
        menu.add_option("みぃてん☆","m10s","選択項目3")
        menu.add_option("test","ts","選択項目4")
        menu.add_option("lol","lol","選択項目5")
        msg = await self.bot.dpyui.send_with_ui(ctx.channel,"> テスト",ui=menu)
        cb:dpyui.interaction_menu_callback = await self.bot.wait_for("menu_select", check=lambda icb:icb.custom_id=="test_1" and icb.message.id==msg.id and icb.clicker_id == ctx.author.id)
        await cb.edit_with_ui(content=f"選択された項目の内部識別文字列一覧:\n{cb.selected_value}", ui=[])


        


async def setup(bot):
    await bot.add_cog(m10s_beta(bot))