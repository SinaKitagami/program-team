# -*- coding: utf-8 -*- #

from typing import Optional, Union
import discord
from discord.ext import commands, tasks
import datetime
import time

from discord import app_commands

import m10s_util as ut

import asyncio

class m10s_remainder(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.remainder_check.start()

    @commands.hybrid_group(description="リマインダー機能")
    @ut.runnable_check()
    async def remainder(self,ctx):
        pass

    @remainder.command(description="リマインダーを作成します。")
    @app_commands.describe(send_text="リマインダーの文面")
    @app_commands.describe(mention_at="メンションする役職")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def set(self,ctx,send_text:str, mention_at:Optional[discord.Role]):
        rid = int(time.time())
        if mention_at:
            mention_at = mention_at.id
        await ctx.send("> リマインダー\n　日時を`2020/12/1 22:00`の形式で入力してください。")
        m = await self.bot.wait_for("message",check=lambda m:m.author.id == ctx.message.author.id)
        try:
            ts = datetime.datetime.strptime(m.content, "%Y/%m/%d %H:%M")
        except:
            await ctx.send("> リマインダー\n　日時の指定が誤っています。もう一度やり直してください。")
            return
        await self.bot.cursor.execute("insert into remaind (id,stext,mention_role,time,chid) values (%s,%s,%s,%s,%s)", (rid, send_text, mention_at, ts.timestamp(), ctx.channel.id))
        await ctx.send(f"> リマインダー\n　{ts.strftime('%Y/%m/%d %H:%M')}にリマインダーの登録をしました。(リマインダーID:`{rid}`)")

    @remainder.command(description="リマインダーの確認をします。")
    @app_commands.describe(rid="リマインダーのID")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def check(self,ctx,rid:Optional[int]):
        if rid:
            i = await self.bot.cursor.fetchone("select * from remaind where id = %s",(int(rid),))
            #i = await self.bot.cursor.fetchone()
            if i:
                e=discord.Embed(title="リマインド情報",color=self.bot.ec)
                try:
                    e.add_field(name="メンションする役職のID",value=f"{i['mention_role'] or '(役職なし)'}")
                except:
                    pass
                e.add_field(name="time",value=f"{datetime.datetime.fromtimestamp(i['time']).strftime('%Y/%m/%d %H:%M')}")
                e.add_field(name="テキスト",value=f"{i['stext']}")
                e.add_field(name="送信先チャンネル",value=f"<#{i['chid']}>")
                await ctx.send("> リマインダー\n　該当IDのリマインドが見つかりました！",embed=e)
            else:
                await ctx.send("> リマインダー\n　該当IDのリマインドは見つかりませんでした。")
        else:
            i = await self.bot.cursor.fetchall("select * from remaind where chid = %s",(ctx.channel.id,))
            #i = await self.bot.cursor.fetchall()
            if i:
                pmax = len(i)-1
                page = 0
                
                def get_page(page):
                    e=discord.Embed(title="リマインド情報",color=self.bot.ec)
                    try:
                        e.add_field(name="メンションする役職のID",value=f"{i[page]['mention_role'] or '(役職なし)'}")
                    except:
                        pass
                    e.add_field(name="time",value=f"{datetime.datetime.fromtimestamp(i[page]['time']).strftime('%Y/%m/%d %H:%M')}")
                    e.add_field(name="テキスト",value=f"{i[page]['stext']}")
                    e.add_field(name="送信先チャンネル",value=f"<#{i[page]['chid']}>")
                    e.add_field(name="リマインダーID",value=i[page]['id'])
                    e.set_footer(text=f"page:{page+1}/{pmax+1}")
                    return e

                msg = await ctx.send(embed=get_page(page))
                await msg.add_reaction(self.bot.create_emoji_str("s_move_left",653161518195671041))
                await msg.add_reaction(self.bot.create_emoji_str('s_move_right',653161518170505216))

                while True:
                    try:
                        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
                    except:
                        break
                    try:
                        await msg.remove_reaction(r, u)
                    except:
                        pass
                    if str(r) == str(self.bot.create_emoji_str('s_move_right',653161518170505216)):
                        if page == pmax:
                            page = 0
                        else:
                            page = page + 1
                    elif str(r) == str(self.bot.create_emoji_str("s_move_left",653161518195671041)):
                        if page == 0:
                            page = pmax
                        else:
                            page = page - 1
                    await msg.edit(embed=get_page(page))
            else:
                await ctx.reply("> リマインダー\n　このチャンネルには、まだ実行時間前のリマインダーはありません。")
            

    @remainder.command(description="リマインダーを削除します。")
    @app_commands.describe(rid="リマインダーのID")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def delete(self,ctx,rid:int):
        await self.bot.cursor.execute("delete from remaind where id = %s",(rid,))
        await ctx.send("> リマインダー\n　該当IDを持ったリマインドがある場合、それを削除しました。")



    @tasks.loop(seconds=2)
    async def remainder_check(self):
        now = datetime.datetime.now()
        remainds = await self.bot.cursor.fetchall("select * from remaind")
        #remainds = await self.bot.cursor.fetchall()
        remaind_list =  [i for i in remainds if datetime.datetime.fromtimestamp(i['time'])<= now]
        for i in remaind_list:
            ch = self.bot.get_channel(i["chid"])
            try:
                role = ch.guild.get_role(i["mention_role"])
            except:
                role = None
            try:
                if ch.guild.id == 574170788165582849:
                    await ch.send(f"> リマインド {role.mention if role else ''}\n　{i['stext']}",allowed_mentions=discord.AllowedMentions(everyone=True, users=True, roles=True))
                else:
                    await ch.send(f"> リマインド {role.mention if role else ''}\n　{i['stext']}")
            except:
                print("失敗したリマインダー")
            finally:
                await self.bot.cursor.execute("delete from remaind where id = %s",(i["id"],))


async def setup(bot):
    await bot.add_cog(m10s_remainder(bot))