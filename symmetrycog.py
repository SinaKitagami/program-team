from discord.ext import commands as c

class Music(c.Cog, name="Music"):
    def __init__(self, bot):
        self.bot = bot
    @c.command()
    async def symmetry(a):
        await a.send("シンメトリーにしたい画像をアップしてください↓")
        global mescheck
        mescheck = 1