# -*- coding: utf-8 -*-

from os import cpu_count
import discord
from discord.ext import commands,tasks

import twitter


class twinotif(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.twi = twitter.Twitter(auth=twitter.OAuth(bot.T_Acs_Token, bot.T_Acs_SToken, bot.T_API_key, bot.T_API_SKey))
        self.target = "sina_chan_dbot"
        self.last_id = self.gtwi_fu(self.target)[0]
        self.ch = self.bot.get_channel(1035026381853167676)
        self.mention = "<@&889157660837048350>"
        self.loop_task.start()

    def gtwi_fu(self,uname):
        ret = self.twi.statuses.user_timeline(screen_name=uname,count=1)
        return (int(ret[0]["id"]), ret[0])

    @tasks.loop(seconds=10)
    async def loop_task(self):
        ret = self.gtwi_fu(self.target)
        if not self.last_id == ret[0]:
            self.last_id = ret[0]
            tweet = ret[1]
            embed = discord.Embed(description=tweet["text"], color=int(
                tweet["user"]["profile_background_color"], 16))
            embed.set_author(name=f'{tweet["user"]["name"]}(@{tweet["user"]["screen_name"]})',
                                url=f'https://twitter.com/{tweet["user"]["screen_name"]}', icon_url=tweet["user"]["profile_image_url_https"])
            try:
                embed.set_image(
                    url=tweet["entities"]["media"][0]["media_url_https"])
            except:
                pass
            embed.add_field(name="Twitterで見る", value=f'https://twitter.com/{tweet["user"]["screen_name"]}/status/{tweet["id"]}')
            await self.ch.send(f"{self.mention}",embed=embed)

async def setup(bot):
    await bot.add_cog(twinotif(bot))