# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json

from typing import Union


class m10s_level_edit(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="leveledit")
    @commands.has_permissions(administrator=True)
    async def edit_level(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.reply("> サーバーレベル編集\n　`add [メンバーor役職を特定できるもの] [追加するレベル] [オプション:追加する経験値]`:追加/減少\n　`set [メンバーor役職を特定できるもの] [設定するレベル] [オプション:設定する経験値]`:設定")

    @edit_level.command(name="add")
    async def level_add(self, ctx, target:Union[commands.MemberConverter,commands.RoleConverter], lev:int, exp:int=None):
        if isinstance(target,discord.Member):
            targets = [target]
        elif isinstance(target,discord.Role):
            targets = target.members
        else:
            return await ctx.reply("> サーバーレベル編集-追加\n　引数が正しくありません。\n　`[メンバーor役職を特定できるもの] [追加するレベル] [オプション:追加する経験値]`")
        pf = await self.bot.cursor.fetchone("SELECT * from guilds WHERE id = %s", (ctx.guild.id,))
        #pf = await self.bot.cursor.fetchone()
        levels = json.loads(pf["levels"])
        for m in targets:
            try:
                levels[str(m.id)]["level"] += lev
                if not exp is None:
                    levels[str(m.id)]["exp"] += exp
            except:pass
        await self.bot.cursor.execute(
            "UPDATE guilds SET levels = %s WHERE id = %s", (json.dumps(levels), ctx.guild.id))
        await ctx.reply(f"> サーバーレベル編集\n　{len(targets)}人のレベルを編集しました。(レベルがないメンバーには干渉していません。)")

    @edit_level.command(name="set")
    async def level_set(self, ctx, target:Union[commands.MemberConverter,commands.RoleConverter], lev:int, exp:int=None):
        if isinstance(target,discord.Member):
            targets = [target]
        elif isinstance(target,discord.Role):
            targets = target.members
        else:
            return await ctx.reply("> サーバーレベル編集-設定\n　引数が正しくありません。\n　`[メンバーor役職を特定できるもの] [設定するレベル] [オプション:設定する経験値]`")
        pf = await self.bot.cursor.fetchone("SELECT * from guilds WHERE id = %s", (ctx.guild.id,))
        #pf = await self.bot.cursor.fetchone()
        levels = pf["levels"]
        for m in targets:
            try:
                levels[str(m.id)]["level"] = lev
                if not exp is None:
                    levels[str(m.id)]["exp"] = exp
            except:pass
        await self.bot.cursor.execute(
            "UPDATE guilds SET levels = %s WHERE id = %s", (json.dumps(levels), ctx.guild.id))
        await ctx.reply(f"> サーバーレベル編集\n　{len(targets)}人のレベルを設定しました。(レベルがないメンバーには干渉していません。)")
        


def setup(bot):
    bot.add_cog(m10s_level_edit(bot))
