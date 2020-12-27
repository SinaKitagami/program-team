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

    @commands.group(name="rolepanel",aliases=["paneledit"])
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True,manage_roles=True)
    async def role_panel(self, ctx:commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("""> 役職パネル機能　
            `create`:このチャンネルに役職パネルを作成します。
            `add [(このチャンネルにある)パネルID] [絵文字] [役職が特定できるもの]`:パネルに役職を追加します。
            `remove [(このチャンネルにある)パネルID] [絵文字]`:パネルから役職を取り除きます。
            `delete [(このチャンネルにある)パネルID]`:該当パネルを削除します。
            """)

    @role_panel.command(name="create")
    async def p_create(self,ctx):
        m = await ctx.send("> パネル発行の確認\nこのチャンネルにパネルを発行してもよろしいですか？")
        await m.add_reaction(self.e_check)
        try:
            r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id)
        except asyncio.TimeoutError:
            await m.edit(content="> パネルは発行されていません！\n時間内に応答がなかったため、作成はキャンセルされました。")
        else:
            if r.emoji == self.e_check:
                pd={}
                pm = await ctx.send(embed=discord.Embed())
                await pm.edit(embed=ut.getEmbed("思惟奈ちゃん役職パネル",f"このパネルは{ctx.author.mention}によって作成されました。",self.bot.ec,f"内容の変更は`s-paneledit {pm.id} (絵文字と役職idをスペース区切りで繰り返す)`"))
                self.bot.cursor.execute("INSERT INTO role_panels(id,roles) VALUES(?,?)", (pm.id,pd))
                await m.edit(content=f"> パネルを発行しました！\n　パネルのIDは`{pm.id}`です。編集や削除時に使用します。(紛失時はパネルのメッセージIDを取り出してください。)")
            else:
                await m.edit(content="> パネルは発行されていません！\n作成はキャンセルされました。")
        
    @role_panel.command(name="delete")
    async def p_delete(self,ctx,pid):
        try:
            pid = int(pid)
        except:
            await ctx.send("> パネルIDが数字ではありません！")
            return
        if self.bot.cursor.execute("select * from role_panels where id = ?",(pid,)).fetchone():

            m = await ctx.send("> パネル削除の確認\n該当パネルを削除してもよろしいですか？")
            await m.add_reaction(self.e_check)
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id)
            except asyncio.TimeoutError:
                await m.edit(content="> パネルは削除されていません！\n時間内に応答がなかったため、削除はキャンセルされました。")
            else:
                if r.emoji == self.e_check:
                    self.bot.cursor.execute("DELETE FROM role_panels WHERE id == ?", (pid,))
                    try:
                        msg = await ctx.channel.fetch_mesasge(pid)
                        await msg.delete()
                    except:
                        pass
                    await m.edit(content="> 役職パネル\n　削除が完了しました。")
                else:
                    await m.edit(content="> パネルは削除されていません！\n削除はキャンセルされました。")


    @role_panel.command(name="add")
    async def p_add(self,ctx,pid,emoji,role:commands.RoleConverter):
        try:
            pid = int(pid)
            pmsg = await ctx.channel.fetch_message(pid)
        except:
            await ctx.send("> パネルIDが数字ではない、またはパネルがこのチャンネルに見つかりません。")
            return
        pd = self.bot.cursor.execute("select * from role_panels where id = ?",(pid,)).fetchone()
        if pd:
            pj = pd["roles"]
            if pj.get(str(emoji),None) is None:
                pj[str(emoji)] = role.id
                try:
                    self.bot.cursor.execute("UPDATE role_panels SET roles = ? WHERE id = ?", (pj, pid))
                except:await ctx.send("DB!")
                e:discord.Embed =  pmsg.embeds[0]
                e.add_field(name=str(emoji),value=role.mention)
                e.set_footer(text=f"最終更新者:{ctx.author}")
                await pmsg.edit(embed=e)

                await pmsg.clear_reactions()

                for i in pj.keys():
                    try:
                        await pmsg.add_reaction(i)
                    except Exception as e:
                        try:
                            eid = re.match(
                                "<:[a-zA-Z0-9_-]+:([0-9]+)>", i).group(1)
                            ej = self.bot.get_emoji(int(eid))
                            await pmsg.add_reaction(ej)
                        except:
                            await ctx.send("付与できていないリアクションがあります。該当の役職はリアクションでの付与ができません。")

            else:
                await ctx.send(">役職パネル\n　該当絵文字を使用した役職付与が既に存在します！")
        else:
            await ctx.send("> 役職パネル\n　該当IDのパネルがありません！")

    @role_panel.command(name="remove")
    async def p_remove(self,ctx,pid,emoji):
        try:
            pid = int(pid)
            pmsg = await ctx.channel.fetch_message(pid)
        except:
            await ctx.send("> パネルIDが数字ではない、またはパネルがこのチャンネルに見つかりません。")
            return
        pd = self.bot.cursor.execute("select * from role_panels where id = ?",(pid,)).fetchone()
        if pd:
            pj = pd["roles"]
            if pj.get(str(emoji),None):
                del pj[str(emoji)]
                self.bot.cursor.execute("UPDATE role_panels SET roles = ? WHERE id = ?", (pj, pid))
                e:discord.Embed =  pmsg.embeds[0]
                e.clear_fields()
                for k,v in pj.items():
                    rl = ctx.guild.get_role(v)
                    e.add_field(name=str(k),value=rl.mention)

                e.set_footer(text=f"最終更新者:{ctx.author}")
                await pmsg.edit(embed=e)

                await pmsg.clear_reactions()

                for i in pj.keys():
                    try:
                        await pmsg.add_reaction(i)
                    except Exception as e:
                        try:
                            eid = re.match(
                                "<:[a-zA-Z0-9_-]+:([0-9]+)>", i).group(1)
                            ej = self.bot.get_emoji(int(eid))
                            await pmsg.add_reaction(ej)
                        except:
                            await ctx.send("付与できていないリアクションがあります。該当の役職はリアクションでの付与ができません。")

            else:
                await ctx.send(">役職パネル\n　該当絵文字を使用した役職付与が既に存在します！")
        else:
            await ctx.send("> 役職パネル\n　該当IDのパネルがありません！")



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
                if member.id == self.bot.user.id:
                    return
                await m.remove_reaction(pr.emoji,member)
                try:
                    if int(rid) in [i.id for i in member.roles]:
                        await member.remove_roles(rl)
                        await ch.send(f"> {member.mention}！役職を除去しました！",delete_after=5)
                    else:
                        await member.add_roles(rl)
                        await ch.send(f"> {member.mention}！役職を付与しました！",delete_after=5)
                except:
                    await ch.send(f"> {str(pr.emoji)}での役職の付与に失敗しました。原因を見つけてパネルを修正してください。",)
        


def setup(bot):
    bot.add_cog(m10s_role_panel(bot))