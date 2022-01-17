import discord
from discord.ext import commands

import re
import random

#get_status
def get_status(member):
    if str(member.status) == "online":
        return "💚オンライン"
    elif str(member.status) == "idle":
        return "🧡退席中"
    elif str(member.status) == "dnd":
        return "❤取り込み中"
    elif str(member.status) == "offline":
        return "🖤オフライン"

#resolve_url
def resolve_url(url):
    HTTP_URL_REGEX = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    URL_REGEX = "[\w/:%#\$&\?\(\)~\.=\+\-]+"
    
    if re.match(HTTP_URL_REGEX, str(url)):
        return str(url)
    elif re.match(URL_REGEX, str(url)):
        return f"http://" + str(url)

#resolve_invite
async def resolve_invite(ctx, code:str):
    try:
        return await ctx.bot.fetch_invite(code)
    except discord.NotFound:
        raise commands.BadArgument(f"Invite {code} not found.")
    except discord.HTTPException as e:
        raise commands.BadArgument(f"Error fetching invite code: {e}")

#get_channel_or_user
def get_channel_or_user(ctx, id:int):
    result = ctx.bot.get_user(id)
    if result is None:
        result = ctx.bot.get_channel(id)
        
        if result is None:
            raise commands.BadArgument(f"Argument {id} not found.")
    return result

#get_features
def get_features(guild):
    feature = guild.features
    
    key = []
    
    features = {
        "VIP_REGIONS":"VIP Region",
        "VANITY_URL":"Vanity URL",
        "INVITE_SPLASH":"Splash Invite",
        "VERIFIED":"Verified",
        "PARTNERED":"Partnered",
        "MORE_EMOJI":"More Emoji",
        "DISCOVERABLE":"Discoverable",
        "FEATUREABLE":"Featureable",
        "COMMUNITY":"Community",
        "PUBLIC":"Public",
        "NEWS":"News",
        "BANNER":"Banner",
        "ANIMATED_ICON":"Animated Icon",
        "PUBLIC_DISABLED":"Public Disabled",
        "WELCOME_SCREEN_ENABLED":"Welcome Screen Enabled",
        "MEMBER_VERIFICATION_GATE_ENABLED":"Member Verification Gate Enabled",
        "PREVIEW_ENABLED":"Preview Enabled"
    }
    
    for i in range(len(feature)):
        try:
            key.append(features[str(feature)])
        except KeyError:
            key.append(str(feature))
    
    return key

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
    
    return member.id in [579598776721735690, 449867036558884866]

#get_guild_or_user
async def get_guild_or_user(ctx, id):
    if ctx.bot.get_guild(id) is None:
        try:
            return await FetchUserConverter().convert(ctx, str(id))
        except:
            raise commands.BadArgument(f"ID {id} not guild or user.")
    
#choice
def choice(l, c=1):
    r = []
    
    for c in range(c):
        d = random.choice(l)
    
        r.append(d)
        l.remove(d)
        
    return r

#VoiceChannelConverter
class VoiceChannelConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.VoiceChannelConverter().convert(ctx, argument)
        except:
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"VoiceChannel {argument!r} not found.")
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f"VoiceChannel {argument!r} not found.")
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
                raise commands.BadArgument(f"TextChannel {argument!r} not found.")
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f"TextChannel {argument!r} not found.")
                return channel

#ChannelConverter
class ChannelConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await TextChannelConverter().convert(ctx, argument)
        except:
            try:
                return await VoiceChannelConverter().convert(ctx, argument)
            except:
                try:
                    return await commands.CategoryChannelConverter().convert(ctx, argument)
                except:
                    raise commands.ChannelNotFound(argument)

#GuildConverter
class GuildConverter(commands.Converter):
    async def convert(self, ctx, argument):
        guild = None
        if argument.isdigit():
            guild = ctx.bot.get_guild(int(argument))
            
            if guild is None:
                raise commands.BadArgument(f"Guild {argument} not found.")
        else:
            if guild is None:
                guild = discord.utils.get(ctx.bot.guilds, name=argument)
                
                if guild is None:
                    raise commands.BadArgument(f"Guild {argument} not found.")
        
        return guild

#BotUserConverter
class BotUserConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument("Not a valid bot user ID.")
        try:
            result = await ctx.bot.fetch_user(argument)
        except discord.NotFound:
            raise commands.BadArgument("Bot user not found (404).")
        except discord.HTTPException as exc:
            raise commands.BadArgument(f"Error fetching bot user: {exc}")
        else:
            if not result.bot:
                raise commands.BadArgument("This is not a bot.")
            return result

#BannedMemberConverter
class BannedMemberConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument(f'User {argument} is not banned.') from None

        ban_list = await ctx.guild.bans()
        entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument(f'User {argument} is not banned.')
        return entity

#FetchUserConverter
class FetchUserConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            return await commands.MemberConverter().convert(ctx, argument)
        try:
            return await ctx.bot.fetch_user(int(argument))
        except discord.NotFound:
            raise commands.BadArgument(f'User {argument} not found.') from None
        except discord.HTTPException as exc:
            raise commands.BadArgument(f'Error fetching user: {exc}') from None

#MemberConverter
class MemberConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            try:
                return await commands.MemberConverter().convert(ctx, argument)
            except:
                try:
                    return await commands.UserConverter().convert(ctx, argument)
                except:
                    raise commands.MemberNotFound(argument)
        else:
            try:
                return await commands.MemberConverter().convert(ctx, argument)
            except:
                try:
                    return await commands.UserConverter().convert(ctx, argument)
                except:
                    try:
                        return await FetchUserConverter().convert(ctx, argument)
                    except:
                        raise commands.MemberNotFound(argument)