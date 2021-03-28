# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from typing import Union

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

メモ:
unknown = -1
playing = 0
streaming = 1
listening = 2
watching = 3
custom = 4
competing = 5

bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS actrole_optin(id integer PRIMARY KEY NOT NULL, is_enable integer NOT NULL default 0);")

self.bot.cursor.execute("INSERT INTO activity_roles(guild_id,activity_type,role_id) VALUES(?,?,?)",(ctx.guild.id,act_id,role_id))


self.bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS activity_roles(guild_id integer PRIMARY KEY NOT NULL,activity_type integer NOT NULL,role_id integer);")

self.bot.cursor.execute("UPDATE activity_roles SET role_id = ? WHERE guild_id = ? AND activity_type = ?",(role_id,ctx.guild.id,act_id))

self.bot.cursor.execute("select * from activity_roles where guild_id = ? AND activity_type = ?", (ctx.guild.id,act_id))
            gpf = self.bot.cursor.fetchone()
"""

class m10s_act_role(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cvtdict = {
            "unknown":-1,
            "playing":0,
            "streaming":1,
            "listening":2,
            "watching":3,
            "custom":4,
            "competing":5
        }

    @commands.command(name="activrole")
    async def actrole_set(self, ctx, is_enable=True):
        self.bot.cursor.execute("UPDATE actrole_optin SET is_enable = ? WHERE id = ?",(int(is_enable),ctx.author.id))
        await ctx.reply(f"プレイ中に応じた役職設定を、{is_enable}に設定したよ！")

    @commands.command(name="prole")
    async def playing_roles(self, ctx, activity_type:str, role_id:Union[int,None]):
        try:
            act_id = self.cvtdict.get(activity_type,None)
            if act_id is None:
                try:
                    await ctx.reply("> エラー\n　アクティビティタイプが不明です。`s-help prole`を参考にしてください。")
                except:
                    await ctx.send("> エラー\n　アクティビティタイプが不明です。`s-help prole`を参考にしてください。")
            else:
                self.bot.cursor.execute("select * from activity_roles where guild_id = ? AND activity_type = ?", (ctx.guild.id,act_id))
                rtn = self.bot.cursor.fetchone()
                if rtn:
                    if role_id:
                        self.bot.cursor.execute("UPDATE activity_roles SET role_id = ? WHERE guild_id = ? AND activity_type = ?",(role_id,ctx.guild.id,act_id))
                    else:
                        self.bot.cursor.execute("DELETE FROM activity_roles WHERE guild_id = ? AND activity_type = ?",(ctx.guild.id,act_id))
                else:
                    if role_id:
                        self.bot.cursor.execute("INSERT INTO activity_roles(guild_id,activity_type,role_id) VALUES(?,?,?)",(ctx.guild.id,act_id,role_id))
                try:
                    await ctx.reply("> アクティビティロール\n　正常に登録/更新/削除が完了しました。")
                except:
                    await ctx.send("> アクティビティロール\n　正常に登録/更新/削除が完了しました。")
        except Exception as e:
            await ctx.send(f"```{e}```")


    @commands.Cog.listener()
    async def on_member_update(self, b,a):
        try:
            self.bot.cursor.execute("select * from actrole_optin where id = ?", (b.id,))
            gpf = self.bot.cursor.fetchone()
            if gpf and gpf["is_enable"] == 1:
                if not b.activity == a.activity:
                    if b.activity and (a.activity is None):
                        bact = self.bot.cursor.execute("select role_id from activity_roles where guild_id = ? AND activity_type = ?", (b.guild.id,int(b.activity.type))).fetchone()
                        await b.remove_roles(b.guild.get_role(bact["role_id"]))
                    elif (b.activity is None) and a.activity:
                        aact = self.bot.cursor.execute("select role_id from activity_roles where guild_id = ? AND activity_type = ?", (a.guild.id,int(a.activity.type))).fetchone()
                        await a.add_roles(a.guild.get_role(aact["role_id"]))
                    elif b.activity and a.activity:
                        bact = self.bot.cursor.execute("select role_id from activity_roles where guild_id = ? AND activity_type = ?", (b.guild.id,int(b.activity.type))).fetchone()
                        await b.remove_roles(b.guild.get_role(bact["role_id"]))
                        aact = self.bot.cursor.execute("select role_id from activity_roles where guild_id = ? AND activity_type = ?", (a.guild.id,int(a.activity.type))).fetchone()
                        await a.add_roles(a.guild.get_role(aact["role_id"]))
        except:
            pass

def setup(bot):
    bot.add_cog(m10s_act_role(bot))
