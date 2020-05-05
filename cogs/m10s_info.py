# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import datetime
from dateutil.relativedelta import relativedelta as rdelta
import traceback

import m10s_util as ut

class info(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def anyuserinfo(self,ctx,*,uid:int=None):
        if uid:
            self.bot.cursor.execute("select * from users where id=?",(uid,))
            upf = self.bot.cursor.fetchone()
            if upf:
                isva=upf["sinapartner"]
            else:
                isva=0
            try:
                u=await self.bot.fetch_user(uid)
            except discord.NotFound:
                await ctx.send(ctx._("aui-nf"))
            except discord.HTTPException:
                await ctx.send(ctx._("aui-he"))
            except:
                await ctx.send(ctx._("aui-othere",traceback.format_exc()))
            else:
                ptn=""
                if u.id in self.bot.team_sina:
                    ptn=f',({ctx._("team_sina-chan")})'
                if u.id in [i[1] for i in self.bot.partnerg]:
                    ptn=ptn+f',({ctx._("partner_guild_o")})'
                if isva:
                    ptn=ptn+f"、(💠{'認証済みアカウント'})"
                e = discord.Embed(title=f"{ctx._('aui-uinfo')}{ptn}",color=self.bot.ec)
                if u.system:
                    e.add_field(name="✅システムアカウント",value="このアカウントは、Discordのシステムアカウントであり、安全です。",inline=False)
                e.add_field(name=ctx._("aui-name"),value=u.name)
                e.add_field(name=ctx._("aui-id"),value=u.id)
                e.add_field(name=ctx._("aui-dr"),value=u.discriminator)
                e.add_field(name=ctx._("aui-isbot"),value=u.bot)
                e.set_thumbnail(url=u.avatar_url)
                tm=(u.created_at + rdelta(hours=9)).strftime("%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}").format(*"年月日時分秒")
                e.set_footer(text=ctx._("aui-created",tm))
                e.timestamp = u.created_at
            await ctx.send(embed=e)
        else:
            await ctx.send(ctx._("aui-nid"))

    @commands.command(aliases=["ui","ユーザー情報","ユーザーの情報を教えて"])
    async def userinfo(self,ctx, mus:commands.MemberConverter=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if mus == None:
            info = ctx.message.author
        else:
            info = mus
        self.bot.cursor.execute("select * from users where id=?",(info.id,))
        upf = self.bot.cursor.fetchone()
        if upf:
            isva=upf["sinapartner"]
        else:
            isva=0
        async with ctx.message.channel.typing():
            ptn=""
            if info.id in self.bot.team_sina:
                ptn=f',({ctx._("team_sina-chan")})'
            if info.id in [i[1] for i in self.bot.partnerg]:
                ptn=ptn+f',({ctx._("partner_guild_o")})'
            if isva:
                ptn=ptn+f"、(💠{'認証済みアカウント'})"
            if ctx.guild.owner == info:
                embed = discord.Embed(title=ctx._("uinfo-title"), description=f"{ptn} - {ctx._('userinfo-owner')}", color=info.color)
            else:
                embed = discord.Embed(title=ctx._("uinfo-title"), description=ptn, color=info.color)
            if info.system:
                embed.add_field(name="✅システムアカウント",value="このアカウントは、Discordのシステムアカウントであり、安全です。",inline=False)
            embed.add_field(name=ctx._("userinfo-name"),value=f"{info.name} - {ut.ondevicon(info)}")
            try:
                if not info.premium_since is None:
                    embed.add_field(name=ctx._("userinfo-guildbooster"), value=f"since {info.premium_since}")
            except:
                pass
            embed.add_field(name=ctx._("userinfo-joindiscord"), value=(info.created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            embed.add_field(name=ctx._("userinfo-id"), value=info.id)
            embed.add_field(name=ctx._("userinfo-online"), value=f"{str(info.status)}")
            embed.add_field(name=ctx._("userinfo-isbot"), value=str(info.bot))
            embed.add_field(name=ctx._("userinfo-displayname"), value=info.display_name)
            embed.add_field(name=ctx._("userinfo-joinserver"), value=(info.joined_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            if not info.activity == None:
                try:
                    if info.activity.type == discord.ActivityType.custom:
                        embed.add_field(name=ctx._("userinfo-nowplaying"), value=info.activity)
                    else:
                        embed.add_field(name=ctx._("userinfo-nowplaying"), value=f'{info.activity.name}')
                except:
                    embed.add_field(name=ctx._("userinfo-nowplaying"), value=info.activity)
            hasroles = ""
            for r in info.roles:
                hasroles = hasroles + f"{r.mention},"
            embed.add_field(name=ctx._("userinfo-roles"), value=hasroles)
            embed.add_field(name=ctx._("userinfo-guildper"),value=f"`{'`,`'.join([ctx._(f'p-{i[0]}') for i in list(info.guild_permissions) if i[1]])}`")
            if not info.avatar_url == None:
                embed.set_thumbnail(url=info.avatar_url_as(static_format='png'))
                embed.add_field(name=ctx._("userinfo-iconurl"),value=info.avatar_url_as(static_format='png'))
            else:
                embed.set_image(url=info.default_avatar_url_as(static_format='png'))
            lmsc=ut.get_vmusic(self.bot,info)
            if lmsc:
                embed.add_field(name=f"思惟奈ちゃんを使って[{lmsc['name']}]({lmsc['url']} )を聴いています。",value=f"サーバー:{lmsc['guild'].name}")
        await ctx.send(embed=embed)


    @commands.command()
    async def cinvite(self,ctx,ivt:str):
        i = await self.bot.fetch_invite(ivt)
        e=discord.Embed(title=ctx._("cinvite-title"),description=ctx._("cinvite-from",str(i.inviter)),color=self.bot.ec)
        e.set_author(name=f'{i.guild.name}({i.guild.id})',icon_url=i.guild.icon_url_as(format="png"))
        e.add_field(name=ctx._("cinvite-memcount"),value=f'{i.approximate_member_count}\n({ctx._("cinvite-onmemcount")}{i.approximate_presence_count})')
        e.add_field(name=ctx._("cinvite-ch"),value=f"{i.channel.name}({i.channel.type})")
        e.add_field(name=ctx._("cinvite-tmp"),value=str(i.temporary))
        e.add_field(name=ctx._("cinvite-deleted"),value=str(i.revoked))
        e.add_field(name=ctx._("cinvite-link"),value=i.url,inline=False)
        e.set_footer(text=ctx._("cinvite-createdat"))
        e.timestamp = i.created_at or discord.Embed.Empty
        await ctx.send(embed=e)

    @commands.command()
    async def emojiinfo(self,ctx,*,emj:commands.EmojiConverter=None):

        if emj==None:
            await ctx.send(ctx._("einfo-needarg"))
        else:
            embed = discord.Embed(title=emj.name, description=f"id:{emj.id}",color=self.bot.ec)
            embed.add_field(name=ctx._("einfo-animated"), value=emj.animated)
            embed.add_field(name=ctx._("einfo-manageout"), value=emj.managed)
            if emj.user:
                embed.add_field(name=ctx._("einfo-adduser"), value=str(emj.user))
            embed.add_field(name="url", value=emj.url)
            embed.set_footer(text=ctx._("einfo-addday"))
            embed.timestamp = emj.created_at
            await ctx.send(embed=embed)

    @commands.command(name="dguild")
    async def serverinfo(self,ctx,sid=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if not sid == None:
            sevinfo = self.bot.get_guild(int(str(sid)))
        else:
            sevinfo = ctx.message.guild
        if sevinfo.id in [i[0] for i in self.bot.partnerg]:
            ptn=f'{ctx._("partner_guild")}:'
        else:
            ptn=""
        try:
            embed = discord.Embed(title=ctx._("serverinfo-name"), description=sevinfo.name, color=self.bot.ec)
            if not sevinfo.icon_url == None:
                embed.set_thumbnail(url=sevinfo.icon_url_as(static_format='png'))
            embed.add_field(name=ctx._("serverinfo-role"), value=len(sevinfo.roles))
            embed.add_field(name=ctx._("serverinfo-emoji"), value=len(sevinfo.emojis))
            embed.add_field(name=ctx._("serverinfo-country"), value=str(sevinfo.region))
            bm = 0
            ubm = 0
            for m in sevinfo.members:
                if m.bot:
                    bm = bm + 1
                else:
                    ubm = ubm + 1
            embed.add_field(name=ctx._("serverinfo-member"), value=f"{len(sevinfo.members)}(bot:{bm}/user:{ubm})")
            embed.add_field(name=ctx._("serverinfo-channel"), value=f'{ctx._("serverinfo-text")}:{len(sevinfo.text_channels)}\n{ctx._("serverinfo-voice")}:{len(sevinfo.voice_channels)}')
            embed.add_field(name=ctx._("serverinfo-id"), value=sevinfo.id)
            embed.add_field(name=ctx._("serverinfo-owner"), value=sevinfo.owner.name)
            embed.add_field(name=ctx._("serverinfo-create"), value=(sevinfo.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
            rlist = ",".join([i.name for i in sevinfo.roles])
            if len(rlist) <= 1000:
                embed.add_field(name=ctx._("serverinfo-roles"),value=rlist)
            try:
                embed.add_field(name=ctx._("serverinfo-nitroboost"),value=ctx._("serverinfo-nitroboost-val",sevinfo.premium_tier))
                embed.add_field(name=ctx._("serverinfo-nitroboost-can-title"),value=ctx._(f"serverinfo-nitroboost-can-{sevinfo.premium_tier}").format(sevinfo.premium_tier,sevinfo.premium_subscription_count))
            except:
                pass

            if sevinfo.system_channel:
                embed.add_field(name=ctx._("serverinfo-sysch"),value=sevinfo.system_channel)
                try:
                    embed.add_field(name=ctx._("serverinfo-sysch-welcome"),value=sevinfo.system_channel_flags.join_notifications)
                    embed.add_field(name=ctx._("serverinfo-sysch-boost"),value=sevinfo.system_channel_flags.premium_subscriptions)
                except:
                    pass
            if sevinfo.afk_channel:
                embed.add_field(name=ctx._("serverinfo-afkch"),value=sevinfo.afk_channel.name)
                embed.add_field(name=ctx._("serverinfo-afktimeout"),value=str(sevinfo.afk_timeout/60))
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
            #await ctx.send(ctx._("serverinfo-except"))

    @commands.command()
    async def cprofile(self,ctx,usid=None):
        uid = usid or ctx.author.id
        self.bot.cursor.execute("select * from users where id=?",(uid,))
        pf = self.bot.cursor.fetchone()
        e = discord.Embed(title=ctx._("cpro-title"),description=f"id:{uid}")
        e.add_field(name="prefix",value=pf["prefix"])
        e.add_field(name=ctx._("cpro-gpoint"),value=pf["gpoint"])
        e.add_field(name=ctx._("cpro-levelcard"),value=pf["levcard"])
        e.add_field(name=ctx._("cpro-renotif"),value=pf["onnotif"])
        e.add_field(name=ctx._("cpro-lang"),value=pf["lang"])
        e.add_field(name="認証済みかどうか", value=pf["sinapartner"])
        await ctx.send(embed=e)

    @commands.command()
    async def checkmember(self,ctx,member:commands.MemberConverter):
        if not ctx.user_lang()=="ja":
            await ctx.send(ctx._("cannot-run"))
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
            await ctx.send(embed=discord.Embed(title=ctx._("ucheck-title",member),description=ctx._("ucheck-not_ban")))
        else:
            await ctx.send(embed=discord.Embed(title=ctx._("ucheck-title",member),description=ctx._("ucheck-not_ban",bunotif)))

    @commands.command(aliases=["次のボイスチャンネルのURLを教えて"])
    async def vcurl(self,ctx,vch:commands.VoiceChannelConverter=None):
        if vch is None and (not ctx.author.voice == None):
            ch = ctx.author.voice.channel
        else:
            ch = vch
        await ctx.send(embed=ut.getEmbed(ch.name,f"https://discordapp.com/channels/{ctx.guild.id}/{ch.id}"))

    @commands.command(name="chinfo",aliases=["チャンネル情報","次のチャンネルについて教えて"])
    async def channelinfo(self,ctx,cid:int=None):

        if cid is None:
            ch = ctx.message.channel
        else:
            ch = ctx.guild.get_channel(cid)
        if isinstance(ch,discord.TextChannel):

            embed = discord.Embed(title=ch.name, description=f"id:{ch.id}", color=ctx.author.colour)

            embed.add_field(name=ctx._("ci-type"),value=ctx._("ci-text"))

            embed.add_field(name=ctx._("ci-topic"),value=ch.topic or ctx._("topic-is-none"))

            embed.add_field(name=ctx._("ci-slow"),value=str(ch.slowmode_delay).replace("0",ctx._("ci-None")))

            embed.add_field(name=ctx._("ci-nsfw"),value=ch.is_nsfw())

            embed.add_field(name=ctx._("ci-cate"),value=ch.category)

            embed.add_field(name=ctx._("ci-created"),value=(ch.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

            embed.add_field(name=ctx._("ci-invitec"),value=str(len(await ch.invites())).replace("0",ctx._("ci-None")))

            embed.add_field(name=ctx._("ci-pinc"),value=str(len(await ch.pins())).replace("0",ctx._("ci-None")))

            embed.add_field(name=ctx._("ci-whc"),value=str(len(await ch.webhooks())).replace("0",ctx._("ci-None")))

            embed.add_field(name=ctx._("ci-url"),value=f"[{ctx._('ci-click')}](https://discordapp.com/channels/{ctx.guild.id}/{ch.id})")

            await ctx.send(embed=embed)

        elif isinstance(ch,discord.VoiceChannel):
            embed = discord.Embed(title=ch.name, description=f"id:{ch.id}", color=ctx.author.colour)

            embed.add_field(name=ctx._("ci-type"),value=ctx._("ci-voice"))

            embed.add_field(name=ctx._("ci-bit"),value=ch.bitrate)

            embed.add_field(name=ctx._("ci-limituser"),value=str(ch.user_limit).replace("0",ctx._("ci-None")))

            embed.add_field(name=ctx._("ci-cate"),value=ch.category)

            embed.add_field(name=ctx._("ci-created"),value=(ch.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

            embed.add_field(name=ctx._("ci-invitec"),value=str(len(await ch.invites())).replace("0",ctx._("ci-None")))

            embed.add_field(name=ctx._("ci-url"),value=f"[{ctx._('ci-click')}](https://discordapp.com/channels/{ctx.guild.id}/{ch.id})")

            await ctx.send(embed=embed)

        elif isinstance(ch,discord.CategoryChannel):

            embed = discord.Embed(title=ch.name, description=f"id:{ch.id}", color=ctx.author.colour)

            embed.add_field(name=ctx._("ci-type"),value=ctx._("ci-cate"))

            embed.add_field(name=ctx._("ci-nsfw"),value=ch.is_nsfw())

            ic = ""

            for c in ch.channels:
                ic = ic + c.mention + ","

            embed.add_field(name=ctx._("ci-inch"),value=ic)

            embed.add_field(name=ctx._("ci-created"),value=(ch.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

            embed.add_field(name=ctx._("ci-url"),value=f"[{ctx._('ci-click')}](https://discordapp.com/channels/{ctx.guild.id}/{ch.id})")

            await ctx.send(embed=embed)
        else:
            await ctx.send(ctx._("ci-notfound"))

    @commands.command(aliases=["ボイス情報","音声情報を教えて"])
    async def voiceinfo(self,ctx,mus:commands.MemberConverter=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if mus == None:
            info = ctx.message.author
        else:
            info = mus
        try:
            embed = discord.Embed(title=info.display_name, description=f"{info.voice.channel.guild.name} - {info.voice.channel.name}", color=info.colour)
            vste=""
            if info.voice.deaf:
                #サバスピーカーミュート
                vste=vste+str(self.bot.get_emoji(653161518057127937))
            else:
                #サバスピーカーオン
                vste=vste+str(self.bot.get_emoji(653161518082293770))
            if info.voice.mute:
                #サバマイクミュート
                vste=vste+str(self.bot.get_emoji(653161518086619137))
            else:
                #サバマイクオン
                vste=vste+str(self.bot.get_emoji(653161518086619137))
            if info.voice.self_deaf:
                #スピーカーミュート
                vste=vste+str(self.bot.get_emoji(653161518258585620))
            else:
                #スピーカーオン
                vste=vste+str(self.bot.get_emoji(653161517881098272))
            if info.voice.self_mute:
                #マイクミュート
                vste=vste+str(self.bot.get_emoji(653161519143714816))
            else:
                #マイクオン
                vste=vste+str(self.bot.get_emoji(653161518224900096))
            if info.voice.self_video:
                #画面共有
                vste=vste+str(self.bot.get_emoji(653161517960658945))
            elif info.voice.self_stream:
                #GoLive
                vste=vste+str(self.bot.get_emoji(653161518250196992))
            embed.add_field(name="ステータス(status)",value=vste)
        except AttributeError:
            await ctx.send(ctx._("vi-nfch"))
        finally:
            lmusic=ut.get_vmusic(self.bot,info)
            if lmusic:
                if lmusic["guild"].id == ctx.guild.id and info.id in [i.id for i in ctx.voice_client.channel.members]:
                    embed.add_field(name="ボイスチャットで思惟奈ちゃんを使って音楽を聞いています。",value=f"[{lmusic['name']}]({lmusic['url']} )")
            await ctx.send(embed=embed)

    @commands.command(aliases=["役職情報","次の役職について教えて"])
    async def roleinfo(self,ctx,*,role:commands.RoleConverter=None):

        if role==None:
            await ctx.send(ctx._("roleinfo-howto"))
        elif role.guild == ctx.guild:
            embed = discord.Embed(title=role.name, description=f"id:{role.id}", color=role.colour)
            embed.add_field(name=ctx._("roleinfo-hoist"), value=role.hoist)
            embed.add_field(name=ctx._("roleinfo-mention"), value=role.mentionable)
            hasmember=""
            for m in role.members:
                hasmember = hasmember + f"{m.mention},"
            if not hasmember == "":
                embed.add_field(name=ctx._("roleinfo-hasmember"), value=hasmember)
            else:
                embed.add_field(name=ctx._("roleinfo-hasmember"), value="(None)")
            hasper = ""
            for pn,bl in iter(role.permissions):
                if bl:
                    hasper = hasper + f"`{ctx._(f'p-{pn}')}`,"
            embed.add_field(name=ctx._("roleinfo-hasper"), value=hasper)
            embed.add_field(name=ctx._("roleinfo-created"), value=(role.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))

            await ctx.send(embed=embed)
        else:
            await ctx.send(ctx._("roleinfo-other"))

    @commands.command(name="activity",aliases=["アクティビティ","なにしてるか見せて"])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def infoactivity(self,ctx, mus:commands.MemberConverter=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        try:
            await self.bot.request_offline_members(ctx.guild)
        except:
            pass
        if mus is None:
            info = ctx.message.author
        else:
            info = mus
        lmsc=ut.get_vmusic(self.bot,info)
        if lmsc:
            embed = discord.Embed(title=ctx._("playinginfo-doing"), description=f"{lmsc['guild'].name}で、思惟奈ちゃんを使って[{lmsc['name']}]({lmsc['url']} )を聞いています", color=info.color)
            await ctx.send(embed=embed)
        if info.activity is None:
            if str(info.status) == "offline":
                embed = discord.Embed(title=ctx._("playinginfo-doing"), description=ctx._("playinginfo-offline"), color=info.color)
            else:
                sete =False
                try:
                    if info.voice.self_stream:
                        embed = discord.Embed(title=ctx._("playinginfo-doing"), description=str(self.bot.get_emoji(653161518250196992))+ctx._("playinginfo-GoLive"), color=info.color)
                        sete=True
                    elif info.voice.self_video:
                        embed = discord.Embed(title=ctx._("playinginfo-doing"), description=str(self.bot.get_emoji(653161517960658945))+ctx._("playinginfo-screenshare"), color=info.color)
                        sete=True
                    elif info.voice:
                        embed = discord.Embed(title=ctx._("playinginfo-doing"), description=str(self.bot.get_emoji(653161518082293770))+ctx._("playinginfo-invc"), color=info.color)
                        sete=True
                except:
                    pass
                if not sete:
                    if info.bot:
                        embed = discord.Embed(title=ctx._("playinginfo-doing"), description=ctx._("playinginfo-bot"), color=info.color)
                    elif "🌐"==ut.ondevicon(info):
                        embed = discord.Embed(title=ctx._("playinginfo-doing"), description=ctx._("playinginfo-onlyWeb"), color=info.color)
                    elif "📱"==ut.ondevicon(info):
                        embed = discord.Embed(title=ctx._("playinginfo-doing"), description=ctx._("playinginfo-onlyPhone"), color=info.color)
                    else:
                        embed = discord.Embed(title=ctx._("playinginfo-doing"), description=ctx._("playinginfo-noActivity"), color=info.color)
            activ=info.activity
            embed.set_author(name=info.display_name, icon_url=info.avatar_url_as(static_format='png'))
            await ctx.send(embed=embed)
        else:
            for anactivity in info.activities:
                if anactivity.type == discord.ActivityType.playing:
                    activName=ctx._("playinginfo-playing")+anactivity.name
                elif anactivity.type == discord.ActivityType.watching:
                    activName=ctx._("playinginfo-watching")+anactivity.name
                elif anactivity.type == discord.ActivityType.listening:
                    activName=ctx._("playinginfo-listening",anactivity.name)
                elif anactivity.type ==  discord.ActivityType.streaming:
                    activName=ctx._("playinginfo-streaming")+anactivity.name
                elif anactivity.type ==  discord.ActivityType.custom:
                    activName=ctx._("playinginfo-custom_status")
                else:
                    activName=ctx._("playinginfo-unknown")+anactivity.name
                embed = discord.Embed(title=ctx._("playinginfo-doing"), description=activName, color=info.color)
                activ=anactivity
                embed.set_author(name=info.display_name, icon_url=info.avatar_url_as(static_format='png'))
                if anactivity.name == "Spotify":
                    try:
                        embed.add_field(name=ctx._("playinginfo-title"), value=activ.title)
                        embed.add_field(name=ctx._("playinginfo-artist"), value=activ.artist)
                        embed.add_field(name=ctx._("playinginfo-album"), value=activ.album)
                        embed.add_field(name="URL", value=f"https://open.spotify.com/track/{activ.track_id}")
                        tmp=str(int((datetime.datetime.utcnow() - activ.start).seconds%60))
                        pnow=f"{int((datetime.datetime.utcnow() - activ.start).seconds/60)}:{tmp if len(tmp)==2 else f'0{tmp}'}"
                        tmp=str(int(activ.duration.seconds%60))
                        pml=f"{int(activ.duration.seconds/60)}:{tmp if len(tmp)==2 else f'0{tmp}'}"
                        embed.add_field(name="経過時間", value=f"{pnow}/{pml}")
                        embed.set_thumbnail(url=activ.album_cover_url)
                    except AttributeError:
                        embed.add_field(name=ctx._("spotify-local"), value=ctx._("spotify-cantlisten-wu"))
                        embed.add_field(name=ctx._("playinginfo-title"), value=activ.details)
                        embed.add_field(name=ctx._("playinginfo-artist"), value=activ.state)
                elif anactivity.type==discord.ActivityType.streaming:
                    try:
                        embed.add_field(name=ctx._("playinginfo-streampage"), value=activ.url)
                    except:
                        pass
                    try:
                        embed.add_field(name=ctx._("playinginfo-do"), value=activ.datails)
                    except:
                        pass
                elif anactivity.type==discord.ActivityType.custom:
                    embed.add_field(name=ctx._("playinginfo-det"), value=str(anactivity))
                else:
                    try:
                        vl = ""
                        if activ.details:
                            vl = f"{activ.details}\n"
                        if activ.state:
                            vl = f"{vl}{activ.state}\n"
                        if vl == "":
                            vl = "なし"
                        embed.add_field(name=ctx._("playinginfo-det"), value=vl)
                    except:
                        pass
                try:
                    if anactivity.created_at:
                        embed.set_footer(text=f"started the activity at")
                        embed.timestamp=anactivity.created_at
                except:
                    pass
                await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def ginfo(self,ctx):
        if ctx.guild.id in [i[0] for i in self.bot.partnerg]:
            ptn=f'{ctx._("partner_guild")}:'
        else:
            ptn=""
        pmax= 12 if "PUBLIC" in ctx.guild.features else 11
        page = 0
        e =discord.Embed(title=ctx._("ginfo-ov-title"),color=self.bot.ec)
        e.set_author(name=f"{ptn}{ctx.guild.name}",icon_url=ctx.guild.icon_url_as(static_format='png'))
        e.add_field(name=ctx._("ginfo-region"),value=ctx.guild.region)
        e.add_field(name=ctx._("ginfo-afkch"),value=ctx.guild.afk_channel)
        if ctx.guild.afk_channel:
            e.add_field(name=ctx._("ginfo-afktout"),value=f"{ctx.guild.afk_timeout/60}min")
        else:
            e.add_field(name=ctx._("ginfo-afktout"),value=ctx._("ginfo-afknone"))
        e.add_field(name=ctx._("ginfo-sysch"),value=ctx.guild.system_channel)
        e.add_field(name=ctx._("ginfo-memjoinnotif"),value=ctx.guild.system_channel_flags.join_notifications)
        e.add_field(name=ctx._("ginfo-serverboostnotif"),value=ctx.guild.system_channel_flags.premium_subscriptions)
        if ctx.guild.default_notifications == discord.NotificationLevel.all_messages:
            e.add_field(name=ctx._("ginfo-defnotif"),value=ctx._("ginfo-allmsg"))
        else:
            e.add_field(name=ctx._("ginfo-defnotif"),value=ctx._("ginfo-omention"))
        if "INVITE_SPLASH" in ctx.guild.features:
            e.add_field(name=ctx._("ginfo-invitesp"),value=ctx._("ginfo-invitesp-pos"))
            e.set_image(url=ctx.guild.splash_url_as(format="png"))
        if "BANNER" in ctx.guild.features:
            e.add_field(name=ctx._("ginfo-banner"),value=ctx._("ginfo-banner-pos"))
            e.set_thumbnail(url=ctx.guild.banner_url_as(format="png"))
        mp = await ctx.send(embed=e)
        await mp.add_reaction(self.bot.get_emoji(653161518195671041))
        await mp.add_reaction(self.bot.get_emoji(653161518170505216))
        while True:
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r,u: r.message.id==mp.id and u.id == ctx.message.author.id,timeout=30)
            except:
                break
            try:
                await mp.remove_reaction(r,u)
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
                    #概要
                    e =discord.Embed(title=ctx._("ginfo-ov-title"),color=self.bot.ec)
                    e.set_author(name=f"{ptn}{ctx.guild.name}",icon_url=ctx.guild.icon_url_as(static_format='png'))
                    e.add_field(name=ctx._("ginfo-region"),value=ctx.guild.region)
                    e.add_field(name=ctx._("ginfo-afkch"),value=ctx.guild.afk_channel)
                    if ctx.guild.afk_channel:
                        e.add_field(name=ctx._("ginfo-afktout"),value=f"{ctx.guild.afk_timeout/60}min")
                    else:
                        e.add_field(name=ctx._("ginfo-afktout"),value=ctx._("ginfo-afknone"))
                    e.add_field(name=ctx._("ginfo-sysch"),value=ctx.guild.system_channel)
                    e.add_field(name=ctx._("ginfo-memjoinnotif"),value=ctx.guild.system_channel_flags.join_notifications)
                    e.add_field(name=ctx._("ginfo-serverboostnotif"),value=ctx.guild.system_channel_flags.premium_subscriptions)
                    if ctx.guild.default_notifications == discord.NotificationLevel.all_messages:
                        e.add_field(name=ctx._("ginfo-defnotif"),value=ctx._("ginfo-allmsg"))
                    else:
                        e.add_field(name=ctx._("ginfo-defnotif"),value=ctx._("ginfo-omention"))
                    if "INVITE_SPLASH" in ctx.guild.features:
                        e.add_field(name=ctx._("ginfo-invitesp"),value=ctx._("ginfo-invitesp-pos"))
                        e.set_image(url=ctx.guild.splash_url_as(format="png"))
                    if "BANNER" in ctx.guild.features:
                        e.add_field(name=ctx._("ginfo-banner"),value=ctx._("ginfo-banner-pos"))
                        e.set_thumbnail(url=ctx.guild.banner_url_as(format="png"))
                    await mp.edit(embed=e)
                elif page == 1:
                    #管理
                    e = discord.Embed(title=ctx._("ginfo-manage"),color=self.bot.ec)
                    if ctx.guild.verification_level == discord.VerificationLevel.none:
                        e.add_field(name=ctx._("ginfo-vlevel"),value=ctx._("ginfo-vlnone"))
                    elif ctx.guild.verification_level == discord.VerificationLevel.low:
                        e.add_field(name=ctx._("ginfo-vlevel"),value=ctx._("ginfo-vl1"))
                    elif ctx.guild.verification_level == discord.VerificationLevel.medium:
                        e.add_field(name=ctx._("ginfo-vlevel"),value=ctx._("ginfo-vl2"))
                    elif ctx.guild.verification_level == discord.VerificationLevel.high:
                        e.add_field(name=ctx._("ginfo-vlevel"),value=ctx._("ginfo-vl3"))
                    elif ctx.guild.verification_level == discord.VerificationLevel.extreme:
                        e.add_field(name=ctx._("ginfo-vlevel"),value=ctx._("ginfo-vl4"))
                    if ctx.guild.explicit_content_filter == discord.ContentFilter.disabled:
                        e.add_field(name=ctx._("ginfo-filter"),value=ctx._("ginfo-fnone"))
                    elif ctx.guild.explicit_content_filter == discord.ContentFilter.no_role:
                        e.add_field(name=ctx._("ginfo-filter"),value=ctx._("ginfo-f1"))
                    elif ctx.guild.explicit_content_filter == discord.ContentFilter.all_members:
                        e.add_field(name=ctx._("ginfo-filter"),value=ctx._("ginfo-f2"))
                    await mp.edit(embed=e)
                elif page == 2:
                    #roles
                    if ctx.author.guild_permissions.manage_roles or ctx.author.id == 404243934210949120:
                        rl = ctx.guild.roles[::-1]
                        rls = ""
                        for r in rl:
                            if len(f"{rls}\n{r.name}")>=1998:
                                rls=rls+"\n…"
                                break
                            else:
                                rls=f"{rls}\n{r.name}"
                        await mp.edit(embed=discord.Embed(title=ctx._("ginfo-roles"),description=rls,color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=ctx._("ginfo-roles"),description=ctx._("ginfo-cantview"),color=self.bot.ec))
                elif page == 3:
                    #emoji
                    ejs=""
                    for i in ctx.guild.emojis:
                        if len( ejs + "," + str(i) ) >=1998:
                            ejs=ejs+"など"
                            break
                        else:
                            ejs=ejs + "," + str(i)
                    await mp.edit(embed=discord.Embed(title=ctx._("ginfo-emoji"),description=ejs,color=self.bot.ec))
                elif page == 4:
                    #webhooks
                    if ctx.author.guild_permissions.manage_webhooks or ctx.author.id == 404243934210949120:
                        await mp.edit(embed=discord.Embed(title="webhooks",description="\n".join([f"{i.name},[link]({i.url}),created by {i.user}" for i in await ctx.guild.webhooks()]),color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title="webhooks",description=ctx._("ginfo-cantview"),color=self.bot.ec))
                elif page == 5:
                    #ウィジェット
                    if ctx.author.guild_permissions.manage_guild or ctx.author.id == 404243934210949120:
                        try:
                            wdt = await ctx.guild.widget()
                            await mp.edit(embed=discord.Embed(title=ctx._("ginfo-widget"),description=f"URL: {wdt.json_url}",color=self.bot.ec))
                        except:
                            await mp.edit(embed=discord.Embed(title=ctx._("ginfo-widget"),description=ctx._("ginfo-ctuw"),color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=ctx._("ginfo-widget"),description=ctx._("ginfo-cantview"),color=self.bot.ec))
                elif page == 6:
                    #Nitro server boost
                    e = discord.Embed(title=str(self.bot.get_emoji(653161518971617281))+"Nitro Server Boost",description=f"Level:{ctx.guild.premium_tier}\n({ctx.guild.premium_subscription_count})",color=self.bot.ec)
                    e.add_field(name=ctx._("ginfo-bst-add"),value=ctx._(f"ginfo-blev{ctx.guild.premium_tier}"))
                    await mp.edit(embed=e)
                elif page == 7:
                    #member
                    vml=ctx._("ginfo-strlenover")
                    if len("\n".join([f"{str(i)}" for i in ctx.guild.members])) <= 1024:
                        vml = "\n".join([f"{str(i)}" for i in ctx.guild.members]).replace(str(ctx.guild.owner),f"👑{str(ctx.guild.owner)}")
                    await mp.edit(embed=discord.Embed(title="member",description=f"member count:{len(ctx.guild.members)}\n```"+vml+"```"),color=self.bot.ec)
                elif page == 8:
                    if ctx.author.guild_permissions.manage_guild or ctx.author.id == 404243934210949120:
                        try:
                            vi = await ctx.guild.vanity_invite()
                            vi = vi.code
                        except:
                            vi = "NF_VInvite"
                        #invites
                        vil = ctx._("ginfo-strlenover")
                        if len("\n".join([f'{i.code},{ctx._("ginfo-use-invite")}:{i.uses}/{i.max_uses},{ctx._("ginfo-created-invite")}:{i.inviter}' for i in await ctx.guild.invites()])) <= 1023:
                            vil = "\n".join([f'{i.code},{ctx._("ginfo-use-invite")}:{i.uses}/{i.max_uses},{ctx._("ginfo-created-invite")}:{i.inviter}' for i in await ctx.guild.invites()]).replace(vi,f"{self.bot.get_emoji(653161518103265291)}{vi}")
                        await mp.edit(embed=discord.Embed(title=ctx._("ginfo-invites"),description=vil,color=self.bot.ec))
                    else:
                        await mp.edit(embed=discord.Embed(title=ctx._("ginfo-invites"),description=ctx._("ginfo-cantview"),color=self.bot.ec))
                elif page == 9:
                    if ctx.author.guild_permissions.ban_members or ctx.author.id == 404243934210949120:
                        #ban_user
                        vbl=ctx._("ginfo-strlenover")
                        bl = []
                        for i in await ctx.guild.bans():
                            bl.append(f"{i.user},reason:{i.reason}")
                        if len("\n".join(bl)) <= 1024:
                            vbl = "\n".join(bl)
                        await mp.edit(embed=discord.Embed(title=ctx._("ginfo-banneduser"),description=vbl),color=self.bot.ec)
                    else:
                        await mp.edit(embed=discord.Embed(title=ctx._("ginfo-banneduser"),description=ctx._("ginfo-cantview"),color=self.bot.ec))
                elif page == 10:
                    #サーバーのチャンネル
                    e =discord.Embed(title=ctx._("ginfo-chlist"),color=self.bot.ec)
                    for mct,mch in ctx.guild.by_category():
                        chs="\n".join([i.name for i in mch])
                        e.add_field(name=str(mct).replace("None",ctx._("ginfo-nocate")),value=f"```{chs}```",inline=True)
                    await mp.edit(embed=e)
                elif page == 11:
                    self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
                    gs = self.bot.cursor.fetchone()
                    e =discord.Embed(title="other",color=self.bot.ec)
                    e.add_field(name="owner",value=ctx.guild.owner.mention)
                    e.add_field(name="features",value=f"```{','.join(ctx.guild.features)}```")
                    e.add_field(name=ctx._("ginfo-sinagprofile"),value=ctx._("ginfo-gprodesc",gs["reward"],gs["sendlog"],gs["prefix"],gs["lang"],))
                    await mp.edit(embed=e)
                elif page == 12:
                    e=discord.Embed(title="公開サーバー設定",description=ctx.guild.description or "概要なし",color=self.bot.ec)
                    e.add_field(name="優先言語",value=ctx.guild.preferred_locale)
                    e.add_field(name="ルールチャンネル",value=ctx.guild.rules_channel.mention)
                    await mp.edit(embed=e)
            except:
                await mp.edit(embed=discord.Embed(title=ctx._("ginfo-anyerror-title"),description=ctx._("ginfo-anyerror-desc",traceback.format_exc(0)),color=self.bot.ec))

    @commands.command(name="team_sina-chan")
    async def view_teammember(self,ctx):
        await ctx.send(embed=ut.getEmbed(ctx._("team_sina-chan"),"\n".join([self.bot.get_user(i).name for i in self.bot.team_sina])))

    @commands.command()
    async def vusers(self,ctx):
        self.bot.cursor.execute("select * from users")
        pf = self.bot.cursor.fetchall()
        async with ctx.message.channel.typing():
            vlist = []
            for i in pf:
                if i["sinapartner"] == True:
                    bu = await self.bot.fetch_user(i["id"])
                    vlist.append(f"ユーザー名:{bu},id:{i['id']}")
            embed=discord.Embed(title=f"認証済みアカウント一覧({len(vlist)}名)",description="```{0}```".format('\n'.join(vlist)),color=self.bot.ec)
        await ctx.send(embed=embed)

    @commands.command()
    async def mutual_guilds(self,ctx,uid=None):
        try:
            user=await self.bot.fetch_user(int(uid))
        except:
            user = ctx.author
        mg=[]
        for g in self.bot.guilds:
            if g.get_member(user.id):
                mg+=[f"{g.name}({g.id})"]
        if mg!=[]:
            t="\n".join(mg)
            e=discord.Embed(description=f"```{t}```",color=self.bot.ec)
            e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
            await ctx.send(embed=e)
        else:
            e=discord.Embed(description="なし",color=self.bot.ec)
            e.set_author(name=f"思惟奈ちゃんと{user}の共通サーバー")
            await ctx.send(embed=e)

    @commands.command()
    async def features(self,ctx):
        await ctx.author.send(embed=ut.getEmbed("あなたのfeatures","```{}```".format(",".join(self.bot.features.get(ctx.author.id,["(なし)"])))))

def setup(bot):
    bot.add_cog(info(bot))
