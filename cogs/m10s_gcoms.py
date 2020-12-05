# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio

import m10s_util as ut


class gcoms(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def globalpost(self, ctx, gmid: int):
        post = None
        self.bot.cursor.execute("select * from globaldates")
        dats = self.bot.cursor.fetchall()
        for i in dats:
            if gmid in i["allid"]:
                post = i
        if post is None:
            await ctx.say("globalpost-notfound")
        self.bot.cursor.execute(
            "select * from users where id=?", (ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        if upf["gmod"]:
            self.bot.cursor.execute(
                "select * from users where id=?", (i["aid"],))
            apf = self.bot.cursor.fetchone()
            u = self.bot.cursor.fetchone()
            g = self.bot.get_guild(post["gid"])
            await ctx.send(embed=ut.getEmbed("メッセージ内容", post['content'], self.bot.ec, "送信者id:", post['aid'], "送信先", post["allid"], "送信者のプロファイルニックネーム", apf['gnick'], "サーバーid", g.id, "サーバーネーム", g.name))
        else:
            self.bot.cursor.execute(
                "select * from users where id=?", (i["aid"],))
            u = self.bot.cursor.fetchone()
            g = self.bot.get_guild(post["gid"])
            apf = self.bot.cursor.fetchone()
            await ctx.send(embed=ut.getEmbed("メッセージ内容", post['content'], self.bot.ec, "送信者id:", post['aid'], "送信者のプロファイルニックネーム", apf['gnick']))

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
            if not self.bot.can_use_online(self.bot.get_user(uid)):
                return await ctx.say("ison-notfound")
        async with ctx.message.channel.typing():
            for guild in self.bot.guilds:
                u = guild.get_member(uid)
                if u is not None:
                    break
        if u is not None:
            await ctx.send(ctx._("ison-now", u.name, str(u.status)))
        else:
            await ctx.send(ctx._("ison-notfound"))

    @commands.command()
    async def gchinfo(self, ctx, name="main"):
        self.bot.cursor.execute(
            "select * from globalchs where name = ?", (name,))
        chs = self.bot.cursor.fetchone()
        if chs:
            retchs = ""
            for ch in chs["ids"]:
                try:
                    retchs = f"{retchs}{self.bot.get_channel(ch).guild.name} -> {self.bot.get_channel(ch).name}\n"
                except:
                    retchs = f"{retchs}不明なサーバー -> チャンネルID:{ch}\n"
            await ctx.send(embed=ut.getEmbed(f"グローバルチャンネル {name} の詳細", f"コネクトされたサーバーとチャンネル\n{retchs}", self.bot.ec))
        else:
            await ctx.send("そのグローバルチャンネルはありません。")

    @commands.command(aliases=["グローバルチャットの色を変える"])
    async def globalcolor(self, ctx, color='0x000000'):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "UPDATE users SET gcolor = ? WHERE id = ?", (int(color, 16), ctx.author.id))
        await ctx.send(ctx._("global-color-changed"))

    @commands.command(aliases=["グローバルチャットのニックネームを変える"])
    async def globalnick(self, ctx, nick):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if 1 < len(nick) < 29:
            self.bot.cursor.execute(
                "UPDATE users SET gnick = ? WHERE id = ?", (nick, ctx.author.id))
            await ctx.send(ctx._("global-nick-changed"))
        else:
            await ctx.send("名前の長さは2文字以上28文字以下にしてください。")

    @commands.command(aliases=["グローバルチャットのステータス", "グローバルチャットのステータスを見せて"])
    async def gprofile(self, ctx, uid: int=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if uid is None:
            cid = ctx.author.id
        else:
            cid = uid
        ap = self.bot.cursor.execute(
            "SELECT gmod FROM users WHERE id=?", (ctx.author.id,)).fetchone()
        self.bot.cursor.execute("select * from users where id=?", (cid,))
        upf = self.bot.cursor.fetchone()
        embed = discord.Embed(title=ctx._(
            "global-status-title", cid), description="", color=upf["gcolor"])
        embed.add_field(name="nick", value=upf["gnick"])
        embed.add_field(name="color", value=str(upf["gcolor"]))
        embed.add_field(name="gmod", value="True" if upf["gmod"] == 1 else "False")
        embed.add_field(name="tester", value="True" if upf["galpha"] == 1 else "False")
        embed.add_field(name="star", value="True" if upf["gstar"] == 1 else "False")
        if ap and ap["gmod"]:
            embed.add_field(name="banned", value="True" if upf["gban"] == 1 else "False")
            if upf["gban"]:
                embed.add_field(name="reason of ban", value=upf["gbanhist"])
        await ctx.send(embed=embed)

    @commands.command()
    async def gchatban(self, ctx, uid: int, ban: bool=True, *, rea="なし"):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "select * from users where id=?", (ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        try:
            bui = await self.bot.fetch_user(uid)
        except:
            await ctx.send("そのIDをもつユーザーがいません！")
        else:
            if upf["gmod"] == 1:
                self.bot.cursor.execute(
                    "select * from users where id=?", (uid,))
                bpf = self.bot.cursor.fetchone()
                if bpf:
                    self.bot.cursor.execute(
                        "UPDATE users SET gban = ? WHERE id = ?", (int(ban), uid))
                    self.bot.cursor.execute(
                        "UPDATE users SET gbanhist = ? WHERE id = ?", (rea, uid))
                    await ctx.send(f"ban状態を{str(ban)}にしました。")
                elif bui:
                    self.bot.cursor.execute("INSERT INTO users(id,prefix,gpoint,memo,levcard,onnotif,lang,accounts,sinapartner,gban,gnick,gcolor,gmod,gstar,galpha,gbanhist) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (bui.id, [
                    ], 0, {}, "m@ji☆", [], "ja", [], 0, 1, bui.name, 0, 0, 0, 0, rea))
                    await ctx.send(f"プロファイルを作成し、ban状態を{str(ban)}にしました。")
                else:
                    await ctx.send("これが呼び出されることは、ありえないっ！")

    @commands.command()
    async def globaltester(self, ctx, uid, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "select * from users where id=?", (ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        if upf["gmod"] is True:
            self.bot.cursor.execute(
                "UPDATE users SET galpha = ? WHERE id = ?", (int(bl), uid))
            await ctx.send(f"テスト機能の使用を{str(bl)}にしました。")

    @commands.command()
    @commands.is_owner()
    async def globalmod(self, ctx, uid, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "UPDATE users SET gmod = ? WHERE id = ?", (int(bl), uid))
        await ctx.send(f"グローバルモデレーターを{str(bl)}にしました。")

    @commands.command()
    @commands.is_owner()
    async def userv(self, ctx, uid, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "UPDATE users SET sinapartner = ? WHERE id = ?", (int(bl), uid))
        await ctx.send(f"該当ユーザーの認証状態を{str(bl)}にしました。")

    @commands.command()
    async def globalstar(self, ctx, uid, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "select * from users where id=?", (ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        if upf["gmod"] is True:
            self.bot.cursor.execute(
                "UPDATE users SET gstar = ? WHERE id = ?", (int(bl), uid))
            await ctx.send(f"スターユーザーを{str(bl)}にしました。")

    @commands.command()
    async def globalguide(self, ctx):
        embed = discord.Embed(description=self.bot.gguide, color=self.bot.ec)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 20, type=commands.BucketType.guild)
    async def gdconnect(self, ctx):
        if ctx.author.permissions_in(ctx.channel).administrator is True or ctx.author.id == 404243934210949120:
            if ctx.channel.permissions_for(ctx.guild.me).manage_webhooks:
                self.bot.cursor.execute("select * from globalchs")
                chs = self.bot.cursor.fetchall()
                if chs is not None:
                    for ch in chs:
                        if ctx.channel.id in ch["ids"]:
                            ch["ids"].remove(ctx.channel.id)
                            for wh in await ctx.guild.webhooks():
                                if wh.name == "sina_global":
                                    wh.delete()
                            self.bot.cursor.execute(
                                "UPDATE globalchs SET ids = ? WHERE name = ?", (ch["ids"], ch["name"]))
                            await ctx.send(ctx._("global-disconnect"))
                            embed = discord.Embed(
                                title="グローバルチャット切断通知", description=f'{ctx.guild.name}の{ctx.channel.name}が`{ch["name"]}`から切断しました。')
                            for cid in ch["ids"]:
                                channel = self.bot.get_channel(cid)
                                try:
                                    await channel.send(embed=embed)
                                except:
                                    pass
                            return
                await ctx.send("ここはどのグローバルチャットにも接続されていません！")
            else:
                await ctx.send("webhooksの管理権限がありません！")
        else:
            await ctx.send("このコマンドを実行するには、このサーバーで管理者権限を持つ必要があります。")

    @commands.command()
    @commands.cooldown(1, 20, type=commands.BucketType.guild)
    async def gconnect(self, ctx, name: str="main", dnf: bool=True):
        self.bot.cursor.execute(
            "select * from users where id=?", (ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        if upf["gban"] == 1:
            await ctx.send("あなたは使用禁止なのでコネクトは使えません。")
            return
        if ctx.author.permissions_in(ctx.channel).administrator is True or ctx.author.id == 404243934210949120:
            if ctx.channel.permissions_for(ctx.guild.me).manage_webhooks:
                self.bot.cursor.execute("select * from globalchs")
                chs = self.bot.cursor.fetchall()
                if chs is not None:
                    for ch in chs:
                        if ctx.channel.id in ch["ids"]:
                            await ctx.send(f"このチャンネルは既に`{ch['name']}`に接続されています！")
                            return
                self.bot.cursor.execute(
                    "select * from globalchs where name=?", (name,))
                chs = self.bot.cursor.fetchone()
                if chs is None:
                    try:
                        ctg = self.bot.get_guild(
                            560434525277126656).get_channel(582489567840436231)
                        cch = await ctg.create_text_channel(f'gch-{name}')
                        await cch.create_webhook(name="sina_global", avatar=None)
                        self.bot.cursor.execute(
                            "INSERT INTO globalchs(name,ids) VALUES(?,?)", (name, [ctx.channel.id, cch.id]))
                    except:
                        self.bot.cursor.execute(
                            "INSERT INTO globalchs(name,ids) VALUES(?,?)", (name, [ctx.channel.id]))
                else:
                    self.bot.cursor.execute(
                        "UPDATE globalchs SET ids = ? WHERE name = ?", (chs["ids"]+[ctx.channel.id], name))
                await ctx.channel.create_webhook(name="sina_global", avatar=None)
                if dnf:
                    embed = discord.Embed(title=f"{self.bot.get_emoji(653161518174699541)}グローバルチャット接続通知",
                                          description=f'{ctx.guild.name}の{ctx.channel.name}({ctx.channel.id})が`{name}`に接続しました。')
                else:
                    embed = discord.Embed(
                        title="グローバルチャット接続通知", description=f'{self.bot.get_emoji(653161518174699541)}どこかが`{name}`に接続しました。')
                self.bot.cursor.execute(
                    "select * from globalchs where name=?", (name,))
                ch = self.bot.cursor.fetchone()
                for cid in ch["ids"]:
                    channel = self.bot.get_channel(cid)
                    try:
                        await channel.send(embed=embed)
                    except:
                        pass
            else:
                await ctx.send("webhooksの管理権限がありません！")
        else:
            await ctx.send("このコマンドを実行するには、このサーバーで管理者権限を持つ必要があります。")

    @commands.command()
    @commands.cooldown(1, 30, type=commands.BucketType.user)
    async def globaldel(self, ctx, gmid: int, gchn: str):
        self.bot.cursor.execute(
            "select * from globalchs where name = ?", (gchn,))
        ch = self.bot.cursor.fetchone()
        self.bot.cursor.execute(
            "select * from users where id=?", (ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        post = None
        self.bot.cursor.execute("select * from globaldates")
        dats = self.bot.cursor.fetchall()
        if upf["gmod"]:
            for i in dats:
                if gmid in i["allid"]:
                    post = i
            if post:
                for cid in ch["ids"]:
                    ch = self.bot.get_channel(cid)
                    for mid in post["allid"]:
                        try:
                            m = await ch.fetch_message(mid)
                            await m.delete()
                        except:
                            pass
            await ctx.send("削除が完了しました。")

    @commands.command()
    async def viewgban(self, ctx):
        self.bot.cursor.execute(
            "select * from users where id=?", (ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        self.bot.cursor.execute("select * from users")
        pf = self.bot.cursor.fetchall()
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


def setup(bot):
    bot.add_cog(gcoms(bot))
