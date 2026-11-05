# -*- coding: utf-8 -*-

from discord.ext import commands

from discord import app_commands


class m10s_tos_guide(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        pass

    @commands.hybrid_command(name="tos_guide", description="アプリの利用規約/Guide on the bot's terms of service")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def tos_guide(self, ctx):
        app_tos_url = "https://home.sina-chan.com/legal/app-tos"
        grobal_tos_url = "https://home.sina-chan.com/legal/tos"
        show_message = f"""
        **アプリの利用規約/Guide on the app's terms of service**
        本アプリの利用規約は、次のURLからご覧いただけます。 : 共通利用規約 {grobal_tos_url} / アプリ利用規約 {app_tos_url}
        The app's terms of service can be found at the following URL: Common Terms of Service {grobal_tos_url} / App Terms of Service {app_tos_url}
        """
        await ctx.send(show_message, ephemeral=True)

    @commands.hybrid_command(name="how_to_remove_my_data", description="アプリの保持しているデータを削除する方法/Guide on how to remove your data from the bot")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def how_to_remove_my_data(self, ctx):
        policy_url = "https://home.sina-chan.com/legal/app-privacy-policy"
        delete_request_form_url = "https://forms.gle/4oaNGqFAMog2iuEL9"
        modify_request_form_url = "https://support.center.sina-chan.com/servicedesk/customer/portal/1/group/15/create/17"
        show_message = f"""
        **アプリの保持しているデータを削除する方法/Guide on how to remove your data from the app**
        本アプリは、サービスの提供のために必要なデータを保持しています。
        保持している内容は、プライバシーポリシーをご覧ください。 : {policy_url}

        **データの削除申請**
        データの削除申請を行うには、次のフォームをご利用ください。 : {delete_request_form_url}

        **データの訂正申請**
        データの訂正申請を行うには、次のフォームをご利用ください : {modify_request_form_url}

        各種申請に必要なあなたのユーザーID : ```{ctx.author.id}```
        -----------------
        The app retains data necessary for providing its services.
        Please refer to the privacy policy (Japanese) for details on what data is retained: {policy_url}

        **Data Deletion Request**
        To request the deletion of your data, please use the following form: {delete_request_form_url}

        **Data Correction Request**
        To request the correction of your data, please use the following form: {modify_request_form_url}

        Your user ID required for the request: ```{ctx.author.id}```"""

        await ctx.send(show_message, ephemeral=True)


async def setup(bot):
    await bot.add_cog(m10s_tos_guide(bot))
