import datetime

import discord
from discord.ext import commands


class AppleFOCCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.cursor
        self.guild_throttle = {}

    async def get_log_channel(self, guild_id):
        guild = await self.db.fetchone(
            "SELECT * FROM guilds WHERE id=%s", (guild_id,))
        #guild = await self.bot.cursor.fetchone()
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
            self.guild_throttle[member_id] = self.bot.apple_util.create_throttle(
                1, 60)
            self.guild_throttle[member_id].use()
            return True

    async def is_offline(self, member):
        return member.status is discord.Status.offline and await self.bot.can_use_online(member)

    async def send(self, member, logc):
        e = discord.Embed(title="オンライン隠し", description=member.mention,
                          timestamp=datetime.datetime.utcnow())
        return
        await logc.send(embed=e)

    async def run(self, member):
        if member.bot or not await self.is_offline(member):
            return
        logc = await self.get_log_channel(member.guild.id)
        if not logc:
            return
        if self.should_check(member):
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
