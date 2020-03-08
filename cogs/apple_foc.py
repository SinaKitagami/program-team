import datetime

import discord
from discord.ext import commands

from apple_util import AppleUtil

class AppleFOCCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.cursor
        if not hasattr(self.bot, "apple_util"):
            self.bot.apple_util = AppleUtil(bot)
        self.guild_throttle = {}

    def get_log_channel(self, guild_id):
        guild = self.db.execute("SELECT * FROM guilds WHERE id=?", (guild_id,)).fetchone()
        if not guild:
            return None
        if guild["sendlog"]:
            return self.bot.get_channel(guild["sendlog"])
        return None

    def should_check(self, member):
        member_id = f"{member.guild.id}-{member.id}"
        if member_id in self.guild_throttle:
            return self.guild_throttle[member_id].use()
        else:
            self.guild_throttle[member_id] = self.bot.apple_util.create_throttle(1, 60)
            self.guild_throttle[member_id].use()
            return True

    def is_offline(self, member):
        return member.status is discord.Status.offline

    async def send(self, member, logc):
        e = discord.Embed(title="オンライン隠し", description=member.mention, timestamp=datetime.datetime.utcnow())
        await logc.send(embed=e)

    async def run(self, member):
        if member.bot:
            return
        logc = self.get_log_channel(member.guild.id)
        if not logc:
            return
        if self.is_offline(member) and self.should_check(member):
            await self.send(member, logc)

    @commands.Cog.listener()
    async def on_typing(self, ch, member, when):
        if isinstance(ch, discord.DMChannel) or isinstance(member, discord.User):
            return
        await self.run(member)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not msg.guild:
            return
        await self.run(msg.author)

    @commands.Cog.listener()
    async def on_reaction_add(self, r, m):
        if isinstance(m, discord.Member):
            await self.run(m)

def setup(bot):
    bot.add_cog(AppleFOCCog(bot))
