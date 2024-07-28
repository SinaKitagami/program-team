# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import traceback
import json

from discord import app_commands

import m10s_util as ut


class manage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @ut.runnable_check()
    async def backup(self, ctx, gid: int):
        if not ctx.guild.me.guild_permissions.administrator:
            await ctx.send("このサーバーで、わたしが管理者権限を持ってないので使用できません。")
            return
        try:
            g = self.bot.get_guild(gid)
            if ctx.channel.permissions_for(ctx.author).administrator is True or ctx.author.id == 404243934210949120:
                pgs = await ctx.send(f"役職\n進行度:0/{len(g.roles)}")
                tk = 0
                rlid = {}
                async with ctx.channel.typing():
                    # 役職。rlid(dict)に旧id(str)で参照すれば新idが返ってくる
                    for r in g.roles[1:][::-1]:
                        rl = await ctx.guild.create_role(name=r.name, permissions=r.permissions, colour=r.colour, hoist=r.hoist, mentionable=r.mentionable, reason=f"{g.name}より。役職転送コマンド実行による。")
                        await asyncio.sleep(2)
                        rlid[str(r.id)] = rl.id
                        tk = tk+1
                        await pgs.edit(content=f"役職\n進行度:{tk}/{len(g.roles)}")
                    await ctx.guild.default_role.edit(permissions=g.default_role.permissions)
                    rlid[str(g.default_role.id)] = ctx.guild.default_role.id
                    await pgs.edit(content=f"チャンネル\n進行度:0/{len(g.channels)}")
                    tk = 0
                    # チャンネル。
                    chlt = {}
                    for mct, mch in g.by_category():
                        await asyncio.sleep(2)
                        try:
                            ovwt = {}
                            await asyncio.sleep(2)
                            for k, v in mct.overwrites.items():
                                try:
                                    rl = ctx.guild.get_role(rlid[str(k.id)])
                                    ovwt[rl] = v
                                except:
                                    pass
                            ct = await ctx.guild.create_category_channel(name=mct.name, overwrites=ovwt)
                            chlt[str(mct.id)] = ct.id
                            tk = tk+1
                            await pgs.edit(content=f"チャンネル\n進行度:{tk}/{len(g.channels)}")
                        except AttributeError:
                            ct = None
                        for c in mch:
                            ovwt = {}
                            await asyncio.sleep(2)
                            for k, v in c.overwrites.items():
                                try:
                                    rl = ctx.guild.get_role(rlid[k])
                                    ovwt[rl] = v
                                except:
                                    pass
                            if isinstance(c, discord.TextChannel):
                                cch = await ctx.guild.create_text_channel(name=c.name, category=ct, topic=c.topic, slowmode_delay=c.slowmode_delay, nsfw=c.is_nsfw(), overwrites=ovwt)
                            elif isinstance(c, discord.VoiceChannel):
                                if ctx.guild.bitrate_limit >= c.bitrate:
                                    cch = await ctx.guild.create_voice_channel(name=c.name, category=ct, bitrate=c.bitrate, user_limit=c.user_limit, overwrites=ovwt)
                                else:
                                    cch = await ctx.guild.create_voice_channel(name=c.name, category=ct, bitrate=ctx.guild.bitrate_limit, user_limit=c.user_limit, overwrites=ovwt)
                            else:
                                pass
                            try:
                                chlt[str(c.id)] = cch.id
                                tk = tk+1
                                await pgs.edit(content=f"チャンネル\n進行度:{tk}/{len(g.channels)}")
                            except:
                                pass
                    await pgs.edit(content="チャンネル完了\nnext:絵文字")
                    # 絵文字
                    tk = 0
                    for e in g.emojis:
                        if len(ctx.guild.emojis) >= ctx.guild.emoji_limit:
                            break
                        print("looping")
                        try:
                            ei = await e.read()
                            await ctx.guild.create_custom_emoji(name=e.name, image=ei)
                            await asyncio.sleep(5)
                            print("done")
                        except:
                            await ctx.send(f"```{traceback.format_exc(3)}```")
                    await pgs.edit(content="絵文字完了\nnext:ユーザーのban状況")
                    # ユーザーのban
                    bm = await g.bans()
                    tk = 0
                    for i in bm:
                        await g.ban(user=i.user, reason=i.reason)
                        await asyncio.sleep(2)
                        tk = tk+1
                        await pgs.edit(content=f"ban状況確認\n進行度:{tk}/{len(bm)}")

                    await pgs.edit(content="ban状況完了\nnext:サーバー設定")
                    # サーバー設定
                    icn = await g.icon.replace(static_format="png").read()
                    await ctx.guild.edit(name=g.name, icon=icn, region=g.region, verification_level=g.verification_level, default_notifications=g.default_notifications, explicit_content_filter=g.explicit_content_filter)
                    # afk
                    if g.afk_channel:
                        await ctx.guild.edit(afk_channel=ctx.guild.get_channel(chlt[str(g.afk_channel.id)]), afk_timeout=g.afk_timeout)
                    # システムチャンネル
                    if g.system_channel:
                        await ctx.guild.edit(system_channel=ctx.guild.get_channel(chlt[str(g.system_channel.id)]), system_channel_flags=g.system_channel_flags)
                    # サーバー招待スプラッシュ
                    if str(g.splash_url) and ("INVITE_SPLASH" in ctx.guild.features):
                        sp = await g.splash_url.read()
                        await ctx.guild.edit(splash=sp)
                    # サーバーバナー
                    if str(g.banner_url) and ("BANNER" in ctx.guild.features):
                        bn = await g.banner_url.read()
                        await ctx.guild.edit(banner=bn)
                    await ctx.send("完了しました。")
            else:
                await ctx.send("このサーバーの管理者である必要があります。")
        except:
            await ctx.send(embed=ut.getEmbed("エラー", f"詳細:```{traceback.format_exc(0)}```"))

    @commands.command()
    @ut.runnable_check()
    async def cemojiorole(self, ctx, name, *rlis):
        ig = await ctx.message.attachments[0].read()
        await ctx.guild.create_custom_emoji(name=name, image=ig, roles=[ctx.guild.get_role(int(i)) for i in rlis])
        await ctx.send(await ctx._("created-text"))


    @commands.hybrid_command(aliases=["メッセージ一括削除", "次の件数分、メッセージを消して"], description="メッセージ一括削除を行います。")
    @app_commands.describe(msgcount="削除する件数")
    @commands.cooldown(1, 15, type=commands.BucketType.guild)
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id))
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def delmsgs(self, ctx:commands.Context, msgcount:int):
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages and (ctx.channel.permissions_for(ctx.author).manage_messages or ctx.author.id == 404243934210949120):
            await ctx.defer(ephemeral=True)
            async with ctx.message.channel.typing():
                if not ctx.interaction:
                    dmc = ctx.message
                    await dmc.delete()
                dr = await ctx.channel.purge(limit=int(msgcount))
            await ctx.send(await ctx._("delmsgs-del", len(dr)), ephemeral=True, delete_after=15)
        else:
            await ctx.send("> メッセージ一括削除\n　あなたか私に権限がありません！", ephemeral=True)


async def setup(bot):
    await bot.add_cog(manage(bot))
