# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio


import m10s_util as ut
"""↑様々な便利コマンド詰め合わせ
ut.ondevicon(Member)
    オンライン状況に基づくデバイスアイコンテキストを返す。
ut.getEmbed(title,description,color,(name,value)...)
    Embedのお手軽生成。これ使ったのがあるから消そうにも消せない。
await ut.opendm(Member/User)
    DMチャンネルを返します。DMチャンネルが存在しないなんてことでは困らせません。
await wait_message_return(ctx,質問するテキスト,←の送信先,待つ時間):
    入力待ちの簡略化。タイムアウトの例外キャッチを忘れずに
ut.get_vmusic(bot,member)
    思惟奈ちゃんの音楽再生機能でそのメンバーがきいている曲を返します。
"""


class m10s_chinfo_rw(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chinfo")
    async def command(self, ctx, target=None):
        if target is None:
            target = ctx.channel
        else:
            try:
                target = await commands.TextChannelConverter().convert(ctx,target)
            except:
                try:
                    target = await commands.VoiceChannelConverter().convert(ctx,target)
                except:
                    try:
                        target = await commands.CategoryChannelConverter().convert(ctx,target)
                    except:
                        try:
                            target = self.bot.get_channel(int(target))
                        except:
                            await ctx.send("引数をチャンネルに変換できませんでした。")
                            return
        if target is None:
            return await ctx.send("そのチャンネルが見つかりませんでした。")
        if not target.guild.id == ctx.guild.id:
            await ctx.send("このサーバーのチャンネルではないため、情報を表示できません。")
            return
        if isinstance(target,discord.TextChannel):
            if target.is_news():
                if "NEWS" in target.guild.features:
                    e=discord.Embed(name="チャンネル情報",description=f"{target.name}(タイプ:アナウンス)\nID:{target.id}",color=self.bot.ec)
                else:
                    e=discord.Embed(name="チャンネル情報",description=f"{target.name}(タイプ:アナウンス(フォロー不可))\nID:{target.id}",color=self.bot.ec)
            else:
                e=discord.Embed(name="チャンネル情報",description=f"{target.name}(タイプ:テキスト)\nID:{target.id}",color=self.bot.ec)
            e.timestamp=target.created_at
            if target.category:
                e.add_field(name="所属するカテゴリ",value=f"{target.category.name}({target.category.id})")
            e.add_field(name="チャンネルトピック",value=target.topic or "(なし)")
            if not target.slowmode_delay == 0:
                e.add_field(name="スローモードの時間",value=f"{target.slowmode_delay}秒")
            e.add_field(name="NSFW指定有無",value=target.is_nsfw())
            mbs=""
            for m in target.members:
                if len(mbs+f"`{m.name}`,")>=1020:
                    mbs=mbs+f"他"
                    break
                else:
                    mbs=mbs+f"`{m.name}`,"
            if mbs != "":
                e.add_field(name=f"閲覧可能なメンバー({len(target.members)}人)",value=mbs,inline=False)
            await ctx.send(embed=e)
        elif isinstance(target,discord.VoiceChannel):
            e=discord.Embed(name="チャンネル情報",description=f"{target.name}(タイプ:ボイス)\nID:{target.id}",color=self.bot.ec)
            e.timestamp=target.created_at
            if target.category:
                e.add_field(name="所属するカテゴリ",value=f"{target.category.name}({target.category.id})")
            e.add_field(name="チャンネルビットレート",value=f"{target.bitrate/1000}Kbps")
            if not target.user_limit == 0:
                e.add_field(name="ユーザー数制限",value=f"{target.user_limit}人")
            mbs=""
            for m in target.members:
                if len(mbs+f"`{m.name}`,")>=1020:
                    mbs=mbs+f"他"
                    break
                else:
                    mbs=mbs+f"`{m.name}`,"
            if mbs != "":
                e.add_field(name=f"参加可能なメンバー({len(target.members)}人)",value=mbs,inline=False)
            e.add_field(name="ボイスチャンネルの地域",value=target.rtc_region if target.rtc_region else "自動")
            await ctx.send(embed=e)
        elif isinstance(target,discord.CategoryChannel):
            e=discord.Embed(name="チャンネル情報",description=f"{target.name}(タイプ:カテゴリ)\nID:{target.id}",color=self.bot.ec)
            e.timestamp=target.created_at
            e.add_field(name="NSFW指定有無",value=target.is_nsfw())
            mbs=""
            for c in target.channels:
                if c.type is discord.ChannelType.news:
                    if "NEWS" in target.guild.features:
                        chtype="アナウンス"
                    else:
                        chtype="アナウンス(フォロー不可)"
                elif c.type is discord.ChannelType.store:
                    chtype="ストア"
                elif c.type is discord.ChannelType.voice:
                    chtype="ボイス"
                elif c.type is discord.ChannelType.text:
                    chtype="テキスト"
                elif c.type is discord.ChannelType.stage_voice:
                    chtype="ステージ"
                else:
                    chtype=str(c.type)
                if len(mbs+f"`{c.name}({chtype})`,")>=1020:
                    mbs=mbs+f"他"
                    break
                else:
                    mbs=mbs+f"`{c.name}({chtype})`,"
            if mbs != "":
                e.add_field(name=f"所属するチャンネル({len(target.channels)}チャンネル)",value=mbs,inline=False)
            await ctx.send(embed=e)
        if isinstance(target,discord.StageChannel):
            e=discord.Embed(name="チャンネル情報",description=f"{target.name}(タイプ:ステージ)\nID:{target.id}",color=self.bot.ec)
            e.timestamp=target.created_at
            if target.category:
                e.add_field(name="所属するカテゴリ",value=f"{target.category.name}({target.category.id})")
            e.add_field(name="チャンネルビットレート",value=f"{target.bitrate/1000}Kbps")
            e.add_field(name="チャンネルトピック",value=target.topic or "(なし)")
            if not target.user_limit == 0:
                e.add_field(name="ユーザー数制限",value=f"{target.user_limit}人")
            mbs=""
            for m in target.members:
                if len(mbs+f"`{m.name}`,")>=1020:
                    mbs=mbs+f"他"
                    break
                else:
                    mbs=mbs+f"`{m.name}`,"
            if mbs != "":
                e.add_field(name=f"参加可能なメンバー({len(target.members)}人)",value=mbs,inline=False)
            e.add_field(name="ボイスチャンネルの地域",value=target.rtc_region if target.rtc_region else "自動")
            await ctx.send(embed=e)
        else:
            await ctx.send("> エラー\n予期しないタイプのチャンネルです。チーム☆思惟奈ちゃんメンバーに報告してください。")



async def setup(bot):
    await bot.add_cog(m10s_chinfo_rw(bot))
