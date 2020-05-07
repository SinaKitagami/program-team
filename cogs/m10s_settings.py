# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import m10s_util as ut


class settings(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def userprefix(self,ctx,mode="view",ipf=""):
        if ipf=="@everyone" or ipf=="@here":
            await ctx.send("その文字列はprefixとして使えません。")
            return
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        if mode=="view":
            await ctx.send(embed=ut.getEmbed("ユーザーのprefix",f'```{",".join(upf["prefix"])}```'))
        elif mode=="set":
            spf = upf["prefix"]+[ipf]
            self.bot.cursor.execute("UPDATE users SET prefix = ? WHERE id = ?", (spf,ctx.author.id))
            await ctx.send(ctx._("upf-add",ipf))
        elif mode=="del":
            spf = upf["prefix"]
            spf.remove(ipf)
            self.bot.cursor.execute("UPDATE users SET prefix = ? WHERE id = ?", (spf,ctx.author.id))
            await ctx.send(f"prefixから{ipf}を削除しました。")
        else:
            await ctx.send(embed=ut.getEmbed("不適切なモード選択","`view`または`set`または`del`を指定してください。"))


    @commands.command(aliases=["switchlevelup"])
    async def switchLevelup(self,ctx):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        dor = self.bot.cursor.fetchone()
        if dor["levels"][str(ctx.author.id)]["dlu"]:
            dor["levels"][str(ctx.author.id)]["dlu"] = False
            await ctx.send(ctx._("sLu-off"))
        else:
            dor["levels"][str(ctx.author.id)]["dlu"] = True
            await ctx.send(ctx._("sLu-on"))
        self.bot.cursor.execute("UPDATE guilds SET levels = ? WHERE id = ?", (dor["levels"],ctx.guild.id))


    @commands.command()
    async def guildprefix(self,ctx,mode="view",ipf=""):
        if ipf=="@everyone" or ipf=="@here":
            await ctx.send("その文字列はprefixとして使えません。")
            return
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        if mode=="view":
            await ctx.send(embed=ut.getEmbed("ユーザーのprefix",f'```{",".join(gs["prefix"])}```'))
        elif mode=="set":
            spf = gs["prefix"]+[ipf]
            self.bot.cursor.execute("UPDATE guilds SET prefix = ? WHERE id = ?", (spf,ctx.guild.id))
            await ctx.send(ctx._("upf-add",ipf))
        elif mode=="del":
            spf = gs["prefix"]
            spf.remove(ipf)
            self.bot.cursor.execute("UPDATE guilds SET prefix = ? WHERE id = ?", (spf,ctx.guild.id))
            await ctx.send(f"{ipf}を削除しました。")
        else:
            await ctx.send(embed=ut.getEmbed("不適切なモード選択","`view`または`set`または`del`を指定してください。"))

    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    @commands.command()
    async def guildlang(self,ctx,lang):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if lang not in self.bot.translate_handler.supported_locales:
            await ctx.send(ctx._("setl-cantuse"))
        else:
            self.bot.cursor.execute("UPDATE guilds SET lang = ? WHERE id = ?", (lang,ctx.guild.id))
            self.bot.translate_handler.update_language_cache(ctx.guild, lang)
            await ctx.send(ctx._("setl-set"))

    @commands.command()
    async def sendlogto(self,ctx,to=None):
        if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
            self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
            gpf = self.bot.cursor.fetchone()
            if to:
                self.bot.cursor.execute("UPDATE guilds SET sendlog = ? WHERE id = ?", (int(to),ctx.guild.id))
                n=ctx.guild.me.nick
                await ctx.guild.me.edit(nick="ニックネーム変更テスト")
                await asyncio.sleep(1)
                await ctx.guild.me.edit(nick=n)
                await asyncio.sleep(1)
                await ctx.send("変更しました。ニックネーム変更通知が送られているかどうか確認してください。")
            else:
                self.bot.cursor.execute("UPDATE guilds SET sendlog = ? WHERE id = ?", (None,ctx.guild.id))
                await ctx.send("解除しました。")
        else:
            await ctx.send("このコマンドの使用には、管理者権限が必要です。")

    @commands.command(aliases=["言語設定","言語を次の言語に変えて"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def userlang(self,ctx,lang):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if lang not in self.bot.translate_handler.supported_locales:
            await ctx.send(ctx._("setl-cantuse"))
        else:
            self.bot.cursor.execute("UPDATE users SET lang = ? WHERE id = ?", (lang,ctx.author.id))
            self.bot.translate_handler.update_language_cache(ctx.author, lang)
            await ctx.send(ctx._("setl-set"))

    @commands.command()
    async def comlock(self,ctx,do="view",comname=""):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        if do =="add":
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120):
                await ctx.send(ctx._("need-admin"))
                return
            if not comname in gs["lockcom"]:
                gs["lockcom"].append(comname)
                self.bot.cursor.execute("UPDATE guilds SET lockcom = ? WHERE id = ?", (gs["lockcom"],ctx.guild.id))
            await ctx.send(ctx._("upf-add",comname))
        elif do =="del":
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120):
                await ctx.send(ctx._("need-admin"))
                return
            if comname in gs["lockcom"]:
                gs["lockcom"].remove(comname)
                self.bot.cursor.execute("UPDATE guilds SET lockcom = ? WHERE id = ?", (gs["lockcom"],ctx.guild.id))
            await ctx.send(ctx._("deleted-text"))
        elif do =="view":
            await ctx.send(ctx._("comlock-view",str(gs["lockcom"])))
        else:
            await ctx.send(ctx._("comlock-unknown"))

    @commands.command()
    async def setsysmsg(self,ctx,mode="check",when="welcome",to="sysch",*,content=None):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        msgs = self.bot.cursor.fetchone()
        sm = msgs["jltasks"]
        if mode == "check":
            embed = discord.Embed(title=ctx._("ssm-sendcontent"), description=ctx.guild.name, color=self.bot.ec)
            try:
                embed.add_field(name=ctx._("ssm-welcome"), value=f'{sm["welcome"].get("content")}({ctx._("ssm-sendto")}):{sm["welcome"].get("sendto")})')
            except:
                pass
            try:
                embed.add_field(name=ctx._("ssm-seeyou"), value=f'{sm["cu"].get("content")}({ctx._("ssm-sendto")}:{sm["cu"].get("sendto")})')
            except:
                pass
            await ctx.send(embed=embed)
        elif mode == "set":
            if ctx.author.permissions_in(ctx.channel).administrator == True or ctx.author.id == 404243934210949120:
                try:
                    msgs["jltasks"][when]={}
                    msgs["jltasks"][when]["content"] = content
                    msgs["jltasks"][when]["sendto"] = to
                    self.bot.cursor.execute("UPDATE guilds SET jltasks = ? WHERE id = ?", (msgs["jltasks"],ctx.guild.id))
                    await ctx.send(ctx._("ssm-set"))
                except:
                    await ctx.send(ctx._("ssm-not"))
            else:
                await ctx.send(ctx._("need-admin"))


    @commands.command(aliases=["サーバーコマンド","次の条件でサーバーコマンドを開く"])
    async def servercmd(self,ctx,mode="all",name=None):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        mmj = self.bot.cursor.fetchone()
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if mode == "add":
            if not mmj["commands"].get(name,None) is None:
                if not(ctx.author.permissions_in(ctx.channel).manage_guild == True and ctx.author.permissions_in(ctx.channel).manage_roles == True or ctx.author.id == 404243934210949120):
                    await ctx.send(ctx._("need-manage"))
                    return
            dc = ctx.author.dm_channel
            if dc == None:
                await ctx.author.create_dm()
                dc = ctx.author.dm_channel

            emojis = ctx.guild.emojis

            se = []
            for e in emojis:
                se = se + [str(e)]

            await dc.send(ctx._("scmd-add-guide1"))

            def check(m):
                return m.channel == dc and m.author == ctx.author

            msg = await self.bot.wait_for('message', check=check)
            if msg.content =="one":
                await dc.send(ctx._("scmd-add-guide2"))
                mes = await self.bot.wait_for('message', check=check)
                guide=mes.content
                try:
                    await dc.send(ctx._("scmd-add-guide3-a",ctx._("scmd-guide-emoji"),str(se)))
                except:
                    await dc.send(ctx._("scmd-add-guide3-a",ctx._("scmd-guide-emoji"),"(絵文字が多すぎて表示できません！)"))
                mg=await self.bot.wait_for('message', check=check)
                rep = mg.clean_content.format(se)
                mmj["commands"][name]={}
                mmj["commands"][name]["mode"]="one"
                mmj["commands"][name]["rep"]=rep
                mmj["commands"][name]["createdBy"]=ctx.author.id
                mmj["commands"][name]["guide"]=guide
            elif msg.content == "random":
                await dc.send(ctx._("scmd-add-guide2"))
                mes = await self.bot.wait_for('message', check=check)
                guide=mes.content
                try:
                    await dc.send(ctx._("scmd-add-guide3-a",ctx._("scmd-guide-emoji"),str(se)))
                except:
                    await dc.send(ctx._("scmd-add-guide3-a",ctx._("scmd-guide-emoji"),"(絵文字が多すぎて表示できません！)"))
                rep = []
                while True:
                    mg=await self.bot.wait_for('message', check=check)
                    if mg.content=="stop":
                        break
                    else:
                        rep = rep + [mg.clean_content.format(se)]
                        try:
                            await dc.send(ctx._("scmd-add-guide3-b",ctx._("scmd-guide-emoji"),str(se)))
                        except:
                            await dc.send(ctx._("scmd-add-guide3-b",ctx._("scmd-guide-emoji"),"(絵文字が多すぎて表示できません！)"))
                mmj["commands"][name]={}
                mmj["commands"][name]["mode"]="random"
                mmj["commands"][name]["rep"]=rep
                mmj["commands"][name]["createdBy"]=ctx.author.id
                mmj["commands"][name]["guide"]=guide
            elif msg.content == "role":
                if ctx.author.permissions_in(ctx.channel).manage_guild == True and ctx.author.permissions_in(ctx.channel).manage_roles == True or ctx.author.id == 404243934210949120:
                    await dc.send(ctx._("scmd-add-guide2"))
                    mes = await self.bot.wait_for('message', check=check)
                    guide=mes.content
                    await dc.send(ctx._("scmd-add-guide3-c",ctx._("scmd-guide-emoji"),str(se)))
                    mg=await self.bot.wait_for('message', check=check)
                    rep = int(mg.clean_content)
                    mmj["commands"][name]={}
                    mmj["commands"][name]["mode"]="role"
                    mmj["commands"][name]["rep"]=rep
                    mmj["commands"][name]["createdBy"]=ctx.author.id
                    mmj["commands"][name]["guide"]=guide
                else:
                    await ctx.send(ctx._("need-manage"))
                    return
            else:
                await dc.send(ctx._("scmd-add-not"))
                return
            self.bot.cursor.execute("UPDATE guilds SET commands = ? WHERE id = ?", (mmj["commands"],ctx.guild.id))
            await ctx.send(ctx._("scmd-add-fin"))
        elif mode == "help":
            if mmj["commands"] == {}:
                await ctx.send(ctx._("scmd-all-notfound"))
            elif mmj["commands"].get(name) is None:
                await ctx.send(ctx._("scmd-help-notfound"))
            else:
                if isinstance(mmj["commands"][name]['createdBy'],int):
                    await ctx.send(ctx._("scmd-help-title",name,await bot.fetch_user(mmj["commands"][name]['createdBy']),mmj["commands"][name]['guide']))
                else:
                    await ctx.send(ctx._("scmd-help-title",name,mmj["commands"][name]['createdBy'],mmj["commands"][name]['guide']))
        elif mode == "all":
            if mmj["commands"] == []:
                await ctx.send(ctx._("scmd-all-notfound"))
            else:
                await ctx.send(str(mmj["commands"].keys()).replace("dict_keys(",ctx._("scmd-all-list")).replace(")",""))
        elif mode == "del":
            if ctx.author.permissions_in(ctx.channel).manage_guild == True and ctx.author.permissions_in(ctx.channel).manage_roles == True or ctx.author.id == 404243934210949120:
                if not mmj["commands"] == None:
                    del mmj["commands"][name]
                await ctx.send(ctx._("scmd-del"))
                self.bot.cursor.execute("UPDATE guilds SET commands = ? WHERE id = ?", (mmj["commands"],ctx.guild.id))
            else:
                await ctx.send(ctx._("need-manage"))
        else:
            await ctx.send(ctx._("scmd-except"))

    @commands.command()
    async def hash(self,ctx):
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        d = self.bot.cursor.fetchone()
        hc = d["hash"]
        if hc == None:
            d["hash"]=[ctx.channel.id]
            await ctx.send(ctx._("hash-connect"))
        elif ctx.channel.id in hc:
            d["hash"].remove(ctx.channel.id)
            await ctx.send(ctx._("hash-disconnect"))
        else:
            d["hash"].append(ctx.channel.id)
            await ctx.send(ctx._("hash-connect"))
        self.bot.cursor.execute("UPDATE guilds SET hash = ? WHERE id = ?", (d["hash"],ctx.guild.id))

    @commands.command(aliases=["オンライン通知"])
    async def onlinenotif(self,ctx,mode,uid:int):
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        if mode=='add':
            upf["onnotif"].append(uid)
            self.bot.cursor.execute("UPDATE users SET onnotif = ? WHERE id = ?", (upf["onnotif"],ctx.author.id))
            await ctx.send(ctx._("onnotif-set"))
        elif mode =='del':
            upf["onnotif"].remove(uid)
            self.bot.cursor.execute("UPDATE users SET onnotif = ? WHERE id = ?", (upf["onnotif"],ctx.author.id))
            await ctx.send(ctx._("onnotif-stop"))
        else:
            await ctx.send(ctx._("onnotif-error"))
        self.bot.cursor.execute("select * from users where id=?",(ctx.author.id,))
        upf = self.bot.cursor.fetchone()
        await ctx.send(f"upf:{upf['onnotif']}")

    @commands.command()
    async def levelupsendto(self,ctx,to):
        if to == "here":
            self.bot.cursor.execute("UPDATE guilds SET levelupsendto = ? WHERE id = ?", ("here",ctx.guild.id))
        else:
            self.bot.cursor.execute("UPDATE guilds SET levelupsendto = ? WHERE id = ?", (int(to),ctx.guild.id))
        await ctx.send(ctx._("changed"))

    @commands.command()
    async def levelreward(self,ctx,lv:int,rl=None):
        if not(ctx.author.permissions_in(ctx.channel).manage_guild == True and ctx.author.permissions_in(ctx.channel).manage_roles == True or ctx.author.id == 404243934210949120):
            await ctx.send(ctx._("need-admin"))
            return
        self.bot.cursor.execute("select * from guilds where id=?",(ctx.guild.id,))
        gs = self.bot.cursor.fetchone()
        if rl is None:
            del gs["reward"][str(lv)]
        else:
            try:
                grl=await commands.RoleConverter().convert(ctx,rl)
            except:
                return await ctx.send("有効な役職IDを指定してください。")
            rid = grl.id
            gs["reward"][str(lv)] = rid
        self.bot.cursor.execute("UPDATE guilds SET reward = ? WHERE id = ?", (gs["reward"],ctx.guild.id))
        await ctx.send(ctx._("changed"))



def setup(bot):
    bot.add_cog(settings(bot))
