# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import traceback

import m10s_util as ut

class info(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def anyuserinfo(self,ctx,*,uid:int=None):
        if uid:
            try:
                u=await bot.fetch_user(uid)
            except discord.NotFound:
                await ctx.send(ut.textto("aui-nf",ctx.author))
            except discord.HTTPException:
                await ctx.send(ut.textto("aui-he",ctx.author))
            except:
                await ctx.send(ut.textto("aui-othere",ctx.author).format(traceback.format_exc()))
            else:
                if u.id in [i[1] for i in self.bot.partnerg]:
                    ptn=":🔗パートナーサーバーオーナー"
                else:
                    ptn=""
                e = discord.Embed(title=f"{ut.textto('aui-uinfo',ctx.author)}{ptn}",color=bot.ec)
                e.add_field(name=ut.textto("aui-name",ctx.author),value=u.name)
                e.add_field(name=ut.textto("aui-id",ctx.author),value=u.id)
                e.add_field(name=ut.textto("aui-dr",ctx.author),value=u.discriminator)
                e.add_field(name=ut.textto("aui-isbot",ctx.author),value=u.bot)
                e.set_thumbnail(url=u.avatar_url)
                e.set_footer(text=ut.textto("aui-created",ctx.author).format(u.created_at))
                e.timestamp = u.created_at
            await ctx.send(embed=e)
        else:
            await ctx.send(ut.textto("aui-nid",ctx.author))

    @commands.command(aliases=["ユーザー情報","ユーザーの情報を教えて"])
    async def userinfo(self,ctx, mus:commands.MemberConverter=None):

        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content )
        if mus == None:
            info = ctx.message.author
        else:
            info = mus
        async with ctx.message.channel.typing(): 
            if info.id in [i[1] for i in self.bot.partnerg]:
                ptn="🔗パートナーサーバーオーナー:"
            else:
                ptn=""
            if ctx.guild.owner == info:
                embed = discord.Embed(title=ut.textto("userinfo-name",ctx.message.author), description=f"{ptn}{info.name} - {ut.ondevicon(info)} - {ut.textto('userinfo-owner',ctx.message.author)}", color=info.color)
            else:
                embed = discord.Embed(title=ut.textto("userinfo-name",ctx.message.author), description=f"{ptn}{info.name} - {ut.ondevicon(info)}", color=info.color)
            try:
                if not info.premium_since is None:
                    embed.add_field(name=ut.textto("userinfo-guildbooster",ctx.message.author), value=f"since {info.premium_since}")
            except:
                pass
            embed.add_field(name=ut.textto("userinfo-joindiscord",ctx.message.author), value=info.created_at)
            embed.add_field(name=ut.textto("userinfo-id",ctx.message.author), value=info.id)
            embed.add_field(name=ut.textto("userinfo-online",ctx.message.author), value=f"{str(info.status)}")
            embed.add_field(name=ut.textto("userinfo-isbot",ctx.message.author), value=str(info.bot))
            embed.add_field(name=ut.textto("userinfo-displayname",ctx.message.author), value=info.display_name)
            embed.add_field(name=ut.textto("userinfo-joinserver",ctx.message.author), value=info.joined_at)
            if not info.activity == None:
                try:
                    if info.activity.name == "Custom Status":
                        embed.add_field(name=ut.textto("userinfo-nowplaying",ctx.message.author), value=f'{info.activity.state}')
                    else:
                        embed.add_field(name=ut.textto("userinfo-nowplaying",ctx.message.author), value=f'{info.activity.name}')
                except:
                    embed.add_field(name=ut.textto("userinfo-nowplaying",ctx.message.author), value=info.activity)
            hasroles = ""
            for r in info.roles:
                hasroles = hasroles + f"{r.mention},"
            embed.add_field(name=ut.textto("userinfo-roles",ctx.message.author), value=hasroles)
            embed.add_field(name="guild permissions",value=f"`{'`,`'.join([i[0] for i in list(info.guild_permissions) if i[1]])}`")
            if not info.avatar_url == None:
                embed.set_thumbnail(url=info.avatar_url_as(static_format='png'))
                embed.add_field(name=ut.textto("userinfo-iconurl",ctx.message.author),value=info.avatar_url_as(static_format='png'))
            else:
                embed.set_image(url=info.default_avatar_url_as(static_format='png'))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(info(bot))