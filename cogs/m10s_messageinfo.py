# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from dateutil.relativedelta import relativedelta as rdelta
from typing import Union
import traceback

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


class m10s_messageinfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="messageinfo",aliases=["minfo","mi"])
    async def msg_info(self, ctx, target:Union[commands.MessageConverter,None]):
        if target:
            fetch_from = "引数"
            msg = target
        else:
            if ctx.message.reference and ctx.message.type == discord.MessageType.default:
                if ctx.message.reference.cached_message:
                    fetch_from = "引用"
                    msg = ctx.message.reference.cached_message
                else:
                    try:
                        fetch_from = "引用"
                        msg = await self.bot.get_channel(ctx.message.reference.channel_id).fetch_message(ctx.message.reference.message_id)
                    except:
                        fetch_from = "コマンド実行メッセージ"
                        msg = ctx.message
            else:
                fetch_from = "コマンド実行メッセージ"
                msg = ctx.message
        #msgに入ったメッセージで詳細情報Embedを作成して送信。
        e = discord.Embed(title=f"メッセージ情報({fetch_from}より取得)", description=msg.system_content, color=self.bot.ec)
        e.set_author(name=f"{msg.author.display_name}({msg.author.id}){'[bot]' if msg.author.bot else ''}のメッセージ",icon_url=msg.author.avatar_url_as(static_format="png"))

        post_time = (msg.created_at + rdelta(hours=9)
                    ).strftime("%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}").format(*"年月日時分秒")

        if msg.edited_at:
            edit_time = (msg.edited_at + rdelta(hours=9)
                    ).strftime("%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}").format(*"年月日時分秒")
        else:
            edit_time = "なし"

        e.set_footer(text=f"メッセージ送信時間:{post_time}/最終編集時間:{edit_time}")
        
        e.add_field(name="含まれる埋め込みの数",value=f"{len(msg.embeds)}個")
        e.add_field(name="含まれる添付ファイルの数",value=f"{len(msg.attachments)}個")
        e.add_field(name="システムメッセージかどうか",value=msg.is_system())

        if msg.guild.rules_channel and msg.channel.id == msg.guild.rules_channel.id:
            chtype = f"{msg.channel.name}({msg.channel.id}):ルールチャンネル"
        elif msg.channel.is_news():
            chtype = f"{msg.channel.name}({msg.channel.id}):アナウンスチャンネル"
        else:
            chtype = f"{msg.channel.name}({msg.channel.id}):テキストチャンネル"
        e.add_field(name="メッセージの送信先チャンネル",value=chtype)

        if msg.reference:
            e.add_field(name="あるメッセージへの返信等",value=f"返信元確認用:`{msg.reference.channel_id}-{msg.reference.message_id}`")

        e.add_field(name="メンションの内訳",value=f"全員あてメンション:{msg.mention_everyone}\nユーザーメンション:{len(msg.mentions)}個\n役職メンション:{len(msg.role_mentions)}個\nチャンネルメンション:{len(msg.channel_mentions)}個")
        e.add_field(name="メッセージID",value=str(msg.id))
        if msg.webhook_id:
            e.add_field(name="Webhook投稿",value=f"ID:{msg.webhook_id}")
        e.add_field(name="ピン留めされているかどうか",value=str(msg.pinned))
        if len(msg.reactions) != 0:
            e.add_field(name="リアクション",value=",".join([f"{r.emoji}:{r.count}" for r in msg.reactions]))
        e.add_field(name="メッセージのフラグ",value=[i[0] for i in iter(msg.flags) if i[1]])

        e.add_field(name="このメッセージに飛ぶ",value=msg.jump_url)
        
        try:
            await ctx.reply(embed=e,mention_author=False)
        except:
            await ctx.send(embed=e)




def setup(bot):
    bot.add_cog(m10s_messageinfo(bot))
