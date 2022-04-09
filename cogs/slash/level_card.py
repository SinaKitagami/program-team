# -*- coding: utf-8 -*-

from typing import Optional
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import asyncio

from operator import itemgetter
import json

from discord import app_commands

import m10s_util as ut


class level_card(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="level_ranking",description="サーバーレベルのランキングを表示します。")
    @app_commands.describe(start_rank="表示する最高の順位")
    @app_commands.describe(end_rank="表示する最低の順位")
    async def ranklev(self, interaction:discord.Interaction, start_rank: Optional[int], end_rank: Optional[int]):
        start = start_rank or 1
        end = end_rank or 10
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (interaction.guild.id,))
        #gs = await self.bot.cursor.fetchone()
        le = json.loads(gs["levels"])
        lrs = [(int(k), v["level"], v["exp"])
                for k, v in le.items() if v["dlu"]]
        text = ""
        lranks = [(ind, i) for ind, i in enumerate(
            sorted(lrs, key=itemgetter(1, 2), reverse=True))]
        for ind, i in lranks[start-1:end]:
            un = interaction.guild.get_member(i[0])
            if un is None:
                un = await self.bot.fetch_user(i[0])
                if un is None:
                    un = f"id:`{i[0]}`"
                else:
                    un = str(un)+f"({await self.bot._(interaction.user, 'ranklev-outsideg')})"
            else:
                un = un.mention
            if len(text+f"> {ind+1}.{un}\n　level:{i[1]},exp:{i[2]}\n") <= 2036:
                text = text + f"> {ind+1}.{un}\n　level:{i[1]},exp:{i[2]}\n"
            else:
                text = text+f"({await self.bot._(interaction.user, 'ranklev-lenover')})"
                break
        e = discord.Embed(title=await self.bot._(interaction.user, "ranklev-title"),
                            description=text, color=self.bot.ec)
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="level",description="サーバーレベルカードを表示します。")
    @app_commands.describe(target="表示するメンバー")
    @app_commands.describe(display="メッセージを非表示にするかどうか")
    async def level(self, interaction:discord.Interaction, display:bool, target:Optional[discord.Member]):
        u = target or interaction.user
        LEVEL_FONT = "meiryo.ttc"

        headers = {
            "User-Agent": "DiscordBot (sina-chan with discord.py)",
            "Authorization": f"Bot {self.bot.http.token}"
        }
        async with self.bot.session.get(f"https://discord.com/api/v10/users/{u.id}", headers=headers) as resp:
            resp.raise_for_status()
            ucb = await resp.json()

        if interaction.channel.permissions_for(interaction.guild.me).attach_files is True:
            gs = await self.bot.cursor.fetchone(
                "select * from guilds where id=%s", (interaction.guild.id,))
            #gs = await self.bot.cursor.fetchone()
            level = json.loads(gs["levels"])
            if level.get(str(u.id), None) is None:
                await interaction.response.send_message(await self.bot._(interaction.user, "level-notcount"))
            else:
                nowl = level[str(u.id)]['level']
                exp = level[str(u.id)]['exp']
                nextl = nowl ** 3 + 20
                tonextexp = nextl - exp
                nextl = str(nextl)
                tonextexp = str(tonextexp)
                try:
                    await u.display_avatar.replace(static_format="png").save("imgs/usericon.png")
                    dlicon = Image.open('imgs/usericon.png', 'r')
                except:
                    dlicon = Image.open('imgs/noimg.png', 'r')
                dlicon = dlicon.resize((100, 100))
                cv = None
                if ucb["banner"]:
                    cb = "banner"
                    banner_url = f'https://cdn.discordapp.com/banners/{u.id}/{ucb["banner"]}.png?size=640'
                    async with self.bot.session.get(banner_url, headers=headers) as resp:
                        resp.raise_for_status()
                        bt = await resp.read()
                        with open(f"imgs/custom_banner_{u.id}.png", mode="wb")as f:
                            f.write(bt)
                    cv = Image.open(f"imgs/custom_banner_{u.id}.png", 'r')
                else:
                    c = await self.bot.cursor.fetchone(
                        "select * from users where id=%s", (u.id,))
                    #c = await self.bot.cursor.fetchone()
                    cb = c["levcard"] or "m@ji☆"
                    cv = Image.open('imgs/'+cb+'.png', 'r')
                cv.paste(dlicon, (200, 10))
                dt = ImageDraw.Draw(cv)
                fonta = ImageFont.truetype(LEVEL_FONT, 30)
                fontb = ImageFont.truetype(LEVEL_FONT, 42)
                fontc = ImageFont.truetype(LEVEL_FONT, 20)
                if len(u.display_name) > 11:
                    etc = "…"
                else:
                    etc = ""
                if cb == "kazuta123-a" or cb == "kazuta123-b" or cb == "kazuta123-c" or cb == "tomohiro0405":
                    dt.text(
                        (300, 60), u.display_name[0:10] + etc, font=fonta, fill='#ffffff')

                    dt.text((50, 110), await self.bot._(interaction.user, "lc-level")+str(level[str(u.id)]['level']), font=fontb, fill='#ffffff')

                    dt.text((50, 170), await self.bot._(interaction.user, "lc-exp") + str(level[str(u.id)]['exp'])+"/"+nextl, font=fonta, fill='#ffffff')

                    dt.text((50, 210), await self.bot._(interaction.user, "lc-next") +
                            tonextexp, font=fontc, fill='#ffffff')
                    
                    if cb != "banner":
                        dt.text((50, 300), await self.bot._(interaction.user, "lc-createdby", cb.replace("m@ji☆", "おあず").replace("kazuta123", "kazuta246").replace("-a", "").replace("-b", "").replace("-c", "")), font=fontc, fill='#ffffff')
                else:
                    dt.text(
                        (300, 60), u.display_name[0:10] + etc, font=fonta, fill='#000000')

                    dt.text((50, 110), await self.bot._(interaction.user, "lc-level")+str(level[str(u.id)]['level']), font=fontb, fill='#000000')

                    dt.text((50, 170), await self.bot._(interaction.user, "lc-exp") + str(level[str(u.id)]['exp'])+"/"+nextl, font=fonta, fill='#000000')

                    dt.text((50, 210), await self.bot._(interaction.user, "lc-next") +
                            tonextexp, font=fontc, fill='#000000')

                    if cb != "banner":
                        dt.text((50, 300), await self.bot._(interaction.user, "lc-createdby", cb.replace("m@ji☆", "おあず").replace("kazuta123", "kazuta246").replace("-a", "").replace("-b", "").replace("-c", "")), font=fontc, fill='#000000')

                cv.save("imgs/sina'slevelcard.png", 'PNG')
                await interaction.response.send_message(file=discord.File("imgs/sina'slevelcard.png"), ephemeral=display)
        else:
            try:
                await interaction.response.send_message(embed=discord.Embed(title=await self.bot._(interaction.user, "dhaveper"), description=await self.bot._(interaction.user, "per-sendfile")), ephemeral=True)
            except:
                await interaction.response.send_message(f"{await self.bot._(interaction.user, 'dhaveper')}\n{await self.bot._(interaction.user, 'per-sendfile')}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(level_card(bot))