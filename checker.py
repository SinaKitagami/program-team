import re
import statistics

INVITE_REGEX = re.compile(r'(?:https?\:\/\/)?discord(?:\.gg|(?:app)?\.com\/invite)\/([a-zA-Z0-9]+)')
CUSTOM_EMOJI_REGEX = re.compile(r'<a?:[a-zA-Z0-9_]{2,32}:[0-9]{18,23}>')
UNICODE_EMOJI_REGEX = re.compile(r'[\U00002600-\U000027BF]|[\U0001f300-\U0001f64F]|[\U0001f680-\U0001f6FF]')

class MaliciousInput(Exception):
    """Input was malicious or spammy."""
    def __init__(self, reason='Unknown reason', should_ban=False):
        super().__init__()
        self.reason = reason
        self.should_ban = should_ban

def content_checker(bot, message):
    """Checks input, and raises MaliciousInput when it is"""
    content = message.content
    is_team = message.author.id in bot.team_sina

    # mentions
    if message.mention_everyone:
        raise MaliciousInput('mentions at-everyone/at-here', True)

    if '@everyone' in content or '@here' in content:
        raise MaliciousInput('mentions at-everyone/at-here', True)

    if len(message.mentions) > 5:
        raise MaliciousInput('too many mentions')

    if len(message.raw_mentions) > 5:
        raise MaliciousInput('too many mentions')

    if len(message.role_mentions) > 3:
        raise MaliciousInput('too many role mentions')

    if len(message.raw_role_mentions) > 3:
        raise MaliciousInput('too many role mentions')

    if not is_team:
        invites = len(INVITE_REGEX.findall(message.content))
        if invites > 2:
            raise MaliciousInput('invite link (insta-ban)', True)
        elif invites:
            raise MaliciousInput('invite link')

    lines = message.content.split('\n')
    if len(lines) > 10:
        line_lengths = [len(line) for line in lines]
        if statistics.median(line_lengths) < 4:
            raise MaliciousInput('too many short lines')

    custom_emojis = len(CUSTOM_EMOJI_REGEX.findall(message.content))
    if custom_emojis > 25:
        raise MaliciousInput('custom emoji spam (insta-ban)', True)
    elif custom_emojis > 10:
        raise MaliciousInput('custom emoji spam')

    unicode_emojis = len(UNICODE_EMOJI_REGEX.findall(message.content))
    if unicode_emojis > 40:
        raise MaliciousInput('unicode emoji spam (insta-ban)', True)
    elif unicode_emojis > 20:
        raise MaliciousInput('unicode emoji spam')
