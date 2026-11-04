# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio

import m10s_util as ut


class m10s_tos_guide(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        pass

    @commands.hybrid_command(name="tos_guide", description="Botの利用規約/Guide on the bot's terms of service")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def tos_guide(self, ctx, args):
        tos_url = ""
        show_message = f"""
        **Botの利用規約/Guide on the bot's terms of service**
        本Botの利用規約は、次のURLからご覧いただけます。 : {tos_url}
        The bot's terms of service can be found at the following URL: {tos_url}
        """
        await ctx.send(show_message, ephemeral=True)

    @commands.hybrid_command(name="how_to_remove_my_data", description="Botの保持しているデータを削除する方法/Guide on how to remove your data from the bot")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def how_to_remove_my_data(self, ctx, args):
        policy_url = ""
        request_form_url = ""
        show_message = f"""
        **Botの保持しているデータを削除する方法/Guide on how to remove your data from the bot**
        本Botは、サービスの提供のために必要なデータを保持しています。
        保持している内容は、プライバシーポリシーをご覧ください。 : {policy_url}
        データの削除申請を行うには、次のフォームをご利用ください。 : {request_form_url}
        申請に必要なあなたのユーザーID : ```{ctx.author.id}```
        
        The bot retains data necessary for providing its services.
        Please refer to the privacy policy (Japanese) for details on what data is retained: {policy_url}
        To request the deletion of your data, please use the following form: {request_form_url}
        Your user ID required for the request: ```{ctx.author.id}```"""

        await ctx.send(show_message, ephemeral=True)


async def setup(bot):
    await bot.add_cog(m10s_tos_guide(bot))
