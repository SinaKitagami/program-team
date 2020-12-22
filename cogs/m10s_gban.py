# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio

import m10s_util as ut
"""↑様々な便利コマンド詰め合わせ
ut.textto("キー",Member)
    ユーザーの言語設定に基づいてキーのテキストを返す。
ut.ondevicon(Member)
    オンライン状況に基づくデバイスアイコンテキストを返す。
ut.getEmbed(title,description,color,(name,value)...)
    Embedのお手軽生成。これ使ったのがあるから消そうにも消せない。
await ut.opendm(Member/User)
    DMチャンネルを返します。DMチャンネルが存在しないなんてことでは困らせません。
await wait_message_return(ctx,質問するテキスト,←の送信先,待つ時間):
    入力待ちの簡略化。タイムアウトの例外キャッチを忘れずに
ut.get_vmusic(bot,member)
    思惟奈ちゃんの音楽再生機能でそのメンバーがきいている曲を返します。
"""


class m10s_gban(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check = bot.get_emoji(653161518103265291)

    @commands.command()
    async def gban(self, ctx, uid: int, tof: bool, *, reason: str=None):
        if "global_ban" in self.bot.features.get(ctx.author.id, []):
            try:
                u = await self.bot.fetch_user(uid)
            except discord.NotFound:
                await ctx.send("存在しないユーザーではないでしょうか？IDを見直してみてください。")
                return

            m = await ctx.send(f"> ❔確認\n　{u}({u.id})のグローバルBAN状態を{tof}で上書きしてもよろしいですか？")
            await m.add_reaction(self.check)
            await m.add_reaction("❌")
            r, us = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id)
            if (not str(r.emoji) == str(self.check)):
                await m.edit(content="> グローバルBANはキャンセルされました。")
                return

            if tof:
                self.bot.cursor.execute(
                    "select * from gban_dates where id=?", (uid,))
                gbaninfo = self.bot.cursor.fetchone()
                if not gbaninfo:
                    self.bot.cursor.execute(
                        "INSERT INTO gban_dates(id,reason,gban_by) VALUES(?,?,?)", (uid, reason or "なし", ctx.author.id))
                    await ctx.send(f"{u.name}のグローバルBANを設定しました。\n登録済みのサーバーでグローバルBANを開始します。")
                    self.bot.cursor.execute("select * from gban_settings")
                    gs = self.bot.cursor.fetchall()
                    for gstg in gs:
                        g = self.bot.get_guild(gstg["id"])
                        if g is None:
                            continue
                        ch = g.get_channel(gstg["chid"])
                        if ch is None:
                            continue
                        by = ctx.author
                        if g:
                            try:
                                await g.ban(u, reason=f"思惟奈ちゃんグローバルBAN:{reason}(実行者:{by}({by.id}))")
                            except:
                                if ch:
                                    await ch.send(embed=ut.getEmbed("グローバルBANに基づく、BANの試行", f"{u}({u.id})は、`{reason}`として思惟奈ちゃんのグローバルBANを受けています。\nBANしようとしましたが、権限不足等の理由でBANできませんでした。\nグローバルBAN実行者:{by}({by.id})"))
                                else:
                                    await g.owner.send(embed=ut.getEmbed("グローバルBANに基づく、BANの試行", f"{u}({u.id})は、`{reason}`として思惟奈ちゃんのグローバルBANを受けています。\nBANしようとしましたが、権限不足等の理由でBANできませんでした。\nグローバルBAN実行者:{by}({by.id})"))
                            else:
                                if ch:
                                    await ch.send(embed=ut.getEmbed("グローバルBANに基づく、BANの実行", f"{u}({u.id})は、`{reason}`として思惟奈ちゃんのグローバルBANを受けています。\nよって、このサーバーからBANを行いました。\nグローバルBAN実行者:{by}({by.id})"))
                                else:
                                    await g.owner.send(embed=ut.getEmbed("グローバルBANに基づく、BANの実行", f"{u}({u.id})は、`{reason}`として思惟奈ちゃんのグローバルBANを受けています。\nよって、このサーバーからBANを行いました。\nグローバルBAN実行者:{by}({by.id})"))
                    await ctx.send("該当ユーザーのグローバルBANが完了しました。")
                else:
                    await ctx.send(f"{u.name}はすでに思惟奈ちゃんのグローバルbanされています。")
            else:
                self.bot.cursor.execute(
                    "select * from gban_dates where id=?", (uid,))
                gbaninfo = self.bot.cursor.fetchone()
                if gbaninfo:
                    self.bot.cursor.execute(
                        f"delete from gban_dates where id = ?", (uid,))
                    await ctx.send(f"{u.name}のグローバルBANを解除しました。")
                else:
                    await ctx.send(f"{u.name}は思惟奈ちゃんのグローバルbanされていません")
        else:
            await ctx.send("グローバルBANの実行には、グローバルBANが使用できる認証を受けたアカウントである必要があります。\n思惟奈ちゃん運営に報告する際は、`s-report`コマンドを使用してください。正確性などを確認し、認められた場合はグローバルBANが行われます。")

    @commands.command()
    async def check_gban(self, ctx, uid: int):
        self.bot.cursor.execute("select * from gban_dates where id=?", (uid,))
        gbaninfo = self.bot.cursor.fetchone()
        if gbaninfo:
            u = await self.bot.fetch_user(uid)
            by = await self.bot.fetch_user(gbaninfo["gban_by"])
            await ctx.send(embed=ut.getEmbed(f"{u.name}のグローバルBANについて", "", self.bot.ec, "理由", gbaninfo["reason"], "実行者", f"{by}({by.id})"))
        else:
            await ctx.send("そのユーザーは思惟奈ちゃんのグローバルbanされていません")

    @commands.command()
    async def gbanlogto(self, ctx, chid: int=None):
        tch = ctx.guild.get_channel(chid)
        if chid and tch:
            self.bot.cursor.execute(
                "select * from gban_settings where id=?", (ctx.guild.id,))
            gs = self.bot.cursor.fetchone()
            if gs:
                self.bot.cursor.execute(
                    "UPDATE gban_settings SET chid = ? WHERE id = ?", (chid, ctx.guild.id))
            else:
                self.bot.cursor.execute(
                    "INSERT INTO gban_settings(id,chid) VALUES(?,?)", (ctx.guild.id, chid))
            await ctx.send("グローバルBANの利用、送信先チャンネルを設定しました。")
        else:
            self.bot.cursor.execute(
                f"delete from gban_settings where id = ?", (ctx.guild.id,))
            await ctx.send("グローバルBANの利用、送信先チャンネルを解除しました。")

    @commands.Cog.listener()
    async def on_member_join(self, m):
        self.bot.cursor.execute("select * from gban_dates where id=?", (m.id,))
        gbaninfo = self.bot.cursor.fetchone()
        if gbaninfo:
            u = await self.bot.fetch_user(gbaninfo["id"])
            by = await self.bot.fetch_user(gbaninfo["gban_by"])
            self.bot.cursor.execute(
                "select * from gban_settings where id=?", (m.guild.id,))
            gs = self.bot.cursor.fetchone()
            g = m.guild
            ch = g.get_channel(gs["chid"])
            if g:
                try:
                    await g.ban(u, reason=f"思惟奈ちゃんグローバルBAN:{gbaninfo['reason']}(実行者:{by}({by.id}))")
                except:
                    await ch.send(embed=ut.getEmbed("グローバルBANに基づく、BANの試行", f"{u}({u.id})は、`{gbaninfo['reason']}`として思惟奈ちゃんのグローバルBANを受けています。\nBANしようとしましたが、権限不足等の理由でBANできませんでした。\nグローバルBAN実行者:{by}({by.id})"))
                finally:
                    await ch.send(embed=ut.getEmbed("グローバルBANに基づく、BANの実行", f"{u}({u.id})は、`{gbaninfo['reason']}`として思惟奈ちゃんのグローバルBANを受けています。\nよって、このサーバーからBANを行いました。\nグローバルBAN実行者:{by}({by.id})"))


def setup(bot):
    bot.add_cog(m10s_gban(bot))
