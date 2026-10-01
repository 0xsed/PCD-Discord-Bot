from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # /WARN
    # =====================================================

    @app_commands.command(
        name="warn",
        description="Warn a member.",
    )
    @app_commands.describe(
        member="Member to warn",
        reason="Reason for the warning",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided",
    ):

        if member == interaction.user:
            await interaction.response.send_message(
                "❌ You cannot warn yourself.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"⚠️ {member.mention} has been warned.\n"
            f"**Reason:** {reason}"
        )

        try:
            await member.send(
                f"⚠️ You received a warning in "
                f"**{interaction.guild.name}**.\n\n"
                f"**Reason:** {reason}"
            )
        except discord.Forbidden:
            pass

    # =====================================================
    # /KICK
    # =====================================================

    @app_commands.command(
        name="kick",
        description="Kick a member.",
    )
    @app_commands.describe(
        member="Member to kick",
        reason="Reason for the kick",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided",
    ):

        if member == interaction.user:
            await interaction.response.send_message(
                "❌ You cannot kick yourself.",
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "❌ You cannot kick this member.",
                ephemeral=True,
            )
            return

        try:
            await member.kick(reason=reason)

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to kick this member.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"👢 {member.mention} has been kicked.\n"
            f"**Reason:** {reason}"
        )

    # =====================================================
    # /BAN
    # =====================================================

    @app_commands.command(
        name="ban",
        description="Ban a member.",
    )
    @app_commands.describe(
        member="Member to ban",
        reason="Reason for the ban",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided",
    ):

        if member == interaction.user:
            await interaction.response.send_message(
                "❌ You cannot ban yourself.",
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "❌ You cannot ban this member.",
                ephemeral=True,
            )
            return

        try:
            await member.ban(reason=reason)

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to ban this member.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"🚫 {member.mention} has been banned.\n"
            f"**Reason:** {reason}"
        )

    # =====================================================
    # /UNBAN
    # =====================================================

    @app_commands.command(
        name="unban",
        description="Unban a user.",
    )
    @app_commands.describe(
        user_id="Discord user ID",
        reason="Reason",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: str = "No reason provided",
    ):

        try:
            user = await self.bot.fetch_user(
                int(user_id)
            )

        except (ValueError, discord.NotFound):
            await interaction.response.send_message(
                "❌ Invalid user ID.",
                ephemeral=True,
            )
            return

        try:
            await interaction.guild.unban(
                user,
                reason=reason,
            )

        except discord.NotFound:
            await interaction.response.send_message(
                "❌ That user is not banned.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ **{user}** has been unbanned."
        )

    # =====================================================
    # /TIMEOUT
    # =====================================================

    @app_commands.command(
        name="timeout",
        description="Timeout a member.",
    )
    @app_commands.describe(
        member="Member to timeout",
        minutes="Duration in minutes",
        reason="Reason",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[
            int,
            1,
            40320,
        ],
        reason: str = "No reason provided",
    ):

        if member == interaction.user:
            await interaction.response.send_message(
                "❌ You cannot timeout yourself.",
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "❌ You cannot timeout this member.",
                ephemeral=True,
            )
            return

        try:
            await member.timeout(
                timedelta(minutes=minutes),
                reason=reason,
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"⏳ {member.mention} has been timed out "
            f"for **{minutes} minute(s)**."
        )

    # =====================================================
    # /UNTIMEOUT
    # =====================================================

    @app_commands.command(
        name="untimeout",
        description="Remove a timeout.",
    )
    @app_commands.describe(
        member="Member",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def untimeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ):

        await member.timeout(None)

        await interaction.response.send_message(
            f"✅ {member.mention} is no longer timed out."
        )

    # =====================================================
    # /CLEAR
    # =====================================================

    @app_commands.command(
        name="clear",
        description="Delete messages.",
    )
    @app_commands.describe(
        amount="Number of messages (1-100)",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[
            int,
            1,
            100,
        ],
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        deleted = await interaction.channel.purge(
            limit=amount
        )

        await interaction.followup.send(
            f"🧹 Deleted **{len(deleted)} messages**.",
            ephemeral=True,
        )

    # =====================================================
    # /SLOWMODE
    # =====================================================

    @app_commands.command(
        name="slowmode",
        description="Set channel slowmode.",
    )
    @app_commands.describe(
        seconds="0-21600 seconds",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def slowmode(
        self,
        interaction: discord.Interaction,
        seconds: app_commands.Range[
            int,
            0,
            21600,
        ],
    ):

        await interaction.channel.edit(
            slowmode_delay=seconds
        )

        await interaction.response.send_message(
            f"🐌 Slowmode: **{seconds} seconds**"
        )

    # =====================================================
    # /LOCK
    # =====================================================

    @app_commands.command(
        name="lock",
        description="Lock this channel.",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def lock(
        self,
        interaction: discord.Interaction,
    ):

        overwrite = (
            interaction.channel.overwrites_for(
                interaction.guild.default_role
            )
        )

        overwrite.send_messages = False

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite,
        )

        await interaction.response.send_message(
            "🔒 This channel has been locked."
        )

    # =====================================================
    # /UNLOCK
    # =====================================================

    @app_commands.command(
        name="unlock",
        description="Unlock this channel.",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def unlock(
        self,
        interaction: discord.Interaction,
    ):

        overwrite = (
            interaction.channel.overwrites_for(
                interaction.guild.default_role
            )
        )

        overwrite.send_messages = None

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite,
        )

        await interaction.response.send_message(
            "🔓 This channel has been unlocked."
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))