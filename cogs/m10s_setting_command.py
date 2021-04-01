# -*- coding: utf-8 -*-

import traceback
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




class m10s_settings_command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="settings",aliases=["setting","edit"])
    async def _setting_command(self, ctx):
        try:
            page=0
            settings=[
                #["表示名","description","name","value","command名"]
                ["コマンド・機能制限","サーバー内でコマンドや機能をロックすることができます。\n機能にロックをかけるときの機能名:\n・`clevel`:レベルカウント機能\n・`shash`:ハッシュタグ機能\n・`scom`:サーバーコマンド機能\n・`disable_defprefix`:デフォルトのprefix(`s-`)の無効化\n・`disable_profile_msg`:ユーザープロファイル作成メッセージ","必要引数","`[add/del] [繰り返し:[コマンド/機能名]]`/`[view]`","comlock"],

                ["サーバーログ","サーバーでのメッセージの削除や編集、チャンネルの作成などをログに設定したチャンネルに書き出します。","必要引数","`(なし)`/`[チャンネルID]`","sendlogto"],

                ["メンバー認証","特定チャンネルでメッセージを読み進めて、最後に役職付与を行う、簡易的メンバー認証を設定することができます。","必要引数","`(なし)`","Authsetting"],

                ["グローバルBAN","グローバルBANを実行するようにし、特定チャンネルに対して、そのログを送ることができます。引数を入力しないことで無効化できます。","必要引数","`(なし)`/`[チャンネルID]`","gbanlogto"],

                ["グローバルチャット-1","他のサーバーとチャンネルをつなぎ、みんなで話しましょう！","必要引数","`(なし)`/`[グローバルチャットチャンネル名]`","gchat connect"],

                ["グローバルチャット-2","何らかの事情で不要になりましたか？切断してみましょう！","必要引数","`(なし)`","gchat dconnect"],

                ["サーバーでの呼び出し文字列の追加","このサーバーで`s-`を使わずに思惟奈ちゃんを使いたい？呼び出し文字列を増やしてみましょう！","必要引数","`[set/del] [prefixにしたい文字列]`/`[view]`","guildprefix"],

                ["サーバーでの言語の追加","このサーバーでほかの言語で思惟奈ちゃんを使いたい？サーバー言語を変えてみましょう！","必要引数","`[ja/en]`","guildlang"],

                ["ウェルカム！&サンキュー！","サーバーに参加した人にようこその言葉を、退出した方にありがとうを設定できます。\n引数の解説---\nsysch:システムチャンネル/dm:DMチャンネル/welcome:参加時/cu:退出時","必要引数","`[set] [welcome/cu] [sysch/dm] [content]`/`[check]`","setsysmsg"],

                ["サーバー独自のコマンドを！","このサーバーでのみ動く特別なコマンドを設定できます。add:追加,del:削除,help:ヘルプを見る","必要引数","`[add/del/help] [コマンド名]`","servercmd"],

                ["ハッシュタグのようにチャンネルを使おう！","設定したチャンネルにメンションすることでハッシュタグのように使用できるようにできます。\n実行するたびに切り替えることができます。","必要引数","`(なし)`","hash"],

                ["サーバーレベルに応じた役職の付与","思惟奈ちゃんサーバーレベルに応じて役職の付与ができます!ここではその設定ができます。\n設定状況は`s-serverinfo`で確認できます。","必要引数","`[役職を付与するレベル] [役職ID/(なし)]`","levelreward"],

                ["レベルアップ通知の送信先を変えよう！","思惟奈ちゃんサーバーレベルのレベルアップメッセージの送信先を変更することができます。","必要引数","`[チャンネルID]`","levelupsendto"],

                ["役職パネル機能、はじめました","思惟奈ちゃんを使って、好きな絵文字で役職を付与できるパネルを製作しましょう！","必要引数","`(なし)/[create]`/`[delete] [パネルID]`/`[add] [パネルID] [絵文字] [役職が特定できるもの]`/`[remove] [パネルID] [絵文字]`","rolepanel"],

                ["サーバーレベル編集","管理者だけができる、サーバーレベルの整理整頓。__add__で相対的に追加/減少、__set__で絶対的に設定できます。","必要引数","`add [メンバーor役職を特定できるもの] [追加するレベル] [オプション:追加する経験値]`/`set [メンバーor役職を特定できるもの] [設定するレベル] [オプション:設定する経験値]`:設定","leveledit"],

                ["プレイ中に応じた役職付与を設定しましょう！","サーバー内のメンバーのプレイ中に基づいた役職付与が行えます！\n> 第一引数の種類\n　Botにわからないステータス:`unknown`\nプレイ中:`playing`\n配信中:`streaming`\n音楽鑑賞:`listening`\n視聴中:`watching`\nカスタムステータス:`custom`\ncompeting(今はまだ使われていない):`competing`\n","必要引数","`[第一引数] [役職を特定できるもの]`(設定や更新時)/`[第一引数]`(削除時)","prole"],

                #ユーザー
                ["ユーザーごとの呼び出し文字列の追加","あなたは`s-`を使わずに思惟奈ちゃんを使いたい？呼び出し文字列を増やしてみましょう！","必要引数","`[set/del] [prefixにしたい文字列]`/`[view]`","userprefix"],

                ["ユーザーごとでの言語の追加","あなたはほかの言語で思惟奈ちゃんを使いたい？言語を変えてみましょう！","必要引数","`[ja/en]`","userlang"],

                ["ユーザーごとのレベルアップ変更","あなたがもしもレベルアップが不要なら、あなただけ切ることができます。実行のたびに切り替わります。","必要引数","`(なし)`","switchLevelup"],

                ["レベルカードでイメチェンしない？","`s-level`のあなたのレベルカードを変更できます。引数がないと今のレベルカードを確認もできます。","必要引数","`(なし)`/`[1から6の数字]`","switchlevelcard"],

                ["グローバルチャットニックネームをかえてみよう！","思惟奈ちゃんグローバルチャットでの表示名を変えることができます。","必要引数","`[表示名]`","globalnick"],

                ["グローバルチャットカラーを変えてみよう！","思惟奈ちゃんグローバルチャットで、他サーバーに送信される下のEmbedの色を変えることができます。","必要引数","`[0xや#を除く16進数のカラーコード]`","globalcolor"],

                ["プレイ中に応じた役職付与が行われるようにしよう！","サーバーごとに設定された、プレイ中に応じた役職付与が行われるようにしましょう！","必要引数","`True`(有効)/`False`(無効)","activrole"]

            ]


            
            e = discord.Embed(title="思惟奈ちゃん設定パネル",description=f"{settings[page][0]}:{settings[page][1]}", color=self.bot.ec)
            e.add_field(name=settings[page][2], value=settings[page][3])
            e.set_footer(text=f"ページ:{page+1}/{len(settings)}")
            msg = await ctx.send(embed=e)
            await msg.add_reaction(self.bot.get_emoji(653161518195671041))
            await msg.add_reaction(self.bot.get_emoji(653161518103265291))
            await msg.add_reaction(self.bot.get_emoji(653161518170505216))



            while True:
                try:
                    r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
                except:
                    break
                try:
                    await msg.remove_reaction(r, u)
                except:
                    pass
                if str(r) == str(self.bot.get_emoji(653161518170505216)):
                    if page == len(settings)-1:
                        page = 0
                    else:
                        page = page + 1
                elif str(r) == str(self.bot.get_emoji(653161518195671041)):
                    if page == 0:
                        page = len(settings)-1
                    else:
                        page = page - 1
                elif str(r) == str(self.bot.get_emoji(653161518103265291)):
                    rtn = await ut.wait_message_return(ctx,"引数を入力してください。(引数がない場合はNoneを入力)",ctx.channel)


                    #form r_danny
                    _msg = ctx.message
                    _msg.channel = ctx.channel
                    if rtn.content == "None":
                        _msg.content = f"{ctx.prefix}{settings[page][4]}"
                    else:
                        _msg.content = f"{ctx.prefix}{settings[page][4]} {rtn.content}"

                    _ctx = await self.bot.get_context(_msg, cls=type(ctx))
                    await self.bot.invoke(_ctx)
                    return

                e = discord.Embed(title="思惟奈ちゃん設定パネル",description=f"{settings[page][0]}:{settings[page][1]}",color=self.bot.ec)
                e.add_field(name=settings[page][2], value=settings[page][3])
                e.set_footer(text=f"ページ:{page+1}/{len(settings)}")
                await msg.edit(embed=e)
        except:
            await ctx.send(traceback.format_exc(4))
        
        




def setup(bot):
    bot.add_cog(m10s_settings_command(bot))
