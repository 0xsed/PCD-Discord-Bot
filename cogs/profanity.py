import re

import discord
from discord.ext import commands


# =========================================================
# PROFANITY WORDS
# =========================================================

PROFANITY_WORDS = {
    # English
    "fuck",
    "fucking",
    "fucker",
    "shit",
    "bitch",
    "bastard",
    "asshole",
    "dumbass",
    "bullshit",

    # Filipino / Tagalog
    "putangina",
    "putang ina",
    "tangina",
    "tang ina",
    "gago",
    "gaga",
    "tarantado",
    "tarantada",
    "ulol",
    "tanga",
    "bobo",
    "bwisit",
    "leche",
    "lintik",
    "hayop",
    "yawa",
    "pakyu",

    # Spanish
    "puta",
    "puto",
    "mierda",
    "cabron",
    "cabrona",
    "coño",

    # French
    "merde",
    "putain",
    "connard",
    "connasse",

    # German
    "scheisse",
    "arschloch",

    # Portuguese
    "merda",
    "caralho",
    "porra",

    # Italian
    "cazzo",
    "merda",
    "stronzo",
    "stronza",
}


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_text(text: str) -> str:
    text = text.lower()

    # Remove spaces and common separators
    text = re.sub(
        r"[\s_\-.*~`]+",
        "",
        text,
    )

    return text


def contains_profanity(text: str) -> bool:

    normalized = normalize_text(text)

    for word in PROFANITY_WORDS:

        normalized_word = normalize_text(word)

        if normalized_word in normalized:
            return True

    return False


# =========================================================
# PROFANITY COG
# =========================================================

class Profanity(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message,
    ):

        # Ignore bots
        if message.author.bot:
            return

        # Ignore DMs
        if message.guild is None:
            return

        # Admin / Manage Messages bypass
        if message.author.guild_permissions.manage_messages:
            return

        # Check profanity
        if not contains_profanity(
            message.content
        ):
            return

        # Delete message
        try:
            await message.delete()

        except discord.Forbidden:
            print(
                "Profanity: Missing Manage Messages permission."
            )

        except discord.NotFound:
            pass

        # DM user
        try:
            await message.author.send(
                f"⚠️ Your message in "
                f"**{message.guild.name}** "
                "was removed because it contained "
                "prohibited language."
            )

        except discord.Forbidden:
            print(
                f"Profanity: Could not DM "
                f"{message.author}."
            )


async def setup(bot):
    await bot.add_cog(Profanity(bot))