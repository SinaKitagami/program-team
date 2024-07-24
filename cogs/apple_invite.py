import discord
from discord.ext import commands, tasks

import m10s_util as ut

class AppleInviteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.cursor
        self._lock = False

    async def get_log_channel(self, guild_id):
        guild = await self.db.fetchone("SELECT * FROM guilds WHERE id=%s", (guild_id,))
        #guild = await self.bot.cursor.fetchone()
        if not guild:
            return None
        if guild["sendlog"]:
            return self.bot.get_channel(guild["sendlog"])
        return None

    async def delete_invite(self, code):
        await self.db.execute("DELETE FROM invites WHERE id = %s", (code,))

    async def add_invite(self, invite):
        # Validate the Invite. If those are missing, we have to return.
        if not all((
            invite,
            hasattr(invite, "code"),
            invite.code,
            hasattr(invite, "guild"),
            invite.guild,
            isinstance(invite.guild, discord.Guild)
        )):
            return

        if not await self.get_log_channel(invite.guild.id):
            return

        if not self.bot.apple_util.has_all_perms(
            invite.guild.me,
            None,
            'manage_guild',
            'create_instant_invite',
            'manage_channels'
        ):
            return

        # If inviter is missing, refetch.
        if not all((
            hasattr(invite, "inviter"),
            invite.inviter,
            isinstance(invite.inviter, discord.abc.User)
        )):
            invites = await invite.guild.invites()
            invite = discord.utils.get(invites, code=invite.code)

        await self.db.execute("INSERT INTO invites values (%s, %s, 0, %s)", (
            invite.code,
            invite.guild.id,
            invite.inviter.id
        ))

    async def sync_invites(self):
        p = await self.bot.cursor.fetchall("SELECT id FROM guilds WHERE sendlog IS NOT NULL")
        guilds = [
            self.bot.get_guild(g["id"])
            for g
            in p
            if self.bot.get_guild(g["id"])
        ]
        touched_invites = set()
        for guild in guilds:
            if not self.bot.apple_util.has_all_perms(
                guild.me,
                None,
                "manage_guild",
                "create_instant_invite",
                "manage_channels"
            ):
                continue
            invites = await guild.invites()
            touched_invites |= set(i.code for i in invites)
            
            for invite in invites:
                a = await self.bot.cursor.fetchone("SELECT id FROM invites WHERE id = %s", (invite.code,))
                if a:
                    # invite exists, updating
                    await self.db.execute(
                        "UPDATE invites SET uses = %s WHERE id = %s", (invite.uses, invite.code))
                else:
                    await self.add_invite(invite)
        b = await self.bot.cursor.fetchall("SELECT id FROM invites")
        invites_in_db = set(i["id"] for i in b)
        needs_deletion = invites_in_db.difference(touched_invites)
        [await self.delete_invite(i) for i in needs_deletion]

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.delete_invite(invite.code)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.add_invite(invite)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.sync_invites()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self._lock = True
        guild = member.guild
        log_ch = await self.get_log_channel(guild.id)
        if not log_ch:
            self._lock = False
            return
        used_invites = []
        invites = await guild.invites()
        invites_in_db = await self.db.fetchall("SELECT * FROM invites WHERE guild_id = %s", (guild.id,))
        #invites_in_db = await self.bot.cursor.fetchall()
        for invite in invites:
            invite_db = discord.utils.find(
                lambda i: i["id"] == invite.code, invites_in_db)
            if invite.uses > invite_db["uses"]:
                used_invites = [{
                    "code": invite.code,
                    "inviter": invite.inviter
                }]
                await self.db.execute(
                    "UPDATE invites SET uses = %s WHERE id = %s", (invite.uses, invite.code))
                break
        if not used_invites:
            await self.bot.cursor.execute("SELECT id FROM invites")
            db_set = set(i["id"] for i in await self.bot.cursor.fetchall())
            api_set = set(i.code for i in invites)
            diff = db_set.difference(api_set)
            used_invites = [
                {"code": code, "inviter": self.bot.get_user(discord.utils.find(
                    lambda i: i["id"] == code, invites_in_db)["inviter"])}
                for code
                in diff
            ]
            _ = [await self.delete_invite(i) for i in diff]
        self._lock = False
        self.bot.dispatch('member_join_with_invites', member, used_invites)

    @tasks.loop(minutes=10)
    async def invite_checker(self):
        if self._lock:
            return
        await self.sync_invites()

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        if event == "on_member_join":
            self._lock = False

    @commands.Cog.listener()
    async def on_member_join_with_invites(self, member, invites):
        log_ch = await self.get_log_channel(member.guild.id)
        e = discord.Embed(title=f"{str(member)}の招待の情報",
                          description=str(member.id))
        e.set_thumbnail(url=str(member.avatar))
        for i in invites:
            e.add_field(
                name=f"招待はこれかも? {i['code']}", value=f"{str(i['inviter'])} - {i['inviter'].id}")
        await log_ch.send(embed=e)

    @commands.command(hidden=True)
    @commands.guild_only()
    @ut.runnable_check()
    @commands.has_permissions(manage_guild=True, create_instant_invite=True)
    async def checkoffline(self, ctx):
        self._lock = True
        i = await ctx.channel.create_invite(max_uses=1, max_age=0, reason="temporary invite")
        i2 = await self.bot.fetch_invite(i.code)
        pc = i2.approximate_presence_count
        await i.delete()
        online = len(
            [m for m in ctx.guild.members if m.status is not discord.Status.offline and await self.bot.can_use_online(m)])
        await ctx.author.send(f"オンライン隠し: {pc - online}人")


async def setup(bot):
    await bot.add_cog(AppleInviteCog(bot))
