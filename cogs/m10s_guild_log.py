# -*- coding: utf-8 -*-

import json
import discord
from discord.ext import commands
import asyncio

import traceback
from datetime import datetime
from dateutil.relativedelta import relativedelta as rdelta

import m10s_util as ut


class m10s_guild_log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, b, a):
        if "cu:auto_sends" in self.bot.features.get(a.guild.id,[]):
            return
        # serverlog
        try:
            e = discord.Embed(
                title="メンバーの更新", description=f"変更メンバー:{str(a)}", color=self.bot.ec)
            e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
            if not b.nick == a.nick:
                e.add_field(name="変更内容", value="ニックネーム")
                if b.nick:
                    bnick = b.nick
                else:
                    bnick = b.name
                if a.nick:
                    anick = a.nick
                else:
                    anick = a.name
                e.add_field(name="変更前", value=bnick.replace("\\", "\\\\").replace("*", "\*").replace(
                    "_", "\_").replace("|", "\|").replace("~", "\~").replace("`", "\`").replace(">", "\>"))
                e.add_field(name="変更後", value=anick.replace("\\", "\\\\").replace("*", "\*").replace(
                    "_", "\_").replace("|", "\|").replace("~", "\~").replace("`", "\`").replace(">", "\>"))
                gpf = await self.bot.cursor.fetchone(
                    "select * from guilds where id=%s", (a.guild.id,))
                #gpf = await self.bot.cursor.fetchone()
                if gpf["sendlog"]:
                    ch = self.bot.get_channel(gpf["sendlog"])
                    if ch.guild.id == a.guild.id:
                        await ch.send(embed=e)
            elif not b.pending == a.pending:
                e.add_field(name="メンバースクリーニングの状態変更",value=f"メンバースクリーニング{'が再度要求されます。' if a.pending else 'を完了しました。'}")
                gpf = await self.bot.cursor.fetchone(
                    "select * from guilds where id=%s", (a.guild.id,))
                #gpf = await self.bot.cursor.fetchone()
                if gpf["sendlog"]:
                    ch = self.bot.get_channel(gpf["sendlog"])
                    if ch.guild.id == a.guild.id:
                        await ch.send(embed=e)
            elif not b.roles == a.roles:
                if len(b.roles) > len(a.roles):
                    e.add_field(name="変更内容", value="役職除去")
                    e.add_field(name="役職", value=list(
                        set(b.roles)-set(a.roles))[0])
                else:
                    e.add_field(name="変更内容", value="役職付与")
                    e.add_field(name="役職", value=list(
                        set(a.roles)-set(b.roles))[0])
                gpf = await self.bot.cursor.fetchone(
                    "select * from guilds where id=%s", (a.guild.id,))
                #gpf = await self.bot.cursor.fetchone()
                if gpf["sendlog"]:
                    ch = self.bot.get_channel(gpf["sendlog"])
                    if ch.guild.id == a.guild.id:
                        await ch.send(embed=e)
        except:
            pass
        # online notif are now handled in apple_onlinenotif

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if "cu:auto_sends" in self.bot.features.get(member.guild.id,[]):
            return
        try:
            gpf = await self.bot.cursor.fetchone(
                "select * from guilds where id=%s", (member.guild.id,))
            #gpf = await self.bot.cursor.fetchone()
            ctt = json.loads(gpf["jltasks"])
            if not ctt.get("welcome") is None:
                if ctt["welcome"]["sendto"] == "sysch":
                    await member.guild.system_channel.send(ctt["welcome"]["content"].format(member.mention))
                else:
                    dc = await ut.opendm(member)
                    await dc.send(ctt["welcome"]["content"].format(member.mention))
        except:
            pass
        e = discord.Embed(
            title="メンバーの参加", description=f"{len(member.guild.members)}人目のメンバー", color=self.bot.ec)
        e.add_field(name="参加メンバー", value=member.mention)
        e.add_field(name="そのユーザーのid", value=member.id)
        e.set_footer(
            text=f"アカウント作成日時(そのままの値:{(member.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')},タイムスタンプ化:")
        e.timestamp = member.created_at
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (member.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        try:
            if gpf["sendlog"]:
                ch = self.bot.get_channel(gpf["sendlog"])
                if ch.guild.id == member.guild.id:
                    await ch.send(embed=e)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if "cu:auto_sends" in self.bot.features.get(member.guild.id,[]):
            return
        try:
            gpf = await self.bot.cursor.fetchone(
                "select * from guilds where id=%s", (member.guild.id,))
            #gpf = await self.bot.cursor.fetchone()
            ctt = json.loads(gpf["jltasks"])
            if not ctt.get("cu") is None:
                if ctt["cu"]["sendto"] == "sysch":
                    await member.guild.system_channel.send(ctt["cu"]["content"].format(str(member)))
                else:
                    dc = await ut.opendm(member)
                    await dc.send(ctt["cu"]["content"].format(str(member)))
        except:
            pass
        e = discord.Embed(title="メンバーの退出", color=self.bot.ec)
        e.add_field(name="退出メンバー", value=str(member))
        e.add_field(name="役職", value=[i.name for i in member.roles])
        # e.set_footer(text=f"{member.guild.name}/{member.guild.id}")
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (member.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == member.guild.id:
                await ch.send(embed=e)
        """if member.guild.id == 611445741902364672:
            c = self.bot.get_channel(613629308166209549)
            await c.send(embed=e)"""


    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        if "cu:auto_sends" in self.bot.features.get(channel.guild.id,[]):
            return
        e = discord.Embed(title="Webhooksの更新", color=self.bot.ec)
        e.add_field(name="チャンネル", value=channel.mention)
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (channel.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == channel.guild.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if "cu:auto_sends" in self.bot.features.get(role.guild.id,[]):
            return
        e = discord.Embed(title="役職の作成", color=self.bot.ec)
        e.add_field(name="役職名", value=role.name)
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (role.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == role.guild.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if "cu:auto_sends" in self.bot.features.get(role.guild.id,[]):
            return
        e = discord.Embed(title="役職の削除", color=self.bot.ec)
        e.add_field(name="役職名", value=role.name)
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (role.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == role.guild.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if "cu:auto_sends" in self.bot.features.get(after.guild.id,[]):
            return
        # サーバーログ
        if before.content != after.content and before.author.id != 462885760043843584:
            e = discord.Embed(title="メッセージの編集", color=self.bot.ec)
            e.add_field(name="編集前", value=before.content)
            e.add_field(name="編集後", value=after.content)
            e.add_field(name="メッセージ送信者", value=after.author.mention)
            e.add_field(name="メッセージチャンネル", value=after.channel.mention)
            e.add_field(name="メッセージのURL", value=after.jump_url)
            e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
            gpf = await self.bot.cursor.fetchone(
                "select * from guilds where id=%s", (after.guild.id,))
            #gpf = await self.bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = self.bot.get_channel(gpf["sendlog"])
                if ch.guild.id == after.guild.id:
                    await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if "cu:auto_sends" in self.bot.features.get(channel.guild.id,[]):
            return
        # bl = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten()
        e = discord.Embed(title="チャンネル削除", color=self.bot.ec)
        e.add_field(name="チャンネル名", value=channel.name)
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (channel.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == channel.guild.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions):
        if "cu:auto_sends" in self.bot.features.get(message.guild.id,[]):
            return
        e = discord.Embed(title="リアクションの一斉除去", color=self.bot.ec)
        e.add_field(name="リアクション", value=[str(i) for i in reactions])
        e.add_field(name="除去されたメッセージ", value=message.content or "(本文なし)")
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (message.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == message.guild.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if "cu:auto_sends" in self.bot.features.get(message.guild.id,[]):
            return
        if not message.author.self.bot:
            e = discord.Embed(title="メッセージ削除", color=self.bot.ec)
            e.add_field(name="メッセージ", value=message.content)
            e.add_field(name="メッセージ送信者", value=message.author.mention)
            e.add_field(name="メッセージチャンネル", value=message.channel.mention)
            e.add_field(name="メッセージのid", value=message.id)
            e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
            gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s",
                            (message.guild.id,))
            #gpf = await self.bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = self.bot.get_channel(gpf["sendlog"])
                if ch.guild.id == message.guild.id:
                    await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if "cu:auto_sends" in self.bot.features.get(messages[0].guild.id,[]):
            return
        logs = ["一括削除ログ\n",f"チャンネル:{messages[0].channel}({messages[0].channel.id})\n","------\n"]
        for m in messages:
            logs.append(f"author(送信者):{m.author.display_name}({m.author}/{m.author.id})\n")
            logs.append(f"content(メッセージ内容):{m.system_content}\n")
            logs.append(f"message id(メッセージid):{m.id}\n")
            c_at = (m.created_at + rdelta(hours=9)).strftime("%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}").format(*"年月日時分秒")
            logs.append(f"created_at(送信日時):{c_at}\n")
            if m.type == discord.MessageType.reply:
                rfm = m.reference
                if rfm.cached_message:
                    logs.append(f"返信メッセージ:(送信者)-{rfm.cached_message.author.display_name}({rfm.cached_message.author}/{rfm.cached_message.author.id})\n")
                    logs.append(f"返信メッセージ:(メッセージ内容)-{rfm.cached_message.system_content}\n")
                    logs.append(f"返信メッセージ:(メッセージid)-{rfm.cached_message.id}\n")
                    c_at = (rfm.cached_message.created_at + rdelta(hours=9)).strftime("%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}").format(*"年月日時分秒")
                    logs.append(f"created_at(送信日時):{c_at}\n")
                else:
                    logs.append(f"返信メッセージ:(guild_id/channel_id/message_id)-{rfm.guild_id}/{rfm.channel_id}/{rfm.message_id}\n")
            logs.append("------\n")
        
        with open("bulk_message_delete.txt",mode="w",encoding="utf_8") as f:
            f.writelines(logs)

        e = discord.Embed(title="メッセージ一括削除", color=self.bot.ec)
        e.add_field(name="件数", value=len(messages))
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s",
                        (messages[0].guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == messages[0].guild.id:
                await ch.send(embed=e,file=discord.File(fp="bulk_message_delete.txt"))


    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if "cu:auto_sends" in self.bot.features.get(channel.guild.id,[]):
            return
        e = discord.Embed(title="チャンネル作成", color=self.bot.ec)
        e.add_field(name="チャンネル名", value=channel.mention)
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (channel.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == channel.guild.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_guild_channel_update(self, b, a):
        if "cu:auto_sends" in self.bot.features.get(a.guild.id,[]):
            return
        e = discord.Embed(title="チャンネル更新", description=a.mention, color=self.bot.ec)
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        if not b.name == a.name:
            if not a.guild.id == 461789442743468073:
                e.add_field(name="変更内容", value="チャンネル名")
                e.add_field(name="変更前", value=b.name)
                e.add_field(name="変更後", value=a.name)
                gpf = await self.bot.cursor.fetchone(
                    "select %s", (a.guild.id,))
                #gpf = await self.bot.cursor.fetchone()
                if gpf["sendlog"]:
                    ch = self.bot.get_channel(gpf["sendlog"])
                    if ch.guild.id == a.guild.id:
                        await ch.send(embed=e)
        elif a.position != b.position:
            pass
        elif not b.changed_roles == a.changed_roles:
            e.add_field(name="変更内容", value="権限の上書き")
            e.add_field(name="確認:", value="チャンネル設定を見てください。")
            gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (a.guild.id,))
            #gpf = await self.bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = self.bot.get_channel(gpf["sendlog"])
                if ch.guild.id == a.guild.id:
                    await ch.send(embed=e)
        elif isinstance(b, discord.TextChannel):
            if not b.topic == a.topic:
                e.add_field(name="変更内容", value="チャンネルトピック")
                e.add_field(name="変更前", value=b.topic)
                e.add_field(name="変更後", value=a.topic)
                gpf = await self.bot.cursor.fetchone(
                    "select * from guilds where id=%s", (a.guild.id,))
                #gpf = await self.bot.cursor.fetchone()
                if gpf["sendlog"]:
                    ch = self.bot.get_channel(gpf["sendlog"])
                    if ch.guild.id == a.guild.id:
                        await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_guild_update(self, b, a):
        if "cu:auto_sends" in self.bot.features.get(a.id,[]):
            return
        e = discord.Embed(title="サーバーの更新", color=self.bot.ec)
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        if b.name != a.name:
            e.add_field(name="変更内容", value="サーバー名")
            e.add_field(name="変更前", value=b.name)
            e.add_field(name="変更後", value=a.name)
            gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (a.id,))
            #gpf = await self.bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = self.bot.get_channel(gpf["sendlog"])
                if ch.guild.id == a.id:
                    await ch.send(embed=e)
        elif b.icon != a.icon:
            e.add_field(name="変更内容", value="サーバーアイコン")
            gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (a.id,))
            #gpf = await self.bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = self.bot.get_channel(gpf["sendlog"])
                if ch.guild.id == a.id:
                    await ch.send(embed=e)
        elif b.owner.id != a.owner.id:
            e.add_field(name="変更内容", value="サーバー所有者の変更")
            e.add_field(name="変更前", value=b.owner)
            e.add_field(name="変更後", value=a.owner)
            gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (a.id,))
            #gpf = await self.bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = self.bot.get_channel(gpf["sendlog"])
                if ch.guild.id == a.id:
                    await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_member_ban(self, g, user):
        if "cu:auto_sends" in self.bot.features.get(g.id,[]):
            return
        guild = self.bot.get_guild(g.id)
        # bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        e = discord.Embed(title="ユーザーのban", color=self.bot.ec)
        e.add_field(name="ユーザー名", value=str(user))
        # e.add_field(name="実行者", value=str(bl[0].user))
        # e.set_footer(text=f"{g.name}/{g.id}")
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (g.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == g.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if "cu:auto_sends" in self.bot.features.get(guild.id,[]):
            return
        e = discord.Embed(title="ユーザーのban解除", color=self.bot.ec)
        e.add_field(name="ユーザー名", value=str(user))
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == guild.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        e = discord.Embed(
            title=f"思惟奈ちゃんが{guild.name}に参加したよ！({len(self.bot.guilds)}サーバー)", description=f"id:{guild.id}", color=self.bot.ec)
        e.add_field(name="サーバー作成日時",
                    value=f"{(guild.created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')}")
        e.add_field(
            name="メンバー数", value=f"{len([i for i in guild.members if not i.self.bot])}ユーザー、{len([i for i in guild.members if i.self.bot])}self.bot")
        e.add_field(
            name="チャンネル数", value=f"テキスト:{len(guild.text_channels)}\nボイス:{len(guild.voice_channels)}\nカテゴリー{len(guild.categories)}")
        e.add_field(name="サーバーオーナー",value=f"{guild.owner.mention}({guild.owner}({guild.owner.id}))")
        ch = self.bot.get_channel(693048937304555529)
        await ch.send(embed=e)

        if "cu:auto_sends" in self.bot.features.get(guild.id,[]):
            return
        
        if "block:invite" in self.bot.features.get(guild.id,[]):
            await guild.leave()

        e=discord.Embed(title="思惟奈ちゃんの導入ありがとうございます！", description="思惟奈ちゃんのコマンドは、原則スラッシュコマンドで使用できます。(`s-`から始まる呼び出しも可)\nまずは`/`と入力して、使ってみましょう！", color=self.bot.ec)
        try:
            await guild.system_channel.send(embed=e)
        except:
            for ch in guild.text_channels:
                try:
                    await ch.send(embed=e)
                    return
                except:
                    continue


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            e = discord.Embed(
                title=f"思惟奈ちゃんが{guild.name}から退出しました。({len(self.bot.guilds)}サーバー)", description=f"原因としてサーバーからのkick/banまたはサーバーの削除などの可能性があります。\nid:{guild.id}", color=self.bot.ec)
            e.add_field(name="サーバー作成日時",
                        value=f"{(guild.created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')}")
            try:
                e.add_field(name="サーバー参加日時",
                            value=f"{(guild.me.joined_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')}")
            except:
                pass
            e.add_field(
                name="メンバー数", value=f"{len([i for i in guild.members if not i.self.bot])}ユーザー、{len([i for i in guild.members if i.self.bot])}self.bot")
            e.add_field(
                name="チャンネル数", value=f"テキスト:{len(guild.text_channels)}\nボイス:{len(guild.voice_channels)}\nカテゴリー{len(guild.categories)}")
            e.add_field(name="サーバーオーナー",value=f"{guild.owner.mention}({guild.owner}({guild.owner.id}))")
        except:
            e=discord.Embed(title="退出通知",description=f"以下のエラーにより正常に生成できていないため、一部情報が断片的な情報を送ります。\n```py\n{traceback.format_exc(3)}```")
            e.add_field(name="サーバー名/id",value=f"{guild.name}({guild.id})")
        ch = self.bot.get_channel(693048937304555529)
        await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if "cu:auto_sends" in self.bot.features.get(invite.guild.id,[]):
            return
        e = discord.Embed(title="サーバー招待の作成", color=self.bot.ec)
        e.add_field(name="作成ユーザー", value=str(invite.inviter))
        e.add_field(name="使用可能回数", value=str(invite.max_uses))
        e.add_field(name="使用可能時間", value=str(invite.max_age))
        e.add_field(name="チャンネル", value=str(invite.channel.mention))
        e.add_field(name="コード", value=str(invite.code))
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (invite.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == invite.guild.id:
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if "cu:auto_sends" in self.bot.features.get(invite.guild.id,[]):
            return
        e = discord.Embed(title="サーバー招待の削除", color=self.bot.ec)
        e.add_field(name="作成ユーザー", value=str(invite.inviter))
        e.add_field(name="チャンネル", value=str(invite.channel.mention))
        e.add_field(name="コード", value=str(invite.code))
        e.timestamp = datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9)
        gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s", (invite.guild.id,))
        #gpf = await self.bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = self.bot.get_channel(gpf["sendlog"])
            if ch.guild.id == invite.guild.id:
                await ch.send(embed=e)


async def setup(bot):
    await bot.add_cog(m10s_guild_log(bot))