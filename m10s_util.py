# -*- coding: utf-8 -*- #

import json
import sqlite3
import pickle
import discord

sqlite3.register_converter('pickle', pickle.loads)
sqlite3.register_converter('json', json.loads)
sqlite3.register_adapter(dict, json.dumps)
sqlite3.register_adapter(list, pickle.dumps)
db = sqlite3.connect("sina_datas.db",detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
db.row_factory = sqlite3.Row
cursor = db.cursor()

# todo: zh-Hans
LANG_CODE = {"ch-TW", "en", "ja"}

def textto(k:str,user):
    if type(user) == str:
        lang = user
        try:
            if lang not in LANG_CODE:
                raise ValueError("invalid lang")
            with open(f"lang/{lang}.json","r",encoding="utf-8") as j:
                f = json.load(j)
        except:
            return f"Not found language:`{lang}`(key:`{k}`)"
        try:
            return f[k]
        except:
            return f"Not found key:`{k}`"
    elif isinstance(user,discord.Guild):
        try:
            cursor.execute("select * from guilds where id=?",(user.guild.id,))
            gpf = cursor.fetchone()
        except:
            gpf={"lang":None}
        lang = gpf["lang"]
        if lang not in LANG_CODE:
            lang = "ja"
        try:
            with open(f"lang/{lang}.json","r",encoding="utf-8") as j:
                f = json.load(j)
        except:
            return f"Not found language:`{lang}`(key:`{k}`)"
        try:
            return f[k]
        except:
            return f"Not found key:`{k}`"
    else:
        cursor.execute("select * from users where id=?",(user.id,))
        upf = cursor.fetchone()
        try:
            cursor.execute("select * from guilds where id=?",(user.guild.id,))
            gpf = cursor.fetchone()
        except:
            gpf={"lang":None}
        lang = upf["lang"]
        if lang is None:
            lang = gpf["lang"]
        if lang not in LANG_CODE:
            lang = "ja"
        try:
            with open(f"lang/{lang}.json","r",encoding="utf-8") as j:
                f = json.load(j)
        except:
            return f"Not found language:`{lang}`(key:`{k}`)"
        try:
            return f[k]
        except:
            return f"Not found key:`{k}`"

def ondevicon(mem):
    tmp = ""
    if not str(mem.desktop_status)=="offline":
        tmp = tmp+"💻"
    if not str(mem.mobile_status)=="offline":
        tmp = tmp+"📱"
    if not str(mem.web_status)=="offline":
        tmp = tmp+"🌐"
    return tmp

def getEmbed(ti,desc,color=int("0x61edff",16),*optiontext):
    e = discord.Embed(title=ti,description=desc,color=color)
    nmb = -2
    while len(optiontext) >= nmb:
        try:
            nmb = nmb + 2
            e.add_field(name=optiontext[nmb],value=optiontext[nmb+1])
        except IndexError:
            pass
    return e

async def opendm(u):
    dc = u.dm_channel
    if dc == None:
        await u.create_dm()
        dc = u.dm_channel
    return dc

async def wait_message_return(ctx,stext,sto,tout=60):
    await sto.send(stext)
    return await ctx.bot.wait_for('message', check=lambda m: m.author==ctx.author and m.channel==sto,timeout=tout)

def get_vmusic(bot,member):
    mg=None
    mn=None
    for v in bot.voice_clients:
        vm_m = [i for i in v.channel.members if i.id == member.id]
        if not vm_m==[]:
            try:
                mg=v.guild
                mn=bot.qu.get(str(v.guild.id),[])[0]
                break
            except:
                pass
    if mg and mn:
        return {
            "name":mn["video_title"],
            "url":mn["video_url"],
            "guild":mg
        }
    else:
        return None
