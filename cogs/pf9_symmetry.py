# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from PIL import Image, ImageOps

from discord import app_commands

import m10s_util as ut

class Symmetry(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="symmetry", description="シンメトリー画像を生成します。")
    @commands.bot_has_permissions(attach_files=True)
    @app_commands.checks.bot_has_permissions(attach_files=True)
    @discord.app_commands.choices(side=[
            discord.app_commands.Choice(name="left", value=0),
            discord.app_commands.Choice(name="right", value=1),
            discord.app_commands.Choice(name="up", value=2),
            discord.app_commands.Choice(name="down", value=3),
        ])
    @app_commands.describe(side="どの面をシンメトリーにするか")
    @app_commands.describe(image="シンメトリー加工する画像")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def symmetry(self, ctx: commands.Context, side: int, image: discord.Attachment):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.channel.typing():
            await image.save("image.png")
            img = Image.open('image.png')
            if side == 0:
                tmp1 = img.crop((0, 0, img.size[0] // 2, img.size[1]))
            elif side == 1:
                tmp1 = img.crop(
                    (img.size[0] // 2, 0, img.size[0], img.size[1]))
            elif side == 2:
                tmp1 = img.crop((0, 0, img.size[0], img.size[1] // 2))
            elif side == 3:
                tmp1 = img.crop(
                    (0, img.size[0] // 2, img.size[0], img.size[1]))
            if side == 0 or side == 1:
                tmp2 = ImageOps.mirror(tmp1)
                dst = Image.new(
                    'RGB', (tmp1.width + tmp2.width, tmp1.height))
            else:
                tmp2 = ImageOps.flip(tmp1)
                dst = Image.new(
                    'RGB', (tmp1.width, tmp1.height + tmp2.height))
            if side == 0:
                dst.paste(tmp1, (0, 0))
                dst.paste(tmp2, (tmp1.width, 0))
            if side == 1:
                dst.paste(tmp1, (tmp2.width, 0))
                dst.paste(tmp2, (0, 0))
            if side == 2:
                dst.paste(tmp1, (0, 0))
                dst.paste(tmp2, (0, tmp1.height))
            if side == 3:
                dst.paste(tmp1, (0, tmp2.height))
                dst.paste(tmp2, (0, 0))
            dst.save('ts2.png')
        await ctx.send(file=discord.File('ts2.png'))


async def setup(bot):
    await bot.add_cog(Symmetry(bot))
