import re
import sqlite3
import time
from collections import defaultdict, deque
from datetime import timedelta
from pathlib import Path

import discord
from discord.ext import commands


# =========================================================
# DATABASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "warnings.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS warnings (
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            warning_count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )
        """
    )

    connection.commit()

    return connection


def add_warning(guild_id: int, user_id: int) -> int:
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO warnings (
            guild_id,
            user_id,
            warning_count
        )
        VALUES (?, ?, 1)

        ON CONFLICT(guild_id, user_id)
        DO UPDATE SET warning_count = warning_count + 1
        """,
        (guild_id, user_id),
    )

    connection.commit()

    cursor = connection.execute(
        """
        SELECT warning_count
        FROM warnings
        WHERE guild_id = ?
        AND user_id = ?
        """,
        (guild_id, user_id),
    )

    warning_count = cursor.fetchone()[0]

    connection.close()

    return warning_count

    # =========================================================
# AUTOMOD CHANNELS
# =========================================================

AUTOMOD_CHANNEL_IDS = {
    1327968957843509278,
    1351392993021530173,
    1436199400304152687,
    1461015922662707353,
    
}


# =========================================================
# SETTINGS
# =========================================================

# -------------------------
# Anti-Spam
# -------------------------

SPAM_MESSAGE_LIMIT = 5
SPAM_TIME_WINDOW = 5

# -------------------------
# Anti-Duplicate
# -------------------------

DUPLICATE_MESSAGE_LIMIT = 3

# -------------------------
# Anti-Raid
# -------------------------

RAID_JOIN_LIMIT = 10
RAID_TIME_WINDOW = 10

# -------------------------
# Anti-Spam punishment
# -------------------------

SPAM_TIMEOUT_SECONDS = 10


# =========================================================
# IMMUNE ROLES
# =========================================================

# These roles are immune ONLY to Anti-Link.
#
# They are NOT immune to:
# - Anti-Spam
# - Anti-Duplicate
# - Anti-Raid

IMMUNE_ROLE_IDS = {
    1201483694507040768,
    1496721835277025351,
    1451247966533976194,
    1422198973598535680,
}


# =========================================================
# LINK DETECTION
# =========================================================

URL_PATTERN = re.compile(
    r"(https?://\S+|www\.\S+|discord\.gg/\S+)",
    re.IGNORECASE,
)


# =========================================================
# AUTOMOD
# =========================================================

class AutoMod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # -------------------------------------------------
        # Anti-Spam
        # guild_id -> user_id -> timestamps
        # -------------------------------------------------

        self.message_times = defaultdict(
            lambda: defaultdict(deque)
        )

        # -------------------------------------------------
        # Anti-Duplicate
        # guild_id -> user_id -> messages
        # -------------------------------------------------

        self.recent_messages = defaultdict(
            lambda: defaultdict(deque)
        )

        # -------------------------------------------------
        # Anti-Raid
        # guild_id -> join timestamps
        # -------------------------------------------------

        self.join_times = defaultdict(deque)

        # Make sure database exists
        connection = get_connection()
        connection.close()

    # =====================================================
    # STAFF CHECK
    # =====================================================

    def is_staff(
        self,
        member: discord.Member,
    ) -> bool:

        return (
            member.guild_permissions.administrator
            or member.guild_permissions.manage_messages
        )

    # =====================================================
    # LINK IMMUNITY
    # =====================================================

    def is_link_immune(
        self,
        member: discord.Member,
    ) -> bool:

        member_role_ids = {
            role.id
            for role in member.roles
        }

        return bool(
            member_role_ids.intersection(
                IMMUNE_ROLE_IDS
            )
        )

    # =====================================================
    # ANTI-SPAM
    # =====================================================

    async def check_spam(
        self,
        message: discord.Message,
    ) -> bool:

        guild_id = message.guild.id
        user_id = message.author.id

        now = time.monotonic()

        timestamps = self.message_times[
            guild_id
        ][user_id]

        timestamps.append(now)

        # Remove timestamps outside the window
        while (
            timestamps
            and now - timestamps[0] > SPAM_TIME_WINDOW
        ):
            timestamps.popleft()

        # Not spam yet
        if len(timestamps) < SPAM_MESSAGE_LIMIT:
            return False

        # Reset tracker
        timestamps.clear()

        # Delete spam message
        try:
            await message.delete()

        except discord.Forbidden:
            print(
                "Anti-Spam: Missing Manage Messages permission."
            )

        except discord.NotFound:
            pass

        # Timeout user
        try:
            await message.author.timeout(
                timedelta(
                    seconds=SPAM_TIMEOUT_SECONDS
                ),
                reason="Anti-Spam violation",
            )

        except discord.Forbidden:
            print(
                "Anti-Spam: Missing Moderate Members permission."
            )

        except discord.HTTPException:
            pass

        # DM user
        try:
            await message.author.send(
                f"⚠️ Your messages in "
                f"**{message.guild.name}** "
                "were detected as spam.\n\n"
                f"You have been timed out for "
                f"**{SPAM_TIMEOUT_SECONDS} seconds**."
            )

        except discord.Forbidden:
            pass

        return True

    # =====================================================
    # ANTI-DUPLICATE
    # =====================================================

    async def check_duplicate(
        self,
        message: discord.Message,
    ) -> bool:

        content = message.content.strip().lower()

        # Ignore empty messages
        if not content:
            return False

        guild_id = message.guild.id
        user_id = message.author.id

        recent = self.recent_messages[
            guild_id
        ][user_id]

        recent.append(content)

        # Keep only recent messages
        while len(recent) > DUPLICATE_MESSAGE_LIMIT:
            recent.popleft()

        # Same message 3 times
        if (
            len(recent) == DUPLICATE_MESSAGE_LIMIT
            and len(set(recent)) == 1
        ):

            recent.clear()

            # Delete repeated message
            try:
                await message.delete()

            except discord.Forbidden:
                print(
                    "Anti-Duplicate: "
                    "Missing Manage Messages permission."
                )

            except discord.NotFound:
                pass

            # DM user
            try:
                await message.author.send(
                    f"⚠️ Repeated messages are not allowed "
                    f"in **{message.guild.name}**."
                )

            except discord.Forbidden:
                pass

            return True

        return False

    # =====================================================
    # ANTI-LINK
    # =====================================================

    async def check_link(
        self,
        message: discord.Message,
    ) -> bool:

        # Immune roles bypass Anti-Link ONLY
        if self.is_link_immune(message.author):
            return False

        # No link
        if not URL_PATTERN.search(
            message.content
        ):
            return False

        guild_id = message.guild.id
        user_id = message.author.id

        # Add warning
        warning_count = add_warning(
            guild_id,
            user_id,
        )

        # Delete message
        try:
            await message.delete()

        except discord.Forbidden:
            print(
                "Anti-Link: Missing Manage Messages permission."
            )

        except discord.NotFound:
            pass

        # =================================================
        # 4TH VIOLATION = BAN
        # =================================================

        if warning_count >= 4:

            try:
                await message.author.ban(
                    reason="Exceeded 3 link warnings."
                )

                await message.channel.send(
                    f"🚫 {message.author.mention} "
                    "has been banned for exceeding "
                    "3 link warnings."
                )

            except discord.Forbidden:
                await message.channel.send(
                    "⚠️ I don't have permission "
                    "to ban this member."
                )

            return True

        # =================================================
        # WARNING 1-3 = DM
        # =================================================

        remaining = 3 - warning_count

        try:
            await message.author.send(
                f"⚠️ **Warning {warning_count}/3**\n\n"
                f"You sent a link in "
                f"**{message.guild.name}** "
                "where links are not allowed.\n\n"
                "Your message has been removed.\n"
                f"You have **{remaining} warning(s) "
                "remaining** before an automatic ban."
            )

        except discord.Forbidden:
            print(
                f"Anti-Link: Could not DM "
                f"{message.author}."
            )

        return True

    # =====================================================
    # MESSAGE EVENT
    # =====================================================

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

        # Admins and moderators bypass AutoMod
        if self.is_staff(message.author):
            return

        # -------------------------------------------------
        # Anti-Link
        # -------------------------------------------------

        if await self.check_link(message):
            return

        # -------------------------------------------------
        # Anti-Spam
        # -------------------------------------------------

        if await self.check_spam(message):
            return

        # -------------------------------------------------
        # Anti-Duplicate
        # -------------------------------------------------

        if await self.check_duplicate(message):
            return

    # =====================================================
    # ANTI-RAID
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member,
    ):

        guild_id = member.guild.id
        now = time.monotonic()

        joins = self.join_times[guild_id]

        joins.append(now)

        # Remove old joins
        while (
            joins
            and now - joins[0] > RAID_TIME_WINDOW
        ):
            joins.popleft()

        # Not enough joins
        if len(joins) < RAID_JOIN_LIMIT:
            return

        # =================================================
        # RAID DETECTED
        # =================================================

        join_count = len(joins)

        print(
            f"⚠️ Possible raid detected in "
            f"{member.guild.name}: "
            f"{join_count} joins in "
            f"{RAID_TIME_WINDOW} seconds."
        )

        # Find usable channel
        alert_channel = None

        for channel in member.guild.text_channels:

            permissions = channel.permissions_for(
                member.guild.me
            )

            if permissions.send_messages:
                alert_channel = channel
                break

        if alert_channel:

            try:
                await alert_channel.send(
                    "🚨 **Possible raid detected!**\n"
                    f"Detected **{join_count} joins** "
                    f"within **{RAID_TIME_WINDOW} seconds**."
                )

            except discord.HTTPException:
                pass

        # Reset counter
        joins.clear()


# =========================================================
# SETUP
# =========================================================

async def setup(bot):
    await bot.add_cog(AutoMod(bot))