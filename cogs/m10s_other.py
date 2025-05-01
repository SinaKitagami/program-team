# -*- coding: utf-8 -*-

from typing import Optional
import discord
from discord.ext import commands
import random
import time
import asyncio
import platform
import re
import psutil
import json

from discord import app_commands

import m10s_util as ut


class other(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="support_server", description="思惟奈ちゃんサポートサーバーのURLを表示します。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def sinaguild(self, ctx):
        await ctx.send("サポートサーバー → https://discord.gg/vtn2V3v")

    @commands.command(aliases=["r", "返信", "引用"])
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def reply(self, ctx, id: int, *, text):

        m = await ctx.channel.fetch_message(id)
        e = discord.Embed(description=text, color=self.bot.ec)
        e.add_field(name=f"引用投稿(引用された投稿の送信者:{m.author.display_name})",
                    value=f"{m.content}\n[{self.bot.create_emoji_str('s_link_jump',653161518451392512)} この投稿に飛ぶ]({m.jump_url})")
        e.set_author(name=ctx.author.display_name,
                     icon_url=ctx.author.display_avatar.replace(static_format='png'))
        await ctx.send(embed=e)
        await ctx.message.delete()


    @commands.command(aliases=["アンケート", "次のアンケートを開いて"])
    @ut.runnable_check()
    async def q(self, ctx, title=None, *ctt):

        if title is None or ctt == []:
            await ctx.send(await ctx._("q-not"))
        else:
            ky = None
            dct = {}
            for tmp in ctt:
                if ky is None:
                    ky = tmp
                else:
                    dct[ky] = tmp
                    ky = None
            itm = ""
            for k, v in dct.items():
                if itm == "":
                    itm = f"{k}:{v}"
                else:
                    itm = itm + f"\n{k}:{v}"
            embed = discord.Embed(title=title, description=itm)
            qes = await ctx.send(embed=embed)

            for k in ctt[::2]:
                try:
                    await qes.add_reaction(k)
                except Exception as e:
                    try:
                        eid = re.match(
                            "<:[a-zA-Z0-9_-]+:([0-9]+)>", k).group(1)
                        ej = self.bot.get_emoji(int(eid))
                        await qes.add_reaction(ej)
                    except:
                        await qes.delete()
                        await ctx.send(await ctx._("q-error"))

    @commands.command(aliases=["クレジット", "クレジットを見せて"])
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def credit(self, ctx):
        await ctx.send(await ctx._("credit"))

    @commands.command()
    @ut.runnable_check()
    async def allonline(self, ctx, mus=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if mus is None:
            info = ctx.message.author
        else:
            if ctx.message.mentions:
                info = ctx.message.mentions[0]
            else:
                info = ctx.guild.get_member(int(mus))
            if not await self.bot.can_use_online(info):
                return await ctx.say("cannot-send-online")
            if not self.bot.shares_guild(info.id, ctx.author.id):
                return await ctx.say("cannot-send-online")
        await ctx.send(f"Status:{str(info.status)}(PC:{str(info.desktop_status)},Mobile:{str(info.mobile_status)},Web:{str(info.web_status)})")

    @commands.hybrid_command(aliases=["ステータス", "あなたの情報を教えて"], description="思惟奈ちゃんについての色々を表示します。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def botinfo(self, ctx):
        mem = psutil.virtual_memory()
        allmem = str(mem.total/1000000000)[0:3]
        used = str(mem.used/1000000000)[0:3]
        ava = str(mem.available/1000000000)[0:3]
        memparcent = mem.percent
        embed = discord.Embed(title=await ctx._(
            "status-inserver"), description=f"{len(self.bot.guilds)}", color=self.bot.ec)
        embed.add_field(name=await ctx._("status-prefix"), value="s-")
        embed.add_field(name=await ctx._("status-starttime"), value=self.bot.StartTime.strftime(
            '%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))
        embed.add_field(name=await ctx._("status-ver"),
                        value=platform.python_version())
        embed.add_field(name=await ctx._("status-pros"), value=platform.processor())
        embed.add_field(name=await ctx._(
            "status-os"), value=f"{platform.system()} {platform.release()}({platform.version()})")
        embed.add_field(
            name="メモリ", value=f"全てのメモリ容量:{allmem}GB\n使用量:{used}GB({memparcent}%)\n空き容量{ava}GB({100-memparcent}%)")
        embed.add_field(name="シャード内ユーザー数", value=len(self.bot.users))
        embed.add_field(name="シャード内チャンネル数", value=len(
            [i for i in self.bot.get_all_channels()]))
        embed.add_field(name="シャードステータス", value=f"このサーバーのシャード番号:{self.bot.shard_id}(全{self.bot.shard_count}個)")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="return_text",aliases=["rt"], description="オウム返しします。")
    @app_commands.describe(te="オウム返しするテキスト")
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    @app_commands.checks.cooldown(1, 5)
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def rettext(self, ctx:commands.Context, *, te):
        e=discord.Embed(color=self.bot.ec)
        e.set_footer(text=f"requested by {ctx.author.nick or ctx.author}({ctx.author.id})",icon_url=ctx.author.display_avatar.replace(static_format="png").url)
        if ctx.interaction:
            await ctx.send(te, allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send(te, embed=e, allowed_mentions=discord.AllowedMentions.none())
            await ctx.message.delete()

    @commands.hybrid_command(name="emoji_reaction",description="絵文字に応じたリアクションをとります。(一部絵文字のみ対応。存在しないものは運営に自動送信されて、いつか増えます。)")
    @app_commands.describe(emoji="絵文字")
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    @app_commands.checks.cooldown(1, 5)
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def eatit(self, ctx, emoji:str):
        it = emoji.replace(" ","")
        if await ctx.user_lang() == "ja":
            if await ctx._(f"er-{it}") == "":
                await ctx.send(await ctx._("er-?"))
                await (await self.bot.fetch_channel(993565802030698627)).send(f"> 思惟奈のわからない絵文字があったよ。`{str(emoji)}`")
            else:
                await ctx.send(await ctx._(f"er-{it}"))
        else:
            await ctx.send(await ctx._("cannot-run"))


    @commands.command(name="randomint", aliases=["randint", "乱数", "次の条件で乱数を作って"])
    @ut.runnable_check()
    async def randomint(self, ctx, *args):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if len(args) == 1:
            s = 1
            e = 6
            c = int(args[0])
        elif len(args) == 2:
            s = int(args[0])
            e = int(args[1])
            c = 1
        elif len(args) == 3:
            s = int(args[0])
            e = int(args[1])
            c = int(args[2])
        else:
            await ctx.send(await ctx._("randomint-arg-error"))
            return
        # try:
        intcount = []
        rnd = 0
        if c >= 256:
            c = 255
        for i in range(c):
            if s <= e:
                tmp = random.randint(s, e)
                intcount = intcount + [tmp]
                rnd = rnd + tmp
            else:
                tmp = random.randint(e, s)
                intcount = intcount + [tmp]
                rnd = rnd + tmp
        await ctx.send(await ctx._("randomint-return1", str(s), str(e), str(c), str(rnd), str(intcount)))
        # except:
        # await ctx.send(await ctx._("randomint-return2"))

    @commands.hybrid_command(name="fortune", aliases=["おみくじ", "今日のおみくじをひく"], description="おみくじです。一日に何度でも引けます。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def fortune(self, ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        rnd = random.randint(0, 6)
        await ctx.send(await ctx._("omikuzi-return", await ctx._("omikuzi-"+str(rnd))))

    @commands.hybrid_command(description="簡易メモ機能。音楽機能のプレイリストも兼ねています。(各行に1URLでプレイリスト扱い)")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @discord.app_commands.choices(mode=[
            discord.app_commands.Choice(name="read_a_memo", value=0),
            discord.app_commands.Choice(name="write", value=1),
            discord.app_commands.Choice(name="check_all_memo", value=2),
        ])
    @app_commands.describe(mode="メモのモード")
    @app_commands.describe(memo_name="メモの名前")
    @app_commands.describe(memo_content="メモに書き込む内容")
    async def memo(self, ctx:commands.Context, mode:int, memo_name:Optional[str]="default", *, memo_content:Optional[str]):
        mn = memo_name
        ctt = memo_content
        mmj = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #mmj = await self.bot.cursor.fetchone()
        memos = json.loads(mmj["memo"])
        if mode == 0:
            if not memos is None:
                if memos.get(mn) is None:
                    await ctx.send(await ctx._("memo-r-notfound1"), ephemeral=True)
                else:
                    await ctx.send(memos[mn].replace("@everyone", "everyone").replace("@here", "here"), ephemeral=True)
            else:
                await ctx.send(await ctx._("memo-r-notfound2"), ephemeral=True)
        elif mode == 1:
            if ctt is None:
                memos[mn] = None
            else:
                memos[mn] = ctt
            await self.bot.cursor.execute(
                "UPDATE users SET memo = %s WHERE id = %s", (json.dumps(memos), ctx.author.id))

            await ctx.send(await ctx._("memo-w-write", str(mn).replace("@everyone", "everyone").replace("@here", "here")), ephemeral=True)
        elif mode == 2:
            if memos == {}:
                await ctx.send(await ctx._("memo-a-notfound"), ephemeral=True)
            else:
                await ctx.send(str(memos.keys()).replace("dict_keys(", await ctx._("memo-a-list")).replace(")", ""), ephemeral=True)
        else:
            await ctx.send(await ctx._("memo-except"), ephemeral=True)

    @commands.hybrid_command(name="create_random_group", description="ランダムなグループ分けを行えます。")
    @app_commands.describe(cou="1グループあたりの人数")
    @app_commands.describe(role="グループ分けするロール")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def rg(self, ctx, cou: int, role: Optional[discord.Role]):

        if role is None:
            role = ctx.guild.default_role
        if cou >= 1:
            ml = [m.mention for m in role.members if not m.bot]
            ogl = []
            gl = []
            tmp = "hoge"
            while len(ml) >= cou:
                for i in range(cou):
                    tmp = random.choice(ml)
                    ogl.append(tmp)
                    ml.remove(tmp)
                gl.append(ogl)
                ogl = []
                tmp = "hoge"
            gtxt = "\n".join([f"{'、'.join(m)}" for m in gl])
            ng = ",".join(ml)
            await ctx.send(embed=discord.Embed(title=await ctx._("rg-title"), description=await ctx._("rg-desc", gtxt, ng), color=self.bot.ec))
        else:
            await ctx.send(await ctx._("rg-block"))


async def setup(bot):
    await bot.add_cog(other(bot))