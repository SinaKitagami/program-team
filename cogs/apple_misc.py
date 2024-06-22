import json
import datetime
from typing import Optional
import discord
from discord.ext import commands, tasks
from discord import app_commands

import m10s_util as ut

import time

LANGUAGE = {"python", "javascript"}
BLOCKS = {"if", "while", "for", "def"}
BLOCK_END = "block_end"

CODE = [
    ("ask", "variable", "string..."),
    ("for", "char", "variable"),
    ("print", "char"),
    ("block_end",)
]

PING_CH = 712564878480637973


class AppleMiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.report_ping.start()

    @commands.command()
    @ut.runnable_check()
    async def code_in(self, ctx, lang):
        if lang in LANGUAGE:
            with open(f"data/programming_info/{lang}.json", "r", encoding="utf-8") as f:
                lang_def = json.load(f)
            result = ""
            indent_times = 0
            for line in CODE:
                suffix = lang_def["after_line"]
                addition = ""
                if line[0] == BLOCK_END:
                    indent_times -= 1
                    suffix = lang_def["after_block"]
                elif line[0] in BLOCKS:
                    suffix = lang_def["before_block"]
                    addition = lang_def[line[0]].format(*line[1:])
                else:
                    addition = lang_def[line[0]].format(*line[1:])
                indents = lang_def["indent"] * indent_times
                result += f"{indents}{addition}{suffix}"
                if line[0] in BLOCKS:
                    indent_times += 1
            await ctx.send(f"```{result}```")

    @commands.command()
    @commands.is_owner()
    @ut.runnable_check()
    async def clear_l10n_cache(self, ctx):
        self.bot.translate_handler.clean_cache()

    @commands.hybrid_command(description="Botの応答速度を返します。")
    @ut.runnable_check()
    @app_commands.describe(is_debug="詳細情報を表示するかどうか(デバッグ用)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def ping(self, ctx, is_debug: Optional[bool] = False):
        if is_debug:
            message_time = ctx.message.created_at.timestamp()
            time_before_send = datetime.datetime.now(datetime.timezone.utc).timestamp()
            msg = await ctx.send("...")
            time_after_send = datetime.datetime.now(datetime.timezone.utc).timestamp()
            latency = self.bot.latency
            tb = abs(time_before_send - message_time)
            ba = abs(time_after_send - time_before_send)
            content = f"LA: {latency:.3}\nTB: {tb:.3}\nBA: {ba:.3}\n"
            if hasattr(ctx, "context_at") and isinstance(ctx.context_at, float):
                context_at = ctx.context_at
                tc = abs(context_at - message_time)
                cb = abs(time_before_send - context_at)
                content += f"TC: {tc:.3}\nCB: {cb:.3}\n"
            await msg.edit(content=content)
        else:
            startt = time.time()
            mes = await ctx.send("please wait")
            await mes.edit(content=str(round(time.time()-startt, 3)*1000)+"ms")

    @tasks.loop(minutes=30)
    async def report_ping(self):
        channel = await self.bot.fetch_channel(PING_CH)
        time_before_send = datetime.datetime.now(datetime.timezone.utc).timestamp()
        msg = await channel.send("...")
        time_after_send = datetime.datetime.now(datetime.timezone.utc).timestamp()
        ba = abs(time_after_send - time_before_send)
        await msg.edit(content=f"LA: {self.bot.latency:.3}\nBA: {ba:.3}")

    @report_ping.before_loop
    async def before_report_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(AppleMiscCog(bot))
