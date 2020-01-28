# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from PIL import Image, ImageDraw,ImageFont,ImageFilter,ImageOps
import requests
import numpy as np
class Symmetry(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="pass")
    async def symmetry(self,ctx):
        await ctx.send("シンメトリーにしたい画像をアップしてください↓")
        global mescheck
        mescheck = 1

    @commands.Cog.listener()
    async def on_message(self,ctx):
        global mescheck
        if mescheck == 1:
            url = ctx.attachments[0].url
            file_name = "image.png"

            response = requests.get(url)
            image = response.content

            with open(file_name, "wb") as a:
                a.write(image)
            img = Image.open('image.png')
            img_array = 255 - np.array(img)
            Image.fromarray(img_array).save(f'ts1.png')
            tmp1 = img.crop((0, 0, img.size[0] // 2, img.size[1]))
            tmp2 = ImageOps.mirror(tmp1)
            dst = Image.new('RGB', (tmp1.width + tmp2.width, tmp1.height))
            dst.paste(tmp1, (0, 0))
            dst.paste(tmp2, (tmp1.width, 0))
            dst.save(f'ts2.png')
            tmp2 = img.crop((img.size[0] // 2, 0, img.size[0], img.size[1]))
            tmp1 = ImageOps.mirror(tmp2)
            dst = Image.new('RGB', (tmp1.width + tmp2.width, tmp1.height))
            dst.paste(tmp1, (0, 0))
            dst.paste(tmp2, (tmp1.width, 0))
            dst.save(f'ts3.png')
            await ctx.channel.send(file=discord.File('ts2.png'))
            await ctx.channel.send(file=discord.File('ts3.png'))
            mescheck = 0
            return

def setup(bot):
    bot.add_cog(Symmetry(bot))