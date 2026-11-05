# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from dateutil.relativedelta import relativedelta as rdelta
import traceback
import m10s_util as ut
import textwrap

import config
import aiohttp

from discord import app_commands

class owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    @ut.runnable_check()
    async def dcomrun(self, ctx, cname, *, ags):
        c = ctx
        c.args = list(ags)
        try:
            await c.invoke(self.bot.get_command(cname))
        except Exception:
            await ctx.send(embed=discord.Embed(title="dcomrunエラー", description=traceback.format_exc(0)))

    @commands.command()
    @commands.is_owner()
    @ut.runnable_check()
    async def cu(self, ctx):
        await ctx.send("see you...")
        await self.bot.close()
    
    #check function
    async def is_evalable(ctx):
        if "allow_eval" in ctx.bot.features.get(ctx.author.id, []):
            return True
        else:
            return False
    
    @commands.command()
    @commands.check(is_evalable)
    @ut.runnable_check()
    async def sql(self, ctx, *, query):
        await ctx.message.add_reaction(self.bot.create_emoji_str('s_gch_sending',653161518346534912,True))
        try:
            ret = await self.bot.cursor.fetchall(query)
        except Exception as exc:
            await ctx.message.remove_reaction(self.bot.create_emoji_str('s_gch_sending',653161518346534912,True), self.bot.user)
            await ctx.message.add_reaction("❌")
            return await ctx.author.send(embed=discord.Embed(title="sql's Error", description=f"```py\n{exc}\n```", color=self.bot.ec))
        else:
            await ctx.message.remove_reaction(self.bot.create_emoji_str('s_gch_sending',653161518346534912,True), self.bot.user)
            await ctx.message.add_reaction(self.bot.create_emoji_str('s_check',653161518103265291))
            
            if ret:
                await ctx.send(f"```\n{ret}\n```")
            else:
                await ctx.send("```\nnone\n```")

    @commands.command()
    @commands.check(is_evalable)
    @ut.runnable_check()
    async def aev(self, ctx, *, cmd):
        try:
            await eval(cmd)
            await ctx.message.add_reaction(self.bot.create_emoji_str('s_check',653161518103265291))
        except Exception:
            await ctx.send(embed=discord.Embed(title="awaitEvalエラー", description=traceback.format_exc(0)))

    @commands.command(name="eval")
    @commands.check(is_evalable)
    @ut.runnable_check()
    async def eval_(self, ctx, *, cmd):
        await ctx.message.add_reaction(self.bot.create_emoji_str('s_gch_sending',653161518346534912,True))
        rt = "\n"
        if cmd.startswith("```py"):
            cmd = cmd[5:-3]
        elif cmd.startswith("```"):
            cmd = cmd[3:-3]
        elif cmd.startswith("```python"):
            cmd = cmd[9:-3]
        txt = f'async def evdf(ctx,bot):{rt}{rt.join([f" {i}" for i in cmd.split(rt)])}'
        try:
            exec(txt)
            rtn = await eval("evdf(ctx,self.bot)")
            await ctx.message.remove_reaction(self.bot.create_emoji_str('s_gch_sending',653161518346534912,True), self.bot.user)
            await ctx.message.add_reaction(self.bot.create_emoji_str('s_check',653161518103265291))
            if rtn:
                if isinstance(rtn,discord.Embed):
                    await ctx.send(embed=rtn)
                else:
                    await ctx.send(f"```{rtn}```")
        except Exception:
            await ctx.message.remove_reaction(self.bot.create_emoji_str('s_gch_sending',653161518346534912,True), self.bot.user)
            await ctx.message.add_reaction("❌")
            await ctx.author.send(embed=discord.Embed(title="eval's Error", description=f"```{traceback.format_exc(3)}```", color=self.bot.ec))


    @commands.command()
    @ut.runnable_check()
    async def cuglobal(self, ctx, *cids):
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        #upf = await self.bot.cursor.fetchone()
        if upf["gmod"] == 1:
            async with ctx.channel.typing():
                for cid in [int(i) for i in cids]:
                    await asyncio.sleep(0.5)
                    try:
                        await self.bot.cursor.execute("delete from gchat_cinfo where id = %s", (cid,))
                    except Exception:
                        # 失敗しても処理を継続するため、例外は意図的に無視する
                        pass
            await ctx.send("強制切断できてるか確認してねー")


    @commands.command()
    @commands.is_owner()
    @ut.runnable_check()
    async def guildv(self, ctx, gid: int, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        await self.bot.cursor.execute(
            "UPDATE guilds SET verified = %s WHERE id = %s", (bl, gid))
        await ctx.send(f"サーバー`{await self.bot.fetch_guild(gid)}`の認証状態を{str(bl)}にしました。")


    @commands.group()
    @commands.is_owner()
    @ut.runnable_check()
    async def manage_features(self, ctx):
        pass

    @manage_features.command(name="view",description="他者のfeaturesを見る")
    @app_commands.describe(uid="ユーザーのid")
    @ut.runnable_check()
    async def view_(self,ctx,uid:int):
        await ctx.reply(f"```py\n{self.bot.features.get(uid,[])}```")

    @manage_features.command(name="del", description="feature削除")
    @app_commands.describe(uid="ユーザーのid")
    @app_commands.describe(feature="取り除くfeature")
    @ut.runnable_check()
    async def del_(self,ctx,uid:int,feature:str):
        uf = self.bot.features.get(uid,None)
        if uf and feature in uf:
            self.bot.features[uid].remove(feature)
        await ctx.message.add_reaction(self.bot.create_emoji_str('s_check',653161518103265291))

    @manage_features.command(name="add",description="feature追加")
    @app_commands.describe(uid="ユーザーのid")
    @app_commands.describe(feature="追加するfeature")
    @ut.runnable_check()
    async def add_(self,ctx,uid:int,feature):
        uf = self.bot.features.get(uid,None)
        if uf:
            self.bot.features[uid].append(feature)
        else:
            self.bot.features[uid] = [feature]
        await ctx.message.add_reaction(self.bot.create_emoji_str('s_check',653161518103265291))

    @manage_features.command(name="reload",description="feature再読み込み")
    @ut.runnable_check()
    async def reload_(self,ctx):
        import importlib
        importlib.reload(config)
        self.bot.features = config.sp_features
        await ctx.message.add_reaction(self.bot.create_emoji_str('s_check',653161518103265291))

async def setup(bot):
    await bot.add_cog(owner(bot))
