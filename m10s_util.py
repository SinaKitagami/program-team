# -*- coding: utf-8 -*- #

import json
import sqlite3
import pickle
import discord

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
    if mg and mn:
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

        flags = flags.zfill(20)[::-1]
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
            "Http Interaction Bot":self.http_interaction_bot
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
