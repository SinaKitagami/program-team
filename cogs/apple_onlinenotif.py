from datetime import datetime
import discord
from discord.ext import commands

# This file is copied from TeraAppleBot

class OnlineNotif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        def shares_guild(user_id_a, user_id_b):
            return not not [
                guild
                for guild
                in self.bot.guilds
                if set([user_id_a, user_id_b]).issubset(frozenset(guild._members.keys()))
            ]
        self.bot.shares_guild = shares_guild
        def get_member(user_id):
            m = [g.get_member(user_id) for g in bot.guilds if g.get_member(user_id)]
            if m:
                return m[0]
            return None
        self.bot.get_member = get_member

        self._last_posted = {}

    def get_subscribers(self):
        return [
            {"user_id": int(i["id"]), "subscribe": [int(j) for j in (i["onnotif"] or []) if j]}
            for i
            in self.bot.cursor.execute("SELECT id, onnotif FROM users").fetchall()
        ]

    def get_subscribing_of_user(self, user):
        return self.bot.cursor.execute("SELECT onnotif FROM users WHERE id = ?", (user.id,)).fetchone()["onnotif"] or []

    def get_subscribed_of_user(self, user):
        return [
            i["user_id"]
            for i
            in self.get_subscribers()
            if user.id in i["subscribe"]
        ]

    def onlinenotif_enabled(self, user):
        enabled = self.bot.cursor.execute("SELECT online_agreed FROM users WHERE id = ?", (user.id,)).fetchone()
        return enabled and enabled["online_agreed"]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.status == after.status:
            return
        if discord.Status.offline not in (before.status, after.status):
            return
        if not self.onlinenotif_enabled(before):
            return
        if self._last_posted.get(before.id, None) and self.bot.apple_util.within(self._last_posted[before.id], 3):
            return
        self._last_posted[before.id] = datetime.utcnow()
        msg = "onlinenotif-notif" if before.status is discord.Status.offline else "onlinenotif-offlinenotif"
        for subsc in self.get_subscribed_of_user(before):
            if self.bot.shares_guild(before.id, subsc) and self.bot.get_member(subsc).status != discord.Status.offline:
                user = self.bot.get_user(subsc)
                await user.send(self.bot._(user, msg, str(before)))

    @commands.group(invoke_without_command=True)
    async def onlinenotif(self, ctx):
        """Returns the name of the users you are receiving online notifications of."""
        users = [
            self.bot.get_user(user_id)
            for user_id
            in self.get_subscribing_of_user(ctx.author)
            if self.bot.shares_guild(ctx.author.id, user_id)
        ]
        if not users:
            return await ctx.author.send(ctx._("onlinenotif-nousers"))
        await ctx.author.send(ctx._("onlinenotif-subscribing", " ".join(map(str, users))))

    @onlinenotif.command(aliases=["add"])
    async def subscribe(self, ctx, user: discord.User):
        """Subscribes to this user."""
        subscribing = self.get_subscribing_of_user(ctx.author)
        if user.id in subscribing:
            return await ctx.say("onlinenotif-already")
        if not self.bot.shares_guild(ctx.author.id, user.id):
            return await ctx.say("onlinenotif-shareGuild")
        subscribing.append(user.id)
        self.bot.cursor.execute("UPDATE users SET onnotif = ? WHERE id = ?",(subscribing, ctx.author.id))
        await ctx.say("onlinenotif-success")

    @onlinenotif.command(aliases=["remove", "del"])
    async def unsubscribe(self, ctx, user: discord.User):
        """Un-subscribes to this user."""
        subscribing = self.get_subscribing_of_user(ctx.author)
        if user.id not in subscribing:
            return await ctx.say("onlinenotif-yet")
        subscribing.remove(user.id)
        self.bot.cursor.execute("UPDATE users SET onnotif = ? WHERE id = ?",(subscribing, ctx.author.id))
        await ctx.say("onlinenotif-removeSuccess")

    @onlinenotif.command()
    async def settings(self, ctx, enabled: bool = False):
        """Choose whether someone can receive your online notification.
        Note that you have to share server with that user."""
        self.bot.cursor.execute("UPDATE users SET online_agreed = ? WHERE id = ?", (int(enabled), ctx.author.id))
        await ctx.say("onlinenotif-settings")


def setup(bot):
    bot.add_cog(OnlineNotif(bot))
