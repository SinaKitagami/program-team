# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from dateutil.relativedelta import relativedelta as rdelta
import traceback
import m10s_util as ut
import textwrap

from discord import app_commands

class owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def get_ch_id(self, ctx, cnm: str):
        text = [f"{str(ch)} ({ch.id})" for ch in ctx.guild.channels if cnm in str(ch)]
        t = "\n".join(text)
        await ctx.send(embed=ut.getEmbed("一致チャンネル", f"```{t}```"))
        
        #await ctx.send(embed=ut.getEmbed("一致チャンネル", str([f"{i.name}({i.id})" for i in ctx.guild.channels if i.name == cnm])))

    @commands.command()
    @commands.is_owner()
    async def chlogs(self, ctx, cid: int, count: int):
        ch = self.bot.get_channel(cid)
        async for m in ch.history(limit=count):
            await ctx.author.send(embed=ut.getEmbed("メッセージ", m.clean_content, self.bot.ec, "送信者", str(m.author)))
            await asyncio.sleep(2)

    @commands.command()
    @commands.is_owner()
    async def dcomrun(self, ctx, cname, *, ags):
        c = ctx
        c.args = list(ags)
        try:
            await c.invoke(self.bot.get_command(cname))
        except:
            await ctx.send(embed=discord.Embed(title="dcomrunエラー", description=traceback.format_exc(0)))

    @commands.command()
    @commands.is_owner()
    async def cu(self, ctx):
        await ctx.send("see you...")
        await self.bot.close()
    
    #check function
    async def is_evalable(ctx):
        if "eval" in ctx.bot.features.get(ctx.author.id, []):
            return True
        else:
            return False
    
    @commands.command()
    @commands.check(is_evalable)
    async def sql(self, ctx, *, query):
        await ctx.message.add_reaction(self.bot.get_emoji(653161518346534912))
        try:
            ret = await self.bot.cursor.fetchall(query)
        except Exception as exc:
            await ctx.message.remove_reaction(self.bot.get_emoji(653161518346534912), self.bot.user)
            await ctx.message.add_reaction("❌")
            return await ctx.author.send(embed=discord.Embed(title="sql's Error", description=f"```py\n{exc}\n```", color=self.bot.ec))
        else:
            await ctx.message.remove_reaction(self.bot.get_emoji(653161518346534912), self.bot.user)
            await ctx.message.add_reaction(self.bot.get_emoji(653161518103265291))
            
            if ret:
                await ctx.send(f"```\n{ret}\n```")
            else:
                await ctx.send("```\nnone\n```")

    @commands.command()
    @commands.check(is_evalable)
    async def aev(self, ctx, *, cmd):
        try:
            await eval(cmd)
            await ctx.message.add_reaction(self.bot.get_emoji(653161518103265291))
        except:
            await ctx.send(embed=discord.Embed(title="awaitEvalエラー", description=traceback.format_exc(0)))

    @commands.command(name="eval")
    @commands.check(is_evalable)
    async def eval_(self, ctx, *, cmd):
        await ctx.message.add_reaction(self.bot.get_emoji(653161518346534912))
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
            await ctx.message.remove_reaction(self.bot.get_emoji(653161518346534912), self.bot.user)
            await ctx.message.add_reaction(self.bot.get_emoji(653161518103265291))
            if rtn:
                if isinstance(rtn,discord.Embed):
                    await ctx.send(embed=rtn)
                else:
                    await ctx.send(f"```{rtn}```")
        except:
            await ctx.message.remove_reaction(self.bot.get_emoji(653161518346534912), self.bot.user)
            await ctx.message.add_reaction("❌")
            await ctx.author.send(embed=discord.Embed(title="eval's Error", description=f"```{traceback.format_exc(3)}```", color=self.bot.ec))

    @commands.command()
    @commands.is_owner()
    async def inserver(self, ctx):
        guilds = self.bot.guilds
        gcount = len(guilds)-1
        page = 0

        embed = discord.Embed(
            title="サーバー情報", description=f"{guilds[page].name}(id:`{guilds[page].id}`)", color=self.bot.ec)
        embed.add_field(name="サーバー人数", value=f"{guilds[page].member_count}人")
        embed.add_field(
            name="ブースト状態", value=f"{guilds[page].premium_tier}レベル({guilds[page].premium_subscription_count}ブースト)")
        embed.add_field(
            name="チャンネル状況", value=f"テキスト:{len(guilds[page].text_channels)}\nボイス:{len(guilds[page].voice_channels)}\nカテゴリー:{len(guilds[page].categories)}")
        embed.add_field(
            name="サーバー作成日時", value=f"{(guilds[page].created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')}")
        embed.add_field(
            name="思惟奈ちゃん導入日時", value=f"{(guilds[page].me.joined_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')}")
        embed.add_field(name="オーナー", value=f"{guilds[page].owner}")
        embed.set_thumbnail(url=guilds[page].icon.replace(static_format="png").url)
        embed.set_footer(text=f"{page+1}/{gcount+1}")

        msg = await ctx.send(embed=embed)
        await msg.add_reaction(self.bot.get_emoji(653161518195671041))
        await msg.add_reaction(self.bot.get_emoji(653161518170505216))
        while True:
            try:
                r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
            except:
                break
            try:
                await msg.remove_reaction(r, u)
            except:
                pass
            if str(r) == str(self.bot.get_emoji(653161518170505216)):
                if page == gcount:
                    page = 0
                else:
                    page = page + 1

            elif str(r) == str(self.bot.get_emoji(653161518195671041)):
                if page == 0:
                    page = gcount
                else:
                    page = page - 1

            embed = discord.Embed(
                title="サーバー情報", description=f"{guilds[page].name}(id:`{guilds[page].id}`)", color=self.bot.ec)
            embed.add_field(
                name="サーバー人数", value=f"{guilds[page].member_count}人")
            embed.add_field(
                name="ブースト状態", value=f"{guilds[page].premium_tier}レベル({guilds[page].premium_subscription_count}ブースト)")
            embed.add_field(
                name="チャンネル状況", value=f"テキスト:{len(guilds[page].text_channels)}\nボイス:{len(guilds[page].voice_channels)}\nカテゴリー:{len(guilds[page].categories)}")
            embed.add_field(
                name="サーバー作成日時", value=f"{(guilds[page].created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')}")
            embed.add_field(
                name="思惟奈ちゃん導入日時", value=f"{guilds[page].me.joined_at.strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')}")
            embed.add_field(name="オーナー", value=f"{guilds[page].owner}")
            embed.set_thumbnail(
                url=guilds[page].icon.replace(static_format="png").url)
            embed.set_footer(text=f"{page+1}/{gcount+1}")
            await msg.edit(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def dmember(self, ctx, *, mus=None):
        info = None
        tmp2 = None
        if mus is None:
            await ctx.send("メンバーid/名前の指定は必須です。")
        else:
            tmp = None
            try:
                tmp = int(mus)
            except:
                pass
            for guild in self.bot.guilds:
                if tmp:
                    tmp2 = guild.get_member(int(mus))
                else:
                    tmp2 = guild.get_member_named(mus)
                if tmp2:
                    info = tmp2
                    break
        if info:
            async with ctx.message.channel.typing():
                if ctx.guild.owner == info:
                    embed = discord.Embed(title=await ctx._(
                        "userinfo-name"), description=f"{info.name} - {ut.ondevicon(info)} - {await ctx._('userinfo-owner')}", color=info.color)
                else:
                    embed = discord.Embed(title=await ctx._(
                        "userinfo-name"), description=f"{info.name} - {ut.ondevicon(info)}", color=info.color)
                embed.add_field(name=await ctx._(
                    "userinfo-joindiscord"), value=info.created_at)
                embed.add_field(name=await ctx._("userinfo-id"), value=info.id)
                embed.add_field(name=await ctx._("userinfo-online"),
                                value=f"{str(info.status)}")
                embed.add_field(name=await ctx._("userinfo-isbot"),
                                value=str(info.bot))
                embed.add_field(name=await ctx._(
                    "userinfo-displayname"), value=info.display_name)
                embed.add_field(name=await ctx._(
                    "userinfo-joinserver"), value=info.joined_at)
                embed.set_footer(
                    text=f"サーバー:{info.guild.name}({info.guild.id})")
                if info.activity is not None:
                    try:
                        embed.add_field(name=await ctx._(
                            "userinfo-nowplaying"), value=f'{info.activity.name}')
                    except:
                        embed.add_field(name=await ctx._(
                            "userinfo-nowplaying"), value=info.activity)
                hasroles = ""
                for r in info.roles:
                    hasroles = hasroles + f"{r.mention},"
                embed.add_field(name=await ctx._("userinfo-roles"), value=hasroles)
                embed.set_thumbnail(
                    url=info.display_avatar.replace(static_format='png'))
                embed.add_field(name=await ctx._("userinfo-iconurl"),
                                value=info.display_avatar.replace(static_format='png').url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("一致するユーザーが、共通サーバーに見つかりませんでした。")

    @commands.command()
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
                    except:
                        pass
            await ctx.send("強制切断できてるか確認してねー")

    @commands.command()
    @commands.is_owner()
    async def retfmt(self, ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        try:
            await ctx.send(ctx.message.clean_content.replace("s-retfmt ", "").format(ctx, self.bot).replace("第三・十勝チャット Japan(beta)", ""))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.is_owner()
    async def changenick(self, ctx, name=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        await ctx.message.guild.me.edit(nick=name)
        if name is None:
            await ctx.send("私のニックネームをデフォルトの名前に変更したよ。")
        else:
            await ctx.send("私のニックネームを"+name+"に変更したよ。")

    @commands.command()
    @commands.is_owner()
    async def guserft(self, ctx, *, nandt):
        lt = [f"{str(m)}({m.id})" for m in self.bot.users if nandt in str(m)]
        if lt:
            t = "\n".join(lt)
            await ctx.send(embed=ut.getEmbed(f"{str(nandt)}に一致するユーザー", f"```{t}```"))
        else:
            await ctx.send(embed=ut.getEmbed("", "一致ユーザーなし"))

    @commands.command()
    @commands.is_owner()
    async def guildv(self, ctx, gid: int, bl: bool=True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        await self.bot.cursor.execute(
            "UPDATE guilds SET verified = %s WHERE id = %s", (bl, gid))
        await ctx.send(f"サーバー`{self.bot.get_guild(gid)}`の認証状態を{str(bl)}にしました。")


    @commands.group()
    @commands.is_owner()
    async def manage_features(self, ctx):
        pass

    @manage_features.command(name="view",description="他者のfeaturesを見る")
    @app_commands.describe(uid="ユーザーのid")
    async def view_(self,ctx,uid:int):
        await ctx.reply(f"```py\n{self.bot.features.get(uid,[])}```")

    @manage_features.command(name="del", description="feature削除")
    @app_commands.describe(uid="ユーザーのid")
    @app_commands.describe(feature="取り除くfeature")
    async def del_(self,ctx,uid:int,feature:str):
        uf = self.bot.features.get(uid,None)
        if uf and feature in uf:
            self.bot.features[uid].remove(feature)
        await ctx.message.add_reaction(self.bot.get_emoji(653161518103265291))

    @manage_features.command(name="add",description="feature追加")
    @app_commands.describe(uid="ユーザーのid")
    @app_commands.describe(feature="追加するfeature")
    async def add_(self,ctx,uid:int,feature):
        uf = self.bot.features.get(uid,None)
        if uf:
            self.bot.features[uid].append(feature)
        else:
            self.bot.features[uid] = [feature]
        await ctx.message.add_reaction(self.bot.get_emoji(653161518103265291))

    @manage_features.command(name="reload",description="feature再読み込み")
    async def reload_(self,ctx):
        import importlib
        import config
        importlib.reload(config)
        self.bot.features = config.sp_features
        await ctx.message.add_reaction(self.bot.get_emoji(653161518103265291))

async def setup(bot):
    await bot.add_cog(owner(bot))
