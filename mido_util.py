import discord
from discord.ext import commands
import asyncio
import sqlite3
import traceback

#InvailedIDException
class InvailedIDException(Exception):
    pass

#InviteNotFound
class InviteNotFound(Exception):
    pass

#resolve_invite
async def resolve_invite(ctx, code:str):
    try:
        ret = await ctx.bot.fetch_invite(code)
    except:
        raise InviteNotFound(f"{code} という招待は見つかりませんでした")
    else:
        return ret

#get_channel_or_user
def get_channel_or_user(ctx, id:int):
    result = ctx.bot.get_user(id)
    if result is None:
        result = ctx.bot.get_channel(id)
    return result

#get_region
def get_region(guild):
    region = guild.region
    
    regions = {
        "brazil":"🇧🇷 Brazil",
        "europe":"🇪🇺 Europe",
        "hongkong":"🇭🇰 HongKong",
        "india":"🇮🇳 India",
        "japan":"🇯🇵 Japan",
        "russia":"🇷🇺 Russia",
        "singapore":"🇸🇬 Singapore",
        "southafrica":"🇿🇦 SouthAfrica",
        "sydney":"🇦🇺 Sydney",
        "us_central":"🇺🇸 US_Central",
        "us_east":"🇺🇸 US_East",
        "us_south":"🇺🇸 US_South",
        "us_west":"🇺🇸 US_West"
    }
    
    try:
        key = regions[str(region)]
    except KeyError:
        key = str(region)
    
    return key

#Neta
def is_jun50(ctx, member=None):
    if member is None:
        member = ctx.author
    else:
        member = member
    
    if member.id == 579598776721735690 or member.id == 449867036558884866:
        result = True
    else:
        result = False
    
    return result

#VoiceChannelConverter
class VoiceChannelConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.VoiceChannelConverter().convert(ctx, argument)
        except:
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument!r} というIDのチャンネルは見つかりませんでした")
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f"{argument!r} というIDのチャンネルは見つかりませんでした")
                return channel

#TextChannelConverter
class TextChannelConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument!r} というIDのチャンネルは見つかりませんでした")
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f"{argument!r} というIDのチャンネルは見つかりませんでした")
                return channel

#BotUserConverter
class BotUserConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument("このIDはBotのIDではありません")
        try:
            user = await ctx.bot.fetch_user(argument)
        except discord.NotFound:
            raise commands.BadArgument("そのユーザーは見つかりませんでした")
        except discord.HTTPException as e:
            raise commands.BadArgument(f"ユーザー検索中にエラーが発生しました: {e}")
        else:
            if not user.bot:
                raise commands.BadArgument("このユーザーはBotではありません")
            return user

#BannedMemberConverter
class BannedMemberConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument('このユーザーはBanされていません') from None

        ban_list = await ctx.guild.bans()
        entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument('このユーザーはBanされていません')
        return entity

#FetchMemberConverter
class FetchUserConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            u = await commands.MemberConverter().convert(ctx, argument)
        try:
            u = await ctx.bot.fetch_user(argument)
        except discord.NotFound:
            raise commands.BadArgument('ユーザーが見つかりませんでした') from None
        except discord.HTTPException:
            raise commands.BadArgument('エラーが発生しました') from None
        
        return u

#MemberConverter
class MemberConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            u = await commands.MemberConverter().convert(ctx, argument)
        except commands.MemberNotFound:
            u = discord.utils.get(ctx.bot.users, name=argument) or discord.utils.get(ctx.bot.users, id=argument)
        except Exception as e:
            raise commands.BadArgument(e) from None
        
        if u is None:
            try:
                u = await FetchUserConverter().convert(ctx, argument)
            except Exception as e:
                raise Exception(e) from None
            
        return u

#get_status_from_url
async def get_status_from_url(ctx, url=None):
    if url is None:
        raise commands.MissingRequiredArgument(url)
    
    if url.startswith("http"):
        url = url
    else:
        url = f"http://{url}"
    
    bot = ctx.bot
    
    async with bot.session.get(url) as resp:
        status = resp.status
    
    return status
