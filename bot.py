import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")


class PaldoBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()

        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self):
        await self.load_extension("cogs.automod")
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.utility")
        await self.load_extension("cogs.profanity")

        await self.tree.sync()

        print("Slash commands synced!")


bot = PaldoBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("Bot is online!")


bot.run(TOKEN)