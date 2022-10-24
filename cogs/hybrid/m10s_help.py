# -*- coding: utf-8 -*-

from threading import Thread
from typing import Union, Optional
import discord
from discord.ext import commands
import asyncio

import json

from discord import app_commands

import traceback

import m10s_util as ut

from my_module import dpy_interaction as dpyui



class bot_help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    @commands.hybrid_command(description="Botのヘルプを表示します。")
    @app_commands.describe(rcmd="詳細表示するコマンド")
    @commands.bot_has_permissions(embed_links=True, external_emojis=True, add_reactions=True)
    @app_commands.checks.bot_has_permissions(embed_links=True, external_emojis=True, add_reactions=True)
    @ut.runnable_check()
    async def help(self, ctx, rcmd:str=None):
        e = discord.Embed(title="思惟奈ちゃんの使い方", description="基本的に、`/`を入力すると出てくる候補にあるコマンドのうち、思惟奈ちゃんのアイコンが表示されている物がすべてです。", color=self.bot.ec)
        e.add_field(name="グローバルチャットのバッジ", value="🌠:チーム☆思惟奈ちゃんメンバー\n💠:認証済みアカウント\n🔗パートナーサーバーオーナー\n🔧:グローバルチャットモデレーター\n🌟:スターユーザー(アカウント作成日制限を受けないユーザー)\n🔔:アルファテスター(一部機能の先行体験)\n🎫:有料支援者バッジ")
        e.add_field(name="思惟奈ちゃんサポートサーバー", value="https://discord.gg/vtn2V3v", inline=False)
        e.add_field(name="思惟奈ちゃんを支援する", value="https://linktr.ee/sina_chan", inline=False)
        await ctx.send(embed =e)
        """# ヘルプ内容
        if rcmd is None:
            page = 1
            embed = discord.Embed(title=await ctx._("help-1-t"),
                                description=await ctx._("help-1-d"), color=self.bot.ec)
            embed.set_footer(text=f"page:{page}")
            msg = await ctx.send("> ヘルプと呼び出し方が変更になっている機能が、多くあります。\n\
それらのコマンドはスラッシュコマンド(`/`を入力することで一覧が表示されます。)での使用を強くお勧めします。\n\
サポートサーバーの質問チャンネルで、変更に関しての質問はうかがいます。\n\
例:❌`s-level`→⭕`/level card`\
　 ❌`s-play` →⭕`/music play` など", embed=embed)
            await msg.add_reaction(self.bot.get_emoji(653161518195671041))
            await msg.add_reaction(self.bot.get_emoji(653161518170505216))
            await msg.add_reaction("🔍")
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
                    if page == 17:
                        page = 1
                    else:
                        page = page + 1
                    embed = discord.Embed(title=await ctx._(
                        f"help-{page}-t"), description=await ctx._(f"help-{page}-d"), color=self.bot.ec)
                    embed.set_footer(text=f"page:{page}")
                    await msg.edit(embed=embed)
                elif str(r) == str(self.bot.get_emoji(653161518195671041)):
                    if page == 1:
                        page = 17
                    else:
                        page = page - 1
                    embed = discord.Embed(title=await ctx._(
                        f"help-{page}-t"), description=await ctx._(f"help-{page}-d"), color=self.bot.ec)
                    embed.set_footer(text=f"page:{page}")
                    await msg.edit(embed=embed)
                elif str(r) == "🔍":
                    await msg.remove_reaction(self.bot.get_emoji(653161518195671041), self.bot.user)
                    await msg.remove_reaction("🔍", self.bot.user)
                    await msg.remove_reaction(self.bot.get_emoji(653161518170505216), self.bot.user)
                    qm = await ctx.send(await ctx._("help-s-send"))
                    try:
                        msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
                        sewd = msg.content
                    except asyncio.TimeoutError:
                        pass
                    else:
                        try:
                            await msg.delete()
                            await qm.delete()
                        except:
                            pass
                        async with ctx.message.channel.typing():
                            lang = await ctx.user_lang() or "ja"
                            with open(f"lang/{lang}.json", "r", encoding="utf-8") as j:
                                f = json.load(j)
                            sre = discord.Embed(title=await ctx._(
                                "help-s-ret-title"), description=await ctx._("help-s-ret-desc", sewd), color=self.bot.ec)
                            for k, v in f.items():
                                if k.startswith("nh-"):
                                    if sewd in k.replace("nh-", "") or sewd in str(v):
                                        sre.add_field(name=k.replace(
                                            "nh-", ""), value=f"詳細を見るには`s-help {k.replace('nh-','')}`と送信")
                        await ctx.send(embed=sre)
            try:
                await msg.remove_reaction(self.bot.get_emoji(653161518195671041), self.bot.user)
                await msg.remove_reaction("🔍", self.bot.user)
                await msg.remove_reaction(self.bot.get_emoji(653161518170505216), self.bot.user)
            except:
                pass
        else:
            dcmd = await ctx._(f"nh-{str(rcmd)}")
            if str(dcmd) == "":
                await ctx.send(await ctx._("h-notfound"))
            else:
                embed = ut.getEmbed(dcmd[0], dcmd[1], self.bot.ec, *dcmd[2:])
                await ctx.send(embed=embed)"""

    @commands.command()
    @ut.runnable_check()
    async def help_generate(self, ctx):
        self.bot.tmp_helps = {}

        def check_c(c):
            if isinstance(c, commands.HybridGroup):
                self.bot.tmp_helps[c.qualified_name] = {
                    "type":1,
                    "title":f"{c.name}について",
                    "description":c.description,
                    "call":{
                        "main":f"{c.name}",
                        "aliases":f"`{'`,`'.join(c.aliases) or 'なし'}`",
                        "args":[f"引数:{v}" for k,v in c.clean_params.items()]
                    },
                    "group":c.full_parent_name,
                    "only_prefix":False
                    }
                for sc in c.commands:
                    check_c(sc)
            elif isinstance(c, commands.Group):
                for sc in c.commands:
                    check_c(sc)
            elif isinstance(c, commands.HybridCommand):
                self.bot.tmp_helps[c.qualified_name]={
                    "type":0,
                    "title":f"{c.name}について",
                    "description":c.description,
                    "call":{
                        "main":f"{c.name}",
                        "aliases":f"`{'`,`'.join(c.aliases) or 'なし'}`",
                        "args":[f"引数:{v}" for k,v in c.clean_params.items()]
                    },
                    "group":c.full_parent_name,
                    "only_prefix":False
                    }
            elif isinstance(c, commands.Command):
                self.bot.tmp_helps[c.qualified_name]={"type":0,"title":f"{c.name}について","description":c.description,"call":{"main":f"{c.name}","aliases":f"`{'`,`'.join(c.aliases) or 'なし'}`","args":[f"引数:{v}" for k,v in c.clean_params.items()]},"group":c.full_parent_name,"only_prefix":True}

        for c in self.bot.commands:
            check_c(c)
        with open("nhelp.json",mode="w") as f:
            json.dump(self.bot.tmp_helps,f)
            
async def setup(bot):
    await bot.add_cog(bot_help(bot))