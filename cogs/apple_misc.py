import json
import discord
from discord.ext import commands

LANGUAGE = {"python", "javascript"}
BLOCKS = {"if", "while", "for", "def"}
BLOCK_END = "block_end"

CODE = [
    ("ask", "variable", "string..."),
    ("for", "char", "variable"),
    ("print", "char"),
    ("block_end",)
]

class AppleMiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    @commans.is_owner()
    async def clear_l10n_cache(self, ctx):
        self.bot.translate_handler.clean_cache()

def setup(bot):
    bot.add_cog(AppleMiscCog(bot))
