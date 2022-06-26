# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

import m10s_util as ut

class m10s_bmail(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="bottle-mail", aliases=["b-mail","bm"], description="ボトルメールをどこかのサーバーに送ることができます。")
    async def b_mail(self, ctx):
        dch = await ut.opendm(ctx.author)
        schs = [i for i in self.bot.get_all_channels()
                if i.name.startswith("sbm-")]
        bmaillog = self.bot.get_channel(701747896621596693)
        try:
            msg = await ut.wait_message_return(ctx, "あなたの思いをここにのせて…", dch, 30)
            sch = random.choice(schs)
            #try:
            smg = await sch.send(embed=ut.getEmbed("誰かの手紙が流れ着いた…", msg.clean_content, self.bot.ec, "もし迷惑ユーザーを見かけたら", "メッセージIDを添えて`s-report`コマンドでお知らせください。"))
            e = ut.getEmbed("ボトルメールログ", msg.clean_content, self.bot.ec,
                            "送信先サーバー:チャンネル", f"{smg.guild.name}({smg.guild.id}):{smg.channel.name}({smg.channel.id})", "メッセージID", str(smg.id))
            e.set_author(name=f"{msg.author}({msg.author.id})",
                            icon_url=msg.author.display_avatar.replace(static_format="png").url)
            await bmaillog.send(embed=e)
            #except:
                #pass
        except asyncio.TimeoutError:
            await dch.send("手紙とボトルはどこかへ消えてしまった…")


async def setup(bot):
    await bot.add_cog(m10s_bmail(bot))
