# -*- coding: utf-8 -*-

from pydoc import describe
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import asyncio

from typing import Optional, Union

from discord import app_commands

from operator import itemgetter
import json

import m10s_util as ut

import time

import random


class levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.is_owner()
    # @ut.runnable_check()
    async def level_transfer(self, ctx):
        async with ctx.channel.typing():
            gs = await self.bot.cursor.fetchall("select * from guilds")
            for s in gs:
                ls = json.loads(s["levels"])
                for k,v in ls.items():
                    try:
                        await self.bot.cursor.execute("INSERT INTO levels(user_id,guild_id,level,exp,last_level_count,is_level_count_enable) VALUES(%s,%s,%s,%s,%s,%s)",
                                (int(k), s["id"], v["level"], v["exp"], v["lltime"], v["dlu"]))
                    except:
                        pass
        await ctx.send("完了しました")

        

    @commands.Cog.listener()
    async def on_message(self, m):
        """if not m.guild.id == 560434525277126656:
            return"""
        if not m.guild:
            return
        try:
            gs = await self.bot.cursor.fetchone("select * from guilds where id=%s", (m.guild.id,))
            if "clevel" in json.loads(gs["lockcom"]):
                return
            if m.author.bot:
                return
        except:
            pass
            
        lvl = await self.bot.cursor.fetchone("select * from levels where guild_id=%s and user_id=%s", (m.guild.id, m.author.id))
        
        if lvl:
            if lvl["is_level_count_enable"]:
                if (int(time.time())-lvl["last_level_count"]) >= 60:
                    add_exp = random.randint(5, 15)
                    w_exp = lvl["exp"] + add_exp
                    w_lvl = lvl["level"]
                    is_level_up = False
                    if w_exp >= w_lvl ** 3 + 20:
                        w_exp -= w_lvl ** 3 + 20
                        w_lvl += 1
                        is_level_up = True
                    await self.bot.cursor.execute("UPDATE levels SET level = %s, exp = %s, last_level_count = %s WHERE guild_id = %s and user_id = %s", (w_lvl, w_exp, int(time.time()), m.guild.id, m.author.id))
                    if is_level_up:
                        if gs["levelupsendto"]:
                            c = self.bot.get_channel(int(gs["levelupsendto"]))
                            try:
                                await c.send(
                                    str(self.bot.create_emoji_str('s_levelup',653161518212448266)) + await self.bot._(m.author, "levelup-notify", m.author.mention, w_lvl),
                                    allowed_mentions=discord.AllowedMentions(users=False)
                                )
                            except:
                                pass
                        else:
                            try:
                                await m.channel.send(
                                    str(self.bot.create_emoji_str('s_levelup',653161518212448266)) + await self.bot._(m.author, "levelup-notify", m.author.mention, w_lvl),
                                    allowed_mentions=discord.AllowedMentions(users=False)
                                )
                            except:
                                pass
                        try:
                            rwds = json.loads(gs["reward"])
                            if rwds.get(str(w_lvl), None):
                                rl = m.guild.get_role(rwds[str(w_lvl)])
                                await m.author.add_roles(rl)
                        except:
                            pass

            
        else:
            await self.bot.cursor.execute("INSERT INTO levels(user_id,guild_id,level,exp,last_level_count,is_level_count_enable) VALUES(%s,%s,%s,%s,%s,%s)",
                           (m.author.id, m.guild.id, 0, random.randint(5, 15), int(time.time()), 1))


    @commands.hybrid_group(name="level", description="レベル関連の機能を表示します。")
    @ut.runnable_check()
    async def level_group(self, ctx):
        pass

    @level_group.command(name="ranking", description="レベルランキングを表示します。")
    @ut.runnable_check()
    @app_commands.describe(start_rank="開始順位")
    @app_commands.describe(end_rank="終了順位")
    async def level_ranking(self, ctx, start_rank:Optional[int]=1, end_rank:Optional[int]=10):
        start = start_rank or 1
        end = end_rank or 10

        async with ctx.channel.typing():
            lvl = await self.bot.cursor.fetchall("select * from levels where guild_id=%s", (ctx.guild.id,))
            lrs = [(v["user_id"], v["level"], v["exp"])
                   for v in lvl if v["is_level_count_enable"]]
            text = ""
            lranks = [(ind, i) for ind, i in enumerate(
                sorted(lrs, key=itemgetter(1, 2), reverse=True))]
            for ind, i in lranks[start-1:end]:
                un = ctx.guild.get_member(i[0])
                if un is None:
                    un = await self.bot.fetch_user(i[0])
                    if un is None:
                        un = f"id:`{i[0]}`"
                    else:
                        un = str(un)+f"({await ctx._('ranklev-outsideg')})"
                else:
                    un = un.mention
                if len(text+f"> {ind+1}.{un}\n　level:{i[1]},exp:{i[2]}\n") <= 2036:
                    text = text + f"> {ind+1}.{un}\n　level:{i[1]},exp:{i[2]}\n"
                else:
                    text = text+f"({await ctx._('ranklev-lenover')})"
                    break
            e = discord.Embed(title=await ctx._("ranklev-title"),
                              description=text, color=self.bot.ec)
        await ctx.send(embed=e)

    @level_group.command(name="card_edit", description="レベルカードを変更します。")
    @ut.runnable_check()
    @app_commands.choices(number=[
        app_commands.Choice(name="kazuta123_1",value=0),
        app_commands.Choice(name="kazuta123_2",value=1),
        app_commands.Choice(name="kazuta123_3",value=6),
        app_commands.Choice(name="m@ji☆(デフォルト)",value=2),
        app_commands.Choice(name="tomohiro0405",value=3),
        app_commands.Choice(name="氷河",value=4),
        app_commands.Choice(name="雪銀 翔",value=5)
    ])
    @app_commands.describe(number="変更するレベルカード")
    async def switchlevelcard(self, ctx, number: int=None):
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        cn = ["kazuta123-a", "kazuta123-b", "m@ji☆",
              "tomohiro0405", "氷河", "雪銀　翔", "kazuta123-c"]
        if number is None:
            await ctx.send(await ctx._("slc-your", upf["levcard"].replace("-a", "").replace("-b", "").replace("-c", "")))
        else:
            if 1 <= number <= 6:
                await ctx.send(await ctx._("slc-set", number, cn[number-1].replace("-a", "").replace("-b", "").replace("-c", "")))
                await self.bot.cursor.execute(
                    "UPDATE users SET levcard = %s WHERE id = %s", (cn[number-1], ctx.author.id))
            else:
                await ctx.send(await ctx._("slc-numb"))
    
    @level_group.command(name="toggle_level_count", aliases=["switchlevelup","switchLevelup"], description="レベルカウントを切り替えます")
    @ut.runnable_check()
    async def switchlevelup(self, ctx):
        lvl = await self.bot.cursor.fetchone("select * from levels where guild_id=%s and user_id=%s", (ctx.guild.id, ctx.author.id))

        if lvl["is_level_count_enable"]:
            act = False
            await ctx.send(await ctx._("sLu-off"))
        else:
            act = True
            await ctx.send(await ctx._("sLu-on"))
        await self.bot.cursor.execute(
            "UPDATE levels SET is_level_count_enable = %s WHERE guild_id = %s and user_id = %s", (act, ctx.guild.id, ctx.author.id))

    @level_group.command(name="card", description="レベルカードを表示します。")
    @ut.runnable_check()
    @commands.cooldown(1, 20, type=commands.BucketType.user)
    @commands.bot_has_permissions(attach_files=True)
    async def level(self, ctx: commands.Context, tu: Optional[discord.Member]):
        if ctx.interaction:
            await ctx.defer()
        if tu:
            u = tu
        else:
            u = ctx.author
        LEVEL_FONT = "meiryo.ttc"

        headers = {
            "User-Agent": "DiscordBot (sina-chan with discord.py)",
            "Authorization": f"Bot {self.bot.http.token}"
        }
        async with self.bot.session.get(f"https://discord.com/api/v10/users/{u.id}", headers=headers) as resp:
            resp.raise_for_status()
            ucb = await resp.json()

        if ctx.channel.permissions_for(ctx.guild.me).attach_files is True:
            lvl = await self.bot.cursor.fetchone("select * from levels where guild_id=%s and user_id=%s", (u.guild.id, u.id))
            if lvl:
                async with ctx.message.channel.typing():
                    nowl = lvl['level']
                    exp = lvl['exp']
                    nextl = nowl ** 3 + 20
                    tonextexp = nextl - exp
                    nextl = str(nextl)
                    tonextexp = str(tonextexp)
                    try:
                        await u.display_avatar.replace(static_format="png").save("imgs/usericon.png")
                        dlicon = Image.open('imgs/usericon.png', 'r')
                    except:
                        dlicon = Image.open('imgs/noimg.png', 'r')
                    dlicon = dlicon.resize((100, 100))
                    cv = None
                    if ucb["banner"]:
                        cb = "banner"
                        banner_url = f'https://cdn.discordapp.com/banners/{u.id}/{ucb["banner"]}.png?size=640'
                        async with self.bot.session.get(banner_url, headers=headers) as resp:
                            resp.raise_for_status()
                            bt = await resp.read()
                            with open(f"imgs/custom_banner_{u.id}.png", mode="wb")as f:
                                f.write(bt)
                        cv = Image.open(f"imgs/custom_banner_{u.id}.png", 'r')
                        cv = cv.resize((640, 235))
                    else:
                        c = await self.bot.cursor.fetchone(
                            "select * from users where id=%s", (u.id,))
                        #c = await self.bot.cursor.fetchone()
                        cb = c["levcard"] or "m@ji☆"
                        cv = Image.open('imgs/'+cb+'.png', 'r') 
                    cv.paste(dlicon, (200, 10))
                    dt = ImageDraw.Draw(cv)
                    fonta = ImageFont.truetype(LEVEL_FONT, 30)
                    fontb = ImageFont.truetype(LEVEL_FONT, 42)
                    fontc = ImageFont.truetype(LEVEL_FONT, 20)
                    if len(u.display_name) > 11:
                        etc = "…"
                    else:
                        etc = ""
                    if cb == "kazuta123-a" or cb == "kazuta123-b" or cb == "kazuta123-c" or cb == "tomohiro0405":
                        dt.text(
                            (300, 60), u.display_name[0:10] + etc, font=fonta, fill='#ffffff')

                        dt.text((50, 110), await ctx.l10n(
                            u, "lc-level")+str(nowl), font=fontb, fill='#ffffff')

                        dt.text((50, 170), await ctx.l10n(
                            u, "lc-exp") + str(exp)+"/"+nextl, font=fonta, fill='#ffffff')

                        dt.text((50, 210), await ctx.l10n(u, "lc-next") +
                                tonextexp, font=fontc, fill='#ffffff')
                        
                        if cb != "banner":
                            dt.text((50, 300), await ctx.l10n(u, "lc-createdby", cb.replace("m@ji☆", "おあず").replace("kazuta123", "kazuta246").replace("-a", "").replace("-b", "").replace("-c", "")), font=fontc, fill='#ffffff')
                    else:
                        dt.text(
                            (300, 60), u.display_name[0:10] + etc, font=fonta, fill='#000000')

                        dt.text((50, 110), await ctx.l10n(
                            u, "lc-level")+str(nowl), font=fontb, fill='#000000')

                        dt.text((50, 170), await ctx.l10n(
                            u, "lc-exp") + str(exp)+"/"+nextl, font=fonta, fill='#000000')

                        dt.text((50, 210), await ctx.l10n(u, "lc-next") +
                                tonextexp, font=fontc, fill='#000000')

                        if cb != "banner":
                            dt.text((50, 300), await ctx.l10n(u, "lc-createdby", cb.replace("m@ji☆", "おあず").replace("kazuta123", "kazuta246").replace("-a", "").replace("-b", "").replace("-c", "")), font=fontc, fill='#000000')

                    cv.save("imgs/sina'slevelcard.png", 'PNG')
                await ctx.send(file=discord.File("imgs/sina'slevelcard.png"))
            else:
                await ctx.send(await ctx._("level-notcount"))
                
        else:
            try:
                await ctx.send(embed=discord.Embed(title=await ctx._("dhaveper"), description=await ctx._("per-sendfile")))
            except:
                await ctx.send(f"{await ctx._('dhaveper')}\n{await ctx._('per-sendfile')}")

    @commands.hybrid_group(name="level_reward", description="レベルに応じた役職付与の設定です。")
    @ut.runnable_check()
    @commands.has_permissions(administrator=True)
    async def reward_cmds(self, ctx):
        pass
    
    @reward_cmds.command(name="sync", description="レベル役職を同期します。設定後に実行してください。")
    @ut.runnable_check()
    async def lrewardupd(self, ctx):
        async with ctx.channel.typing():
            gs = await self.bot.cursor.fetchone(
                "select * from guilds where id=%s", (ctx.guild.id,))
            #gs = await self.bot.cursor.fetchone()
            lvls = await self.bot.cursor.fetchall("select * from levels where guild_id=%s", (ctx.guild.id,))
            rewards = json.loads(gs["reward"])
            rslt = {}
            for lvl in lvls:
                u = ctx.guild.get_member(lvl["user_id"])
                for k, v in rewards.items():
                    if int(k) <= lvl["level"]:
                        try:
                            rl = ctx.message.guild.get_role(v)
                            await u.add_roles(rl)
                            if rslt[k]:
                                rslt[k].append(u.display_name)
                            else:
                                rslt[k] = [u.display_name]
                            await asyncio.sleep(0.2)
                        except:
                            pass
        await ctx.send("完了しました。", embed=ut.getEmbed("追加者一覧", f"```{','.join([f'レベル{k}:{v}'] for k,v in rslt.items())}```"))

    @reward_cmds.command(name="set", description="レベルに応じた役職を設定できます。")
    @ut.runnable_check()
    async def levelreward(self, ctx, lv: int, rl:Optional[discord.Role]):
        if not(ctx.channel.permissions_for(ctx.author).manage_guild is True and ctx.channel.permissions_for(ctx.author).manage_roles is True or ctx.author.id == 404243934210949120):
            await ctx.send(await ctx._("need-admin"))
            return
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #gs = await self.bot.cursor.fetchone()
        rewards = json.loads(gs["reward"])
        if rl is None:
            del rewards[str(lv)]
        else:
            rid = rl.id
            rewards[str(lv)] = rid
        await self.bot.cursor.execute(
            "UPDATE guilds SET reward = %s WHERE id = %s", (json.dumps(rewards), ctx.guild.id))
        await ctx.send(await ctx._("changed"))

    @commands.hybrid_group(name="level_edit", description="サーバーレベルを変更できます。")
    @commands.has_permissions(administrator=True)
    @ut.runnable_check()
    async def edit_level(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.reply("> サーバーレベル編集\n　`[user/role] add [メンバーor役職を特定できるもの] [追加するレベル] [オプション:追加する経験値]`:追加/減少\n　`[user/role] set [メンバーor役職を特定できるもの] [設定するレベル] [オプション:設定する経験値]`:設定")

    @edit_level.group(name="user", description="ユーザーに関して設定を変更します。")
    @ut.runnable_check()
    async def group_user(self,ctx):
        pass

    @edit_level.group(name="role", description="ロールに関して設定を変更します。")
    @ut.runnable_check()
    async def group_role(self,ctx):
        pass

    @group_user.command(name="add", description="ユーザーレベルに、特定の値を加算します。")
    @ut.runnable_check()
    async def user_add(self, ctx, target:discord.User, lev:int, exp:Optional[int]=0):
        await level_add(self, ctx, target, lev, exp)

    @group_user.command(name="set", description="ユーザーレベルを、特定の値に設定します。")
    @ut.runnable_check()
    async def user_set(self, ctx, target:discord.User, lev:int, exp:Optional[int]=0):
        await level_set(self, ctx, target, lev, exp)

    @group_role.command(name="add", description="そのロールを持つメンバーのレベルに、特定の値を加算します。")
    @ut.runnable_check()
    async def role_add(self, ctx, target:discord.Role, lev:int, exp:Optional[int]=0):
        await level_add(self,ctx, target, lev, exp)

    @group_role.command(name="set", description="そのロールを持つメンバーのレベルを、特定の値に設定します。")
    @ut.runnable_check()
    async def role_set(self, ctx, target:discord.Role, lev:int, exp:Optional[int]=0):
        await level_set(self, ctx, target, lev, exp)


async def level_add(self, ctx, target:Union[commands.MemberConverter,commands.UserConverter,commands.RoleConverter], lev:int, exp:Optional[int]=0):
    if isinstance(target,discord.Member) or isinstance(target,discord.User):
        targets = [target]
    elif isinstance(target,discord.Role):
        targets = target.members
    else:
        return await ctx.reply("> サーバーレベル編集-追加\n　引数が正しくありません。\n　`[メンバーor役職を特定できるもの] [追加するレベル] [オプション:追加する経験値]`")
    for m in targets:
        lvl = await self.bot.cursor.fetchone("select * from levels where guild_id=%s and user_id=%s", (ctx.guild.id, m.id))
        if lvl:
            await self.bot.cursor.execute("UPDATE levels SET level = %s, exp = %s WHERE guild_id = %s and user_id = %s", (lvl["level"] + lev, lvl["exp"] + exp, ctx.guild.id, m.id))
        else:
            await self.bot.cursor.execute("INSERT INTO levels(user_id, guild_id, level, exp, last_level_count, is_level_count_enable) VALUE (%s, %s, %s, %s, %s, %s)", (m.id, ctx.guild.id, lev, exp, int(time.time()), 1))
    await ctx.reply(f"> サーバーレベル編集\n　{len(targets)}人のレベルを編集しました。(レベルがないメンバーには干渉していません。)")

async def level_set(self, ctx, target:Union[commands.MemberConverter,commands.UserConverter,commands.RoleConverter], lev:int, exp:Optional[int]=0):
    if isinstance(target,discord.Member) or isinstance(target,discord.User):
        targets = [target]
    elif isinstance(target,discord.Role):
        targets = target.members
    else:
        return await ctx.reply("> サーバーレベル編集-設定\n　引数が正しくありません。\n　`[メンバーor役職を特定できるもの] [設定するレベル] [オプション:設定する経験値]`")
    for m in targets:
        lvl = await self.bot.cursor.fetchone("select * from levels where guild_id=%s and user_id=%s", (ctx.guild.id, m.id))
        if lvl:
            await self.bot.cursor.execute("UPDATE levels SET level = %s, exp = %s WHERE guild_id = %s and user_id = %s", (lev, exp, ctx.guild.id, m.id))
        else:
            await self.bot.cursor.execute("INSERT INTO levels(user_id, guild_id, level, exp, last_level_count, is_level_count_enable) VALUE (%s, %s, %s, %s, %s, %s)", (m.id, ctx.guild.id, lev, exp, int(time.time()), 1))

    await ctx.reply(f"> サーバーレベル編集\n　{len(targets)}人のレベルを設定しました。(レベルがないメンバーには干渉していません。)")


async def setup(bot):
    await bot.add_cog(levels(bot))
