import time
import datetime
import discord

# AppleUtil - utility tool made by apple502j.


class RateLimiter(object):
    """rate: int, per: seconds"""

    def __init__(self, rate, per):
        self.rate = rate
        self.per = per
        self._token_left = rate
        self._last_updated = time.time()

    def use(self):
        _upd = time.time()
        if self._last_updated + self.per < _upd:
            self._last_updated = _upd
            self._token_left = self.rate - 1
            return True
        if self._token_left > 0:
            self._token_left -= 1
            return True
        return False


class AppleUtil(object):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def has_all_perms(member, channel, *perms):
        """Check if someone has all permissions. channel may be None for global permissions."""
        if not isinstance(member, discord.Member):
            raise TypeError(
                "has_all_perms take a Member as its first argument")
        if channel:
            perm = channel.permissions_for(member)
        else:
            perm = member.guild_permissions
        for p in perms:
            if not getattr(perm, p, False):
                return False
        return True

    @staticmethod
    def create_throttle(rate, per):
        return RateLimiter(rate, per)

    async def get_as_binary(self, url):
        async with self.bot.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.read()

    async def get_as_json(self, url):
        async with self.bot.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_as_text(self, url):
        async with self.bot.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    @staticmethod
    def within(dt, minutes):
        return (datetime.datetime.now(datetime.timezone.utc) - dt) < datetime.timedelta(minutes=minutes)


def setup(bot):
    pass
