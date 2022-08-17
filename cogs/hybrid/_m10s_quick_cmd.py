# -*- coding: utf-8 -*-

from typing import Union
import discord
from discord.ext import commands
import asyncio
import datetime

from discord import app_commands

import m10s_util as ut

from my_module import dpy_interaction as dpyui



class m10s_quick_cmd(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shortcut", description="クイックコマンド呼び出しのパネルを作成します。")
    @app_commands.describe(label="呼び出しボタンの表示名")
    @app_commands.describe(run_command="呼び出すコマンド")
    @ut.runnable_check()
    async def quick_command_create(self, ctx:commands.Context, label:str, *, run_command:str):
        if run_command == "":
            await ctx.send("> 実行コマンドの指定がありません！")
            return
        act_button = dpyui.interaction_buttons()
        act_button.add_button(
            label = label,
            style = dpyui.button_style.Primary,
            custom_id = f"quickact:{'__'.join(run_command.split())}"
        )
        embed = discord.Embed(title="クイックコマンド呼び出し", description=f"このメッセージのボタンを押すと`{run_command}`コマンドが実行されます。", color=self.bot.ec)
        embed.set_footer(text="使用しなくなった場合は、このメッセージを削除してください。")
        await self.bot.dpyui.send_with_ui(ctx.channel, "", embed=embed, ui = act_button)
        if ctx.interaction:
            await ctx.interaction.response.send_message("> 設定しました。", ephemeral=True)

    @commands.Cog.listener()
    async def on_button_click(self, cb:dpyui.interaction_button_callback):
        if cb.custom_id.startswith("quickact:"):
            act_cmd = " ".join(cb.custom_id.replace("quickact:", "").split("__"))
            
            _msg = cb.message
            _msg.id = int(cb.interaction_id)
            _msg.channel = cb._channel
            _msg.author = cb.user
            _msg.content = f"s-{act_cmd}"

            _ctx = await self.bot.get_context(_msg)
            await cb.send_response_with_ui(content=f"> クイックコマンド呼び出し(ベータ版)による{cb.user}のコマンド`{act_cmd}`の実行")
            await self.bot.invoke(_ctx)


async def setup(bot):
    await bot.add_cog(m10s_quick_cmd(bot))
