# -*- coding: utf-8 -*- #

import json
import sqlite3
import pickle
import discord

import aiohttp

sqlite3.register_converter('pickle', pickle.loads)
sqlite3.register_converter('json', json.loads)
sqlite3.register_adapter(dict, json.dumps)
sqlite3.register_adapter(list, pickle.dumps)
db = sqlite3.connect(
    "sina_datas.db", detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
db.row_factory = sqlite3.Row
cursor = db.cursor()

# todo: zh-Hans
LANG_CODE = {"ch-TW", "en", "ja"}


def textto(k: str, user):
    if type(user) == str:
        lang = user
        try:
            if lang not in LANG_CODE:
                raise ValueError("invalid lang")
            with open(f"lang/{lang}.json", "r", encoding="utf-8") as j:
                f = json.load(j)
        except:
            return f"Not found language:`{lang}`(key:`{k}`)"
        try:
            return f[k]
        except:
            return f"Not found key:`{k}`"
    elif isinstance(user, discord.Guild):
        try:
            cursor.execute("select * from guilds where id=?", (user.guild.id,))
            gpf = cursor.fetchone()
        except:
            gpf = {"lang": None}
        lang = gpf["lang"]
        if lang not in LANG_CODE:
            lang = "ja"
        try:
            with open(f"lang/{lang}.json", "r", encoding="utf-8") as j:
                f = json.load(j)
        except:
            return f"Not found language:`{lang}`(key:`{k}`)"
        try:
            return f[k]
        except:
            return f"Not found key:`{k}`"
    else:
        cursor.execute("select * from users where id=?", (user.id,))
        upf = cursor.fetchone()
        try:
            cursor.execute("select * from guilds where id=?", (user.guild.id,))
            gpf = cursor.fetchone()
        except:
            gpf = {"lang": None}
        lang = upf["lang"]
        if lang is None:
            lang = gpf["lang"]
        if lang not in LANG_CODE:
            lang = "ja"
        try:
            with open(f"lang/{lang}.json", "r", encoding="utf-8") as j:
                f = json.load(j)
        except:
            return f"Not found language:`{lang}`(key:`{k}`)"
        try:
            return f[k]
        except:
            return f"Not found key:`{k}`"


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
                mn = bot.qu.get(str(v.guild.id), [])[0]
                break
            except:
                pass
    if mg and mn:
        return {
            "name": mn["video_title"],
            "url": mn["video_url"],
            "guild": mg
        }
    else:
        return None


async def get_badges(bot, user):
    headers = {
        "User-Agent": "DiscordBot ()",
        "Authorization": f"Bot {bot.http.token}"
    }
    uid = user.id

    async with bot.session.get(f"https://discord.com/api/v6/users/{uid}", headers=headers) as resp:
        resp.raise_for_status()
        rq = await resp.json()
    return m10s_badges(rq["public_flags"])


class m10s_badges:

    def __init__(self, flags):

        self.raw_flags = flags
        flags = format(flags, "b")

        flags = flags.zfill(18)[::-1]
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
        self.verified_bot_developer = flags[17] == "1"

        self.dict_flags = {
            "Discord Staff": self.staff,
            "Discord Partner": self.partner,
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
            "Verified Bot Developer": self.verified_bot_developer,
        }

    def get_dict(self):
        return self.dict_flags

    def get_list(self):
        return [bn for bn, bl in self.dict_flags.items() if bl]