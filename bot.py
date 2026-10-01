import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is missing.")


# --------------------------------------------------
# Render Health Server
# --------------------------------------------------

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"PCD Discord Bot is running!")

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler,
    )

    print(f"Health server running on port {port}")

    server.serve_forever()


threading.Thread(
    target=start_health_server,
    daemon=True,
).start()


# --------------------------------------------------
# Discord Bot
# --------------------------------------------------

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


# --------------------------------------------------
# Bot Ready
# --------------------------------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("Bot is online!")


# --------------------------------------------------
# Start Bot
# --------------------------------------------------

bot.run(TOKEN)