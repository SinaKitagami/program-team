# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from PIL import Image, ImageOps


class Symmetry(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="symmetry")
    @commands.bot_has_permissions(attach_files=True)
    async def symmetry(self, ctx, side: str="left"):
        if side == "left" or side == "right" or side == "up" or side == "down":
            await ctx.send("シンメトリーにしたい画像をアップしてください↓")
            try:
                msg = await self.bot.wait_for("message", check=lambda msg: msg.author.id == ctx.author.id and msg.channel == ctx.channel and msg.attachments, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send("タイムアウト。もう一度お試し下さい。")
            else:
                await ctx.channel.trigger_typing()
                await msg.attachments[0].save("image.png")
                img = Image.open('image.png')
                if side == "left":
                    tmp1 = img.crop((0, 0, img.size[0] // 2, img.size[1]))
                elif side == "right":
                    tmp1 = img.crop(
                        (img.size[0] // 2, 0, img.size[0], img.size[1]))
                elif side == "up":
                    tmp1 = img.crop((0, 0, img.size[0], img.size[1] // 2))
                elif side == "down":
                    tmp1 = img.crop(
                        (0, img.size[0] // 2, img.size[0], img.size[1]))
                if side == "left" or side == "right":
                    tmp2 = ImageOps.mirror(tmp1)
                    dst = Image.new(
                        'RGB', (tmp1.width + tmp2.width, tmp1.height))
                else:
                    tmp2 = ImageOps.flip(tmp1)
                    dst = Image.new(
                        'RGB', (tmp1.width, tmp1.height + tmp2.height))
                if side == "left":
                    dst.paste(tmp1, (0, 0))
                    dst.paste(tmp2, (tmp1.width, 0))
                if side == "right":
                    dst.paste(tmp1, (tmp2.width, 0))
                    dst.paste(tmp2, (0, 0))
                if side == "up":
                    dst.paste(tmp1, (0, 0))
                    dst.paste(tmp2, (0, tmp1.height))
                if side == "down":
                    dst.paste(tmp1, (0, tmp2.height))
                    dst.paste(tmp2, (0, 0))
                dst.save('ts2.png')
                await ctx.channel.send(file=discord.File('ts2.png'))
        else:
            await ctx.send("サイドの指定が間違っています!")


def setup(bot):
    bot.add_cog(Symmetry(bot))
