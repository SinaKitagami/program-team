# -*- coding: utf-8 -*-

import datetime
import discord
from discord.ext import commands
import asyncio
from dateutil.relativedelta import relativedelta as rdelta

import json
import m10s_util as ut

import config

from checker import MaliciousInput, content_checker

"""

bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS gchat_clist(name text PRIMARY KEY NOT NULL,pass text)")
bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS gchat_cinfo(id integer PRIMARY KEY NOT NULL,connected_to text NOT NULL, wh_id integer NOT NULL)")
bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS gchat_pinfo(id integer PRIMARY KEY NOT NULL,content pickle,allids pickle,author_id integer,guild_id integer,timestamp pickle)")

    allids = [ [wh_id, post_id],... ]

"""

class m10s_re_gchat(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.manage_category = bot.get_channel(809280196192108564)
        self.without_react = ["rsp_main-chat"]
        self.ignore_ch = []

    async def gchat_send(self, to, fch, content, name, avatar, embeds=None, attachments=None):
        tasks = []
        for t in to:
            try:
                wh = await self.bot.fetch_webhook(t["wh_id"])
            except:
                continue
            else:
                try:
                    if not t["id"] == fch.id:
                        tasks.append(
                            asyncio.ensure_future(
                                wh.send(content=content, wait=True, username=name, avatar_url=avatar, embeds=embeds, files=[await i.to_file(spoiler=i.is_spoiler()) for i in attachments], allowed_mentions=discord.AllowedMentions.none())
                            )
                        )
                except:
                    pass
        return [[m.webhook_id, m.id] for m in await asyncio.gather(*tasks) if not m is None]

    async def repomsg(self, msg, rs, should_ban=False):
        ch = self.bot.get_channel(628929788421210144)
        e = discord.Embed(title="グローバルメッセージブロック履歴",
                        description=f"メッセージ内容:{msg.clean_content}", color=self.bot.ec)
        e.set_author(name=f"{msg.author}(id:{msg.author.id})",
                    icon_url=msg.author.avatar_url_as(static_format="png"))
        e.set_footer(text=f"サーバー:{msg.guild.name}(id:{msg.guild.id})",
                    icon_url=msg.guild.icon_url_as(static_format="png"))
        e.timestamp = msg.created_at
        e.add_field(name="ブロック理由", value=rs or "なし")
        await ch.send(embed=e)
        if should_ban:
            await self.bot.cursor.execute(
                "UPDATE users SET gban = %s WHERE id = %s", (1, msg.author.id))
            await self.bot.cursor.execute("UPDATE users SET gbanhist = %s WHERE id = %s",
                            ("予防グローバルチャットBAN: {}".format(rs), msg.author.id))


    @commands.group()
    @commands.cooldown(1, 20, type=commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def gchat(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("""> re_global_chat　
            `connect [接続先名(デフォルト:main)]`:このチャンネルをグローバルチャットに接続します。
            `dconnect`:グローバルチャットから切断します。
            """)

    @gchat.command()
    async def connect(self, ctx, *, name="main"):
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        if upf["gban"] == 1:
            await ctx.send("あなたはグローバルチャットを使えないため、このコマンドは使用できません。")
            return
        p = await self.bot.cursor.fetchone("select * from gchat_cinfo where id = %s",(ctx.channel.id,))
        if p:
            await ctx.reply("> 接続エラー\n　このチャンネルは既にグローバルチャットに接続されています。")
        else:
            gch = await self.bot.cursor.fetchone("select * from gchat_clist where name = %s",(name,))
            #gch = await self.bot.cursor.fetchone()
            if gch:
                if gch["pass"]:
                    try:
                        m = await ut.wait_message_return(ctx, f"{name}に接続するためのパスワードを送信してください。", ctx.author.dm_channel or await ctx.author.create_dm(),tout=30)
                        if m.content != gch["pass"]:
                            await ctx.author.send("> 接続エラー\n　パスワードが違います。もう一度最初からやり直してください。")
                            sendto = await self.bot.cursor.fetchall("select * from gchat_cinfo where connected_to = %s",(name,))
                            #sendto = await self.bot.cursor.fetchall()
                            await self.gchat_send(sendto, ctx.channel, f"> {ctx.author}({ctx.author.id})が{ctx.channel.name}({ctx.channel.id})をこのチャンネルに接続しようとしました。(パスワードが違うことにより失敗)",
                                "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.avatar_url_as(static_format="png"))
                            return
                    except:
                        await ctx.author.send("> 接続エラー\n　パスワードが入力されませんでした。")
                        sendto = await self.bot.cursor.fetchall("select * from gchat_cinfo where connected_to = %s",(name,))
                        #sendto = await self.bot.cursor.fetchall()
                        await self.gchat_send(sendto, ctx.channel, f"> {ctx.author}({ctx.author.id})が{ctx.channel.name}({ctx.channel.id})をこのチャンネルに接続しようとしました。(パスワード未入力により失敗)",
                            "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.avatar_url_as(static_format="png"))
                        return
                wh = await ctx.channel.create_webhook(name="sina_gchat_webhook",reason=f"思惟奈ちゃんグローバルチャット:{name}への接続が行われたため")
                await self.bot.cursor.execute("insert into gchat_cinfo(id,connected_to,wh_id) values(%s,%s,%s)",(ctx.channel.id,name,wh.id))
                sendto = await self.bot.cursor.fetchall("select * from gchat_cinfo where connected_to = %s",(name,))
                #sendto = await self.bot.cursor.fetchall()
                await self.gchat_send(sendto, ctx.channel, f"> グローバルチャットに{ctx.channel.name}({ctx.channel.id})が接続しました！ようこそ！",
                    "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.avatar_url_as(static_format="png"))

                await ctx.send("> 接続が完了しました。")
            else:
                try:
                    m = await ut.wait_message_return(ctx, "グローバルチャットにパスワードを設定する場合は送信してください。(パスワードを設定しない場合はしばらくお待ちください。)",
                        ctx.author.dm_channel or await ctx.author.create_dm(),tout=30)
                except:
                    m = None
                finally:    
                    await self.bot.cursor.execute("insert into gchat_clist(name,pass) values(%s,%s)", (name, m.content if not m is None else None))

                    wh = await ctx.channel.create_webhook(name="sina_gchat_webhook",reason=f"思惟奈ちゃんグローバルチャット:{name}への接続が行われたため")
                    await self.bot.cursor.execute("insert into gchat_cinfo(id,connected_to,wh_id) values(%s,%s,%s)",(ctx.channel.id,name,wh.id))

                    mch = await self.manage_category.create_text_channel(name=f"gch_{name}",topic=f"接続先名:`{name}`{f',接続パスワード:{m.content}' if not m is None else ''}")
                    mwh = await mch.create_webhook(name="sina_gchat_webhook",reason=f"思惟奈ちゃんグローバルチャット:{name}の作成が行われたため")
                    await self.bot.cursor.execute("insert into gchat_cinfo(id,connected_to,wh_id) values(%s,%s,%s)",(mch.id,name,mwh.id))
                    
                    sendto = await self.bot.cursor.fetchall("select * from gchat_cinfo where connected_to = %s",(name,))
                    #sendto = await self.bot.cursor.fetchall()
                    await self.gchat_send(sendto, ctx.channel, f"> グローバルチャットに{ctx.channel.name}({ctx.channel.id})が接続しました！",
                        "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.avatar_url_as(static_format="png"))

                    await ctx.send("> 接続が完了しました。")


    @gchat.command()
    async def dconnect(self, ctx):
        cgch = await self.bot.cursor.fetchone("select * from gchat_cinfo where id = %s",(ctx.channel.id,))
        #cgch = await self.bot.cursor.fetchone()
        if cgch:
            try:
                wh = await self.bot.fetch_webhook(cgch["wh_id"])
                await wh.delete(reason=f"思惟奈ちゃんグローバルチャット:{cgch['connected_to']}からの切断が行われたため")
            except:
                pass
            finally:
                await self.bot.cursor.execute("delete from gchat_cinfo where id = %s",(ctx.channel.id,))

                sendto = await self.bot.cursor.fetchall("select * from gchat_cinfo where connected_to = %s",(cgch["connected_to"],))
                #sendto = await self.bot.cursor.fetchall()
                await self.gchat_send(sendto, ctx.channel, f"> グローバルチャットから{ctx.channel.name}({ctx.channel.id})が切断しました。さようなら。",
                    "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.avatar_url_as(static_format="png"))

                await ctx.reply("> 切断が完了しました。\n　このチャンネルでの思惟奈ちゃんグローバルチャットのご利用ありがとうございました。")
        else:
            await ctx.reply("> 切断エラー\n　このチャンネルはグローバルチャットに接続されていません。")


    @commands.Cog.listener()
    async def on_message(self, m):
        if m.channel.id in self.ignore_ch: #グローバルチャットの外部との相互連携作成時用
            return
        
        if m.content.startswith("s-"):
            return
        if m.content.startswith("//"):
            return
        if m.author.id == self.bot.user.id:
            return
        if m.is_system():
            return
        if "cu:on_msg" in self.bot.features.get(m.author.id, []):
            return
        if isinstance(m.channel, discord.DMChannel):
            return
        if m.webhook_id:
            return
        
        if not m.author.id in self.bot.team_sina:
            if self.bot.maintenance:
                return
                
        upf = await self.bot.cursor.fetchone("select * from users where id=%s",
            (m.author.id,))
        #upf = await self.bot.cursor.fetchone()

        gchat_info = await self.bot.cursor.fetchone("select * from gchat_cinfo where id = %s", (m.channel.id,))
        #gchat_cinfo = await self.bot.cursor.fetchone()

        if gchat_info:

            if upf["gban"] == 1:
                if not gchat_info["connected_to"] in self.without_react:

                    dc = await ut.opendm(m.author)
                    await dc.send(await self.bot._(m.author, "global-banned", m.author.mention))
                    await self.repomsg(m, "思惟奈ちゃんグローバルチャットの使用禁止")
                    await m.add_reaction("❌")
                    await asyncio.sleep(5)
                    await m.remove_reaction("❌", self.bot.user)
                    return

            if (datetime.datetime.now() - rdelta(hours=9) - rdelta(days=7) >= m.author.created_at) or upf["gmod"] or upf["gstar"]:

                try:
                    content_checker(self.bot, m)
                except MaliciousInput as err:
                    await self.repomsg(m, err.reason, err.should_ban)
                    return

                try:
                    if not gchat_info["connected_to"] in self.without_react:
                        await m.add_reaction(self.bot.get_emoji(653161518346534912))
                except:
                    pass

                gpf = await self.bot.cursor.fetchone("select * from guilds where id=%s",
                    (m.guild.id,))
                #gpf = await self.bot.cursor.fetchone()

                status_embed = discord.Embed(title="", description="", color=upf["gcolor"])
                status_embed.set_author(
                    name=f"{ut.ondevicon(m.author)},({str(m.author.id)})")
                if gpf["verified"]:
                    status_embed.set_footer(text=f"✅:{m.guild.name}(id:{m.guild.id})", icon_url=m.guild.icon_url_as(
                        static_format="png"))
                else:
                    status_embed.set_footer(text=f"{m.guild.name}(id:{m.guild.id})",
                                    icon_url=m.guild.icon_url_as(static_format="png"))

                if m.type == discord.MessageType.default and m.reference:
                    ref = m.reference
                    if ref.cached_message:
                        msg = ref.cached_message
                    else:
                        try:
                            msg = await self.bot.get_channel(ref.channel_id).fetch_message(ref.message_id)
                        except:
                            msg = None
                    if msg:
                        status_embed.add_field(name=f"{msg.author.display_name}のメッセージへの返信",value=f"{msg.clean_content}")
                    else:
                        status_embed.add_field(name="メッセージへの返信",value="(このメッセージは削除されている等で取得できません。)")

                if gchat_info["connected_to"] in self.without_react:
                    embeds = []
                else:
                    embeds = [status_embed]

                if m.stickers:
                    sticker = m.stickers[0]
                    sembed = discord.Embed(title=f"スタンプ:{sticker.name}",)
                    if sticker.format == discord.StickerType.png:
                        sembed.set_image(url=sticker.image_url)
                    elif sticker.format == discord.StickerType.apng:
                        sembed.set_image(url=f"https://dsticker.herokuapp.com/convert.gif?url={sticker.image_url}")
                    elif sticker.format == discord.StickerType.lottie:
                        # メモ: https://cdn.discordapp.com/stickers/{id}/{hash}.json?size=1024
                        sembed.description = "画像取得非対応のスタンプです。"
                    embeds.append(sembed)

                
                embeds = embeds + m.embeds[0:10-len(embeds)]
                attachments = m.attachments
                spicon = ""

                if m.author.id in self.bot.team_sina:  # チーム☆思惟奈ちゃん
                    spicon = spicon + "🌠"
                if m.author.bot:
                    spicon = spicon + "⚙"
                if upf["sinapartner"]:
                    spicon = spicon + "💠"  # 認証済みアカウント
                if m.author.id in config.partner_ids:
                    spicon = spicon + "🔗"
                if upf["gmod"]:
                    spicon = spicon + "🔧"
                if upf["gstar"]:
                    spicon = spicon + "🌟"
                if spicon == "":
                    spicon = "👤"
                
                name = f"[{spicon}]{upf['gnick']}"

                sendto = await self.bot.cursor.fetchall("select * from gchat_cinfo where connected_to = %s", (gchat_info["connected_to"],))
                #sendto = await self.bot.cursor.fetchall()
                rtn = await self.gchat_send(sendto, m.channel, m.clean_content,
                    name, m.author.avatar_url_as(static_format="png"), embeds, attachments)

                await self.bot.cursor.execute("INSERT INTO gchat_pinfo(id,allids,author_id,guild_id) VALUES(%s,%s,%s,%s)", (m.id, 
                            json.dumps(rtn), m.author.id, m.guild.id))

                try:
                    if not gchat_info["connected_to"] in self.without_react:
                        await m.remove_reaction(self.bot.get_emoji(653161518346534912),self.bot.user)
                        await m.add_reaction(self.bot.get_emoji(653161518195539975))
                        await asyncio.sleep(5)
                        await m.remove_reaction(self.bot.get_emoji(653161518195539975), self.bot.user)
                except:
                    pass
            else:
                await self.repomsg(m, "作成後7日に満たないアカウント")


    @commands.Cog.listener()
    async def on_raw_message_edit(self, pr):
        ncon = pr.data.get("content",None)
        if ncon:
            gpost = await self.bot.cursor.fetchone("select * from gchat_pinfo where id = %s",(pr.message_id,))
            #gpost = await self.bot.cursor.fetchone()
            if gpost:
                tasks = []
                for t in json.loads(gpost["allids"]):
                    try:
                        wh = await self.bot.fetch_webhook(t[0])
                    except:
                        continue
                    else:
                        tasks.append(
                            asyncio.ensure_future(
                                wh.edit_message(t[1], content=ncon)
                            )
                        )
                await asyncio.gather(*tasks)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, pr):
        gpost = await self.bot.cursor.fetchone("select * from gchat_pinfo where id = %s", (pr.message_id,))
        #gpost = await self.bot.cursor.fetchone()
        if gpost:
            tasks = []
            for t in json.loads(gpost["allids"]):
                try:
                    wh = await self.bot.fetch_webhook(t[0])
                except:
                    continue
                else:
                    if wh.guild.id != 560434525277126656:
                        tasks.append(
                            asyncio.ensure_future(
                                wh.delete_message(t[1])
                            )
                        )
            await asyncio.gather(*tasks)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, ch):
        cgch = await self.bot.cursor.fetchone("select * from gchat_cinfo where id = %s",(ch.id,))
        #cgch = await self.bot.cursor.fetchone()
        if cgch:
            await self.bot.cursor.execute("delete from gchat_cinfo where id = %s",(ch.id,))

    @commands.Cog.listener()
    async def on_webhooks_update(self, ch):
        cgch = await self.bot.cursor.fetchone("select * from gchat_cinfo where id = %s",(ch.id,))
        #cgch = await self.bot.cursor.fetchone()
        if cgch:
            if cgch["wh_id"] in [i.id for i in await ch.webhooks()]:
                await self.bot.cursor.execute("delete from gchat_cinfo where id = %s",(ch.id,))


def setup(bot):
    bot.add_cog(m10s_re_gchat(bot))
