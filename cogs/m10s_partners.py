# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import config as cf

import m10s_util as ut

from discord import app_commands


class m10s_partner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.partner_ids = cf.partner_ids
        self.partners = cf.partners

    @commands.hybrid_command(name="partners",description="思惟奈ちゃんのパートナーを表示します。")
    @ut.runnable_check()
    async def view_partners(self, ctx):
        pmax = len(self.partner_ids)-1
        page = 0
        
        async def get_page(page):
            return discord.Embed(title=f"思惟奈ちゃんパートナー:{await self.bot.fetch_user(self.partner_ids[page])}のご紹介",
            description=self.partners[page],
            color=self.bot.ec)

        msg = await ctx.send(embed=await get_page(page))
        await msg.add_reaction(self.bot.create_emoji_str("s_move_left",653161518195671041))
        await msg.add_reaction(self.bot.create_emoji_str('s_move_right',653161518170505216))

        while True:
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
            except:
                break
            try:
                await msg.remove_reaction(r, u)
            except:
                pass
            if str(r) == str(self.bot.create_emoji_str('s_move_right',653161518170505216)):
                if page == pmax:
                    page = 0
                else:
                    page = page + 1
            elif str(r) == str(self.bot.create_emoji_str("s_move_left",653161518195671041)):
                if page == 0:
                    page = pmax
                else:
                    page = page - 1
            await msg.edit(embed=await get_page(page))



async def setup(bot):
    await bot.add_cog(m10s_partner(bot))
