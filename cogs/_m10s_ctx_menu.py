#codiing:utf-8

import aiohttp
from dateutil.relativedelta import relativedelta as rdelta
import discord
from discord.ext import commands

import asyncio

import m10s_util as ut

from my_module import dpy_interaction as dpyui

import traceback

class _m10s_ctx_menu(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot:commands.Bot = bot

    @commands.command()
    async def add_slash_cmd(self, ctx):
        try:
            """await self.bot.dpyui.register_guild_app_command(764088457785638922, "random_music", 1, "プロセカの楽曲抽選を行います。(データベース更新が手動なので、反映が遅れます。)", options=[
                dpyui.interaction_register_option("difficult", "楽曲の難易度を選択します。", 4,True, choices=[
                    dpyui.interaction_register_choice(name="easy",value=0),
                    dpyui.interaction_register_choice(name="normal",value=1),
                    dpyui.interaction_register_choice(name="hard",value=2),
                    dpyui.interaction_register_choice(name="expart",value=3),
                    dpyui.interaction_register_choice(name="master",value=4),
                ]),
                dpyui.interaction_register_option("min_level", "選出する最低難易度を指定します。",4),
                dpyui.interaction_register_option("max_level", "選出する最高難易度を指定します。",4),
                dpyui.interaction_register_option("count", "選出する楽曲数を指定します。",4, min_value=1)
            ])"""
            await self.bot.dpyui.register_global_app_command("spread spoiler",3)
        except:
            traceback.print_exc()
        await ctx.send("登録しました。")

    @commands.command()
    async def reg_ctx_guild(self, ctx, name, ctype, description=None):
        await self.bot.dpyui.register_guild_app_command(
            ctx.guild.id, name, ctype, description
        )

    @commands.command()
    async def get_ctx_guild(self, ctx):
        info = await self.bot.dpyui.get_guild_app_commands(ctx.guild.id)
        ctt = "\n".join([f'{i["name"]}(type:{i["type"]}):{i["id"]}' for i in info])
        await ctx.send(f"```json\n{ctt}```")

    @commands.command()
    async def del_ctx_guild(self, ctx, command_id):
        await self.bot.dpyui.delete_guild_app_command(ctx.guild.id, command_id)

    @commands.command()
    async def reg_ctx_global(self, ctx, name, ctype, description=None):
        await self.bot.dpyui.register_global_app_command(
            name, ctype, description
        )

    @commands.command()
    async def get_ctx_global(self, ctx):
        info = await self.bot.dpyui.get_global_app_commands()
        ctt = "\n".join([f'{i["name"]}(type:{i["type"]}):{i["id"]}' for i in info])
        await ctx.send(f"```json\n{ctt}```")

    @commands.command()
    async def del_ctx_global(self, ctx, command_id):
        await self.bot.dpyui.delete_global_app_command(command_id)

    # @commands.Cog.listener()
    async def on_message_command_interaction(self, mccb:dpyui.message_command_callback):
        if mccb.command_name == "spread spoiler":
            await mccb.send_response_with_ui(embed=discord.Embed(title="スポイラー展開", description=f"{mccb.target_message.content.replace('||','')}", color=self.bot.ec), hidden=True)

    @commands.Cog.listener()
    async def on_user_command_interaction(self, uccb:dpyui.user_command_callback):
        if uccb.command_name == "userinfo":
            try:
                target = uccb.guild.get_member(uccb.target_id)

                upf = await self.bot.cursor.fetchone("select * from users where id=%s", (target.id,))
                #upf = await self.bot.cursor.fetchone()
                headers = {
                    "User-Agent": "DiscordBot (sina-chan with discord.py)",
                    "Authorization": f"Bot {self.bot.http.token}"
                }
                async with self.bot.session.get(f"https://discord.com/api/v9/users/{target.id}", headers=headers) as resp:
                    resp.raise_for_status()
                    ucb = await resp.json()
                flags = ut.m10s_badges(ucb["public_flags"])


                menu = dpyui.interaction_menu(f"userinfo_ctx_user_{uccb.interaction_id}", "表示する項目をここから選択", 1, 1)
                menu.add_option("基本情報", "user_basic", "ユーザー名やディスクリミネーター等を表示します。")
                menu.add_option("アバター", "avatar","ユーザーアバターを表示します。")
                menu.add_option("ユーザーバッジ", "badges", "ユーザーのバッジ情報を表示します。")
                if ucb["banner"]:
                    menu.add_option("ユーザーバナー", "banner", "ユーザーの設定しているバナー画像を表示します。")
                if upf:
                    menu.add_option("思惟奈ちゃんユーザープロファイル情報", "sina_info", "思惟奈ちゃん上での扱いなどを表示します。")
                menu.add_option("サーバー内基本情報", "server_basic", "サーバー内での基本的な情報を表示します。")
                menu.add_option("プレゼンス情報", "presence", "ユーザーのオンライン状況やトップ表示されているアクティビティについて表示します。")
                menu.add_option("役職情報", "roles", "所有している役職/権限情報を表示します。")
                await uccb.send_response_with_ui("下から表示したい情報を選んでください。タイムアウトは30秒です。", ui=menu)
                while True:
                    try:
                        cb:dpyui.interaction_menu_callback = await self.bot.wait_for("menu_select", check=lambda icb: icb.custom_id==f"userinfo_ctx_user_{uccb.interaction_id}" and icb.user_id == uccb.user_id, timeout=30)
                    except:
                        return
                    e = discord.Embed(title="ユーザー情報", color=self.bot.ec)
                    e.set_author(name=target.name)
                    if cb.selected_value[0] == "user_basic":
                        e.description="基本情報ページ"
                        if target.system:
                            e.add_field(name="Discord システムアカウント",value="Discordがあなたのパスワードやアカウントトークンを要求することはありません！")
                        if target.bot:
                            e.add_field(name="Botアカウント",value="(認証済みかどうかは、「ユーザーバッジ」ページを参照してください。)")
                        e.add_field(name="ユーザー名", value=target.name)
                        e.add_field(name="ユーザーのタグ", value=target.discriminator)
                        e.add_field(name="アカウント作成日", value=(target.created_at + rdelta(
                        hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
                        try:
                            e.add_field(name="思惟奈との共通サーバー数",value=f"{len(target.mutual_guilds)}個".replace("0個","(なし)"))
                        except:
                            pass

                    elif cb.selected_value[0] == "avatar":
                        e.description="ユーザーアバターページ"
                        e.add_field(name="アバターURL",value=target.avatar_url)
                        e.set_image(url=target.avatar_url)
                    
                    elif cb.selected_value[0] == "badges":
                        e.description="ユーザーバッジページ"
                        e.add_field(name="アカウントのバッジ/フラグ",
                                    value=f'\n'.join(flags.get_list()) or "(なし)")
                    elif cb.selected_value[0] == "sina_info":
                        e.description="ユーザープロファイルページ"
                        e.add_field(name="prefix", value=upf["prefix"])
                        e.add_field(name="ゲームポイント", value=upf["gpoint"])
                        e.add_field(name="レベルカード", value=upf["levcard"])
                        e.add_field(name="オンライン通知を受け取っているユーザーid", value=upf["onnotif"])
                        e.add_field(name="言語", value=upf["lang"])
                        e.add_field(name="思惟奈ちゃん認証済みアカウント", value=upf["sinapartner"])

                    elif cb.selected_value[0] == "server_basic":
                        if target.premium_since is not None:
                            e.add_field(name="サーバーブースト情報",
                                value=f"since {target.premium_since}")
                        e.add_field(name="表示名",value=target.display_name)
                        e.add_field(name="サーバー参加時間", value=(target.joined_at + rdelta(
                            hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))


                    elif cb.selected_value[0] == "presence":
                        e.description = "プレゼンス情報ページ"
                        e.add_field(name="オンライン状況(PC)", value=target.desktop_status)
                        e.add_field(name="オンライン状況(mobile)", value=target.mobile_status)
                        e.add_field(name="オンライン状況(web)", value=target.web_status)
                        if target.activities:
                            e.add_field(name="アクティビティ",value="プレイ中の情報を、アプリケーション名と種類のみ表示します。詳細は`s-activity`でご覧ください。",inline=False)
                            for a in target.activities:
                                if a.type == discord.ActivityType.playing:
                                    acttype = "プレイ中"
                                elif a.type == discord.ActivityType.watching:
                                    acttype = "視聴中"
                                elif a.type == discord.ActivityType.listening:
                                    acttype = "リスニング"
                                elif a.type == discord.ActivityType.streaming:
                                    acttype = "配信中"
                                elif a.type == discord.ActivityType.custom:
                                    acttype = "カスタムステータス"
                                else:
                                    acttype = "不明"
                                e.add_field(name=a.name, value=acttype)

                        else:
                            e.add_field(name="アクティビティ", value="アクティビティなし", inline=False)
                        
                    elif cb.selected_value[0] == "roles":
                        hasroles = ""
                        for r in target.roles:
                            if len(hasroles + f"{r.mention},") > 1020:
                                hasroles += "など"
                                break
                            else:
                                hasroles = hasroles + f"{r.mention},"
                        e.add_field(name="役職情報", value=hasroles)

                        e.add_field(name="権限情報",
                            value=f"`{'`,`'.join([self.bot.l10n_raw('ja,'f'p-{i[0]}') for i in list(target.guild_permissions) if i[1]])}`",inline=False)

                    elif cb.selected_value[0] == "banner":
                        # https://cdn.discordapp.com/banners/404243934210949120/4d22b0afc7bf59810ab3ca44559be8a5.png?size=1024
                        banner_url = f'https://cdn.discordapp.com/banners/{target.id}/{ucb["banner"]}.png?size=1024'
                        e.description="ユーザーバナーページ"
                        e.add_field(name="バナーURL",value=banner_url)
                        e.set_image(url=banner_url)
                    else:
                        e.add_field(name="例外", value="このメッセージを読んでいるあなたは、どうやってこのメッセージを表示させましたか？")
                    
                    await cb.response()
                    await cb.message.edit(content="",embed=e)
            except:
                    traceback.print_exc()


    @commands.Cog.listener()
    async def on_slash_command_interaction(self, sccb:dpyui.slash_command_callback):
        if sccb.command_name == "userinfo":
            try:
                if sccb.args.get("target",None) != None:
                    target = sccb.guild.get_member(int(sccb.args["target"]))
                    print(target)
                else:
                    target = sccb.guild.get_member(sccb.user_id)

                upf = await self.bot.cursor.fetchone("select * from users where id=%s", (target.id,))
                #upf = await self.bot.cursor.fetchone()
                headers = {
                    "User-Agent": "DiscordBot (sina-chan with discord.py)",
                    "Authorization": f"Bot {self.bot.http.token}"
                }
                async with self.bot.session.get(f"https://discord.com/api/v9/users/{target.id}", headers=headers) as resp:
                    resp.raise_for_status()
                    ucb = await resp.json()
                flags = ut.m10s_badges(ucb["public_flags"])


                menu = dpyui.interaction_menu(f"userinfo_ctx_user_{sccb.interaction_id}", "表示する項目をここから選択", 1, 1)
                menu.add_option("基本情報", "user_basic", "ユーザー名やディスクリミネーター等を表示します。")
                menu.add_option("アバター", "avatar","ユーザーアバターを表示します。")
                menu.add_option("ユーザーバッジ", "badges", "ユーザーのバッジ情報を表示します。")
                if ucb["banner"]:
                    menu.add_option("ユーザーバナー", "banner", "ユーザーの設定しているバナー画像を表示します。")
                if upf:
                    menu.add_option("思惟奈ちゃんユーザープロファイル情報", "sina_info", "思惟奈ちゃん上での扱いなどを表示します。")
                menu.add_option("サーバー内基本情報", "server_basic", "サーバー内での基本的な情報を表示します。")
                menu.add_option("プレゼンス情報", "presence", "ユーザーのオンライン状況やトップ表示されているアクティビティについて表示します。")
                menu.add_option("役職情報", "roles", "所有している役職/権限情報を表示します。")
                await sccb.send_response_with_ui("下から表示したい情報を選んでください。タイムアウトは30秒です。", ui=menu)
                while True:
                    try:
                        cb:dpyui.interaction_menu_callback = await self.bot.wait_for("menu_select", check=lambda icb: icb.custom_id==f"userinfo_ctx_user_{sccb.interaction_id}" and icb.user_id == sccb.user_id, timeout=30)
                    except:
                        return
                    e = discord.Embed(title="ユーザー情報", color=self.bot.ec)
                    e.set_author(name=target.name)
                    if cb.selected_value[0] == "user_basic":
                        e.description="基本情報ページ"
                        if target.system:
                            e.add_field(name="Discord システムアカウント",value="Discordがあなたのパスワードやアカウントトークンを要求することはありません！")
                        if target.bot:
                            e.add_field(name="Botアカウント",value="(認証済みかどうかは、「ユーザーバッジ」ページを参照してください。)")
                        e.add_field(name="ユーザー名", value=target.name)
                        e.add_field(name="ユーザーのタグ", value=target.discriminator)
                        e.add_field(name="アカウント作成日", value=(target.created_at + rdelta(
                        hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
                        try:
                            e.add_field(name="思惟奈との共通サーバー数",value=f"{len(target.mutual_guilds)}個".replace("0個","(なし)"))
                        except:
                            pass

                    elif cb.selected_value[0] == "avatar":
                        e.description="ユーザーアバターページ"
                        e.add_field(name="アバターURL",value=target.avatar_url)
                        e.set_image(url=target.avatar_url)
                    
                    elif cb.selected_value[0] == "badges":
                        e.description="ユーザーバッジページ"
                        e.add_field(name="アカウントのバッジ/フラグ",
                                    value=f'\n'.join(flags.get_list()) or "(なし)")
                    elif cb.selected_value[0] == "sina_info":
                        e.description="ユーザープロファイルページ"
                        e.add_field(name="prefix", value=upf["prefix"])
                        e.add_field(name="ゲームポイント", value=upf["gpoint"])
                        e.add_field(name="レベルカード", value=upf["levcard"])
                        e.add_field(name="オンライン通知を受け取っているユーザーid", value=upf["onnotif"])
                        e.add_field(name="言語", value=upf["lang"])
                        e.add_field(name="思惟奈ちゃん認証済みアカウント", value=upf["sinapartner"])

                    elif cb.selected_value[0] == "server_basic":
                        if target.premium_since is not None:
                            e.add_field(name="サーバーブースト情報",
                                value=f"since {target.premium_since}")
                        e.add_field(name="表示名",value=target.display_name)
                        e.add_field(name="サーバー参加時間", value=(target.joined_at + rdelta(
                            hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))


                    elif cb.selected_value[0] == "presence":
                        e.description = "プレゼンス情報ページ"
                        e.add_field(name="オンライン状況(PC)", value=target.desktop_status)
                        e.add_field(name="オンライン状況(mobile)", value=target.mobile_status)
                        e.add_field(name="オンライン状況(web)", value=target.web_status)
                        if target.activities:
                            e.add_field(name="アクティビティ",value="プレイ中の情報を、アプリケーション名と種類のみ表示します。詳細は`s-activity`でご覧ください。",inline=False)
                            for a in target.activities:
                                if a.type == discord.ActivityType.playing:
                                    acttype = "プレイ中"
                                elif a.type == discord.ActivityType.watching:
                                    acttype = "視聴中"
                                elif a.type == discord.ActivityType.listening:
                                    acttype = "リスニング"
                                elif a.type == discord.ActivityType.streaming:
                                    acttype = "配信中"
                                elif a.type == discord.ActivityType.custom:
                                    acttype = "カスタムステータス"
                                else:
                                    acttype = "不明"
                                e.add_field(name=a.name, value=acttype)

                        else:
                            e.add_field(name="アクティビティ", value="アクティビティなし", inline=False)
                        
                    elif cb.selected_value[0] == "roles":
                        hasroles = ""
                        for r in target.roles:
                            if len(hasroles + f"{r.mention},") > 1020:
                                hasroles += "など"
                                break
                            else:
                                hasroles = hasroles + f"{r.mention},"
                        e.add_field(name="役職情報", value=hasroles)

                        e.add_field(name="権限情報",
                            value=f"`{'`,`'.join([self.bot.l10n_raw('ja,'f'p-{i[0]}') for i in list(target.guild_permissions) if i[1]])}`",inline=False)

                    elif cb.selected_value[0] == "banner":
                        # https://cdn.discordapp.com/banners/404243934210949120/4d22b0afc7bf59810ab3ca44559be8a5.png?size=1024
                        banner_url = f'https://cdn.discordapp.com/banners/{target.id}/{ucb["banner"]}.png?size=1024'
                        e.description="ユーザーバナーページ"
                        e.add_field(name="バナーURL",value=banner_url)
                        e.set_image(url=banner_url)
                    else:
                        e.add_field(name="例外", value="このメッセージを読んでいるあなたは、どうやってこのメッセージを表示させましたか？")
                    
                    await cb.response()
                    await cb.message.edit(content="",embed=e)
            except:
                    traceback.print_exc()

    @commands.command()
    async def reg_slash_ui(self,ctx,only_guild=1):
        if only_guild == 0:
            await self.bot.dpyui.register_global_app_command(
                "userinfo", 1, "該当ユーザーのユーザー情報を表示します。", [dpyui.interaction_register_option("target","あなた以外のユーザーについて表示する場合に、ほかのユーザーを指定してください。",6)]
            )
        else:
            await self.bot.dpyui.register_guild_app_command(
                ctx.guild.id, "userinfo", 1, "該当ユーザーのユーザー情報を表示します。", [dpyui.interaction_register_option("target","あなた以外のユーザーについて表示する場合に、ほかのユーザーを指定してください。",6)]
            )

async def setup(bot):
    await bot.add_cog(_m10s_ctx_menu(bot))