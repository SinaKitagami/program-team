# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from typing import Optional

from discord import app_commands

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

await self.bot.cursor.execute("INSERT INTO activity_roles(guild_id,activity_type,role_id) VALUES(%s,%s,%s)",(ctx.guild.id,act_id,role_id))


await self.bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS activity_roles(guild_id integer PRIMARY KEY NOT NULL,activity_type integer NOT NULL,role_id integer);")

await self.bot.cursor.execute("UPDATE activity_roles SET role_id = %s WHERE guild_id = %s AND activity_type = %s",(role_id,ctx.guild.id,act_id))

await self.bot.cursor.execute("select * from activity_roles where guild_id = %s AND activity_type = %s", (ctx.guild.id,act_id))
            gpf = await self.bot.cursor.fetchone()
"""

class m10s_act_role(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cvtdict = {
            -1:"unknown",
            0:"playing",
            1:"streaming",
            2:"listening",
            3:"watching",
            4:"custom",
            5:"competing"
        }

    @commands.hybrid_command(name="activity_role_setting", description="プレイ中ステータスに応じた役職付与を受け付けるかどうか")
    @app_commands.describe(is_enable="有効化するかどうか")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def actrole_set(self, ctx, is_enable:bool):
        await self.bot.cursor.execute("UPDATE actrole_optin SET is_enable = %s WHERE id = %s",(int(is_enable),ctx.author.id))
        await ctx.reply(f"プレイ中に応じた役職設定を、{is_enable}に設定したよ！")

    @commands.hybrid_command(aliases=["prole"], description="特定アクティビティタイプで付与する役職設定")
    @app_commands.describe(activity_type="検出するアクティビティタイプ")
    @app_commands.describe(role="付与するロール")
    @discord.app_commands.choices(activity_type=[
            discord.app_commands.Choice(name="unknown(不明)", value=-1),
            discord.app_commands.Choice(name="playing(プレイ中)", value=0),
            discord.app_commands.Choice(name="streaming(配信中)", value=1),
            discord.app_commands.Choice(name="listening(再生中)", value=2),
            discord.app_commands.Choice(name="watching(視聴中)", value=3),
            discord.app_commands.Choice(name="custom(カスタムステータス)", value=4),
            discord.app_commands.Choice(name="competing(競争中)", value=5)
        ])
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def playing_roles(self, ctx, activity_type:int, role:Optional[discord.Role]):
        try:
            act_id = self.cvtdict.get(activity_type,None)
            if act_id is None:
                try:
                    await ctx.reply("> エラー\n　アクティビティタイプが不明です。`s-help prole`を参考にしてください。")
                except:
                    await ctx.send("> エラー\n　アクティビティタイプが不明です。`s-help prole`を参考にしてください。")
            else:
                rtn = await self.bot.cursor.fetchone("select * from activity_roles where guild_id = %s AND activity_type = %s", (ctx.guild.id,activity_type))
                # await self.bot.cursor.execute()
                if rtn:
                    if role:
                        await self.bot.cursor.execute("UPDATE activity_roles SET role_id = %s WHERE guild_id = %s AND activity_type = %s",(role.id,ctx.guild.id,activity_type))
                    else:
                        await self.bot.cursor.execute("DELETE FROM activity_roles WHERE guild_id = %s AND activity_type = %s",(ctx.guild.id,activity_type))
                else:
                    if role:
                        await self.bot.cursor.execute("INSERT INTO activity_roles(guild_id,activity_type,role_id) VALUES(%s,%s,%s)",(ctx.guild.id,activity_type,role.id))
                try:
                    await ctx.reply("> アクティビティロール\n　正常に登録/更新/削除が完了しました。")
                except:
                    await ctx.send("> アクティビティロール\n　正常に登録/更新/削除が完了しました。")
        except Exception as e:
            await ctx.send(f"```{e}```")


    # @commands.Cog.listener()
    async def on_presence_update(self, b,a):
        try:
            gpf = await self.bot.cursor.fetchone("select * from actrole_optin where id = %s", (b.id,))
            #gpf = await self.bot.cursor.fetchone()
            if gpf and gpf["is_enable"] == 1:
                if not b.activity == a.activity:
                    if b.activity and (a.activity is None):
                        bact = await self.bot.cursor.fetchone("select role_id from activity_roles where guild_id = %s AND activity_type = %s", (b.guild.id,int(b.activity.type)))
                        #bact = await self.bot.cursor.fetchone()
                        await b.remove_roles(b.guild.get_role(bact["role_id"]))
                    elif (b.activity is None) and a.activity:
                        aact = await self.bot.cursor.fetchone("select role_id from activity_roles where guild_id = %s AND activity_type = %s", (a.guild.id,int(a.activity.type)))
                        #aact = await self.bot.cursor.fetchone()
                        await a.add_roles(a.guild.get_role(aact["role_id"]))
                    elif b.activity and a.activity:
                        bact = await self.bot.cursor.fetchone("select role_id from activity_roles where guild_id = %s AND activity_type = %s", (b.guild.id,int(b.activity.type)))
                        #bact = await self.bot.cursor.fetchone()
                        await b.remove_roles(b.guild.get_role(bact["role_id"]))
                        aact = await self.bot.cursor.fetchone("select role_id from activity_roles where guild_id = %s AND activity_type = %s", (a.guild.id,int(a.activity.type)))
                        #aact = await self.bot.cursor.fetchone()
                        await a.add_roles(a.guild.get_role(aact["role_id"]))
        except:
            pass

async def setup(bot):
    await bot.add_cog(m10s_act_role(bot))
