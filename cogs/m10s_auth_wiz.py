import discord
from discord.ext import commands
import asyncio
import m10s_util as ut

import json


class m10s_auth_wiz(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, m):
        auths = await self.bot.cursor.fetchone(
            "select * from welcome_auth where id = %s", (m.guild.id,))
        #auths = await self.bot.cursor.fetchone()
        if auths:
            if bool(auths["uses"]) and not(m.bot):
                if type(auths["next_reaction"]) is int:
                    nr = self.bot.get_emoji(auths["next_reaction"])
                else:
                    nr = auths["next_reaction"]
                ow = {
                    m: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    m.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    m.guild.me: discord.PermissionOverwrite(
                        read_messages=True, send_messages=True, manage_messages=True)
                }
                for i in json.loads(auths["can_view"]):
                    rl = m.guild.get_role(i)
                    if rl:
                        ow[rl] = discord.PermissionOverwrite(
                            read_messages=True)
                cg = m.guild.get_channel(auths["category"])
                if cg:
                    ch = await cg.create_text_channel(f"sinaauth-{m.name}", overwrites=ow, topic=str(m.id), position=0)
                else:
                    ch = await m.guild.create_text_channel(f"sinaauth-{m.name}", overwrites=ow, topic=str(m.id), position=0)
                msg = await ch.send("please wait...\nしばらくお待ちください…")
                for i in json.loads(auths["au_w"]):
                    await msg.edit(content=None, embed=ut.getEmbed(f"サーバーユーザー認証", f"※{nr}で進行します。\n{i['text']}"))
                    for r in i["reactions"]:
                        if type(r) is int:
                            rct = self.bot.get_emoji(r)
                        else:
                            rct = r
                        await msg.add_reaction(rct)
                    await msg.add_reaction(nr)
                    r, _ = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == m.id and r.emoji == auths["next_reaction"])
                    ridx = [i["reactions"].index(str(r.emoji)) for r in r.message.reactions if r.count == 2 and r.emoji != nr]
                    for ri in ridx:
                        grl = m.guild.get_role(i["give_role"][ri])
                        if grl:
                            await m.add_roles(grl)
                    await msg.clear_reactions()
                await m.add_roles(m.guild.get_role(auths["give_role"]))
                await ch.send("> サーバーユーザー認証\n あなたの認証が完了しました！")

    @commands.hybrid_command(name="authsetting", aliases=["Auth","Authsettings"], description="簡易メンバー認証を作成できます。")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True,manage_roles=True)
    async def _setting(self, ctx):
        auths = await self.bot.cursor.fetchone(
            "select * from welcome_auth where id = %s", (ctx.guild.id,))
        #auths = await self.bot.cursor.fetchone()
        if auths:
            use = bool(auths["uses"])
        else:
            use = False
        e = discord.Embed(title="認証ウィザードの設定", description="""
        ✏で設定を行います。
        🔄で利用設定を切り替えます。
        ❌で表示を消します。""", color=self.bot.ec)
        e.set_footer(text="create by mii-10")
        if use:
            e.add_field(name="利用状況", value="使用する", inline=False)
            roles = "\n".join([str(ctx.guild.get_role(i))
                               for i in json.loads(auths["can_view"])])
            e.add_field(name="認証を閲覧できる役職", value=roles, inline=False)
            if auths["category"]:
                category = self.bot.get_channel(auths["category"])
                e.add_field(
                    name="作成されるカテゴリー", value=f"{category.name}({category.id})", inline=False)
            else:
                catagory = None
                e.add_field(name="作成されるカテゴリー",
                            value=f"カテゴリーに所属しない", inline=False)
            if isinstance(auths["next_reaction"], str):
                nr = auths["next_reaction"]
            elif isinstance(auths["next_reaction"], int):
                nr = self.bot.get_emoji(auths["next_reaction"])
            e.add_field(name="次に進むリアクション", value=nr, inline=False)
            auth_w = json.loads(auths["au_w"])
            e.add_field(name="現在の認証の長さ", value=len(auth_w), inline=False)
            grole = ctx.guild.get_role(auths["give_role"])
            e.add_field(name="与える役職", value=str(grole), inline=False)
        else:
            e.add_field(name="利用状況", value="使用しない", inline=False)
        m = await ctx.send(embed=e)
        await m.add_reaction("✏")
        await m.add_reaction("🔄")
        await m.add_reaction("❌")
        try:
            r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id and r.emoji in ["✏", "🔄", "❌"])
        except asyncio.TimeoutError:
            await m.delete()
            await ctx.send("一定時間リアクションがなかったため、パネルを削除しました。設定する際は再度コマンド実行をお願いします。")
            return
        if r.emoji == "✏":
            await m.clear_reactions()
            await ctx.send("設定を開始します。DMに移動してください。")
            if auths:  # 設定がある場合の処理を行います メモ:保存処理をちゃんと書くこと！
                udm = await ut.opendm(ctx.author)
                msg = await udm.send("""> 既に設定があります。何を変更しますか？
                ▶:次へ進む共通の絵文字
                🎫:作成するカテゴリー
                📖:ウィザードの内容
                🔍:閲覧できる役職の変更
                🎖:与える役職
                """)
                await msg.add_reaction("▶")
                await msg.add_reaction("🎫")
                await msg.add_reaction("📖")
                await msg.add_reaction("🔍")
                await msg.add_reaction("🎖")
                r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id and r.emoji in "▶🎫📖🔍🎖")
                if r.emoji == "🎖":
                    m = await ut.wait_message_return(ctx, "認証後、与える役職のIDを送信してください。", udm, 60)
                    grole = int(m.content)
                    await self.bot.cursor.execute(
                        "UPDATE welcome_auth SET give_role = %s WHERE id = %s", (grole, ctx.guild.id))
                    await udm.send("変更が完了しました。")
                elif r.emoji == "▶":
                    m = await ut.wait_message_return(ctx, "作成するウィザードの進行絵文字を送ってください。\nサーバー絵文字の場合は、IDを送信してください。", udm, 60)
                    try:
                        nr = int(m.content)
                    except:
                        nr = m.content
                    await self.bot.cursor.execute(
                        "UPDATE welcome_auth SET next_reaction = %s WHERE id = %s", (nr, ctx.guild.id))
                    await udm.send("変更が完了しました。")
                elif r.emoji == "🎫":
                    m = await ut.wait_message_return(ctx, "チャンネルを作成するカテゴリーのIDを送信してください。\nカテゴリーを作らない場合は、任意のテキストを送信してください。", udm, 60)
                    try:
                        category = int(m.content)
                    except:
                        category = None
                    await self.bot.cursor.execute(
                        "UPDATE welcome_auth SET category = %s WHERE id = %s", (category, ctx.guild.id))
                    await udm.send("変更が完了しました。")
                elif r.emoji == "📖":
                    auths = await self.bot.cursor.fetchone(
                        "select * from welcome_auth where id = %s", (ctx.guild.id,))
                    #auths = await self.bot.cursor.fetchone()
                    if isinstance(auths["next_reaction"], str):
                        nr = auths["next_reaction"]
                    elif isinstance(auths["next_reaction"], int):
                        nr = self.bot.get_emoji(auths["next_reaction"])
                    else:
                        nr = "➡"

                    seted = False
                    auth_w = []
                    while not seted:
                        msg = await udm.send("> 編集ウィザード\n注意:ページ情報は新しいものに置き換えられます。\n✏:次のページを作成\n✅:終了する")
                        await msg.add_reaction("✏")
                        await msg.add_reaction("✅")
                        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id and r.emoji in ["✏", "✅"])
                        if r.emoji == "✅":
                            if len(auth_w) == 0:
                                await udm.send("> 作成はまだ続いています！\nウィザードは、必ず1ページは作成する必要があります！")
                            else:
                                seted = True
                        elif r.emoji == "✏":
                            tmp = {}
                            msg = await udm.send(f"> 編集ウィザード\nこのメッセージに使いたいリアクションをした後、最後に{nr}を押してください。")
                            await msg.add_reaction(nr)
                            r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id and r.emoji == nr)
                            tmp["reactions"] = [
                                str(r.emoji) for r in r.message.reactions if not r.emoji == nr]
                            tmp["give_role"] = []
                            for r in tmp["reactions"]:
                                ridm = await ut.wait_message_return(ctx, f"> 編集ウィザード\n{r}で役職を付与する場合は役職のIDを、しない場合は数字ではない任意のテキストを送信してください。", udm, 60)
                                try:
                                    rid = int(ridm.content)
                                except:
                                    rid = None
                                tmp["give_role"].append(rid)
                            tmsg = await ut.wait_message_return(ctx, f"> 編集ウィザード\n最後に、そのページのテキストを送信してください。", udm, 60)
                            tmp["text"] = tmsg.content
                            auth_w.append(tmp)
                    await self.bot.cursor.execute(
                        "UPDATE welcome_auth SET au_w = %s WHERE id = %s", (json.dumps(auth_w), ctx.guild.id))
                    await udm.send("変更が完了しました。")
                elif r.emoji == "🔍":
                    tmsg = await ut.wait_message_return(ctx, f"> 編集ウィザード\nそのチャンネルを閲覧できる役職のIDをスペース区切りで送信してください。", udm, 60)
                    cv = [int(i) for i in tmsg.content.split(" ")]
                    await self.bot.cursor.execute(
                        "UPDATE welcome_auth SET can_view = %s WHERE id = %s", (json.dumps(cv), ctx.guild.id))
                    await udm.send("変更が完了しました。")
            else:  # 設定が存在しない場合、初期設定を行います。
                udm = await ut.opendm(ctx.author)
                try:
                    m = await ut.wait_message_return(ctx, "作成するウィザードの進行絵文字を送ってください。\nサーバー絵文字の場合は、IDを送信してください。", udm, 60)
                    try:
                        nr = int(m.content)
                    except:
                        nr = m.content

                    # カテゴリ→ウィザードの内容で設定を作る

                    tmsg = await ut.wait_message_return(ctx, f"> 作成ウィザード\nそのチャンネルを閲覧できる役職のIDをスペース区切りで送信してください。", udm, 60)
                    cv = [int(i) for i in tmsg.content.split(" ")]

                    m = await ut.wait_message_return(ctx, "チャンネルを作成するカテゴリーのIDを送信してください。\nカテゴリーを作らない場合は、任意のテキストを送信してください。", udm, 60)
                    try:
                        category = int(m.content)
                    except:
                        category = None

                    m = await ut.wait_message_return(ctx, "認証後、与える役職のIDを送信してください。", udm, 60)
                    grole = int(m.content)
                    seted = False
                    auth_w = []
                    while not seted:
                        msg = await udm.send("> ウィザードの作成\n✏:次のページを作成\n✅:終了する")
                        await msg.add_reaction("✏")
                        await msg.add_reaction("✅")
                        r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id and r.emoji in ["✏", "✅"])
                        if r.emoji == "✅":
                            if len(auth_w) == 0:
                                await udm.send("> 作成はまだ続いています！\nウィザードは、必ず1ページは作成する必要があります！")
                            else:
                                seted = True
                        elif r.emoji == "✏":
                            tmp = {}
                            msg = await udm.send(f"> 作成ウィザード\nこのメッセージに使いたいリアクションをした後、最後に{nr}を押してください。")
                            await msg.add_reaction(nr)
                            r, u = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id and r.emoji == nr)
                            tmp["reactions"] = [
                                str(r.emoji) for r in r.message.reactions if not r.emoji == nr]
                            tmp["give_role"] = []
                            for r in tmp["reactions"]:
                                ridm = await ut.wait_message_return(ctx, f"> 作成ウィザード\n{r}で役職を付与する場合は役職のIDを、しない場合は数字ではない任意のテキストを送信してください。", udm, 60)
                                try:
                                    rid = int(ridm.content)
                                except:
                                    rid = None
                                tmp["give_role"].append(rid)
                            tmsg = await ut.wait_message_return(ctx, f"> 作成ウィザード\n最後に、そのページのテキストを送信してください。", udm, 60)
                            tmp["text"] = tmsg.content
                            auth_w.append(tmp)
                    await self.bot.cursor.execute("insert into welcome_auth (id,category,use,can_view,next_reaction,au_w,give_role) values(%s,%s,%s,%s,%s,%s,%s)", (
                        ctx.guild.id, category, 1, json.dumps(cv), nr, json.dumps(auth_w), grole))
                    await udm.send("> 作成ウィザード\n作成が完了しました！設定の確認や変更は、再度`s-Authsetting`コマンドで行えます。")
                except asyncio.TimeoutError:
                    await udm.send("タイムアウトしました。再度設定をするには、初めからやり直してください。")
        elif r.emoji == "🔄":
            if auths:
                await m.clear_reactions()
                if use:
                    await self.bot.cursor.execute(
                        "UPDATE welcome_auth SET uses = %s WHERE id = %s", (0, ctx.guild.id))
                else:
                    await self.bot.cursor.execute(
                        "UPDATE welcome_auth SET uses = %s WHERE id = %s", (1, ctx.guild.id))
                await m.edit(embed=ut.getEmbed("認識ウィザード", f"利用設定を{not use}に切り替えました。"))
            else:
                await m.edit(embed=ut.getEmbed("認識ウィザード", f"初めに✏絵文字から利用設定を行ってください。"))
        elif r.emoji == "❌":
            await m.delete()


async def setup(bot):
    await bot.add_cog(m10s_auth_wiz(bot))
