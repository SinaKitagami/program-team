# -*- coding: utf-8 -*-

import datetime
from typing import Optional
import discord
from discord.ext import commands
import asyncio
from dateutil.relativedelta import relativedelta as rdelta

from discord import app_commands

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

    async def gchat_send(self, to, fch, content, name, avatar, embeds=[], attachments=[]):
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
                    icon_url=msg.author.display_avatar.replace(static_format="png").url)
        if msg.guild.icon:
            e.set_footer(text=f"サーバー:{msg.guild.name}(id:{msg.guild.id})",
                        icon_url=msg.guild.icon.replace(static_format="png").url)
        else:
            e.set_footer(text=f"サーバー:{msg.guild.name}(id:{msg.guild.id})")
        e.timestamp = msg.created_at
        e.add_field(name="ブロック理由", value=rs or "なし")
        await ch.send(embed=e)
        if should_ban:
            await self.bot.cursor.execute(
                "UPDATE users SET gban = %s WHERE id = %s", (1, msg.author.id))
            await self.bot.cursor.execute("UPDATE users SET gbanhist = %s WHERE id = %s",
                            ("予防グローバルチャットBAN: {}".format(rs), msg.author.id))


    @commands.hybrid_group(name="global_chat",short_doc="グローバルチャットの接続を切り替えます。")
    @commands.cooldown(1, 20, type=commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def gchat(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("""> re_global_chat　
            `connect [接続先名(デフォルト:main)]`:このチャンネルをグローバルチャットに接続します。
            `dconnect`:グローバルチャットから切断します。
            """)

    @gchat.command(description="グローバルチャットに接続します。")
    @app_commands.describe(name="グローバルチャット名。同じものを指定して接続したチャンネル同士がつながります。(デフォルト:main)")
    async def connect(self, ctx, *, name:str="main"):
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
                                "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.display_avatar.replace(static_format="png").url)
                            return
                    except:
                        await ctx.author.send("> 接続エラー\n　パスワードが入力されませんでした。")
                        sendto = await self.bot.cursor.fetchall("select * from gchat_cinfo where connected_to = %s",(name,))
                        #sendto = await self.bot.cursor.fetchall()
                        await self.gchat_send(sendto, ctx.channel, f"> {ctx.author}({ctx.author.id})が{ctx.channel.name}({ctx.channel.id})をこのチャンネルに接続しようとしました。(パスワード未入力により失敗)",
                            "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.display_avatar.replace(static_format="png").url)
                        return
                wh = await ctx.channel.create_webhook(name="sina_gchat_webhook",reason=f"思惟奈ちゃんグローバルチャット:{name}への接続が行われたため")
                await self.bot.cursor.execute("insert into gchat_cinfo(id,connected_to,wh_id) values(%s,%s,%s)",(ctx.channel.id,name,wh.id))
                sendto = await self.bot.cursor.fetchall("select * from gchat_cinfo where connected_to = %s",(name,))
                #sendto = await self.bot.cursor.fetchall()
                await self.gchat_send(sendto, ctx.channel, f"> グローバルチャットに{ctx.channel.name}({ctx.channel.id})が接続しました！ようこそ！",
                    "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.display_avatar.replace(static_format="png").url)

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
                        "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.display_avatar.replace(static_format="png").url)

                    await ctx.send("> 接続が完了しました。")


    @gchat.command(description="グローバルチャットから切断します。")
    async def dconnect(self, ctx:commands.Context):
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
                    "[🛠💠]思惟奈ちゃんグローバルチャット接続案内", ctx.guild.me.display_avatar.replace(static_format="png").url)

                await ctx.reply("> 切断が完了しました。\n　このチャンネルでの思惟奈ちゃんグローバルチャットのご利用ありがとうございました。")
        else:
            await ctx.reply("> 切断エラー\n　このチャンネルはグローバルチャットに接続されていません。", )


    @gchat.command(description="グローバルチャットに投稿されたメッセージについて確認します。")
    @app_commands.describe(globalchat_message_id="グローバルチャットに投稿されたメッセージのid")
    async def check_post(self, ctx, globalchat_message_id: int):
        gmid = globalchat_message_id
        post = None
        dats = await self.bot.cursor.fetchall("select * from gchat_pinfo")
        #dats = await self.bot.cursor.fetchall()
        for i in dats:
            if gmid in ([j[1] for j in json.loads(i["allids"])]+[i["id"]]):
                post = i
                break
        if post is None:
            await ctx.say("globalpost-notfound")
            return
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        if upf["gmod"]:
            apf = await self.bot.cursor.fetchone(
                "select * from users where id=%s", (post["author_id"],))
            #apf = await self.bot.cursor.fetchone()
            g = self.bot.get_guild(post["guild_id"])
            await ctx.send(embed=ut.getEmbed(f"オリジナルID:'{post['id']}", "", self.bot.ec, "送信者id:", str(post['author_id']), "送信先", str([i[1] for i in json.loads(post["allids"])]), "送信者のプロファイルニックネーム", apf['gnick'], "サーバーid", g.id, "サーバーネーム", g.name))
        else:
            apf = await self.bot.cursor.fetchone(
                "select * from users where id=%s", (post["author_id"],))
            #apf = await self.bot.cursor.fetchone()
            g = self.bot.get_guild(post["guild_id"])
            await ctx.send(embed=ut.getEmbed("グローバルチャンネル投稿情報", "", self.bot.ec, "送信者id:", str(post['author_id']), "送信者のプロファイルニックネーム", apf['gnick']))

    @commands.command(aliases=["オンライン状況", "次の人のオンライン状況を教えて"])
    async def isonline(self, ctx, uid: int=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if uid is None:
            cid = ctx.message.author.id
        else:
            cid = uid
            if not self.bot.shares_guild(uid, ctx.author.id):
                return await ctx.say("ison-notfound")
            if not await self.bot.can_use_online(self.bot.get_user(uid)):
                return await ctx.say("ison-notfound")
        async with ctx.message.channel.typing():
            for guild in self.bot.guilds:
                u = guild.get_member(uid)
                if u is not None:
                    break
        if u is not None:
            await ctx.send(await ctx._("ison-now", u.name, str(u.status)))
        else:
            await ctx.send(await ctx._("ison-notfound"))

    @gchat.command(description="グローバルチャットに接続しているチャンネル一覧を返します。")
    @app_commands.describe(name="接続先名(デフォルト:main)")
    async def gchinfo(self, ctx, name:Optional[str]="main"):
        gch = await self.bot.cursor.fetchone(
            "select * from gchat_clist where name = %s", (name,))
        #gch = await self.bot.cursor.fetchone()
        if gch:
            chs = await self.bot.cursor.fetchall(
                "select * from gchat_cinfo where connected_to = %s", (name,))
            #chs = await self.bot.cursor.fetchall()
            retchs = ""
            for ch in chs:
                try:
                    retchs = f"{retchs}{self.bot.get_channel(ch['id']).guild.name} -> {self.bot.get_channel(ch['id']).name}\n"
                except:
                    retchs = f"{retchs}不明なサーバー -> チャンネルID:{ch['id']}\n"
            await ctx.send(embed=ut.getEmbed(f"グローバルチャンネル {name} の詳細", f"コネクトされたサーバーとチャンネル\n{retchs}", self.bot.ec))
        else:
            await ctx.send("そのグローバルチャンネルはありません。")

    @gchat.command(aliases=["グローバルチャットの色を変える"],description="グローバルチャットの埋め込みカラーを変更できます。")
    @app_commands.describe(color="16進数の色コード")
    async def edit_color(self, ctx, color:str='0x000000'):
        await self.bot.cursor.execute(
            "UPDATE users SET gcolor = %s WHERE id = %s", (int(color, 16), ctx.author.id))
        await ctx.send(await ctx._("global-color-changed"))

    @gchat.command(aliases=["グローバルチャットのニックネームを変える"], description="グローバルチャットでの表示名を変更できます。")
    @app_commands.describe(nick="変更するニックネーム")
    async def edit_nick(self, ctx, nick:str):
        if 1 < len(nick) < 29:
            await self.bot.cursor.execute(
                "UPDATE users SET gnick = %s WHERE id = %s", (nick, ctx.author.id))
            await ctx.send(await ctx._("global-nick-changed"))
        else:
            await ctx.send("名前の長さは2文字以上28文字以下にしてください。")

    @commands.command()
    async def gchatban(self, ctx, uid: int, ban: bool=True, *, rea="なし"):
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        try:
            bui = await self.bot.fetch_user(uid)
        except:
            await ctx.send("そのIDをもつユーザーがいません！")
        else:
            if upf["gmod"] == 1:
                bpf = await self.bot.cursor.fetchone(
                    "select * from users where id=%s", (uid,))
                # bpf = await self.bot.cursor.fetchone()
                if bpf:
                    await self.bot.cursor.execute(
                        "UPDATE users SET gban = %s WHERE id = %s", (int(ban), uid))
                    await self.bot.cursor.execute(
                        "UPDATE users SET gbanhist = %s WHERE id = %s", (rea, uid))
                    await ctx.send(f"ban状態を{str(ban)}にしました。")
                elif bui:
                    await self.bot.cursor.execute("INSERT INTO users(id,prefix,gpoint,memo,levcard,onnotif,lang,accounts,sinapartner,gban,gnick,gcolor,gmod,gstar,galpha,gbanhist) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (bui.id, "[]",
                    0, "{}", "m@ji☆", "[]", "ja", "[]", 0, int(ban), bui.name, 0, 0, 0, 0, rea))
                    await ctx.send(f"プロファイルを作成し、ban状態を{str(ban)}にしました。")
                else:
                    await ctx.send("これが呼び出されることは、ありえないっ！")

    @commands.command()
    async def globaltester(self, ctx, uid, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        if upf["gmod"] == 1:
            await self.bot.cursor.execute(
                "UPDATE users SET galpha = %s WHERE id = %s", (int(bl), uid))
            await ctx.send(f"テスト機能の使用を{str(bl)}にしました。")

    @commands.command()
    @commands.is_owner()
    async def globalmod(self, ctx, uid, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        await self.bot.cursor.execute(
            "UPDATE users SET gmod = %s WHERE id = %s", (int(bl), uid))
        await ctx.send(f"グローバルモデレーターを{str(bl)}にしました。")

    @commands.command()
    @commands.is_owner()
    async def userv(self, ctx, uid, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        await self.bot.cursor.execute(
            "UPDATE users SET sinapartner = %s WHERE id = %s", (int(bl), uid))
        await ctx.send(f"該当ユーザーの認証状態を{str(bl)}にしました。")

    @commands.command()
    async def globalstar(self, ctx, uid, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        if upf["gmod"] == 1:
            await self.bot.cursor.execute(
                "UPDATE users SET gstar = %s WHERE id = %s", (int(bl), uid))
            await ctx.send(f"スターユーザーを{str(bl)}にしました。")

    @gchat.command(description="グローバルチャットの利用ガイドを表示します。")
    async def guide(self, ctx):
        embed = discord.Embed(description=self.bot.gguide, color=self.bot.ec)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 30, type=commands.BucketType.user)
    async def globaldel(self, ctx, gmid: int):
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        post = None
        dats = await self.bot.cursor.fetchall("select * from gchat_pinfo")
        #dats = await self.bot.cursor.fetchall()
        if upf["gmod"]:
            for i in dats:
                if gmid in [j[1] for j in json.loads(i["allids"])] or gmid  == i["id"]:
                    post = i
                    break
            if post:
                tasks = []
                for t in json.loads(post["allids"]):
                    try:
                        wh = await self.bot.fetch_webhook(t[0])
                    except:
                        continue
                    else:
                        tasks.append(
                            asyncio.ensure_future(
                                wh.delete_message(t[1])
                            )
                        )
                await asyncio.gather(*tasks)
                await ctx.send("削除が完了しました。")
            else:
                await ctx.send("削除するコンテンツが見つかりませんでした。")
        else:
            await ctx.send("このコマンドは運営のみ実行できます。")

    @commands.command()
    async def viewgban(self, ctx):
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        pf = await self.bot.cursor.fetchall("select * from users")
        #pf = await self.bot.cursor.fetchall()
        if upf["gmod"]:
            async with ctx.message.channel.typing():
                blist = []
                for i in pf:
                    if i["gban"] == 1:
                        bu = await self.bot.fetch_user(i["id"])
                        blist.append(
                            f"ユーザー名:{bu},表示名:{i['gnick']},id:{i['id']},理由:{i['gbanhist']}")
                embed = discord.Embed(title=f"banされたユーザーの一覧({len(blist)}名)", description="```{0}```".format(
                    '\n'.join(blist)), color=self.bot.ec)
            await ctx.send(embed=embed)


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

            if (datetime.datetime.now(datetime.timezone.utc) - rdelta(hours=9) - rdelta(days=7) >= m.author.created_at) or upf["gmod"] or upf["gstar"]:
                
                if not gchat_info["connected_to"] in self.without_react:
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
                    if m.guild.icon:
                        status_embed.set_footer(text=f"✅:{m.guild.name}(id:{m.guild.id})", icon_url=m.guild.icon.replace(
                            static_format="png").url)
                    else:
                        status_embed.set_footer(text=f"✅:{m.guild.name}(id:{m.guild.id})")
                else:
                    if m.guild.icon:
                        status_embed.set_footer(text=f"{m.guild.name}(id:{m.guild.id})",
                                        icon_url=m.guild.icon.replace(static_format="png").url)
                    else:
                        status_embed.set_footer(text=f"{m.guild.name}(id:{m.guild.id})")

                if m.type == discord.MessageType.reply:
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
                    if sticker.format == discord.StickerFormatType.png:
                        sembed.set_image(url=sticker.url)
                    elif sticker.format == discord.StickerFormatType.apng:
                        sembed.set_image(url=f"https://dsticker.herokuapp.com/convert.gif?url={sticker.url}")
                    elif sticker.format == discord.StickerFormatType.lottie:
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
                    name, m.author.display_avatar.replace(static_format="png").url, embeds, attachments)

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
            if not (cgch["wh_id"] in [i.id for i in await ch.webhooks()]):
                await self.bot.cursor.execute("delete from gchat_cinfo where id = %s",(ch.id,))


async def setup(bot):
    await bot.add_cog(m10s_re_gchat(bot))
