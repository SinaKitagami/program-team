# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import re

import m10s_util as ut
"""↑様々な便利コマンド詰め合わせ
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


class m10s_role_panel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.e_check = self.bot.get_emoji(653161518103265291)

    @commands.command(name="paneledit")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True,manage_roles=True)
    async def _setting(self, ctx, mid=None, *reactions):
        if mid is None:
            m = await ctx.send("> パネル発行の確認\nこのチャンネルにパネルを発行してもよろしいですか？")
            await m.add_reaction(self.e_check)
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id)
            except asyncio.TimeoutError:
                await m.edit("> パネルは発行されていません！\n時間内に応答がなかったため、作成はキャンセルされました。")
            else:
                if r.emoji == self.e_check:
                    pd={}
                    pm = await ctx.send(embed=discord.Embed())
                    await pm.edit(embed=ut.getEmbed("思惟奈ちゃん役職パネル",f"made by {ctx.author.mention}",self.bot.ec,f"内容の変更は`s-paneledit {pm.id} (絵文字と役職idをスペース区切りで繰り返す)`"))
                    self.bot.cursor.execute("INSERT INTO role_panels(id,roles) VALUES(?,?)", (pm.id,pd))
                else:
                    await m.edit("> パネルは発行されていません！\n作成はキャンセルされました。")
        else:
            try:
                mid = int(mid)
            except:
                await ctx.send("> メッセージIDが数字ではありません！")
                return
            if self.bot.cursor.execute("select * from role_panels where id = ?",(mid,)).fetchone():
                await ctx.send("該当のパネルを上書きます。")
                emotes = reactions[::2]
                rids = reactions[1::2]
                pd={}
                for i in range(len(emotes)):
                    pd[emotes[i]] = rids[i]
                rt = []
                for i in reactions:
                    try:
                        i = int(i)
                    except:
                        rt.append(str(i))
                    else:
                        try:
                            rt.append(ctx.guild.get_role(i).mention)
                        except:
                            await ctx.send("パネルの上書きに失敗しました。")
                            return
                try:
                    msg = await ctx.channel.fetch_message(mid)
                except:
                    await ctx.send("> パネルが見つかりません\nパネルのあるチャンネルで更新を行ってください。削除されている場合は再発行してください。")
                else:
                    for i in emotes:
                        try:
                            await msg.add_reaction(i)
                        except Exception as e:
                            try:
                                eid = re.match(
                                    "<:[a-zA-Z0-9_-]+:([0-9]+)>", i).group(1)
                                ej = self.bot.get_emoji(int(eid))
                                await msg.add_reaction(ej)
                            except:
                                await ctx.send("付与できていないリアクションがあります。該当の役職はリアクションでの付与ができません。")
                    await msg.edit(embed=ut.getEmbed("思惟奈ちゃん役職パネル",f"made by {ctx.author.mention}",self.bot.ec,*rt))
                    self.bot.cursor.execute("UPDATE role_panels SET roles = ? WHERE id = ?", (pd, mid))
            else:
                await ctx.send("> パネルが見つかりません。\nパネルではないIDが指定されています。")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self,pr):
        self.bot.cursor.execute("select roles from role_panels where id = ?",(pr.message_id,))
        rs = self.bot.cursor.fetchone()
        if rs:
            rid = rs["roles"].get(str(pr.emoji),None)
            if rid:
                g = self.bot.get_guild(pr.guild_id)
                ch = g.get_channel(pr.channel_id)
                m = await ch.fetch_message(pr.message_id)
                rl = g.get_role(int(rid))
                member = g.get_member(pr.user_id)
                await m.remove_reaction(pr.emoji,member)
                try:
                    if int(rid) in [i.id for i in member.roles]:
                        await member.remove_roles(rl)
                        await ch.send("> 役職を除去しました！",delete_after=5)
                    else:
                        await member.add_roles(rl)
                        await ch.send("> 役職を付与しました！",delete_after=5)
                except:
                    await ch.send("> 役職の付与に失敗しました",delete_after=5)
        


def setup(bot):
    bot.add_cog(m10s_role_panel(bot))
