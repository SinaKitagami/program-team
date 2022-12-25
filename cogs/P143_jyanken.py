# -*- coding: utf-8 -*-

from __future__ import annotations

import discord
from discord.ext import commands
from typing import Any
import random
import asyncio

import m10s_util as ut

# このプログラムはPoteto143氏によって作成され、yaakiyuによって改善されています。


class ContentEvent(asyncio.Event):
    content: Any


class JankenView(discord.ui.View):
    msg: discord.Message

    def __init__(self, event: ContentEvent):
        super().__init__(timeout=15.0)
        self.event = event
        self.closed = False

    async def on_timeout(self):
        if self.closed:
            return
        await self.msg.edit(view=None, embed=discord.Embed(
            title="ジャンケン", description="15秒間操作がされなかったのでゲームを終了しました。",
            color=0xff0000
        ))
        self.event.set()

    @discord.ui.button(emoji="🖐")
    async def pa(self, interaction: discord.Interaction, _):
        self.event.content = (interaction, 0)
        self.event.set()

    @discord.ui.button(emoji="✊")
    async def gu(self, interaction: discord.Interaction, _):
        self.event.content = (interaction, 0)
        self.event.set()

    @discord.ui.button(emoji="✌️")
    async def tyoki(self, interaction: discord.Interaction, _):
        self.event.content = (interaction, 0)
        self.event.set()


class jyanken(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    EMOJIS = ["🖐", "✊", "✌️"]

    RESULT_PATTERNS = [
        ["あいこで...", "あいこで...", "まだまだ！あいこで..."],
        ["残念、負けちゃった...", "あーあ、負けちゃった。", "負けた、くやしい！"],
        ["やった、私の勝ち！", "私の勝ち、残念でした！", "勝った！また挑戦してね！"]
    ]

    @commands.hybrid_command(name="jyanken", description="じゃんけんできます。")
    @commands.bot_has_permissions(manage_messages=True)
    @ut.runnable_check()
    async def command(self, ctx):
        embed = discord.Embed(
            title="ジャンケン", description="ジャンケンをするよ。\n最初はグー、ジャンケン…",
            color=0xffff00
        )
        event = ContentEvent()
        view = JankenView(event)
        msg = await ctx.send(embed=embed, view=view)
        view.msg = msg

        while True:
            await event.wait()

            hands = [event.content[1], random.randint(0, 2)]  # [ユーザー, Bot]
            if hands[0] == hands[1]:
                await event.content[0].response.edit_message(embed=discord.Embed(
                    title="ジャンケン", description=f"ポン!{EMOJIS[hands[1]]}\n{random.choice(self.RESULT_PATTERNS[0])}",
                    color=self.bot.ec
                ))
                event.set()
                continue

            if (hands[0] + 1) % 3 == hands[1]:
                result = random.choice(self.RESULT_PATTERNS[1])  # ユーザーの勝ち
            else:
                result = random.choice(self.RESULT_PATTERNS[2])  # ユーザーの負け

            await event.content[0].response.edit_message(embed=discord.Embed(
                title="ジャンケン", description=f"ポン!{EMOJIS[hands[1]]}\n{result}",
                color=self.bot.ec
            ))
            view.closed = True
            return


async def setup(bot):
    await bot.add_cog(jyanken(bot))
