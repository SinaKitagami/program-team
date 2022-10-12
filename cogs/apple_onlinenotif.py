from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands

import json

import m10s_util as ut

# This file is copied from TeraAppleBot


class OnlineNotif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        def get_member(user_id):
            m = [g.get_member(user_id)
                 for g in bot.guilds if g.get_member(user_id)]
            if m:
                return m[0]
            return None
        self.bot.get_member = get_member
        self.onlinenotif_enabled = bot.can_use_online

        self._last_posted = {}

    async def get_subscribers(self):
        p = await self.bot.cursor.fetchall("SELECT id, onnotif FROM users")
        return [
            {"user_id": int(i["id"]), "subscribe": [int(j) for j in (json.loads(i["onnotif"]) or []) if j]}
            for i
            in p
        ]

    async def get_subscribing_of_user(self, user):
        p = await self.bot.cursor.fetchone("SELECT onnotif FROM users WHERE id = %s", (user.id,))
        return json.loads(p["onnotif"]) or []

    async def get_subscribed_of_user(self, user):
        return [
            i["user_id"]
            for i
            in await self.get_subscribers()
            if user.id in i["subscribe"]
        ]

    # @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.status == after.status:
            return
        if discord.Status.offline not in (before.status, after.status):
            return
        if not await self.onlinenotif_enabled(before):
            return
        if self._last_posted.get(before.id, None) and self.bot.apple_util.within(self._last_posted[before.id], 3):
            return
        self._last_posted[before.id] = discord.utils.utcnow()
        msg = "onlinenotif-notif" if before.status is discord.Status.offline else "onlinenotif-offlinenotif"
        for subsc in await self.get_subscribed_of_user(before):
            if self.bot.shares_guild(before.id, subsc) and self.bot.get_member(subsc).status != discord.Status.offline:
                user = self.bot.get_user(subsc)
                await user.send(await self.bot._(user, msg, str(before)))

    @commands.hybrid_group(invoke_without_command=True)
    @ut.runnable_check()
    async def onlinenotif(self, ctx):
        """Returns the name of the users you are receiving online notifications of."""
        users = [
            self.bot.get_user(user_id)
            for user_id
            in await self.get_subscribing_of_user(ctx.author)
            if self.bot.shares_guild(ctx.author.id, user_id)
        ]
        if not users:
            return await ctx.author.send(await ctx._("onlinenotif-nousers"))
        await ctx.author.send(await ctx._("onlinenotif-subscribing", " ".join(map(str, users))))

    @onlinenotif.command(aliases=["add"])
    @ut.runnable_check()
    async def subscribe(self, ctx, user: discord.User):
        """Subscribes to this user."""
        subscribing = await self.get_subscribing_of_user(ctx.author)
        if user.id in subscribing:
            return await ctx.say("onlinenotif-already")
        if not self.bot.shares_guild(ctx.author.id, user.id):
            return await ctx.say("onlinenotif-shareGuild")
        subscribing.append(user.id)
        await self.bot.cursor.execute(
            "UPDATE users SET onnotif = %s WHERE id = %s", (json.dumps(subscribing), ctx.author.id))
        await ctx.say("onlinenotif-success")

    @onlinenotif.command(aliases=["remove", "del"])
    @ut.runnable_check()
    async def unsubscribe(self, ctx, user: discord.User):
        """Un-subscribes to this user."""
        subscribing = await self.get_subscribing_of_user(ctx.author)
        if user.id not in subscribing:
            return await ctx.say("onlinenotif-yet")
        subscribing.remove(user.id)
        await self.bot.cursor.execute(
            "UPDATE users SET onnotif = %s WHERE id = %s", (json.dumps(subscribing), ctx.author.id))
        await ctx.say("onlinenotif-removeSuccess")

    @onlinenotif.command()
    @ut.runnable_check()
    async def settings(self, ctx, enabled: bool=False):
        """Choose whether someone can receive your online notification.
        Note that you have to share server with that user."""
        await self.bot.cursor.execute(
            "UPDATE users SET online_agreed = %s WHERE id = %s", (int(enabled), ctx.author.id))
        await ctx.say("onlinenotif-settings")


async def setup(bot):
    await bot.add_cog(OnlineNotif(bot))
