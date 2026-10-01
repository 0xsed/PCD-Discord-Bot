import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # /PING
    # =====================================================

    @app_commands.command(
        name="ping",
        description="Check bot latency.",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def ping(
        self,
        interaction: discord.Interaction,
    ):

        latency = round(
            self.bot.latency * 1000
        )

        await interaction.response.send_message(
            f"🏓 Pong! `{latency}ms`"
        )

    # =====================================================
    # /SERVERINFO
    # =====================================================

    @app_commands.command(
        name="serverinfo",
        description="Show server information.",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def serverinfo(
        self,
        interaction: discord.Interaction,
    ):

        guild = interaction.guild

        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="👥 Members",
            value=str(guild.member_count),
            inline=True,
        )

        embed.add_field(
            name="🆔 Server ID",
            value=str(guild.id),
            inline=True,
        )

        embed.add_field(
            name="💬 Channels",
            value=str(len(guild.channels)),
            inline=True,
        )

        embed.add_field(
            name="🎭 Roles",
            value=str(len(guild.roles)),
            inline=True,
        )

        if guild.icon:
            embed.set_thumbnail(
                url=guild.icon.url
            )

        await interaction.response.send_message(
            embed=embed
        )

    # =====================================================
    # /USERINFO
    # =====================================================

    @app_commands.command(
        name="userinfo",
        description="Show member information.",
    )
    @app_commands.describe(
        member="Member to inspect",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def userinfo(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
    ):

        member = member or interaction.user

        embed = discord.Embed(
            title=f"👤 {member}",
            color=member.color,
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="🆔 User ID",
            value=str(member.id),
            inline=False,
        )

        embed.add_field(
            name="📅 Account Created",
            value=discord.utils.format_dt(
                member.created_at,
                style="D",
            ),
            inline=False,
        )

        roles = [
            role.mention
            for role in member.roles
            if role != interaction.guild.default_role
        ]

        embed.add_field(
            name="🎭 Roles",
            value=", ".join(roles)
            if roles
            else "No roles",
            inline=False,
        )

        await interaction.response.send_message(
            embed=embed
        )

    # =====================================================
    # /AVATAR
    # =====================================================

    @app_commands.command(
        name="avatar",
        description="Show a member's avatar.",
    )
    @app_commands.describe(
        member="Member",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
    ):

        member = member or interaction.user

        embed = discord.Embed(
            title=f"🖼️ {member.display_name}'s Avatar",
            color=discord.Color.blurple(),
        )

        embed.set_image(
            url=member.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )

    # =====================================================
    # /BOTINFO
    # =====================================================

    @app_commands.command(
        name="botinfo",
        description="Show bot information.",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def botinfo(
        self,
        interaction: discord.Interaction,
    ):

        embed = discord.Embed(
            title="🤖 PaldoCryptoDAO",
            description=(
                "PaldoCryptoDAO moderation "
                "and utility bot."
            ),
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="📡 Latency",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True,
        )

        embed.add_field(
            name="🆔 Bot ID",
            value=str(self.bot.user.id),
            inline=True,
        )

        embed.add_field(
            name="🛡️ Servers",
            value=str(len(self.bot.guilds)),
            inline=True,
        )

        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )

    # =====================================================
    # /HELP
    # =====================================================

    @app_commands.command(
        name="help",
        description="Show bot commands.",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def help(
        self,
        interaction: discord.Interaction,
    ):

        embed = discord.Embed(
            title="🤖 PaldoCryptoDAO Commands",
            description="Available bot commands:",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="🛡️ Moderation",
            value=(
                "`/warn` • `/kick` • `/ban`\n"
                "`/unban` • `/timeout` • `/untimeout`\n"
                "`/clear` • `/slowmode`\n"
                "`/lock` • `/unlock`"
            ),
            inline=False,
        )

        embed.add_field(
            name="🔧 Utility",
            value=(
                "`/ping` • `/serverinfo`\n"
                "`/userinfo` • `/avatar`\n"
                "`/botinfo` • `/help`"
            ),
            inline=False,
        )

        embed.add_field(
            name="🔗 AutoMod",
            value=(
                "Links are automatically removed.\n"
                "Warnings are sent through DM.\n"
                "4th violation results in a ban."
            ),
            inline=False,
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Utility(bot))