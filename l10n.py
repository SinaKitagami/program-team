import os
import discord
from discord.ext import commands

LOCALES = [lang[:-5] for lang in os.listdir("lang") if lang.endswith(".json")]

class MissingTranslation(Exception):
    pass

class TranslateHandler:
    def __init__(self, bot, supported_locales=LOCALES):
        self.bot = bot
        self.supported_locales = supported_locales
        self._translation_cache = {}
        self._lang_cache = {}

    def get_string_for(self, lang, key, placeholder=""):
        if lang not in self.supported_locales:
            return placeholder
        if self._translation_cache and lang in self._translation_cache and key in self._translation_cache[lang]:
            return self._translation_cache[lang][key]
        try:
            with open(f"lang/{lang}.json", "r", encoding="utf-8") as f:
                self.cache_with_same_key(lang, key, f)
                value = f.get(key, None)
                if value:
                    return value
                raise MissingTranslation
        except (FileNotFoundError, MissingTranslation):
            if lang == "ja":
                return placeholder
            else:
                return self.get_string_for("ja", key, placeholder)

    def cache_with_same_key(self, lang, key, f):
        if lang not in self._translation_cache:
            self._translation_cache[lang] = {}
        key_name = key.split("-")[0]
        keys = [file_key for file_key in f.keys() if file_key.startswith(key_name)]
        for cache_key in keys:
            self._translation_cache[cache_key] = f[cache_key]

    def clean_cache(self):
        self._translation_cache = {}
        self._lang_cache = {}

    def update_language_cache(self, target, to=None):
        if to is None:
            if isinstance(target, discord.Guild):
                to = self.get_lang_by_guild(target, cache=False)
            else:
                to = self.get_lang_by_user(target, cache=False)
            return # get function caches
        if to not in self.supported_locales:
            return
        self._lang_cache[target.id] = to

    def get_lang_by_guild(self, guild, cache=True):
        if cache and guild.id in self._lang_cache:
            return self._lang_cache[guild.id]
        guild_db = self.bot.cursor.execute("SELECT lang FROM guilds WHERE id=?", (guild.id,)).fetchone()
        lang = None
        if not guild_db:
            lang = guild.preferred_locale
        elif not guild_db["lang"]:
            lang = guild.preferred_locale
        else:
            lang = guild_db["lang"]
            if lang in self.supported_locales:
                self._lang_cache[guild.id] = lang
                return lang
        if lang in self.supported_locales:
            return lang
        return None

    def get_lang_by_user(self, user, cache=True):
        if cache and user.id in self._lang_cache:
            return self._lang_cache[user.id]
        user_db = self.bot.cursor.execute("SELECT lang FROM users WHERE id=?", (user.id,)).fetchone()
        if user_db and user_db["lang"] and user_db["lang"] in self.supported_locales:
            self._lang_cache[user.id] = lang
            return user_db["lang"]
        return None

    def get_lang(self, user):
        lang = self.get_lang_by_user(user)
        if lang:
            return lang
        if isinstance(user, discord.Member):
            lang = self.get_lang_by_guild(user.guild)
            if lang:
                return lang
        return "ja"

    def get_translation_for(self, user, key, *args, **kwargs):
        return self.get_raw_translation(self.get_lang(user), key, *args, **kwargs)

    def get_guild_translation_for(self, guild, key, *args, **kwargs):
        lang = self.get_lang_by_guild(guild)
        if not lang:
            lang = "ja"
        return self.get_raw_translation(lang, key, *args, **kwargs)

    def get_raw_translation(self, lang, key, *args, **kwargs):
        word = self.get_string_for(lang, key)
        return word.format(*args, **kwargs)

    def get_any_translation(self, target, key, *args, **kwargs):
        if isinstance(target, discord.abc.User):
            return self.get_translation_for(target, key, *args, **kwargs)
        elif isinstance(target, discord.Guild):
            return self.get_guild_translation_for(target, key, *args, **kwargs)
        return self.get_raw_translation(target, key, *args, **kwargs)

class LocalizedContext(commands.Context):
    def _(self, key, *args, **kwargs):
        return self.bot.translate_handler.get_translation_for(self.author, key, *args, **kwargs)

    def l10n(self, user, key, *args, **kwargs):
        return self.bot.translate_handler.get_translation_for(user, key, *args, **kwargs)

    def l10n_guild(self, guild, key, *args, **kwargs):
        return self.bot.translate_handler.get_guild_translation_for(guild, key, *args, **kwargs)

    def l10n_any(self, target, key, *args, **kwargs):
        return self.bot.translate_handler.get_any_translation(target, key, *args, **kwargs)

    def l10n_raw(self, lang, key, *args, **kwargs):
        return self.bot.translate_handler.get_raw_translation(lang, key, *args, **kwargs)

    def user_lang(self, user=None):
        if user is None:
            user = self.author
        return self.bot.translate_handler.get_lang_by_user(user)
