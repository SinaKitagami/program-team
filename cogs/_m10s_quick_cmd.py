# -*- coding: utf-8 -*-

from typing import Union
import discord
from discord.ext import commands
import asyncio
import datetime

import m10s_util as ut

from my_module import dpy_interaction as dpyui



class m10s_quick_cmd(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shortcut")
    async def quick_command_create(self, ctx, label, *run_command):
        if run_command == []:
            await ctx.send("> 実行コマンドの指定がありません！")
            return
        act_button = dpyui.interaction_buttons()
        act_button.add_button(
            label = label,
            style = dpyui.button_style.Primary,
            custom_id = f"quickact:{'__'.join(run_command)}"
        )
        embed = discord.Embed(title="クイックコマンド呼び出し", description=f"このメッセージのボタンを押すと`{' '.join(run_command)}`コマンドが実行されます。", color=self.bot.ec)
        embed.set_footer(text="使用しなくなった場合は、このメッセージを削除してください。")
        await self.bot.dpyui.send_with_ui(ctx.channel, "", embed=embed, ui = act_button)

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



def setup(bot):
    bot.add_cog(m10s_quick_cmd(bot))
