# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import m10s_util as ut

import json


class settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userprefix(self, ctx, mode="view", ipf=""):
        if ipf == "@everyone" or ipf == "@here":
            await ctx.send("その文字列はprefixとして使えません。")
            return
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        prefixes = json.loads(upf["prefix"])
        #upf = await self.bot.cursor.fetchone()
        if mode == "view":
            await ctx.send(embed=ut.getEmbed("ユーザーのprefix", f'```{",".join(prefixes)}```'))
        elif mode == "set":
            spf = prefixes + [ipf]
            await self.bot.cursor.execute(
                "UPDATE users SET prefix = %s WHERE id = %s", (json.dumps(spf), ctx.author.id))
            await ctx.send(await ctx._("upf-add", ipf))
        elif mode == "del":
            prefixes.remove(ipf)
            await self.bot.cursor.execute(
                "UPDATE users SET prefix = %s WHERE id = %s", (json.dumps(prefixes), ctx.author.id))
            await ctx.send(f"prefixから{ipf}を削除しました。")
        else:
            await ctx.send(embed=ut.getEmbed("不適切なモード選択", "`view`または`set`または`del`を指定してください。"))

    @commands.command(aliases=["switchlevelup"])
    async def switchLevelup(self, ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        dor = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #dor = await self.bot.cursor.fetchone()
        if dor["levels"][str(ctx.author.id)]["dlu"]:
            dor["levels"][str(ctx.author.id)]["dlu"] = False
            await ctx.send(await ctx._("sLu-off"))
        else:
            dor["levels"][str(ctx.author.id)]["dlu"] = True
            await ctx.send(await ctx._("sLu-on"))
        await self.bot.cursor.execute(
            "UPDATE guilds SET levels = %s WHERE id = %s", (json.dumps(dor["levels"]), ctx.guild.id))

    @commands.command()
    async def guildprefix(self, ctx, mode="view", ipf=""):
        if ipf == "@everyone" or ipf == "@here":
            await ctx.send("その文字列はprefixとして使えません。")
            return
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #gs = await self.bot.cursor.fetchone()
        prefixes = gs["prefix"]
        if mode == "view":
            await ctx.send(embed=ut.getEmbed("ユーザーのprefix", f'```{",".join(prefixes)}```'))
        elif mode == "set":
            spf = prefixes + [ipf]
            await self.bot.cursor.execute(
                "UPDATE guilds SET prefix = %s WHERE id = %s", (json.dumps(spf), ctx.guild.id))
            await ctx.send(await ctx._("upf-add", ipf))
        elif mode == "del":
            prefixes.remove(ipf)
            await self.bot.cursor.execute(
                "UPDATE guilds SET prefix = %s WHERE id = %s", (json.dumps(prefixes), ctx.guild.id))
            await ctx.send(f"{ipf}を削除しました。")
        else:
            await ctx.send(embed=ut.getEmbed("不適切なモード選択", "`view`または`set`または`del`を指定してください。"))

    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    @commands.command()
    async def guildlang(self, ctx, lang):
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #gs = await self.bot.cursor.fetchone()
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if lang not in self.bot.translate_handler.supported_locales:
            await ctx.send(await ctx._("setl-cantuse"))
        else:
            await self.bot.cursor.execute(
                "UPDATE guilds SET lang = %s WHERE id = %s", (lang, ctx.guild.id))
            self.bot.translate_handler.update_language_cache(ctx.guild, lang)
            await ctx.send(await ctx._("setl-set"))

    @commands.command()
    async def sendlogto(self, ctx, to=None):
        if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
            gpf = await self.bot.cursor.fetchone(
                "select * from guilds where id=%s", (ctx.guild.id,))
            #gpf = await self.bot.cursor.fetchone()
            if to:
                await self.bot.cursor.execute(
                    "UPDATE guilds SET sendlog = %s WHERE id = %s", (int(to), ctx.guild.id))
                n = ctx.guild.me.nick
                await ctx.guild.me.edit(nick="ニックネーム変更テスト")
                await asyncio.sleep(1)
                await ctx.guild.me.edit(nick=n)
                await asyncio.sleep(1)
                await ctx.send("変更しました。ニックネーム変更通知が送られているかどうか確認してください。")
            else:
                await self.bot.cursor.execute(
                    "UPDATE guilds SET sendlog = %s WHERE id = %s", (None, ctx.guild.id))
                await ctx.send("解除しました。")
        else:
            await ctx.send("このコマンドの使用には、管理者権限が必要です。")

    @commands.command(aliases=["言語設定", "言語を次の言語に変えて"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def userlang(self, ctx, lang):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if lang not in self.bot.translate_handler.supported_locales:
            await ctx.send(await ctx._("setl-cantuse"))
        else:
            await self.bot.cursor.execute(
                "UPDATE users SET lang = %s WHERE id = %s", (lang, ctx.author.id))
            self.bot.translate_handler.update_language_cache(ctx.author, lang)
            await ctx.send(await ctx._("setl-set"))

    @commands.command()
    async def comlock(self, ctx, do="view", *comname):
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        locks = json.loads(gs["lockcom"])
        #gs = await self.bot.cursor.fetchone()
        if do == "add":
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120):
                await ctx.send(await ctx._("need-admin"))
                return
            for i in comname:
                locks.append(i)
            await self.bot.cursor.execute(
                "UPDATE guilds SET lockcom = %s WHERE id = %s", (json.dumps(locks), ctx.guild.id))
            await ctx.send(await ctx._("upf-add", str(comname)))
        elif do == "del":
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120):
                await ctx.send(await ctx._("need-admin"))
                return
            for i in comname:
                try:
                    locks.remove(i)
                except:
                    pass
            await self.bot.cursor.execute(
                "UPDATE guilds SET lockcom = %s WHERE id = %s", (json.dumps(locks), ctx.guild.id))
            await ctx.send(await ctx._("deleted-text"))
        elif do == "view":
            await ctx.send(await ctx._("comlock-view", gs["lockcom"]))
        else:
            await ctx.send(await ctx._("comlock-unknown"))

    @commands.command()
    async def setsysmsg(self, ctx, mode="check", when="welcome", to="sysch", *, content=None):
        msgs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #msgs = await self.bot.cursor.fetchone()
        sm = json.loads(msgs["jltasks"])
        if mode == "check":
            embed = discord.Embed(title=await ctx._(
                "ssm-sendcontent"), description=ctx.guild.name, color=self.bot.ec)
            try:
                embed.add_field(name=await ctx._(
                    "ssm-welcome"), value=f'{sm["welcome"].get("content")}({await ctx._("ssm-sendto")}):{sm["welcome"].get("sendto")})')
            except:
                pass
            try:
                embed.add_field(name=await ctx._(
                    "ssm-seeyou"), value=f'{sm["cu"].get("content")}({await ctx._("ssm-sendto")}:{sm["cu"].get("sendto")})')
            except:
                pass
            await ctx.send(embed=embed)
        elif mode == "set":
            if ctx.author.permissions_in(ctx.channel).administrator is True or ctx.author.id == 404243934210949120:
                try:
                    sm[when] = {}
                    sm[when]["content"] = content
                    sm[when]["sendto"] = to
                    await self.bot.cursor.execute(
                        "UPDATE guilds SET jltasks = %s WHERE id = %s", (json.dumps(sm), ctx.guild.id))
                    await ctx.send(await ctx._("ssm-set"))
                except:
                    await ctx.send(await ctx._("ssm-not"))
            else:
                await ctx.send(await ctx._("need-admin"))

    @commands.command(aliases=["サーバーコマンド", "次の条件でサーバーコマンドを開く"])
    async def servercmd(self, ctx, mode="all", name=None):
        mmj = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #mmj = await self.bot.cursor.fetchone()
        cmds = json.loads(mmj["commands"])
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if mode == "add":
            if not cmds.get(name, None) is None:
                if not(ctx.author.permissions_in(ctx.channel).manage_guild is True and ctx.author.permissions_in(ctx.channel).manage_roles is True or ctx.author.id == 404243934210949120):
                    await ctx.send(await ctx._("need-manage"))
                    return
            dc = ctx.author.dm_channel
            if dc is None:
                await ctx.author.create_dm()
                dc = ctx.author.dm_channel

            emojis = ctx.guild.emojis

            se = [str(i) for i in emojis]

            await dc.send(await ctx._("scmd-add-guide1"))

            def check(m):
                return m.channel == dc and m.author == ctx.author

            msg = await self.bot.wait_for('message', check=check)
            if msg.content == "one":
                await dc.send(await ctx._("scmd-add-guide2"))
                mes = await self.bot.wait_for('message', check=check)
                guide = mes.content
                try:
                    await dc.send(await ctx._("scmd-add-guide3-a", await ctx._("scmd-guide-emoji"), str(se)))
                except:
                    await dc.send(await ctx._("scmd-add-guide3-a", await ctx._("scmd-guide-emoji"), "(絵文字が多すぎて表示できません！)"))
                mg = await self.bot.wait_for('message', check=check)
                rep = mg.clean_content.format(se)
                cmds[name] = {}
                cmds[name]["mode"] = "one"
                cmds[name]["rep"] = rep
                cmds[name]["createdBy"] = ctx.author.id
                cmds[name]["guide"] = guide
            elif msg.content == "random":
                await dc.send(await ctx._("scmd-add-guide2"))
                mes = await self.bot.wait_for('message', check=check)
                guide = mes.content
                try:
                    await dc.send(await ctx._("scmd-add-guide3-a", await ctx._("scmd-guide-emoji"), str(se)))
                except:
                    await dc.send(await ctx._("scmd-add-guide3-a", await ctx._("scmd-guide-emoji"), "(絵文字が多すぎて表示できません！)"))
                rep = []
                while True:
                    mg = await self.bot.wait_for('message', check=check)
                    if mg.content == "stop":
                        break
                    else:
                        rep = rep + [mg.clean_content.format(se)]
                        try:
                            await dc.send(await ctx._("scmd-add-guide3-b", await ctx._("scmd-guide-emoji"), str(se)))
                        except:
                            await dc.send(await ctx._("scmd-add-guide3-b", await ctx._("scmd-guide-emoji"), "(絵文字が多すぎて表示できません！)"))
                cmds[name] = {}
                cmds[name]["mode"] = "random"
                cmds[name]["rep"] = rep
                cmds[name]["createdBy"] = ctx.author.id
                cmds[name]["guide"] = guide
            elif msg.content == "role":
                if ctx.author.permissions_in(ctx.channel).manage_guild is True and ctx.author.permissions_in(ctx.channel).manage_roles is True or ctx.author.id == 404243934210949120:
                    await dc.send(await ctx._("scmd-add-guide2"))
                    mes = await self.bot.wait_for('message', check=check)
                    guide = mes.content
                    await dc.send(await ctx._("scmd-add-guide3-c", await ctx._("scmd-guide-emoji"), str(se)))
                    mg = await self.bot.wait_for('message', check=check)
                    rep = int(mg.clean_content)
                    cmds[name] = {}
                    cmds[name]["mode"] = "role"
                    cmds[name]["rep"] = rep
                    cmds[name]["createdBy"] = ctx.author.id
                    cmds[name]["guide"] = guide
                else:
                    await ctx.send(await ctx._("need-manage"))
                    return
            else:
                await dc.send(await ctx._("scmd-add-not"))
                return
            await self.bot.cursor.execute(
                "UPDATE guilds SET commands = %s WHERE id = %s", (json.dumps(cmds), ctx.guild.id))
            await ctx.send(await ctx._("scmd-add-fin"))
        elif mode == "help":
            if cmds == {}:
                await ctx.send(await ctx._("scmd-all-notfound"))
            elif cmds.get(name) is None:
                await ctx.send(await ctx._("scmd-help-notfound"))
            else:
                if isinstance(cmds[name]['createdBy'], int):
                    await ctx.send(await ctx._("scmd-help-title", name, await self.bot.fetch_user(cmds[name]['createdBy']), cmds[name]['guide']))
                else:
                    await ctx.send(await ctx._("scmd-help-title", name, cmds[name]['createdBy'], cmds[name]['guide']))
        elif mode == "all":
            if cmds == {}:
                await ctx.send(await ctx._("scmd-all-notfound"))
            else:
                await ctx.send(str(cmds.keys()).replace("dict_keys(", await ctx._("scmd-all-list")).replace(")", ""))
        elif mode == "del":
            if ctx.author.permissions_in(ctx.channel).manage_guild is True and ctx.author.permissions_in(ctx.channel).manage_roles is True or ctx.author.id == 404243934210949120:
                if not cmds is None:
                    del cmds[name]
                await ctx.send(await ctx._("scmd-del"))
                await self.bot.cursor.execute(
                    "UPDATE guilds SET commands = %s WHERE id = %s", (json.dumps(cmds), ctx.guild.id))
            else:
                await ctx.send(await ctx._("need-manage"))
        else:
            await ctx.send(await ctx._("scmd-except"))

    @commands.command()
    async def hash(self, ctx):
        d = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #d = await self.bot.cursor.fetchone()
        hc = json.loads(d["hash"])
        if hc == None:
            hc = [ctx.channel.id]
            await ctx.send(await ctx._("hash-connect"))
        elif ctx.channel.id in hc:
            hc.remove(ctx.channel.id)
            await ctx.send(await ctx._("hash-disconnect"))
        else:
            hc.append(ctx.channel.id)
            await ctx.send(await ctx._("hash-connect"))
        await self.bot.cursor.execute(
            "UPDATE guilds SET hash = %s WHERE id = %s", (json.dumps(hc), ctx.guild.id))

    # @commands.command(aliases=["オンライン通知"])
    # moved to apple_onlinenotif

    @commands.command()
    async def levelupsendto(self, ctx, to:discord.TextChannel = None):
        if to is None:
            await self.bot.cursor.execute(
                "UPDATE guilds SET levelupsendto = %s WHERE id = %s", (0, ctx.guild.id))
        else:
            await self.bot.cursor.execute(
                "UPDATE guilds SET levelupsendto = %s WHERE id = %s", (to.id, ctx.guild.id))
        await ctx.send(await ctx._("changed"))

    @commands.command()
    async def levelreward(self, ctx, lv: int, rl=None):
        if not(ctx.author.permissions_in(ctx.channel).manage_guild is True and ctx.author.permissions_in(ctx.channel).manage_roles is True or ctx.author.id == 404243934210949120):
            await ctx.send(await ctx._("need-admin"))
            return
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #gs = await self.bot.cursor.fetchone()
        rewards = json.loads(gs["reward"])
        if rl is None:
            del rewards[str(lv)]
        else:
            try:
                grl = await commands.RoleConverter().convert(ctx, rl)
            except:
                return await ctx.send("有効な役職IDを指定してください。")
            rid = grl.id
            rewards[str(lv)] = rid
        await self.bot.cursor.execute(
            "UPDATE guilds SET reward = %s WHERE id = %s", (json.dumps(rewards), ctx.guild.id))
        await ctx.send(await ctx._("changed"))


def setup(bot):
    bot.add_cog(settings(bot))
