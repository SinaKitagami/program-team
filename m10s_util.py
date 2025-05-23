# -*- coding: utf-8 -*- #

import json
import sqlite3
import pickle
import discord

from discord.ext import commands
from discord import app_commands

import aiohttp

#sqlite3.register_converter('pickle', pickle.loads)
#sqlite3.register_converter('json', json.loads)
#sqlite3.register_adapter(dict, json.dumps)
#sqlite3.register_adapter(list, pickle.dumps)
#db = sqlite3.connect(
#    "sina_datas.db", detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
#db.row_factory = sqlite3.Row
#cursor = db.cursor()

# todo: zh-Hans
LANG_CODE = {"ch-TW", "en", "ja"}


def ondevicon(mem):
    tmp = ""
    if not str(mem.desktop_status) == "offline":
        tmp = tmp+"💻"
    if not str(mem.mobile_status) == "offline":
        tmp = tmp+"📱"
    if not str(mem.web_status) == "offline":
        tmp = tmp+"🌐"
    return tmp


def getEmbed(ti, desc, color=int("0x61edff", 16), *optiontext):
    e = discord.Embed(title=ti, description=desc, color=color)
    nmb = -2
    while len(optiontext) >= nmb:
        try:
            nmb = nmb + 2
            e.add_field(name=optiontext[nmb], value=optiontext[nmb+1])
        except IndexError:
            pass
    return e


async def opendm(u):
    dc = u.dm_channel
    if dc is None:
        await u.create_dm()
        dc = u.dm_channel
    return dc


async def wait_message_return(ctx, stext, sto, tout=60):
    await sto.send(stext)
    return await ctx.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == sto, timeout=tout)


def get_vmusic(bot, member):
    mg = None
    mn = None
    ml = False # Default value for ml
    mvc = None  # Initialize mvc to None
    for v in bot.voice_clients:
        vm_m = [i for i in v.channel.members if i.id == member.id]
        if not vm_m == []:
            try:
                mg = v.guild
                mn = bot.qu.get(str(v.guild.id), [])
                ml = bot.lp.get(str(v.guild.id), False)
                mvc = v
                break
            except:
                pass
    if mg and mn and mvc is not None:  # Ensure mvc is not None
        rtn = {
            "name": mn[0]["video_title"],
            "url": mn[0]["video_url"],
            "uploader":mn[0]["video_up_name"],
            "image":mn[0]["video_thumbnail"],
            "guild": mg,

            "queue":mn,
            "isPlaying":mvc.is_playing(),
            "loop":ml,
        }
        if mvc.source:
            rtn["volume"] = mvc.source.volume
        else:
            rtn["volume"] = 0.5
        return rtn
    else:
        return None

def runnable_check():
    async def predicate(ctx):
        if isinstance(ctx, commands.Context) and hasattr(ctx.bot, "comlocks") and ctx.guild:
            if ctx.bot.comlocks.get(str(ctx.guild.id), []):
                if ctx.command.name in ctx.bot.comlocks[str(ctx.guild.id)] and not ctx.author.guild_permissions.administrator and ctx.author.id != 404243934210949120: # comlockされているかどうか
                    return False
        elif isinstance(ctx, discord.Interaction) and hasattr(ctx.client, "comlocks") and ctx.guild:
            if ctx.client.comlocks.get(str(ctx.guild.id), []):
                if ctx.command.name in ctx.bot.comlocks[str(ctx.guild.id)] and not ctx.author.guild_permissions.administrator and ctx.author.id != 404243934210949120: # comlockされているかどうか
                    return False
        if ctx.command.name in ctx.bot.features[0] and (not ctx.author.id in ctx.bot.team_sina): # グローバルfeatureでロックされているかどうか(メンテナンス)
            return False
        elif ctx.command.name in ctx.bot.features.get(ctx.author.id, []) or "cu:cmd" in ctx.bot.features.get(ctx.author.id, []): # featuresでのユーザーごとのコマンドロック
            return False
        elif ctx.guild and (ctx.command.name in ctx.bot.features.get(ctx.guild.id, []) or "cu:cmd" in ctx.bot.features.get(ctx.guild.id, [])): # featuresでのサーバーごとのコマンドロック
            return False
        else:
            return True
    return commands.check(predicate)

def runnable_check_for_appcmd():
    async def predicate(interaction: discord.Interaction):
        if isinstance(interaction, commands.Context) and hasattr(interaction.client, "comlocks") and interaction.guild:
            if interaction.client.comlocks.get(str(interaction.guild.id), []):
                if interaction.command.name in interaction.client.comlocks[str(interaction.guild.id)] and not interaction.user.guild_permissions.administrator and interaction.user.id != 404243934210949120: # comlockされているかどうか
                    return False
        if interaction.command.name in interaction.client.features[0] and (not interaction.user.id in interaction.client.team_sina): # グローバルfeatureでロックされているかどうか(メンテナンス)
            return False
        elif interaction.command.name in interaction.client.features.get(interaction.user.id, []) or "cu:cmd" in interaction.client.features.get(interaction.user.id, []): # featuresでのユーザーごとのコマンドロック
            return False
        elif interaction.guild and (interaction.command.name in interaction.client.features.get(interaction.guild.id, []) or "cu:cmd" in interaction.client.features.get(interaction.guild.id, [])): # featuresでのサーバーごとのコマンドロック
            return False
        else:
            return True
    return app_commands.check(predicate)

async def get_badges(bot, user):
    headers = {
        "User-Agent": "DiscordBot (sina-chan with discord.py)",
        "Authorization": f"Bot {bot.http.token}"
    }
    uid = user.id

    async with bot.session.get(f"https://discord.com/api/v10/users/{uid}", headers=headers) as resp:
        resp.raise_for_status()
        rq = await resp.json()
    return m10s_badges(rq["public_flags"])


class m10s_badges:

    def __init__(self, flags):

        self.raw_flags = flags
        flags = format(flags, "b")

        flags = flags.zfill(24)[::-1]
        self.staff = flags[0] == "1"
        self.partner = flags[1] == "1"
        self.hypesquad_events = flags[2] == "1"
        self.bug_hunter_1 = flags[3] == "1"
        self.hypesquad_h_bravery = flags[6] == "1"
        self.hypesquad_h_brilliance = flags[7] == "1"
        self.hypesquad_h_balance = flags[8] == "1"
        self.ealry_supporter = flags[9] == "1"
        self.team_user = flags[10] == "1"
        self.system = flags[12] == "1"
        self.bug_hunter_2 = flags[14] == "1"
        self.verified_bot = flags[16] == "1"
        self.early_verified_bot_developer = flags[17] == "1"
        self.discord_certified_moderator = flags[18] == "1"
        self.http_interaction_bot = flags[19] == "1"
        self.active_developer = flags[22] == "1"
        self.supports_commands = flags[23] == "1"

        self.dict_flags = {
            "Discord Staff": self.staff,
            "Partnered Server Owner": self.partner,
            "Hypesquad Events": self.hypesquad_events,
            "Bug Hunter Level 1": self.bug_hunter_1,
            "House Bravery": self.hypesquad_h_bravery,
            "House Brilliance": self.hypesquad_h_brilliance,
            "House Balance": self.hypesquad_h_balance,
            "Early Supporter": self.ealry_supporter,
            "Team User": self.team_user,
            "System": self.system,
            "Bug Hunter Level 2": self.bug_hunter_2,
            "Verified Bot": self.verified_bot,
            "Early Verified Bot Developer": self.early_verified_bot_developer,
            "Discord Certified Moderator":self.discord_certified_moderator,
            "Http Interaction Bot":self.http_interaction_bot,
            "Active Developer":self.active_developer,
            "Supports commands":self.supports_commands
        }

        self.n = 0

    def __eq__(self, arg):
        if isinstance(arg,m10s_badges):
            return self.raw_flags == arg.raw_flags
        else:
            return False

    def __str__(self):
        return ",".join(self.get_list)

    def __ne__(self, o: object):
        return not self.__eq__(o)

    def __hash__(self):
        return self.raw_flags

    def get_dict(self):
        return self.dict_flags

    def get_list(self):
        return [bn for bn, bl in self.dict_flags.items() if bl]

