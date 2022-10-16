# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord import app_commands
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

        @app_commands.context_menu(name="message info")
        @ut.runnable_check()
        async def message_info(interaction:discord.Interaction, msg:discord.Message):
            #msgに入ったメッセージで詳細情報Embedを作成して送信。
            if msg.is_system():
                author_status = "[System]"
            elif msg.webhook_id:
                author_status = "[WebHook]"
            elif msg.author.bot:
                if msg.author.public_flags.verified_bot:
                    author_status = "[✅Bot]"
                else:
                    author_status = "[Bot]"
            else:
                author_status = ""

            e = discord.Embed(title=f"メッセージ情報", description=msg.system_content, color=self.bot.ec)
            e.set_author(name=f"{msg.author.display_name}({msg.author.id}){author_status}のメッセージ", icon_url=msg.author.display_avatar.replace(static_format="png").url)

            post_time = msg.created_at.strftime("%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}").format(*"年月日時分秒")

            if msg.edited_at:
                edit_time = msg.edited_at.strftime("%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}").format(*"年月日時分秒")
            else:
                edit_time = "なし"

            e.set_footer(text=f"メッセージ送信時間:{post_time}/最終編集時間:{edit_time}")
            
            e.add_field(name="含まれる埋め込みの数",value=f"{len(msg.embeds)}個", inline=False)
            attach_url = '\n'.join([f'{i.url}\n' for i in msg.attachments])
            e.add_field(name="含まれる添付ファイルの数",value=f"{len(msg.attachments)}個\n{attach_url.replace('cdn.discordapp.com','media.discordapp.net')}", inline=False)
            e.add_field(name="システムメッセージかどうか",value=msg.is_system(), inline=False)


            if isinstance(msg.channel, discord.TextChannel):
                if msg.guild.rules_channel and msg.channel.id == msg.guild.rules_channel.id:
                    chtype = f"{msg.channel.name}({msg.channel.id}):ルールチャンネル"
                elif msg.channel.is_news():
                    chtype = f"{msg.channel.name}({msg.channel.id}):アナウンスチャンネル"
                else:
                    chtype = f"{msg.channel.name}({msg.channel.id}):テキストチャンネル"
            elif isinstance(msg.channel, discord.VoiceChannel):
                chtype = f"{msg.channel.name}({msg.channel.id}):ボイスチャンネル内テキストチャット"
            elif isinstance(msg.channel, discord.Thread):
                chtype = f"{msg.channel.name}({msg.channel.id}):テキストチャンネル内スレッド"
            e.add_field(name="メッセージの送信先チャンネル", value=chtype, inline=False)

            if msg.type == discord.MessageType.reply:
                e.add_field(name="メッセージへの返信等", value=f"返信元確認用:`{msg.reference.channel_id}-{msg.reference.message_id}`", inline=False)

            e.add_field(name="メンションの内訳", value=f"全員あてメンション:{msg.mention_everyone}\nユーザーメンション:{len(msg.mentions)}個\n役職メンション:{len(msg.role_mentions)}個\nチャンネルメンション:{len(msg.channel_mentions)}個", inline=False)
            e.add_field(name="メッセージID", value=str(msg.id), inline=False)
            if msg.webhook_id:
                e.add_field(name="Webhook投稿", value=f"ID:{msg.webhook_id}", inline=False)
            e.add_field(name="ピン留めされているかどうか", value=str(msg.pinned), inline=False)
            if msg.reactions:
                e.add_field(name="リアクション",value=",".join([f"{r.emoji}:{r.count}" for r in msg.reactions]), inline=False)
            e.add_field(name="メッセージのフラグ", value=[i[0] for i in iter(msg.flags) if i[1]], inline=False)

            e.add_field(name="このメッセージに飛ぶ", value=msg.jump_url, inline=False)
            
            await interaction.response.send_message(embed=e, ephemeral=True)
        
        bot.tree.add_command(message_info)




async def setup(bot):
    await bot.add_cog(m10s_messageinfo(bot))
