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
        self.bmaillog = self.bot.get_channel(1206643710788632606)

    @commands.hybrid_command(name="bottle-mail", aliases=["b-mail","bm"], description="ボトルメールをどこかのサーバーに送ることができます。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def b_mail(self, ctx:commands.Context):
        await ctx.send("DMをご確認ください。", ephemeral=True)
        dch = await ut.opendm(ctx.author)
        schs = [i for i in self.bot.get_all_channels() if i.name.startswith("sbm-")]
        try:
            msg: discord.Message = await ut.wait_message_return(ctx, "送信するメッセージをここに入力してください。", dch, 30)
            sch = random.choice(schs)
            #try:
            e = ut.getEmbed("ボトルメールリクエスト", msg.clean_content, self.bot.ec, "送信予定先", f"{sch.name}({sch.id}) in {sch.guild.name}({sch.guild.id})", )
            e.set_author(name=f"{ctx.author}({ctx.author.id})",
                            icon_url=ctx.author.display_avatar.replace(static_format="png").url)
            e.set_footer(text=f"{ctx.guild}({ctx.guild.id})",
                            icon_url=ctx.guild.icon.replace(static_format="png").url)
            check_msg:discord.Message = await self.bmaillog.send(embed=e)
            await check_msg.add_reaction("✅")
            r,u = await self.bot.wait_for("reaction_add", check = lambda r,u: u.id in self.bot.chat_mod and r.message.id == check_msg.id and str(r.emoji) == "✅")
            smg = await sch.send(embed=ut.getEmbed("誰かの手紙が流れ着いた…", msg.clean_content, self.bot.ec))

            #except:
                #pass
        except asyncio.TimeoutError:
            await dch.send("手紙とボトルはどこかへ消えてしまった…")


async def setup(bot):
    await bot.add_cog(m10s_bmail(bot))
