# -*- coding: utf-8 -*-

from threading import Thread
from typing import Union, Optional
import discord
from discord.ext import commands
import asyncio
import datetime

from discord import app_commands

from dateutil.relativedelta import relativedelta as rdelta

import traceback

import m10s_util as ut

from my_module import dpy_interaction as dpyui



class info_check(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="information")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def info_group(self, ctx):
        pass

    @info_group.command(name="user", aliases=["ui", "anyuserinfo"], description="ユーザーに関する情報を表示します。")
    @app_commands.describe(target="表示するメンバー")
    @app_commands.describe(uid="表示する外部ユーザーのID")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def _info_of_user(self, ctx:commands.Context, target:Optional[discord.Member], uid:Optional[str]):
        if uid:
            uid = int(uid)
        if target:
            if ctx.interaction:
                target = ctx.guild.get_member(target.id)
            in_guild = True
        elif uid:
            try:
                target = await self.bot.fetch_user(uid)
                in_guild = False
            except:
                return await ctx.send("> 存在しないIDの指定です。")
        else:
            if ctx.interaction:
                target = ctx.guild.get_member(ctx.author.id)
            else:
                target = ctx.author
            in_guild = True

        upf = await self.bot.cursor.fetchone("select * from users where id=%s", (target.id,))
        #upf = await self.bot.cursor.fetchone()
        headers = {
            "User-Agent": "DiscordBot (sina-chan with discord.py)",
            "Authorization": f"Bot {self.bot.http.token}"
        }
        async with self.bot.session.get(f"https://discord.com/api/v10/users/{target.id}", headers=headers) as resp:
            resp.raise_for_status()
            ucb = await resp.json()
        flags = ut.m10s_badges(ucb["public_flags"])


        menu = dpyui.interaction_menu(f"userinfo_{ctx.message.id}","表示する項目をここから選択",1,1)
        menu.add_option("基本情報","user_basic","ユーザー名やディスクリミネーター等を表示します。")
        menu.add_option("アバター","avatar","ユーザーアバターを表示します。")
        menu.add_option("ユーザーバッジ","badges","ユーザーのバッジ情報を表示します。")
        if ucb["banner"]:
            menu.add_option("ユーザーバナー","banner","ユーザーの設定しているバナー画像を表示します。")
        if upf and target.id == ctx.author.id:
            menu.add_option("思惟奈ちゃんユーザープロファイル情報","sina_info","思惟奈ちゃん上での扱いなどを表示します。")
        if in_guild:
            menu.add_option("サーバー内基本情報","server_basic","サーバー内での基本的な情報を表示します。")
            menu.add_option("役職情報","roles","所有している役職/権限情報を表示します。")
            if target.voice:
                menu.add_option("ボイス情報", "voice", "ユーザーのボイス/ステージチャンネルでの状態を表示します。")
        
        msg = await ctx.send("下から表示したい情報を選んでください。タイムアウトは30秒です。", view=menu)
        """if ctx.interaction:
            ctp:dpyui.slash_command_callback = await dpyui.slash_command_callback.from_dpy_interaction(ctx.interaction)
            await ctp.send_response_with_ui("下から表示したい情報を選んでください。タイムアウトは30秒です。", ui=menu)
            ctx.interaction.response._response_type = discord.InteractionResponseType.channel_message
            msg = await ctx.interaction.original_response()     
        else:
            msg = await self.bot.dpyui.send_with_ui(ctx.channel, "下から表示したい情報を選んでください。タイムアウトは30秒です。",ui=menu)"""
        
        while True:
            try:
                cb:dpyui.interaction_menu_callback = await self.bot.wait_for("menu_select", check=lambda icb:icb.custom_id==f"userinfo_{ctx.message.id}" and icb.message.id==msg.id and icb.user_id == ctx.author.id, timeout=30)
            except:
                return
            e = discord.Embed(title="ユーザー情報", color=self.bot.ec)
            e.set_author(name=target.name, icon_url=target.display_avatar.url)
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
                e.add_field(name="ユーザーID", value=str(target.id))
                try:
                    e.add_field(name="思惟奈との共通サーバー数",value=f"{len(target.mutual_guilds)}個".replace("0個","(なし)"))
                except:
                    pass

            elif cb.selected_value[0] == "avatar":
                e.description="ユーザーアバターページ"
                e.add_field(name="アバターURL",value=target.display_avatar.url)
                e.set_image(url=target.display_avatar.url)
            
            elif cb.selected_value[0] == "badges":
                e.description="ユーザーバッジページ"
                e.add_field(name=await ctx._("aui-flags"),
                            value=f'\n'.join(flags.get_list()) or "(なし)")
            elif cb.selected_value[0] == "sina_info":
                e.description="ユーザープロファイルページ"
                e.add_field(name="prefix", value=upf["prefix"])
                e.add_field(name=await ctx._("cpro-gpoint"), value=upf["gpoint"])
                e.add_field(name=await ctx._("cpro-levelcard"), value=upf["levcard"])
                e.add_field(name=await ctx._("cpro-renotif"), value=upf["onnotif"])
                e.add_field(name=await ctx._("cpro-lang"), value=upf["lang"])
                e.add_field(name=await ctx._("sina-v-ac"), value=upf["sinapartner"])
                e.add_field(name="グローバルチャットニックネーム", value=upf["gnick"])
                e.add_field(name="グローバルチャットカラー", value=str(upf["gcolor"]))
                e.add_field(name="グローバルチャットモデレーター", value="はい" if upf["gmod"] == 1 else "いいえ")
                e.add_field(name="グローバルチャットテスター", value="はい" if upf["galpha"] == 1 else "いいえ")
                e.add_field(name="グローバルチャットスターユーザー", value="はい" if upf["gstar"] == 1 else "いいえ")
            elif cb.selected_value[0] == "server_basic":
                if target.premium_since is not None:
                    e.add_field(name="サーバーブースト情報",
                        value=f"since {target.premium_since}")
                e.add_field(name="表示名",value=target.display_name)
                e.add_field(name="サーバー参加時間", value=(target.joined_at + rdelta(
                    hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

                
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
                    value=f"`{'`,`'.join([await ctx._(f'p-{i[0]}') for i in list(target.guild_permissions) if i[1]])}`",inline=False)
            elif cb.selected_value[0] == "banner":
                # https://cdn.discordapp.com/banners/404243934210949120/4d22b0afc7bf59810ab3ca44559be8a5.png?size=1024
                banner_url = f'https://cdn.discordapp.com/banners/{target.id}/{ucb["banner"]}.png?size=1024'
                e.description="ユーザーバナーページ"
                e.add_field(name="バナーURL",value=banner_url)
                e.set_image(url=banner_url)
            elif cb.selected_value[0] == "voice":
                e.description = f"{target.voice.channel.guild.name} - {target.voice.channel.name}{'(AFK)' if target.voice.afk else ''}"
                vste = ""
                if target.voice.deaf:
                    # サバスピーカーミュート
                    vste = vste+str(self.bot.create_emoji_str('s_g_mute_sp',653161518057127937))
                else:
                    # サバスピーカーオン
                    vste = vste+str(self.bot.create_emoji_str('s_g_on_sp',653161518082293770))
                if target.voice.mute:
                    # サバマイクミュート
                    vste = vste+str(self.bot.create_emoji_str('s_g_mute_mic',653161518086619137))
                else:
                    # サバマイクオン
                    vste = vste+str(self.bot.create_emoji_str('s_g_on_mic',653161518086619137))
                if target.voice.self_deaf:
                    # スピーカーミュート
                    vste = vste+str(self.bot.create_emoji_str('s_u_mute_sp',653161518258585620))
                else:
                    # スピーカーオン
                    vste = vste+str(self.bot.create_emoji_str('s_u_on_sp',653161517881098272))
                if target.voice.self_mute:
                    # マイクミュート
                    vste = vste+str(self.bot.create_emoji_str('s_u_mute_mic',653161519143714816))
                else:
                    # マイクオン
                    vste = vste+str(self.bot.create_emoji_str('s_u_on_mic',653161518224900096))
                if target.voice.self_video:
                    # 画面共有
                    vste = vste+str(self.bot.create_emoji_str('s_screen_share',653161517960658945))
                elif target.voice.self_stream:
                    # GoLive
                    vste = vste+str(self.bot.create_emoji_str('s_Golive',653161518250196992))
                e.add_field(name="ステータス(status)", value=vste)
                lmusic = ut.get_vmusic(self.bot, target)
                if lmusic:
                    if lmusic["guild"].id == ctx.guild.id and target.id in [i.id for i in ctx.voice_client.channel.members]:
                        e.add_field(name="ボイス/ステージチャンネルで思惟奈ちゃんを使って音楽を聞いています。",
                                        value=f"[{lmusic['name']}]({lmusic['url']} )")

            else:
                e.add_field(name="例外", value="このメッセージを読んでいるあなたは、どうやってこのメッセージを表示させましたか？")
            await cb.response()
            await msg.edit(content="",embed=e)

    @info_group.command(name="server",aliases=["si"], description="サーバーについての情報を表示します。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def ginfo(self, ctx: commands.Context):
        u = ctx.author
        # b = ctx.guild.me
        gp = await self.bot.cursor.fetchone("select * from guilds where id = %s",(ctx.guild.id,))
        #gp = await self.bot.cursor.fetchone()
        menu = dpyui.interaction_menu(f"serverinfo_{ctx.message.id}","表示する項目をここから選択",1,1)
        menu.add_option("概要","description","サーバー概要を表示します。")
        menu.add_option("ロール","role","ロール一覧を表示します。")
        menu.add_option("絵文字","emoji","絵文字一覧を表示します。")
        menu.add_option("チャンネル","channels","チャンネル一覧を表示します。")
        if u.guild_permissions.manage_guild and u.guild_permissions.create_instant_invite:
            menu.add_option("ウィジェット","widget","サーバーウィジェットを表示します。")
        menu.add_option("カスタム招待リンク","custom_invite","カスタム招待リンクを表示します。")
        menu.add_option("安全設定","safety_setting","ユーザーの安全性にかかわる設定を表示します。")
        if u.guild_permissions.ban_members:
            menu.add_option("BANしたユーザー","banned_user","BANされているメンバー一覧を表示します。")
        if u.guild_permissions.manage_guild and "COMMUNITY" in u.guild.features:
            menu.add_option("コミュニティ設定","community","コミュニティの設定を表示します。")
            menu.add_option("ようこそ画面","welcome_screen","ようこそ画面の状態を表示します。")
        menu.add_option("サーバーブースト","boost_status","サーバーブーストと追加要素を表示します。")
        menu.add_option("メンバー","members","メンバー一覧状態を表示します。")
        if u.guild_permissions.manage_guild and u.guild_permissions.create_instant_invite:
            menu.add_option("招待リンク","invites","作成されている招待リンク一覧を表示します。")
        menu.add_option("思惟奈ちゃんプロファイル","profile","思惟奈ちゃん内での情報を表示します。")
        menu.add_option("その他","other","その他、サーバーに関する情報を表示します。")

        msg = await ctx.send("下から表示したい情報を選んでください。タイムアウトは30秒です。", view=menu)

        """if ctx.interaction:
            ctp:dpyui.slash_command_callback = await dpyui.slash_command_callback.from_dpy_interaction(ctx.interaction)
            await ctp.send_response_with_ui("下から表示したい情報を選んでください。タイムアウトは30秒です。", ui=menu)
            ctx.interaction.response._response_type = discord.InteractionResponseType.channel_message
            msg = await ctx.interaction.original_response()
        else:
            msg = await self.bot.dpyui.send_with_ui(ctx.channel, "下から表示したい情報を選んでください。タイムアウトは30秒です。",ui=menu)"""
        
        while True:
            try:
                cb:dpyui.interaction_menu_callback = await self.bot.wait_for("menu_select", check=lambda icb:icb.custom_id==f"serverinfo_{ctx.message.id}" and icb.message.id==msg.id and icb.user_id == ctx.author.id, timeout=30)
            except:
                return
            e = discord.Embed(title="サーバー情報", color=self.bot.ec)
            e.set_author(name=ctx.guild.name, icon_url=getattr(ctx.guild.icon,"id", None))
            if cb.selected_value[0] == "description":
                e.add_field(name="AFKチャンネル/タイムアウト時間", value=f"{ctx.guild.afk_channel}/{ctx.guild.afk_timeout}")
                sysch_setting = []
                if ctx.guild.system_channel_flags.join_notifications:
                    sysch_setting.append("メンバー参加時のメッセージ")
                if ctx.guild.system_channel_flags.join_notification_replies:
                    sysch_setting.append("ウェルカムメッセージへのスタンプ返信の提案")
                if ctx.guild.system_channel_flags.premium_subscriptions:
                    sysch_setting.append("サーバーブースト時のメッセージ")
                if ctx.guild.system_channel_flags.guild_reminder_notifications:
                    sysch_setting.append("サーバー設定に役立つヒント")
                e.add_field(name="システムメッセージチャンネル設定", value=f"{ctx.guild.system_channel}/(`{'`,`'.join(sysch_setting) or '(なし)'})`")
                e.add_field(name="デフォルト通知設定", value=ctx.guild.default_notifications)
                e.add_field(name="ブースト進捗バーの表示", value=ctx.guild.premium_progress_bar_enabled)
            elif cb.selected_value[0] == "role":
                rl = ctx.guild.roles[::-1]
                rls = ""
                for r in rl:
                    if len(f"{rls}\n{r.name}") >= 1998:
                        rls = rls+"\n…"
                        break
                    else:
                        rls = f"{rls}\n{r.name}"
                e.description = rls
            elif cb.selected_value[0] == "emoji":
                ejs = ""
                for i in ctx.guild.emojis:
                    if len(ejs + "," + str(i)) >= 1998:
                        ejs = ejs+"など"
                        break
                    else:
                        ejs = ejs + "," + str(i)
                e.description = ejs
            elif cb.selected_value[0] == "channels":
                for mct, mch in ctx.guild.by_category():
                    chs = "\n".join([i.name for i in mch])
                    e.add_field(name=str(mct).replace("None", await ctx._(
                        "ginfo-nocate")), value=f"```{chs}```", inline=True)
            elif cb.selected_value[0] == "widget":
                if ctx.guild.widget_enabled:
                    wd = await ctx.guild.widget()
                    e.add_field(name="json_url", value=wd.json_url)
                    e.add_field(name="招待リンク", value=wd.invite_url)

            elif cb.selected_value[0] == "custom_invite":
                try:
                    vi = await ctx.guild.vanity_invite()
                    vi = vi.code
                except:
                    vi = "このサーバーには、カスタム招待リンクがありません"
                e.description = vi
            elif cb.selected_value[0] == "safety_setting":
                if ctx.guild.verification_level == discord.VerificationLevel.none:
                    e.add_field(name=await ctx._("ginfo-vlevel"),
                                value=await ctx._("ginfo-vlnone"))
                elif ctx.guild.verification_level == discord.VerificationLevel.low:
                    e.add_field(name=await ctx._("ginfo-vlevel"),
                                value=await ctx._("ginfo-vl1"))
                elif ctx.guild.verification_level == discord.VerificationLevel.medium:
                    e.add_field(name=await ctx._("ginfo-vlevel"),
                                value=await ctx._("ginfo-vl2"))
                elif ctx.guild.verification_level == discord.VerificationLevel.high:
                    e.add_field(name=await ctx._("ginfo-vlevel"),
                                value=await ctx._("ginfo-vl3"))
                elif ctx.guild.verification_level == discord.VerificationLevel.highest:
                    e.add_field(name=await ctx._("ginfo-vlevel"),
                                value=await ctx._("ginfo-vl4"))
                if ctx.guild.explicit_content_filter == discord.ContentFilter.disabled:
                    e.add_field(name=await ctx._("ginfo-filter"),
                                value=await ctx._("ginfo-fnone"))
                elif ctx.guild.explicit_content_filter == discord.ContentFilter.no_role:
                    e.add_field(name=await ctx._("ginfo-filter"),
                                value=await ctx._("ginfo-f1"))
                elif ctx.guild.explicit_content_filter == discord.ContentFilter.all_members:
                    e.add_field(name=await ctx._("ginfo-filter"),
                                value=await ctx._("ginfo-f2"))
            elif cb.selected_value[0] == "banned_user":
                vbl = await ctx._("ginfo-strlenover")
                bl = []
                async for i in ctx.guild.bans():
                    bl.append(f"{i.user},reason:{i.reason}")
                if len("\n".join(bl)) <= 1024:
                    vbl = "\n".join(bl)
                e.description = vbl
            elif cb.selected_value[0] == "community":
                e.description = ctx.guild.description or "概要なし"
                e.add_field(name="優先言語", value=ctx.guild.preferred_locale)
                e.add_field(name="ルールチャンネル",
                            value=ctx.guild.rules_channel.mention)
                e.add_field(name="コミュニティ更新情報チャンネル",
                            value=ctx.guild.public_updates_channel.mention)
            elif cb.selected_value[0] == "welcome_screen":
                pass
            elif cb.selected_value[0] == "boost_status":
                e.description=f"レベル:{ctx.guild.premium_tier}\n({ctx.guild.premium_subscription_count}ブースト)"
                e.add_field(name=await ctx._("ginfo-bst-add"),
                            value=await ctx._(f"ginfo-blev{ctx.guild.premium_tier}"))
            elif cb.selected_value[0] == "members":
                vml = await ctx._("ginfo-strlenover")
                if len("\n".join([f"{str(i)}" for i in ctx.guild.members])) <= 1024:
                    vml = "\n".join([f"{str(i)}" for i in ctx.guild.members]).replace(
                        str(ctx.guild.owner), f"👑{str(ctx.guild.owner)}")
                e.description=f"member count:{len(ctx.guild.members)}\n```"+vml+"```"
            elif cb.selected_value[0] == "invites":
                vil = await ctx._("ginfo-strlenover")
                if len("\n".join([f'{i.code},{await ctx._("ginfo-use-invite")}:{i.uses}/{i.max_uses},{await ctx._("ginfo-created-invite")}:{i.inviter}' for i in await ctx.guild.invites()])) <= 1023:
                    vil = "\n".join([f'{i.code},{await ctx._("ginfo-use-invite")}:{i.uses}/{i.max_uses},{await ctx._("ginfo-created-invite")}:{i.inviter}' for i in await ctx.guild.invites()])
                e.description=vil
            elif cb.selected_value[0] == "profile":
                e.description = await ctx._(
                    "ginfo-gprodesc", gp["reward"], gp["sendlog"], gp["prefix"], gp["lang"],)
            elif cb.selected_value[0] == "other":
                e.add_field(name="owner", value=ctx.guild.owner.mention)
                e.add_field(name="features", value=f"```{','.join(ctx.guild.features)}```")
            await cb.response()
            await msg.edit(content="",embed=e)


    @info_group.command(name="role", aliases=["役職情報", "次の役職について教えて"], description="特定役職について表示します。")
    @app_commands.describe(role="表示する役職")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def roleinfo(self, ctx, *, role: discord.Role):
        if role.guild == ctx.guild:
            embed = discord.Embed(
                title=role.name, description=f"id:{role.id}", color=role.colour)
            embed.add_field(name=await ctx._("roleinfo-hoist"), value=role.hoist)
            embed.add_field(name=await ctx._("roleinfo-mention"),
                            value=role.mentionable)
            hasmember = ""
            for m in role.members:
                hasmember = hasmember + f"{m.mention},"
            if not hasmember == "":
                if len(hasmember) <= 1024:
                    embed.add_field(name=await ctx._(
                        "roleinfo-hasmember"), value=hasmember)
                else:
                    embed.add_field(name=await ctx._(
                        "roleinfo-hasmember"), value="たくさんのユーザー")
            else:
                embed.add_field(name=await ctx._(
                    "roleinfo-hasmember"), value="(None)")
            hasper = ""
            for pn, bl in iter(role.permissions):
                if bl:
                    hasper = hasper + f"`{await ctx._(f'p-{pn}')}`,"
            embed.add_field(name=await ctx._("roleinfo-hasper"), value=hasper or "(権限なし)")
            embed.add_field(name=await ctx._("roleinfo-created"), value=(role.created_at + rdelta(
                hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            if role.icon:
                embed.set_thumbnail(role.icon.url)

            await ctx.send(embed=embed)
        else:
            await ctx.send(await ctx._("roleinfo-other"))


    @info_group.command(name="invite", description="招待情報を表示します。")
    @app_commands.describe(invite="表示する招待")
    @ut.runnable_check()
    async def cinvite(self, ctx, invite:str):
        i:discord.Invite = await self.bot.fetch_invite(invite)
        e = discord.Embed(title=await ctx._(
            "cinvite-title"), description=await ctx._("cinvite-from", str(i.inviter)), color=self.bot.ec)
        e.set_author(name=f'{i.guild.name}({i.guild.id})',
                     icon_url=i.guild.icon.replace(format="png"))
        e.add_field(name=await ctx._("cinvite-memcount"),
                    value=f'{i.approximate_member_count}\n({await ctx._("cinvite-onmemcount")}{i.approximate_presence_count})')
        e.add_field(name=await ctx._("cinvite-ch"),
                    value=f"{i.channel.name}({i.channel.type})")
        e.add_field(name=await ctx._("cinvite-tmp"), value=str(i.temporary))
        e.add_field(name=await ctx._("cinvite-deleted"), value=str(i.revoked))
        e.add_field(name="サーバーのブースト数", value=i.guild.premium_subscription_count)
        e.add_field(name=await ctx._("cinvite-link"), value=i.url, inline=False)
        e.add_field(name="サーバーのfeatures",value=f"```{','.join(i.guild.features)}```", inline=False)


        if i.guild.splash:
            e.set_thumbnail(url=i.guild.splash.replace(static_format="png"))
        if i.guild.banner:
            e.set_image(url=i.guild.banner.replace(static_format="png"))
        e.set_footer(text=await ctx._("cinvite-createdat"))
        e.timestamp = i.created_at or None
        await ctx.send(embed=e)

    @info_group.command(name="channel", description="特定チャンネルについて表示する")
    @app_commands.describe(channel="表示するチャンネル")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def chinfo(self, ctx:commands.Context, channel:commands.GuildChannelConverter):
        try:
            if channel:
                channel = await channel.fetch()
        except:pass
        ch = channel or ctx.channel
        e = discord.Embed(title="チャンネル情報", color=self.bot.ec)
        e.timestamp=ch.created_at
        if isinstance(ch, discord.TextChannel):
            if ch == ctx.guild.rules_channel:
                e.description = f"{ch.name}(id:{ch.id})[ルールチャンネル]"
            elif ch.is_news():
                e.description = f"{ch.name}(id:{ch.id})[ニュースチャンネル]"
            else:
                e.description = f"{ch.name}(id:{ch.id})[テキストチャンネル]"

            e.add_field(name="トピック", value=ch.topic or "(トピックなし)")

            if ch.category:
                e.add_field(name="所属カテゴリー", value=f"{ch.category.name}(ID:{ch.category.id})")
                e.add_field(name="権限同期", value="はい" if ch.permissions_synced else "いいえ")
            
            e.add_field(name="NSFW指定", value="はい" if ch.nsfw else "いいえ")
            e.add_field(name="チャンネルリンク", value=ch.jump_url)
            e.add_field(name="スレッド数", value=f"{len(ch.threads)}個")

            if not ch.slowmode_delay == 0:
                e.add_field(name="スローモードの時間",value=f"{ch.slowmode_delay}秒")
            
        elif isinstance(ch, discord.ForumChannel):
            e.description = f"{ch.name}(id:{ch.id})[フォームチャンネル]"

            e.add_field(name="トピック", value=ch.topic or "(トピックなし)")

            if ch.category:
                e.add_field(name="所属カテゴリー", value=f"{ch.category.name}(ID:{ch.category.id})")
                e.add_field(name="権限同期", value="はい" if ch.permissions_synced else "いいえ")
            
            e.add_field(name="NSFW指定", value="はい" if ch.nsfw else "いいえ")
            e.add_field(name="チャンネルリンク", value=ch.jump_url)
            e.add_field(name="スレッド数", value=f"{len(ch.threads)}個")

            if not ch.slowmode_delay == 0:
                e.add_field(name="スローモードの時間",value=f"{ch.slowmode_delay}秒")
        elif isinstance(ch, discord.Thread):
            e.description = f"{ch.name}(id:{ch.id})[スレッド]"

            e.add_field(name="所属チャンネル", value=f"{ch.parent.name}(ID:{ch.parent.id})")

            e.add_field(name="メンバー招待可能か", value="はい" if ch.invitable else "いいえ")
            e.add_field(name="アーカイブされているかどうか", value="はい" if ch.archived else "いいえ")
            e.add_field(name="ロックされているかどうか", value="はい" if ch.locked else "いいえ")
            e.add_field(name="チャンネルリンク", value=ch.jump_url)
            if ch.starter_message:
                e.add_field(name="最初のメッセージリンク", value=ch.starter_message.jump_url)

            e.add_field(name="自動アーカイブ時間", value=f"{ch.auto_archive_duration/60}時間")

            if not ch.slowmode_delay == 0:
                e.add_field(name="スローモードの時間",value=f"{ch.slowmode_delay}秒")

        elif isinstance(ch, discord.VoiceChannel):
            e.description = f"{ch.name}(id:{ch.id})[ボイスチャンネル]"
            if ch.category:
                e.add_field(name="所属するカテゴリ",value=f"{ch.category.name}({ch.category.id})")
                e.add_field(name="権限同期", value="はい" if ch.permissions_synced else "いいえ")
            e.add_field(name="チャンネルビットレート",value=f"{ch.bitrate/1000}Kbps")
            if not ch.user_limit == 0:
                e.add_field(name="ユーザー数制限",value=f"{ch.user_limit}人")
            e.add_field(name="ボイスチャンネルの地域",value=ch.rtc_region if ch.rtc_region else "自動")
            e.add_field(name="NSFW指定", value="はい" if ch.nsfw else "いいえ")
            e.add_field(name="チャンネルリンク", value=ch.jump_url)
            e.add_field(name="予定されているイベント数", value=f"{len(ch.scheduled_events)}個")

        elif isinstance(ch, discord.StageChannel):
            e.description = f"{ch.name}(id:{ch.id})[ステージチャンネル]"
            if ch.category:
                e.add_field(name="所属するカテゴリ",value=f"{ch.category.name}({ch.category.id})")
                e.add_field(name="権限同期", value="はい" if ch.permissions_synced else "いいえ")
            e.add_field(name="トピック", value=ch.topic or "(トピックなし)")
            e.add_field(name="チャンネルビットレート",value=f"{ch.bitrate/1000}Kbps")
            if not ch.user_limit == 0:
                e.add_field(name="ユーザー数制限",value=f"{ch.user_limit}人")
            e.add_field(name="ボイスチャンネルの地域",value=ch.rtc_region if ch.rtc_region else "自動")
            e.add_field(name="NSFW指定", value="はい" if ch.nsfw else "いいえ")
            e.add_field(name="チャンネルリンク", value=ch.jump_url)
            e.add_field(name="予定されているイベント数", value=f"{len(ch.scheduled_events)}個")

        elif isinstance(ch, discord.CategoryChannel):
            e.description = f"{ch.name}(id:{ch.id})[カテゴリー]"

            e.add_field(name="NSFW指定", value="はい" if ch.nsfw else "いいえ")
            e.add_field(name="チャンネルリンク", value=ch.jump_url)
            e.add_field(name="テキストチャンネル数", value=f"{len(ch.text_channels)}個")
            e.add_field(name="ボイスチャンネル数", value=f"{len(ch.voice_channels)}個")
            e.add_field(name="ステージチャンネル数", value=f"{len(ch.stage_channels)}個")

        else:
            e.description = f"{ch.name}(id:{ch.id})[不明]"

        await ctx.send(embed=e)

    @info_group.command(name="emoji",description="絵文字に関して表示します。")
    @app_commands.describe(emj="詳細表示する絵文字")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def emojiinfo(self, ctx, *, emj: discord.Emoji):
        embed = discord.Embed(
            title=emj.name, description=f"id:{emj.id}", color=self.bot.ec)
        embed.add_field(name=await ctx._("einfo-animated"), value=emj.animated)
        embed.add_field(name=await ctx._("einfo-manageout"), value=emj.managed)
        if emj.user:
            embed.add_field(name=await ctx._("einfo-adduser"),
                            value=str(emj.user))
        embed.add_field(name="url", value=emj.url)
        embed.set_footer(text=await ctx._("einfo-addday"))
        embed.set_thumbnail(url=emj.url)
        embed.timestamp = emj.created_at
        await ctx.send(embed=embed)



    @commands.hybrid_command(description="思惟奈ちゃんや他のBotの招待URLを作成できます。")
    @app_commands.describe(target="招待を作るBot")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def invite(self,ctx,*,target:Optional[discord.Member]):
        if target is None:
            target = ctx.guild.me
        if target.bot:
            if isinstance(target,discord.Member):
                ilink = discord.utils.oauth_url(str(target.id),permissions=target.guild_permissions,scopes=("bot","applications.commands"))
                e=discord.Embed(title="bot招待リンク",description=ilink,color=self.bot.ec)
                e.add_field(name="このリンクで導入した際の権限",
                                value=f"`{'`,`'.join([await ctx._(f'p-{i[0]}') for i in list(target.guild_permissions) if i[1]])}`")
                e.set_author(name=f"{target}({target.id})",icon_url=target.display_avatar.replace(static_format="png").url)
            else:
                ilink = discord.utils.oauth_url(str(target.id),permissions=ctx.guild.me.guild_permissions,scopes=("bot","applications.commands"))
                e=discord.Embed(title="bot招待リンク",description=ilink,color=self.bot.ec)
                e.add_field(name="このリンクで導入した際の権限",
                                value=f"`{'`,`'.join([await ctx._(f'p-{i[0]}') for i in list(ctx.guild.me.guild_permissions) if i[1]])}`")
                e.set_author(name=f"{target}({target.id})",icon_url=target.display_avatar.replace(static_format="png").url)
            await ctx.send(embed=e)
        else:
            await ctx.send(embed=discord.Embed(title="エラー",description="ユーザーアカウントの導入リンクは作成できません！",color=self.bot.ec))

    @commands.hybrid_command(description="このBotでの特権を表示します。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def features(self, ctx:commands.Context):
        if ctx.interaction:
            await ctx.send(embed=ut.getEmbed("あなたのfeatures", "```{}```".format(",".join(self.bot.features.get(ctx.author.id, ["(なし)"])))), ephemeral=True)
        else:
            await ctx.author.send(embed=ut.getEmbed("あなたのfeatures", "```{}```".format(",".join(self.bot.features.get(ctx.author.id, ["(なし)"])))))

async def setup(bot):
    await bot.add_cog(info_check(bot))
