import json
import time
import discord
from discord.ext import commands, tasks

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
    async def clear_l10n_cache(self, ctx):
        self.bot.translate_handler.clean_cache()

    @commands.command()
    async def ping(self, ctx):
        message_time = ctx.message.created_at.timestamp
        time_before_send = time.time()
        msg = await ctx.send("...")
        time_after_send = time.time()
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

    @tasks.loop(hours=1)
    async def report_ping(self):
        channel = bot.get_channel(PING_CH)
        time_before_send = time.time()
        msg = await channel.send("...")
        time_after_send = time.time()
        ba = abs(time_after_send - time_before_send)
        await msg.edit(f"LA: {self.bot.latency:.3}\nBA: {ba:.3}")

    @report_ping.before_loop
    async def before_report_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(AppleMiscCog(bot))
