# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import datetime
from dateutil.relativedelta import relativedelta as rdelta
import traceback
from typing import Union

import config as cf

import m10s_util as ut

from my_module import dpy_interaction as dpyui


class info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo", aliases=["ui", "anyuserinfo", "user"])
    async def _info_of_user(self, ctx, target:Union[commands.MemberConverter,commands.UserConverter,None]):
        if target:
            if isinstance(target, discord.User):
                in_guild = False
            else:
                in_guild = True
        else:
            target = ctx.author
            in_guild = True

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


        menu = dpyui.interaction_menu(f"userinfo_{ctx.message.id}","表示する項目をここから選択",1,1)
        menu.add_option("基本情報","user_basic","ユーザー名やディスクリミネーター等を表示します。")
        menu.add_option("アバター","avatar","ユーザーアバターを表示します。")
        menu.add_option("ユーザーバッジ","badges","ユーザーのバッジ情報を表示します。")
        if ucb["banner"]:
            menu.add_option("ユーザーバナー","banner","ユーザーの設定しているバナー画像を表示します。")
        if upf:
            menu.add_option("思惟奈ちゃんユーザープロファイル情報","sina_info","思惟奈ちゃん上での扱いなどを表示します。")
        if in_guild:
            menu.add_option("サーバー内基本情報","server_basic","サーバー内での基本的な情報を表示します。")
            menu.add_option("プレゼンス情報","presence","ユーザーのオンライン状況やトップ表示されているアクティビティについて表示します。")
            menu.add_option("役職情報","roles","所有している役職/権限情報を表示します。")
        msg = await self.bot.dpyui.send_with_ui(ctx.channel, "下から表示したい情報を選んでください。タイムアウトは30秒です。",ui=menu)
        while True:
            try:
                cb:dpyui.interaction_menu_callback = await self.bot.wait_for("menu_select", check=lambda icb:icb.custom_id==f"userinfo_{ctx.message.id}" and icb.message.id==msg.id and icb.user_id == ctx.author.id, timeout=30)
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
                e.add_field(name="ユーザーID", value=str(target.id))
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
                    value=f"`{'`,`'.join([await ctx._(f'p-{i[0]}') for i in list(target.guild_permissions) if i[1]])}`",inline=False)

            elif cb.selected_value[0] == "banner":
                # https://cdn.discordapp.com/banners/404243934210949120/4d22b0afc7bf59810ab3ca44559be8a5.png?size=1024
                banner_url = f'https://cdn.discordapp.com/banners/{target.id}/{ucb["banner"]}.png?size=1024'
                e.description="ユーザーバナーページ"
                e.add_field(name="バナーURL",value=banner_url)
                e.set_image(url=banner_url)
            else:
                e.add_field(name="例外", value="このメッセージを読んでいるあなたは、どうやってこのメッセージを表示させましたか？")
            await cb.response()
            await msg.edit(content="",embed=e)
            

    @commands.command()
    async def cinvite(self, ctx, ivt: str):
        i = await self.bot.fetch_invite(ivt)
        e = discord.Embed(title=await ctx._(
            "cinvite-title"), description=await ctx._("cinvite-from", str(i.inviter)), color=self.bot.ec)
        e.set_author(name=f'{i.guild.name}({i.guild.id})',
                     icon_url=i.guild.icon_url_as(format="png"))
        e.add_field(name=await ctx._("cinvite-memcount"),
                    value=f'{i.approximate_member_count}\n({await ctx._("cinvite-onmemcount")}{i.approximate_presence_count})')
        e.add_field(name=await ctx._("cinvite-ch"),
                    value=f"{i.channel.name}({i.channel.type})")
        e.add_field(name=await ctx._("cinvite-tmp"), value=str(i.temporary))
        e.add_field(name=await ctx._("cinvite-deleted"), value=str(i.revoked))
        e.add_field(name=await ctx._("cinvite-link"), value=i.url, inline=False)
        e.set_footer(text=await ctx._("cinvite-createdat"))
        e.timestamp = i.created_at or discord.Embed.Empty
        await ctx.send(embed=e)

    @commands.command()
    async def emojiinfo(self, ctx, *, emj: commands.EmojiConverter=None):

        if emj is None:
            await ctx.send(await ctx._("einfo-needarg"))
        else:
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

    @commands.command(name="dguild")
    async def serverinfo(self, ctx, sid=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if sid is not None:
            sevinfo = self.bot.get_guild(int(str(sid)))
        else:
            sevinfo = ctx.message.guild
        
        if sevinfo is None:
            return await ctx.send("そのサーバーに思惟奈ちゃんがいるかどうか確認してください。")

        try:
            embed = discord.Embed(title=await ctx._(
                "serverinfo-name"), description=sevinfo.name, color=self.bot.ec)
            if sevinfo.icon_url is not None:
                embed.set_thumbnail(
                    url=sevinfo.icon_url_as(static_format='png'))
            embed.add_field(name=await ctx._("serverinfo-role"),
                            value=len(sevinfo.roles))
            embed.add_field(name=await ctx._("serverinfo-emoji"),
                            value=len(sevinfo.emojis))
            embed.add_field(name=await ctx._("serverinfo-country"),
                            value=str(sevinfo.region))
            bm = 0
            ubm = 0
            for m in sevinfo.members:
                if m.bot:
                    bm = bm + 1
                else:
                    ubm = ubm + 1
            embed.add_field(name=await ctx._("serverinfo-member"),
                            value=f"{len(sevinfo.members)}(bot:{bm}/user:{ubm})")
            embed.add_field(name=await ctx._("serverinfo-channel"),
                            value=f'{await ctx._("serverinfo-text")}:{len(sevinfo.text_channels)}\n{await ctx._("serverinfo-voice")}:{len(sevinfo.voice_channels)}')
            embed.add_field(name=await ctx._("serverinfo-id"), value=sevinfo.id)
            embed.add_field(name=await ctx._("serverinfo-owner"),
                            value=sevinfo.owner.name)
            embed.add_field(name=await ctx._("serverinfo-create"), value=(sevinfo.created_at + rdelta(
                hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            rlist = ",".join([i.name for i in sevinfo.roles])
            if len(rlist) <= 1000:
                embed.add_field(name=await ctx._("serverinfo-roles"), value=rlist)
            try:
                embed.add_field(name=await ctx._("serverinfo-nitroboost"),
                                value=await ctx._("serverinfo-nitroboost-val", sevinfo.premium_tier))
                embed.add_field(name=await ctx._("serverinfo-nitroboost-can-title"), value=await ctx._(
                    f"serverinfo-nitroboost-can-{sevinfo.premium_tier}", sevinfo.premium_tier, sevinfo.premium_subscription_count))
            except:
                pass

            if sevinfo.system_channel:
                embed.add_field(name=await ctx._("serverinfo-sysch"),
                                value=sevinfo.system_channel)
                try:
                    embed.add_field(name=await ctx._("serverinfo-sysch-welcome"),
                                    value=sevinfo.system_channel_flags.join_notifications)
                    embed.add_field(name=await ctx._("serverinfo-sysch-boost"),
                                    value=sevinfo.system_channel_flags.premium_subscriptions)
                except:
                    pass
            if sevinfo.afk_channel:
                embed.add_field(name=await ctx._("serverinfo-afkch"),
                                value=sevinfo.afk_channel.name)
                embed.add_field(name=await ctx._("serverinfo-afktimeout"),
                                value=str(sevinfo.afk_timeout/60))
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
            # await ctx.send(await ctx._("serverinfo-except"))

    @commands.command()
    async def cprofile(self, ctx, usid=None):
        uid = usid or ctx.author.id
        await self.bot.cursor.execute("select * from users where id=%s", (uid,))
        pf = await self.bot.cursor.fetchone()
        e = discord.Embed(title=await ctx._("cpro-title"), description=f"id:{uid}")
        e.add_field(name="prefix", value=pf["prefix"])
        e.add_field(name=await ctx._("cpro-gpoint"), value=pf["gpoint"])
        e.add_field(name=await ctx._("cpro-levelcard"), value=pf["levcard"])
        e.add_field(name=await ctx._("cpro-renotif"), value=pf["onnotif"])
        e.add_field(name=await ctx._("cpro-lang"), value=pf["lang"])
        e.add_field(name=await ctx._("sina-v-ac"), value=pf["sinapartner"])
        await ctx.send(embed=e)

    @commands.command()
    async def checkmember(self, ctx, member: commands.MemberConverter):
        if not await ctx.user_lang() == "ja":
            await ctx.send(await ctx._("cannot-run"))
            return
        bunotif = 0
        for g in self.bot.guilds:
            try:
                tmp = await g.bans()
            except:
                continue
            banulist = [i.user.id for i in tmp]
            if member.id in banulist:
                bunotif = bunotif + 1
        if bunotif == 0:
            await ctx.send(embed=discord.Embed(title=await ctx._("ucheck-title", member), description=await ctx._("ucheck-not_ban")))
        else:
            await ctx.send(embed=discord.Embed(title=await ctx._("ucheck-title", member), description=await ctx._("ucheck-not_ban", bunotif)))

    @commands.command(aliases=["次のボイスチャンネルのURLを教えて"])
    async def vcurl(self, ctx, vch: commands.VoiceChannelConverter=None):
        if vch is None and (ctx.author.voice is not None):
            ch = ctx.author.voice.channel
        else:
            ch = vch
        await ctx.send(embed=ut.getEmbed(ch.name, f"https://discordapp.com/channels/{ctx.guild.id}/{ch.id}"))

    #chinfo is 'm10s_chinfo_rewrite' now

    @commands.command(aliases=["ボイス情報", "音声情報を教えて"])
    async def voiceinfo(self, ctx, mus: commands.MemberConverter=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if mus is None:
            info = ctx.message.author
        else:
            info = mus
        try:
            embed = discord.Embed(
                title=info.display_name, description=f"{info.voice.channel.guild.name} - {info.voice.channel.name}", color=info.colour)
            vste = ""
            if info.voice.deaf:
                # サバスピーカーミュート
                vste = vste+str(self.bot.get_emoji(653161518057127937))
            else:
                # サバスピーカーオン
                vste = vste+str(self.bot.get_emoji(653161518082293770))
            if info.voice.mute:
                # サバマイクミュート
                vste = vste+str(self.bot.get_emoji(653161518086619137))
            else:
                # サバマイクオン
                vste = vste+str(self.bot.get_emoji(653161518086619137))
            if info.voice.self_deaf:
                # スピーカーミュート
                vste = vste+str(self.bot.get_emoji(653161518258585620))
            else:
                # スピーカーオン
                vste = vste+str(self.bot.get_emoji(653161517881098272))
            if info.voice.self_mute:
                # マイクミュート
                vste = vste+str(self.bot.get_emoji(653161519143714816))
            else:
                # マイクオン
                vste = vste+str(self.bot.get_emoji(653161518224900096))
            if info.voice.self_video:
                # 画面共有
                vste = vste+str(self.bot.get_emoji(653161517960658945))
            elif info.voice.self_stream:
                # GoLive
                vste = vste+str(self.bot.get_emoji(653161518250196992))
            embed.add_field(name="ステータス(status)", value=vste)
        except AttributeError:
            await ctx.send(await ctx._("vi-nfch"))
        finally:
            lmusic = ut.get_vmusic(self.bot, info)
            if lmusic:
                if lmusic["guild"].id == ctx.guild.id and info.id in [i.id for i in ctx.voice_client.channel.members]:
                    embed.add_field(name="ボイスチャットで思惟奈ちゃんを使って音楽を聞いています。",
                                    value=f"[{lmusic['name']}]({lmusic['url']} )")
            await ctx.send(embed=embed)

    @commands.command(aliases=["役職情報", "次の役職について教えて"])
    async def roleinfo(self, ctx, *, role: commands.RoleConverter=None):

        if role is None:
            await ctx.send(await ctx._("roleinfo-howto"))
        elif role.guild == ctx.guild:
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

            await ctx.send(embed=embed)
        else:
            await ctx.send(await ctx._("roleinfo-other"))

    @commands.command(name="activity")
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def infoactivity(self, ctx, mus: commands.MemberConverter=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if mus is None:
            info = ctx.message.author
        else:
            info = mus
        lmsc = ut.get_vmusic(self.bot, info)
        activs = []
        embeds = []
        if lmsc:
            embed = discord.Embed(title=await ctx._(
                "playinginfo-doing"), description=f"{lmsc['guild'].name}で、思惟奈ちゃんを使って[{lmsc['name']}]({lmsc['url']} )を聞いています", color=info.color)
            activs.append("思惟奈ちゃんでの音楽鑑賞")
            embeds.append(embed)
        if info.activity is None:
            if str(info.status) == "offline":
                embed = discord.Embed(title=await ctx._(
                    "playinginfo-doing"), description=await ctx._("playinginfo-offline"), color=info.color)
                activs.append("オフラインユーザー")
            else:
                sete = False
                try:
                    if info.voice.self_stream:
                        embed = discord.Embed(title=await ctx._("playinginfo-doing"), description=str(
                            self.bot.get_emoji(653161518250196992))+await ctx._("playinginfo-GoLive"), color=info.color)
                        activs.append("GoLiveストリーミング")
                        sete = True
                    elif info.voice.self_video:
                        embed = discord.Embed(title=await ctx._("playinginfo-doing"), description=str(
                            self.bot.get_emoji(653161517960658945))+await ctx._("playinginfo-screenshare"), color=info.color)
                        activs.append("サーバービデオ")
                        sete = True
                    elif info.voice:
                        embed = discord.Embed(title=await ctx._("playinginfo-doing"), description=str(
                            self.bot.get_emoji(653161518082293770))+await ctx._("playinginfo-invc"), color=info.color)
                        activs.append("ボイスチャット参加中")
                        sete = True
                except:
                    pass
                if not sete:
                    if info.bot:
                        embed = discord.Embed(title=await ctx._(
                            "playinginfo-doing"), description=await ctx._("playinginfo-bot"), color=info.color)
                        activs.append("botユーザー")
                    elif "🌐" == ut.ondevicon(info):
                        embed = discord.Embed(title=await ctx._(
                            "playinginfo-doing"), description=await ctx._("playinginfo-onlyWeb"), color=info.color)
                        activs.append("Webクライアント")
                    elif "📱" == ut.ondevicon(info):
                        embed = discord.Embed(title=await ctx._(
                            "playinginfo-doing"), description=await ctx._("playinginfo-onlyPhone"), color=info.color)
                        activs.append("スマートフォンクライアント")
                    else:
                        embed = discord.Embed(title=await ctx._(
                            "playinginfo-doing"), description=await ctx._("playinginfo-noActivity"), color=info.color)
                        activs.append("なにもしてない…のかな？")
            activ = info.activity
            embed.set_author(name=info.display_name,
                             icon_url=info.avatar_url_as(static_format='png'))
            spflag = True
            embeds.append(embed)
        else:
            for anactivity in info.activities:
                if anactivity.type == discord.ActivityType.playing:
                    activName = await ctx._("playinginfo-playing")+anactivity.name
                elif anactivity.type == discord.ActivityType.watching:
                    activName = await ctx._("playinginfo-watching")+anactivity.name
                elif anactivity.type == discord.ActivityType.listening:
                    activName = await ctx._("playinginfo-listening", anactivity.name)
                elif anactivity.type == discord.ActivityType.streaming:
                    activName = await ctx._("playinginfo-streaming")+anactivity.name
                elif anactivity.type == discord.ActivityType.custom:
                    activName = await ctx._("playinginfo-custom_status")
                else:
                    activName = await ctx._("playinginfo-unknown")+anactivity.name
                embed = discord.Embed(title=await ctx._(
                    "playinginfo-doing"), description=activName, color=info.color)
                activ = anactivity
                embed.set_author(name=info.display_name,
                                 icon_url=info.avatar_url_as(static_format='png'))
                if anactivity.name == "Spotify":
                    activs.append("Spotifyでの音楽鑑賞")
                    try:
                        embed.add_field(name=await ctx._(
                            "playinginfo-title"), value=activ.title)
                        embed.add_field(name=await ctx._(
                            "playinginfo-artist"), value=activ.artist)
                        embed.add_field(name=await ctx._(
                            "playinginfo-album"), value=activ.album)
                        embed.add_field(
                            name="URL", value=f"https://open.spotify.com/track/{activ.track_id}")
                        tmp = str(
                            int((datetime.datetime.utcnow() - activ.start).seconds % 60))
                        pnow = f"{int((datetime.datetime.utcnow() - activ.start).seconds/60)}:{tmp if len(tmp)==2 else f'0{tmp}'}"
                        tmp = str(int(activ.duration.seconds % 60))
                        pml = f"{int(activ.duration.seconds/60)}:{tmp if len(tmp)==2 else f'0{tmp}'}"
                        embed.add_field(name="経過時間", value=f"{pnow}/{pml}")
                        embed.set_thumbnail(url=activ.album_cover_url)
                    except AttributeError:
                        try:
                            embed.add_field(name=await ctx._("spotify-local"),
                                            value=await ctx._("spotify-cantlisten-wu"))
                            embed.add_field(name=await ctx._(
                                "playinginfo-title"), value=activ.details)
                            embed.add_field(name=await ctx._(
                                "playinginfo-artist"), value=activ.state)
                            tmp = str(
                                int((datetime.datetime.utcnow() - activ.start).seconds % 60))
                            pnow = f"{int((datetime.datetime.utcnow() - activ.start).seconds/60)}:{tmp if len(tmp)==2 else f'0{tmp}'}"
                            deua = activ.end - activ.start
                            tmp = str(int(deua.seconds % 60))
                            pml = f"{int(deua.seconds/60)}:{tmp if len(tmp)==2 else f'0{tmp}'}"
                            embed.add_field(name="経過時間", value=f"{pnow}/{pml}")
                        except:
                            activName = "プレイ中:"+anactivity.name
                            embed = discord.Embed(title="していること", description=activName, color=info.color)
                            activ = anactivity
                            embed.set_author(name=info.display_name,
                                            icon_url=info.avatar_url_as(static_format='png'))
                            activs.append(f"{activ.name}をプレイ中")
                            try:
                                vl = ""
                                if activ.details:
                                    vl = f"{activ.details}\n"
                                if activ.state:
                                    vl = f"{vl}{activ.state}\n"
                                if vl == "":
                                    vl = "なし"
                                embed.add_field(name="詳細", value=vl)
                            except:
                                pass
                elif anactivity.type == discord.ActivityType.streaming:
                    activs.append("外部でのストリーミング")
                    try:
                        embed.add_field(name=await ctx._(
                            "playinginfo-streampage"), value=activ.url)
                    except:
                        pass
                    try:
                        embed.add_field(name=await ctx._(
                            "playinginfo-do"), value=activ.datails)
                    except:
                        pass
                elif anactivity.type == discord.ActivityType.custom:
                    activs.append("カスタムステータス")
                    embed.add_field(name=await ctx._(
                        "playinginfo-det"), value=str(anactivity))
                else:
                    activs.append(f"{activ.name}をプレイ中")
                    try:
                        vl = ""
                        if activ.details:
                            vl = f"{activ.details}\n"
                        if activ.state:
                            vl = f"{vl}{activ.state}\n"
                        if vl == "":
                            vl = "なし"
                        embed.add_field(name=await ctx._(
                            "playinginfo-det"), value=vl)
                    except:
                        pass
                try:
                    if anactivity.created_at:
                        embed.set_footer(text=f"the activity started at")
                        embed.timestamp = anactivity.created_at
                except:
                    pass
                embeds.append(embed)
        # ページわけ
        doingdis = f"{len(activs)}件のアクティビティ"
        e = discord.Embed(title=doingdis,description="```\n"+f"\n".join(activs)+"```",color = self.bot.ec)
        e.set_author(name=info.display_name,
                        icon_url=info.avatar_url_as(static_format='png'))
        embeds.insert(0,e)
        page = 0
        msg = await ctx.send(embed=embeds[page])
        await msg.add_reaction(self.bot.get_emoji(653161518195671041))
        await msg.add_reaction(self.bot.get_emoji(653161518170505216))
        while True:
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
            except:
                break
            try:
                await msg.remove_reaction(r, u)
            except:
                pass
            if str(r) == str(self.bot.get_emoji(653161518170505216)):
                if page == len(embeds) - 1:
                    page = 0
                else:
                    page = page + 1
                await msg.edit(embed=embeds[page])
            elif str(r) == str(self.bot.get_emoji(653161518195671041)):
                if page == 0:
                    page = len(embeds) - 1
                else:
                    page = page - 1
                await msg.edit(embed=embeds[page])


    @commands.command(name="serverinfo",aliases=["si"])
    async def ginfo(self, ctx):
        gp = await self.bot.cursor.fetchone("select * from guilds where id = %s",(ctx.guild.id,))
        #gp = await self.bot.cursor.fetchone()
        if gp["verified"]:
            ptn = f'{await ctx._("sina_verified_guild")}:'
        else:
            ptn = ""
        if "PARTNER" in ctx.guild.features:
            ptn = ptn+f'{await ctx._("discord_partner_guild")}:'
        pmax = 12 if "COMMUNITY" in ctx.guild.features else 11
        page = 0
        e = discord.Embed(title=await ctx._("ginfo-ov-title"), color=self.bot.ec)
        e.set_author(name=f"{ptn}{ctx.guild.name}",
                     icon_url=ctx.guild.icon_url_as(static_format='png'))
        e.add_field(name=await ctx._("ginfo-region"), value=ctx.guild.region)
        e.add_field(name=await ctx._("ginfo-afkch"), value=ctx.guild.afk_channel)
        if ctx.guild.afk_channel:
            e.add_field(name=await ctx._("ginfo-afktout"),
                        value=f"{ctx.guild.afk_timeout/60}min")
        else:
            e.add_field(name=await ctx._("ginfo-afktout"),
                        value=await ctx._("ginfo-afknone"))
        e.add_field(name=await ctx._("ginfo-sysch"), value=ctx.guild.system_channel)
        e.add_field(name=await ctx._("ginfo-memjoinnotif"),
                    value=ctx.guild.system_channel_flags.join_notifications)
        e.add_field(name=await ctx._("ginfo-serverboostnotif"),
                    value=ctx.guild.system_channel_flags.premium_subscriptions)
        if ctx.guild.default_notifications == discord.NotificationLevel.all_messages:
            e.add_field(name=await ctx._("ginfo-defnotif"),
                        value=await ctx._("ginfo-allmsg"))
        else:
            e.add_field(name=await ctx._("ginfo-defnotif"),
                        value=await ctx._("ginfo-omention"))
        if "INVITE_SPLASH" in ctx.guild.features:
            e.add_field(name=await ctx._("ginfo-invitesp"),
                        value=await ctx._("ginfo-invitesp-pos"))
            e.set_image(url=ctx.guild.splash_url_as(format="png"))
        if "BANNER" in ctx.guild.features:
            e.add_field(name=await ctx._("ginfo-banner"),
                        value=await ctx._("ginfo-banner-pos"))
            e.set_thumbnail(url=ctx.guild.banner_url_as(format="png"))
        mp = await ctx.send(embed=e)
        await mp.add_reaction(self.bot.get_emoji(653161518195671041))
        await mp.add_reaction(self.bot.get_emoji(653161518170505216))
        while True:
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == mp.id and u.id == ctx.message.author.id, timeout=30)
            except:
                break
            try:
                await mp.remove_reaction(r, u)
            except:
                pass
            if str(r) == str(self.bot.get_emoji(653161518170505216)):
                if page == pmax:
                    page = 0
                else:
                    page = page + 1
            elif str(r) == str(self.bot.get_emoji(653161518195671041)):
                if page == 0:
                    page = pmax
                else:
                    page = page - 1
            try:
                if page == 0:
                    # 概要
                    e = discord.Embed(title=await ctx._(
                        "ginfo-ov-title"), color=self.bot.ec)
                    e.set_author(name=f"{ptn}{ctx.guild.name}", icon_url=ctx.guild.icon_url_as(
                        static_format='png'))
                    e.add_field(name=await ctx._("ginfo-region"),
                                value=ctx.guild.region)
                    e.add_field(name=await ctx._("ginfo-afkch"),
                                value=ctx.guild.afk_channel)
                    if ctx.guild.afk_channel:
                        e.add_field(name=await ctx._("ginfo-afktout"),
                                    value=f"{ctx.guild.afk_timeout/60}min")
                    else:
                        e.add_field(name=await ctx._("ginfo-afktout"),
                                    value=await ctx._("ginfo-afknone"))
                    e.add_field(name=await ctx._("ginfo-sysch"),
                                value=ctx.guild.system_channel)
                    e.add_field(name=await ctx._("ginfo-memjoinnotif"),
                                value=ctx.guild.system_channel_flags.join_notifications)
                    e.add_field(name=await ctx._("ginfo-serverboostnotif"),
                                value=ctx.guild.system_channel_flags.premium_subscriptions)
                    if ctx.guild.default_notifications == discord.NotificationLevel.all_messages:
                        e.add_field(name=await ctx._("ginfo-defnotif"),
                                    value=await ctx._("ginfo-allmsg"))
                    else:
                        e.add_field(name=await ctx._("ginfo-defnotif"),
                                    value=await ctx._("ginfo-omention"))
                    if "INVITE_SPLASH" in ctx.guild.features:
                        e.add_field(name=await ctx._("ginfo-invitesp"),
                                    value=await ctx._("ginfo-invitesp-pos"))
                        e.set_image(url=ctx.guild.splash_url_as(format="png"))
                    if "BANNER" in ctx.guild.features:
                        e.add_field(name=await ctx._("ginfo-banner"),
                                    value=await ctx._("ginfo-banner-pos"))
                        e.set_thumbnail(
                            url=ctx.guild.banner_url_as(format="png"))
                    await mp.edit(embed=e)
                elif page == 1:
                    # 管理
                    e = discord.Embed(title=await ctx._(
                        "ginfo-manage"), color=self.bot.ec)
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
                    elif ctx.guild.verification_level == discord.VerificationLevel.extreme:
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
                    await mp.edit(embed=e)
                elif page == 2:
                    # roles
                    if ctx.author.guild_permissions.manage_roles or ctx.author.id == 404243934210949120:
                        rl = ctx.guild.roles[::-1]
                        rls = ""
                        for r in rl:
                            if len(f"{rls}\n{r.name}") >= 1998:
                                rls = rls+"\n…"
                                break
                            else:
                                rls = f"{rls}\n{r.name}"
                        await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-roles"), description=rls, color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-roles"), description=await ctx._("ginfo-cantview"), color=self.bot.ec))
                elif page == 3:
                    # emoji
                    ejs = ""
                    for i in ctx.guild.emojis:
                        if len(ejs + "," + str(i)) >= 1998:
                            ejs = ejs+"など"
                            break
                        else:
                            ejs = ejs + "," + str(i)
                    await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-emoji"), description=ejs, color=self.bot.ec))
                elif page == 4:
                    # webhooks
                    if ctx.author.guild_permissions.manage_webhooks or ctx.author.id == 404243934210949120:
                        await mp.edit(embed=discord.Embed(title="webhooks", description="\n".join([f"{i.name},[link]({i.url}),created by {i.user}" for i in await ctx.guild.webhooks()]), color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title="webhooks", description=await ctx._("ginfo-cantview"), color=self.bot.ec))
                elif page == 5:
                    # ウィジェット
                    if ctx.author.guild_permissions.manage_guild or ctx.author.id == 404243934210949120:
                        try:
                            wdt = await ctx.guild.widget()
                            await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-widget"), description=f"URL: {wdt.json_url}", color=self.bot.ec))
                        except:
                            await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-widget"), description=await ctx._("ginfo-ctuw"), color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-widget"), description=await ctx._("ginfo-cantview"), color=self.bot.ec))
                elif page == 6:
                    # Nitro server boost
                    e = discord.Embed(title=str(self.bot.get_emoji(653161518971617281))+"Nitro Server Boost",
                                      description=f"Level:{ctx.guild.premium_tier}\n({ctx.guild.premium_subscription_count})", color=self.bot.ec)
                    e.add_field(name=await ctx._("ginfo-bst-add"),
                                value=await ctx._(f"ginfo-blev{ctx.guild.premium_tier}"))
                    await mp.edit(embed=e)
                elif page == 7:
                    # member
                    vml = await ctx._("ginfo-strlenover")
                    if len("\n".join([f"{str(i)}" for i in ctx.guild.members])) <= 1024:
                        vml = "\n".join([f"{str(i)}" for i in ctx.guild.members]).replace(
                            str(ctx.guild.owner), f"👑{str(ctx.guild.owner)}")
                    await mp.edit(embed=discord.Embed(title="member", description=f"member count:{len(ctx.guild.members)}\n```"+vml+"```"), color=self.bot.ec)
                elif page == 8:
                    if ctx.author.guild_permissions.manage_guild or ctx.author.id == 404243934210949120:
                        try:
                            vi = await ctx.guild.vanity_invite()
                            vi = vi.code
                        except:
                            vi = "NF_VInvite"
                        # invites
                        vil = await ctx._("ginfo-strlenover")
                        if len("\n".join([f'{i.code},{await ctx._("ginfo-use-invite")}:{i.uses}/{i.max_uses},{await ctx._("ginfo-created-invite")}:{i.inviter}' for i in await ctx.guild.invites()])) <= 1023:
                            vil = "\n".join([f'{i.code},{await ctx._("ginfo-use-invite")}:{i.uses}/{i.max_uses},{await ctx._("ginfo-created-invite")}:{i.inviter}' for i in await ctx.guild.invites()]).replace(vi, f"{self.bot.get_emoji(653161518103265291)}{vi}")
                        await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-invites"), description=vil, color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-invites"), description=await ctx._("ginfo-cantview"), color=self.bot.ec))
                elif page == 9:
                    if ctx.author.guild_permissions.ban_members or ctx.author.id == 404243934210949120:
                        # ban_user
                        vbl = await ctx._("ginfo-strlenover")
                        bl = []
                        for i in await ctx.guild.bans():
                            bl.append(f"{i.user},reason:{i.reason}")
                        if len("\n".join(bl)) <= 1024:
                            vbl = "\n".join(bl)
                        await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-banneduser"), description=vbl), color=self.bot.ec)
                    else:
                        await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-banneduser"), description=await ctx._("ginfo-cantview"), color=self.bot.ec))
                elif page == 10:
                    # サーバーのチャンネル
                    e = discord.Embed(title=await ctx._(
                        "ginfo-chlist"), color=self.bot.ec)
                    for mct, mch in ctx.guild.by_category():
                        chs = "\n".join([i.name for i in mch])
                        e.add_field(name=str(mct).replace("None", await ctx._(
                            "ginfo-nocate")), value=f"```{chs}```", inline=True)
                    await mp.edit(embed=e)
                elif page == 11:
                    gs = await self.bot.cursor.fetchone(
                        "select * from guilds where id=%s", (ctx.guild.id,))
                    #gs = await self.bot.cursor.fetchone()
                    e = discord.Embed(title="other", color=self.bot.ec)
                    e.add_field(name="owner", value=ctx.guild.owner.mention)
                    e.add_field(name="features",
                                value=f"```{','.join(ctx.guild.features)}```")
                    e.add_field(name=await ctx._("ginfo-sinagprofile"), value=await ctx._(
                        "ginfo-gprodesc", gs["reward"], gs["sendlog"], gs["prefix"], gs["lang"],))
                    await mp.edit(embed=e)
                elif page == 12:
                    e = discord.Embed(
                        title="コミュニティサーバー設定", description=ctx.guild.description or "概要なし", color=self.bot.ec)
                    e.add_field(name="優先言語", value=ctx.guild.preferred_locale)
                    e.add_field(name="ルールチャンネル",
                                value=ctx.guild.rules_channel.mention)
                    e.add_field(name="コミュニティ更新情報チャンネル",
                                value=ctx.guild.public_updates_channel.mention)
                    await mp.edit(embed=e)
            except:
                await mp.edit(embed=discord.Embed(title=await ctx._("ginfo-anyerror-title"), description=await ctx._("ginfo-anyerror-desc", traceback.format_exc(0)), color=self.bot.ec))

    @commands.command(name="team_sina-chan")
    async def view_teammember(self, ctx):
        await ctx.send(embed=ut.getEmbed(await ctx._("team_sina-chan"), "\n".join([self.bot.get_user(i).name for i in self.bot.team_sina])))

    @commands.command()
    async def vusers(self, ctx):
        await self.bot.cursor.execute("select * from users")
        pf = await self.bot.cursor.fetchall()
        async with ctx.message.channel.typing():
            vlist = []
            for i in pf:
                if i["sinapartner"] is True:
                    bu = await self.bot.fetch_user(i["id"])
                    vlist.append(f"ユーザー名:{bu},id:{i['id']}")
            embed = discord.Embed(title=f"認証済みアカウント一覧({len(vlist)}名)", description="```{0}```".format(
                '\n'.join(vlist)), color=self.bot.ec)
        await ctx.send(embed=embed)

    @commands.command()
    async def mutual_guilds(self, ctx, uid=None):
        if ctx.author.id in self.bot.team_sina:
            try:
                user = await self.bot.fetch_user(int(uid))
            except:
                user = ctx.author
            mg = []
            for g in self.bot.guilds:
                if g.get_member(user.id):
                    mg += [f"{g.name}({g.id})"]
            if mg != []:
                t = "\n".join(mg)
                e = discord.Embed(description=f"```{t}```", color=self.bot.ec)
                e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
                await ctx.send(embed=e)
            else:
                e = discord.Embed(description="なし", color=self.bot.ec)
                e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
                await ctx.send(embed=e)
        else:
            await ctx.reply("> 共通サーバーチェッカー\n　Discord公式の機能でチェックできるようになったため、このコマンドは運営専用になりました。プロフィールから確認してください。")

    @commands.command()
    async def features(self, ctx):
        await ctx.author.send(embed=ut.getEmbed("あなたのfeatures", "```{}```".format(",".join(self.bot.features.get(ctx.author.id, ["(なし)"])))))

    @commands.command()
    async def invite(self,ctx,*,target:Union[commands.MemberConverter,commands.UserConverter,int,None]):
        if target is None:
            target = ctx.guild.me
        if isinstance(target,int):
            try:
                target = await self.bot.fetch_user(target)
            except:
                await ctx.send("> エラー\n　そのIDを持つユーザーが存在しません。")
        if target.bot:
            if isinstance(target,discord.Member):
                ilink = discord.utils.oauth_url(str(target.id),permissions=target.guild_permissions,scopes=("bot","applications.commands"))
                e=discord.Embed(title="bot招待リンク",description=ilink,color=self.bot.ec)
                e.add_field(name="このリンクで導入した際の権限",
                                value=f"`{'`,`'.join([await ctx._(f'p-{i[0]}') for i in list(target.guild_permissions) if i[1]])}`")
                e.set_author(name=f"{target}({target.id})",icon_url=target.avatar_url_as(static_format="png"))
            else:
                ilink = discord.utils.oauth_url(str(target.id),permissions=ctx.guild.me.guild_permissions,scopes=("bot","applications.commands"))
                e=discord.Embed(title="bot招待リンク",description=ilink,color=self.bot.ec)
                e.add_field(name="このリンクで導入した際の権限",
                                value=f"`{'`,`'.join([await ctx._(f'p-{i[0]}') for i in list(ctx.guild.me.guild_permissions) if i[1]])}`")
                e.set_author(name=f"{target}({target.id})",icon_url=target.avatar_url_as(static_format="png"))
            await ctx.send(embed=e)
        else:
            await ctx.send(embed=discord.Embed(title="エラー",description="ユーザーアカウントの導入リンクは作成できません！",color=self.bot.ec))


def setup(bot):
    bot.add_cog(info(bot))
