# -*- coding: utf-8 -*- #

from cogs import apple_invite
from cogs import apple_foc
import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import random
import wikipedia
import wikidata.client
import asyncio
import datetime
import traceback

import aiohttp
import aiosqlite
import database

from twitter import *
from dateutil.relativedelta import relativedelta as rdelta

from my_module import dpy_interaction as dpyui

# textto etc
import m10s_util as ut
from apple_util import AppleUtil
from l10n import TranslateHandler, LocalizedContext
from checker import MaliciousInput, content_checker
# tokens
import config

import logging
import sys

logging.basicConfig(filename = config.LOG_FILE, encoding='utf-8', format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

syslogger = logging.getLogger()

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))

syslogger.addHandler(stdout_handler)

# logging.basicConfig(level=logging.DEBUG)

intents:discord.Intents = discord.Intents.default()
intents.typing = False
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.AutoShardedBot(command_prefix="s-", status=discord.Status.invisible,
                   allowed_mentions=discord.AllowedMentions(everyone=False),
                   intents=intents,
                   enable_debug_events=True,
                   )

"""bot = commands.Bot(command_prefix="s-", status=discord.Status.invisible,
                   allowed_mentions=discord.AllowedMentions(everyone=False),
                   intents=intents,
                   enable_debug_events=True,
                   shard_id=0,
                   shard_count=2
                   )"""
bot.owner_id = None
bot.owner_ids = {404243934210949120, 525658651713601536}
bot.maintenance = False


bot.dpyui = dpyui.interaction_actions(bot)

bot.team_sina = config.team_sina

bot.comlocks = {}

# トークンたち
bot.BOT_TEST_TOKEN = config.BOT_TEST_TOKEN
bot.BOT_TOKEN = config.BOT_TOKEN
bot.NAPI_TOKEN = config.NAPI_TOKEN
bot.GAPI_TOKEN = config.GAPI_TOKEN
bot.T_API_key = config.T_API_key
bot.T_API_SKey = config.T_API_SKey
bot.T_Acs_Token = config.T_Acs_Token
bot.T_Acs_SToken = config.T_Acs_SToken


# test
postcount = {}

db = None

async def db_setup():
    global db
    try:
        #db = await aiomysql.connect(host=config.DB_HOST,
        #    user=config.DB_USER,
        #    password=config.DB_PW,
        #    db=config.DB_NAME,
        #    loop=main_loop,
        #    autocommit=True,
        #    charset="utf8mb4"
        #    )
        bot.cursor = database.Database(host=config.DB_HOST, port=3306, user=config.DB_USER, password=config.DB_PW, db=config.DB_NAME)
        #bot.cursor = await db.cursor(aiomysql.DictCursor)

    except:
        traceback.print_exc()

async def main():
    async with bot:
        await db_setup()

        await bot.load_extension("cogs.apple_misc")
        await bot.load_extension("cogs.apple_onlinenotif")

        await apple_invite.setup(bot)
        await apple_foc.setup(bot)

        bot.session = aiohttp.ClientSession(loop=bot.loop)

        # 通常トークン
        await bot.start(bot.BOT_TOKEN)

        # テストトークン
        # await bot.start(bot.BOT_TEST_TOKEN)


bot._default_close = bot.close


async def close_handler():
    await bot._default_close()
    await bot.session.close()
    try:
        await db.commit()
    except aiosqlite.ProgrammingError:
        pass
    else:
        await db.close()
bot.close = close_handler

bot.translate_handler = TranslateHandler(bot, ["en", "ja"])
bot._get_context = bot.get_context


async def get_context(msg, cls=LocalizedContext):
    ctx = await bot._get_context(msg, cls=cls)
    ctx.context_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
    return ctx
bot.get_context = get_context

def create_emoji_str(name:str, id:int, is_animate:bool = False):
    return f'<{"a" if is_animate else ""}:{name}:{id}>'

bot.create_emoji_str = create_emoji_str

bot._ = bot.translate_handler.get_translation_for
bot.l10n_guild = bot.translate_handler.get_guild_translation_for
bot.l10n_any = bot.translate_handler.get_any_translation
bot.l10n_raw = bot.translate_handler.get_raw_translation

"""
au_w:[
        {
            "reactions":["str" or "id"(0-19)],
            "give_role"[None or id(int)],
            "text":str""
        },...
    ]
"""


DoServercmd = False
gprofilever = "v1.0.1"
wikipedia.set_lang('ja')
bot.mwc = wikidata.client.Client()
rpcct = 0
rpcs = [
    "ヘルプ:/help",
    "アイコン:しおさばきゅーさん",
    "サーバー数:{0}/ユーザー数:{1}",
    "シャード番号:{2}",
    "作成:チーム☆思惟奈ちゃん",
    "help:/help",
    "icon:しおさばきゅー",
    "{0}guilds/{1}users",
    "shard id:{2}",
    "created by team-sina"
]
"""db = dropbox.Dropbox(DROP_TOKEN)
db.users_get_current_account()"""
bot.twi = Twitter(auth=OAuth(
    bot.T_Acs_Token, bot.T_Acs_SToken, bot.T_API_key, bot.T_API_SKey))
bot.ec = 0x42bcf4
Donotif = False
bot.StartTime = datetime.datetime.now(datetime.timezone.utc)

aglch = None


bot.features = config.sp_features

bot.apple_util = AppleUtil(bot)


def shares_guild(user_id_a, user_id_b):
    return not not [
        guild
        for guild
        in bot.guilds
        if set([user_id_a, user_id_b]).issubset(frozenset(guild._members.keys()))
    ]


bot.shares_guild = shares_guild


async def can_use_online(user):
    enabled = await bot.cursor.fetchone("SELECT online_agreed FROM users WHERE id = %s", (user.id,))
    #enabled = await bot.cursor.fetchone()
    return enabled and enabled["online_agreed"]


bot.can_use_online = can_use_online

# 初回ロード
"""db.files_download_to_file( "guildsetting.json" , "/guildsetting.json" )
db.files_download_to_file( "profiles.json" , "/profiles.json" )
db.files_download_to_file( "gp.json" , "/gp.json" )
db.files_download_to_file( "globaldatas.json" , "/globaldatas.json" )
db.files_download_to_file( "gchatchs.json" , "/gchatchs.json" )"""

bot.gguide = """グローバルチャット利用規約は以下リンクよりご確認いただけます
https://home.sina-chan.com/legal/gchat-tos
変更履歴はこちらから
https://home.sina-chan.com/legal/release-note
"""


@tasks.loop(minutes=20.0)
async def cRPC():
    global rpcct
    if rpcct == 7:
        rpcct = 0
    else:
        rpcct = rpcct+1
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=rpcs[rpcct].format(len(bot.guilds), len(bot.users), bot.shard_id)))



@bot.event
async def on_ready():
    global aglch
    print('ログインしました。')
    print(bot.user.name)
    print(bot.user.id)
    print('------------------')
    # aglch = await bot.fetch_channel(659706303521751072)
    # pmsgc = await bot.fetch_channel(676371380111015946)
    cRPC.start()
    """invite_tweet.start()
    now_sina_tweet.start()"""
    await bot.load_extension("jishaku")
    
    files = [
            "m10s_info", "m10s_owner", "m10s_settings", "m10s_manage",
            "m10s_other", "m10s_search", "m10s_games", "P143_jyanken",
            "nekok500_mee6", "pf9_symmetry", "syouma", "m10s_bmail",
            "m10s_auth_wiz",
            "m10s_role_panel", "m10s_partners", "m10s_remainder", "m10s_set_activity_roles",

            "m10s_api", "m10s_app_metadata",
            
            # "__part_pjsekai_music_select"
            "slash.pjsekai_music_select", # 思惟奈ちゃんパートナー向け機能-ぱすこみゅ
            "slash.mini_features", # -> スポイラー展開
            "slash.m10s_messageinfo", # -> メッセージコマンドでの実行

            "hybrid.m10s_re_gchat",
            "hybrid.m10s_quick_cmd",
            "hybrid.m10s_levels",
            "hybrid.m10s_music",
            "hybrid.info_check",
            "hybrid.m10s_help",
            "m10s_guild_log",
            "m10s_direct_msg"
            ]
    
    embed = discord.Embed(title="読み込みに失敗したCog", color=bot.ec)
    txt = ""
    for file in files:
        try:
            await bot.load_extension(f"cogs.{file}")
        except:

            traceback.print_exc()
            print(f"Extension {file} Load Failed.")
            txt += f"`{file}`, "
        else:
            print(f"Extension {file} Load.")
    embed.description = txt

    # テストサバ
    # await bot.tree.sync(guild=discord.Object(id=560434525277126656))

    # パートナーコマンド
    # await bot.tree.sync(guild=discord.Object(id=764088457785638922))

    # グローバルコマンド
    await bot.tree.sync()

    boot_info_channel_id = 595526013031546890

    try:
        ch = bot.get_channel(boot_info_channel_id)
        if ch == None:
            try:
                await bot.fetch_channel(boot_info_channel_id)
            except:
                return
        e=discord.Embed(title="起動時インフォメーション", description=f"シャードID:{bot.shard_id}\nシャード内認識ユーザー数:{len(bot.users)}\nシャード内認識サーバー数:{len(bot.guilds)}\nシャード内認識チャンネル数:{len([c for c in bot.get_all_channels()])}\ndiscord.py ver_{discord.__version__}", color=bot.ec)
        await ch.send(f"{bot.create_emoji_str('s_online',653161518531215390)}on_ready!", embed=e)
        if txt:
            await ch.send(embed=embed)
    except:
        pass


@bot.event
async def on_message(message):
    if "cu:on_msg" in bot.features.get(message.author.id, []):
        return
    if "cu:on_msg" in bot.features.get(getattr(message.guild, "id", None), []):
        return
    if isinstance(message.channel, discord.DMChannel):
        return
    if message.webhook_id:
        return
    if message.author.id == bot.user.id:
        return
    if postcount.get(str(message.guild.id), None) is None:
        postcount[str(message.guild.id)] = 1
    else:
        postcount[str(message.guild.id)] += 1
    # if message.content == "check_msgs":
        # on_messageを呼ぶだけの処理がすぐに終わるかの確認
        # with open("post_count.json", mode="w", encoding="utf-8") as f:
            # json.dump(postcount, f, indent=4)
        # await message.channel.send(file=discord.File("post_count.json"))
    # db.files_download_to_file( "guildsetting.json" , "/guildsetting.json" )
    # db.files_download_to_file( "profiles.json" , "/profiles.json" )
    tks = [
        domsg(message)
        # globalSend(message), グローバルチャットは進化した！ -> cogs.m10s_re_gchat
    ]
    await asyncio.gather(*tks)
    # await domsg(message)
    # await globalSend(message)


async def domsg(message):
    global DoServercmd

    if not message.author.id in bot.team_sina:
        if bot.maintenance:
            return
        else:
            pass
    else:
        pass

    gs = await bot.cursor.fetchone("select * from guilds where id=%s", (message.guild.id,))
    #gs = await bot.cursor.fetchone()
    if not gs:
        guild_lang = await bot.translate_handler.get_lang_by_guild(
            message.guild, False)
        await bot.cursor.execute("INSERT INTO guilds(id,levels,commands,hash,levelupsendto,reward,jltasks,lockcom,sendlog,prefix,lang,verified) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (message.guild.id, "{}", "{}", "[]", None, "{}", "{}", "[]", None, "[]", guild_lang, 0))
        try:
            await message.channel.send(f"{bot.create_emoji_str('s_profile_created', 653161518153596950)}このサーバーの思惟奈ちゃんサーバープロファイルを作成しました！いくつかの項目はコマンドを使って書き換えることができます。詳しくはヘルプ(`s-help`)をご覧ください。\nまた、不具合や疑問点などがありましたら`mii-10#3110`にお願いします。\n思惟奈ちゃんのお知らせは`/rnotify [チャンネル(省略可能)]`で、コマンド等の豆知識は`/rtopic [チャンネル(省略可能)]`で受信する設定にできます。(Webhook管理権限が必要です。)")
        except:
            pass
        gs = await bot.cursor.fetchone("select * from guilds where id=%s",
                           (message.guild.id,))
        #gs = await bot.cursor.fetchone()

    pf = await bot.cursor.fetchone("select * from users where id=%s", (message.author.id,))
    #pf = await bot.cursor.fetchone()
    if not pf:
        if message.is_system():
            return
        
        try:
            await bot.cursor.execute("INSERT INTO users(id,prefix,gpoint,memo,levcard,onnotif,lang,sinapartner,gban,gnick,gcolor,gmod,gstar,galpha,gbanhist,online_agreed, agree_to_gchat_tos) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (message.author.id, "[]", 0, "{}", "m@ji☆", "[]", "ja", 0, 0, message.author.name, 0, 0, 0, 0, "なし", 0, 0))
        except Exception as exc:
            print(exc)
            
        try:
            if not "disable_profile_msg" in json.loads(gs["lockcom"]):
                await message.add_reaction(bot.create_emoji_str("s_profile_created",653161518153596950))
        except:
            pass
        pf = await bot.cursor.fetchone("select * from users where id=%s",
                        (message.author.id,))
        #pf = await bot.cursor.fetchone()

    """await bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS actrole_optin(id integer PRIMARY KEY NOT NULL, is_enable integer NOT NULL default 0);")"""

    data = await bot.cursor.fetchone("select * from actrole_optin where id=%s", (message.author.id,))
    if not data:
        if message.is_system():
            return
        await bot.cursor.execute("INSERT INTO actrole_optin(id,is_enable) VALUES(%s,%s)",
                        (message.author.id, 0))
        data = await bot.cursor.execute("select * from actrole_optin where id=%s",
                        (message.author.id,))


    tks = [
        asyncio.ensure_future(gahash(message, gs)),
        asyncio.ensure_future(runsercmd(message, gs, pf))
    ]
    await asyncio.gather(*tks)

    try:
        tpf = json.loads(pf["prefix"]) + json.loads(gs["prefix"])
    except:
        tpf = []
    if not ("disable_defprefix" in json.loads(gs["lockcom"])):
        tpf.insert(0,"s-")
    bot.command_prefix = tpf
    bot.comlocks[str(message.guild.id)] = json.loads(gs["lockcom"])
    if message.author.id in bot.team_sina:
        await bot.process_commands(message)
    else:
        for pf in tpf:
            if message.content.startswith(pf):
                if ("disable_prefix_cmd" in bot.features[0]):
                    await message.channel.send("> お知らせ\n　メッセージコンテントインテントの特権化に伴い、ご利用の呼び出し方法はサポートされません。\n　スラッシュコマンドで利用していただくよう、お願いします。")
                    break
                else:
                    await message.channel.send("> お知らせ\n　メッセージコンテントインテントの特権化に伴い、ご利用の呼び出し方法は近日サポートを終了します。\n　スラッシュコマンドで利用していただくよう、お願いします。")
                    break
        if not "disable_prefix_cmd" in bot.features[0]:
            await bot.process_commands(message)

async def runsercmd(message, gs, pf):
    if "cu:cmd" in bot.features.get(message.author.id, []):
        return
    if "cu:cmd" in bot.features.get(message.guild.id, []):
        return
    # servercmd
    if "scom" not in json.loads(gs["lockcom"]):
        if not message.author.id == bot.user.id and message.webhook_id is None:
            try:
                tpf = json.loads(pf["prefix"]) + json.loads(gs["prefix"])
            except:
                tpf = []
            tpf.append("s-")
            try:
                if not json.loads(gs["commands"]) is None:
                    cmds = json.loads(gs["commands"])
                    ctts = message.content.split(" ")
                    for k, v in cmds.items():
                        for px in tpf:
                            if px+k == ctts[0]:
                                DoServercmd = True
                                if v["mode"] == "random":
                                    await message.channel.send(random.choice(v["rep"]))
                                elif v["mode"] == "one":
                                    await message.channel.send(v["rep"])
                                elif v["mode"] == "role":
                                    try:
                                        role = message.guild.get_role(v["rep"])
                                    except:
                                        await message.channel.send(await bot._(message.author, "scmd-notfound-role"))
                                        return
                                    if role < message.author.top_role:
                                        if role in message.author.roles:
                                            await message.author.remove_roles(role)
                                            await message.channel.send(await bot._(message.author, "scmd-delrole"))
                                        else:
                                            await message.author.add_roles(role)
                                            await message.channel.send(await bot._(message.author, "scmd-addrole"))
                                    else:
                                        await message.channel.send(await bot._(message.author, "scmd-notrole"))
                                break
            except:
                pass


async def gahash(message, gs):
    # hash
    if "cu:auto_sends" in bot.features.get(message.author.id,[]):
        return
    if "cu:auto_sends" in bot.features.get(message.guild.id,[]):
        return
    try:
        if "s-noHashSend" in (message.channel.topic or ""):
            return
    except:
        pass
    if "shash" not in json.loads(gs["lockcom"]):
        ch = json.loads(gs["hash"])
        if ch:
            menchan = message.channel_mentions
            for sch in menchan:
                if sch.id in ch:
                    if message.channel.is_nsfw():
                        embed = discord.Embed(title="", description=await bot.l10n_guild(
                            message.guild, "hash-nsfw"), color=message.author.color)
                        embed.add_field(name=await bot.l10n_guild(message.guild, "hash-from"),
                                        value=f'{await bot.l10n_guild(message.guild,"hash-chmention")}:{message.channel.mention}\n{await bot.l10n_guild(message.guild,"hash-chname")}:{message.channel.name}')
                        embed.add_field(name=await bot.l10n_guild(
                            message.guild, "hash-link"), value=message.jump_url)
                        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.replace(
                            static_format='png'))
                    else:
                        embed = discord.Embed(
                            title="", description=message.content, color=message.author.color)
                        embed.add_field(name=await bot.l10n_guild(message.guild, "hash-from"),
                                        value=f'{await bot.l10n_guild(message.guild,"hash-chmention")}:{message.channel.mention}\n{await bot.l10n_guild(message.guild,"hash-chname")}:{message.channel.name}')
                        embed.add_field(name=await bot.l10n_guild(
                            message.guild, "hash-link"), value=message.jump_url)
                        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.replace(
                            static_format='png'))
                        if not message.attachments == [] and (not message.attachments[0].is_spoiler()):
                            embed.set_image(url=message.attachments[0].url)
                    await sch.send(embed=embed)



@commands.is_owner()
@ut.runnable_check()
@bot.command()
async def ldb(ctx, name):
    sddb = await bot.cursor.fetchall(f"select * from {name}")
    #sddb = await bot.cursor.fetchall()
    await ctx.send(f"{len(sddb)}")


@commands.is_owner()
@ut.runnable_check()
@bot.command()
async def mentdb(ctx):
    sddb = await bot.cursor.fetchall(f"select * from users")
    #sddb = await bot.cursor.fetchall()
    async with ctx.channel.typing():
        for ctt in sddb:
            if not (ctt["id"] in [i.id for i in bot.users]):
                await bot.cursor.execute(f"delete from users where id = {ctt['id']}")
    await ctx.send("完了しました☆")

@commands.is_owner()
@ut.runnable_check()
@bot.command()
async def maintenance(ctx):
    if bot.maintenance:
        bot.maintenance = False
        await ctx.send("falseにしたよ")
    else:
        bot.maintenance = True
        await ctx.send("trueにしたよ")

@bot.command(description="思惟奈ちゃんの豆知識チャンネルをフォローします。")
@app_commands.describe(ch="受け取るチャンネル")
@commands.bot_has_permissions(manage_webhooks=True)
@commands.has_permissions(administrator=True)
@ut.runnable_check()
async def rnotify(ctx, ch: discord.TextChannel=None):
    if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
        tch = ch or ctx.channel
        fch = await bot.fetch_channel(667351221106901042)
        await fch.follow(destination=tch)
        await ctx.send("フォローが完了しました。")
    else:
        await ctx.send("サーバー管理者である必要があります。")


@bot.hybrid_command(description="トピックチャンネルをフォローします")
@app_commands.describe(ch="受け取るチャンネル")
@commands.bot_has_permissions(manage_webhooks=True)
@commands.has_permissions(administrator=True)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.bot_has_permissions(manage_webhooks=True)
@ut.runnable_check()
@ut.runnable_check_for_appcmd()
async def rtopic(ctx, ch:discord.TextChannel=None):
    if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
        tch = ch or ctx.channel
        fch = await bot.fetch_channel(677862542298710037)
        await fch.follow(destination=tch)
        await ctx.send("フォローが完了しました。")
    else:
        await ctx.send("サーバー管理者である必要があります。")



@bot.event
async def on_command(ctx:commands.Context):
    if ctx.interaction:return
    ch = await bot.fetch_channel(693048961107230811)
    e = discord.Embed(title=f"prefixコマンド:{ctx.command.full_parent_name}の実行",
                      description=f"実行文:`{ctx.message.clean_content}`", color=bot.ec)
    e.set_author(name=f"実行者:{str(ctx.author)}({ctx.author.id})",
                 icon_url=ctx.author.display_avatar.replace(static_format="png").url)
    if ctx.guild:
        if ctx.guild.icon:
            e.set_footer(text=f"実行サーバー:{ctx.guild.name}({ctx.guild.id})",
                        icon_url=ctx.guild.icon.replace(static_format="png").url)
        else:
            e.set_footer(text=f"実行サーバー:{ctx.guild.name}({ctx.guild.id})")
    else:
        e.set_footer(text=f"DM/グループDMでの実行")
    e.add_field(name="実行チャンネル", value=getattr(ctx.channel,"name", "DMでの実行"))
    e.timestamp = ctx.message.created_at
    await ch.send(embed=e)

@bot.event
async def on_interaction(interaction:discord.Interaction):
    ch = await bot.fetch_channel(693048961107230811)
    e = discord.Embed(title=f"スラッシュコマンド:{interaction.command.qualified_name}の実行",color=bot.ec)
    e.set_author(name=f"実行者:{str(interaction.user)}({interaction.user.id})",
                 icon_url=interaction.user.display_avatar.replace(static_format="png").url)
    if interaction.guild:
        if interaction.guild.icon:
            e.set_footer(text=f"実行サーバー:{interaction.guild.name}({interaction.guild.id})",
                    icon_url=interaction.guild.icon.replace(static_format="png").url)
        else:
            e.set_footer(text=f"実行サーバー:{interaction.guild.name}({interaction.guild.id})")
    else:
        e.set_footer(text=f"DM/グループDMでの実行")
    e.add_field(name="実行チャンネル", value=getattr(interaction.channel,"name", "DMでの実行"))
    e.timestamp = interaction.created_at
    await ch.send(embed=e)


@bot.event
async def on_command_error(ctx, error):
    # await ctx.send(f"{error}")
    # global DoServercmd
    """if isinstance(error, commands.CommandNotFound):
        if not DoServercmd:
            embed = discord.Embed(title=await ctx._("cmd-error-t"), description=await ctx._("cmd-notfound-d"), color=bot.ec)
            DoServercmd = False
            await ctx.send(embed=embed)
    el"""
    if isinstance(error, commands.HybridCommandError):
        error = error.original
    if isinstance(error, (commands.CommandOnCooldown, app_commands.CommandOnCooldown)):
        # クールダウン
        embed = discord.Embed(title=await ctx._("cmd-error-t"), description=await ctx._(
            "cmd-cooldown-d", str(error.retry_after)[:4]), color=bot.ec)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.NotOwner):
        # オーナー専用コマンド
        embed = discord.Embed(title=await ctx._("cmd-error-t"),
                              description=await ctx._("only-mii-10"), color=bot.ec)
        await ctx.send(embed=embed)
        ch = await bot.fetch_channel(652127085598474242)
        await ch.send(embed=ut.getEmbed("エラーログ", f"コマンド:`{ctx.command.full_parent_name}`\n```{str(error)}```", bot.ec, f"サーバー", getattr(ctx.guild,"name","DM or GDM実行"), "実行メンバー", ctx.author.name, "メッセージ内容", ctx.message.content or "(本文なし)"))
    elif isinstance(error, commands.MissingRequiredArgument):
        # 引数がないよっ☆
        embed = discord.Embed(title=await ctx._("cmd-error-t"),
                              description=await ctx._("pls-arg"), color=bot.ec)
        await ctx.send(embed=embed)
    elif isinstance(error, (commands.MissingPermissions, app_commands.MissingPermissions)):
        embed = discord.Embed(title=await ctx._("cmd-error-t"),
                              description=f"このコマンドの実行には、あなたに次の権限が必要です。\n```py\n{error.missing_perms}```", color=bot.ec)
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send(f'> {await ctx._("cmd-error-t")}\n　このコマンドの実行には、あなたに次の権限が必要です。\n```py\n{error.missing_perms}```')
    elif isinstance(error, (commands.BotMissingPermissions, app_commands.BotMissingPermissions)):
        embed = discord.Embed(title=await ctx._("cmd-error-t"),
                              description=f"このコマンドの実行には、Botに次の権限が必要です。\n```py\n{error.missing_perms}```", color=bot.ec)
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send(f'> {await ctx._("cmd-error-t")}\n　このコマンドの実行には、Botに次の権限が必要です。\n```py\n{error.missing_perms}```')
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=await ctx._("cmd-error-t"), description="comlock、メンテナンス、使用制限等、実行時チェックを通過できなかったため、コマンド実行が失敗しました。", color=bot.ec)
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send(f'> {await ctx._("cmd-error-t")}\n　comlock、メンテナンス、使用制限等、実行時チェックを通過できなかったため、コマンド実行が失敗しました。')

    else:
        # その他例外
        from traceback import format_exception as f_exc
        ch = await bot.fetch_channel(652127085598474242)
        msg = await ch.send(embed=ut.getEmbed("エラーログ", f"コマンド:`{ctx.command.full_parent_name}`\n```py\n{''.join(f_exc(error))}```", bot.ec, "サーバー", getattr(ctx.guild,"name","DM or GDM実行"), "実行メンバー", ctx.author.name, "メッセージ内容", ctx.message.content or "(本文なし)"))
        await ctx.send(embed=ut.getEmbed(await ctx._("com-error-t"), await ctx._("cmd-other-d", "詳細は無効化されています…。"), bot.ec, "error id", msg.id, "サポートが必要ですか？", "[サポートサーバー](https://discord.gg/vtn2V3v)に参加して、「view-思惟奈ちゃんch」役職をつけて質問してみましょう！"))


"""
@tasks.loop(time=datetime.time(hour=23,minute=0,second=0))
async def invite_tweet():
    try:
        bot.twi.statuses.update(status=f"[定期投稿]\nみぃてん☆の公開Discordサーバー:https://discord.gg/GbHq7fz\nみぃてん☆制作、多機能Discordbot思惟奈ちゃん:https://discordapp.com/oauth2/authorize?client_id=462885760043843584&permissions=8&scope=bot\n<この投稿は思惟奈ちゃんより行われました。>")
    except:
        dc=bot.get_user(404243934210949120)
        await dc.send(f"have error:```{traceback.format_exc(1)}```")
@tasks.loop(time=datetime.time(hour=8,minute=0,second=0))
async def now_sina_tweet():
    try:
        bot.twi.statuses.update(status=f"[定期投稿]\n思惟奈ちゃんのいるサーバー数:{len(bot.guilds)}\n思惟奈ちゃんの公式サーバー:https://discord.gg/udA3qgZ\n<この投稿は思惟奈ちゃんより行われました。>")
    except:
        dc=bot.get_user(404243934210949120)
        await dc.send(f"have error:```{traceback.format_exc(1)}```")
"""


asyncio.run(main())
