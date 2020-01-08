# -*- coding: utf-8 -*- #

import json
import sqlite3
import pickle

sqlite3.register_converter('pickle', pickle.loads)
sqlite3.register_converter('json', json.loads)
sqlite3.register_adapter(dict, json.dumps)
sqlite3.register_adapter(list, pickle.dumps)
db = sqlite3.connect("sina_datas.db",detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
db.row_factory = sqlite3.Row
cursor = db.cursor()


def textto(k:str,user):
    if type(user) == str:
        lang = user
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
        if lang is None:
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