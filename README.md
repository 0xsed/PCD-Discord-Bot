# PaldoCryptoDAO Discord Bot

A custom Discord moderation and security bot built for **PaldoCryptoDAO (PCD)**.
The bot provides automated moderation, anti-abuse protection, warning management, and administrator utilities.

## Features

### 🛡️ AutoMod & Security

#### Anti-Spam

Detects users who send messages too quickly.

**Behavior:**

* Detects 5 messages within 5 seconds.
* Deletes the detected spam message.
* Automatically applies a 10-second timeout.
* Sends the user a DM explaining the action.

#### Anti-Raid

Detects sudden/unusual member joins that may indicate a raid.

**Behavior:**

* Monitors member joins.
* Detects 10 joins within 10 seconds.
* Sends an alert to an available text channel.
* Logs the detection in the bot console.

> Anti-Raid currently detects and alerts. It does not automatically ban members or lock the server.

#### Anti-Duplicate

Detects users repeatedly sending the exact same message.

**Behavior:**

* Detects the same message sent 3 times consecutively.
* Deletes the repeated message.
* Sends the user a DM warning.

#### Anti-Link

Prevents unauthorized links from being posted.

**Warning system:**

* **1st violation:** Message deleted + Warning 1/3 via DM.
* **2nd violation:** Message deleted + Warning 2/3 via DM.
* **3rd violation:** Message deleted + Warning 3/3 via DM.
* **4th violation:** Message deleted + Automatic ban + Public notification.

Warning counts are stored in SQLite so they persist even after the bot restarts.

Certain configured roles can be made immune to Anti-Link.

#### Anti-Mass Mention

Planned protection against users mentioning large numbers of members or roles in a short period.

#### Anti-Invite

Planned protection against unauthorized Discord server invites.

#### Anti-Caps

Planned protection against excessive use of uppercase messages.

#### Profanity Filter

Automatically detects prohibited language and removes messages containing configured profanity.

**Behavior:**

* Detects configured profanity.
* Deletes the offending message.
* Sends the user a DM explaining why the message was removed.

The profanity list can be expanded with additional languages and terms.

---

## ⚠️ Warning System

The bot uses **SQLite** to store user warning counts.

Warnings are associated with:

* Server/Guild ID
* User ID
* Warning count

This allows warning data to persist across bot restarts.

Database location:

```text
data/warnings.db
```

Currently, Anti-Link violations use the persistent warning system.

---

## 🔨 Automatic Punishments

The bot can automatically take moderation actions when specific rules are violated.

Current automatic actions include:

| Protection     | Action                      |
| -------------- | --------------------------- |
| Anti-Spam      | 10-second timeout           |
| Anti-Duplicate | Delete message + DM warning |
| Anti-Link 1st  | Delete + warning            |
| Anti-Link 2nd  | Delete + warning            |
| Anti-Link 3rd  | Delete + warning            |
| Anti-Link 4th  | Delete + ban                |

More configurable punishment levels can be added later.

---

# 👮 Administrator Commands

All moderation and utility commands are restricted to Discord members with the **Administrator** permission.

## Moderation Commands

### `/warn`

Warn a member.

**Purpose:**
Manually record a warning for a user.

---

### `/kick`

Kick a member from the server.

**Permission:**
Administrator

---

### `/ban`

Ban a member from the server.

**Permission:**
Administrator

---

### `/unban`

Remove a user's ban.

**Permission:**
Administrator

---

### `/timeout`

Temporarily timeout a member.

**Permission:**
Administrator

---

### `/untimeout`

Remove a member's timeout.

**Permission:**
Administrator

---

### `/clear`

Delete messages from a channel.

**Features:**

* Can delete between 1 and 100 messages.
* Useful for cleaning spam or unwanted content.

---

### `/slowmode`

Set the channel's slowmode delay.

**Range:**

```text
0 – 21600 seconds
```

---

### `/lock`

Lock the current channel.

Members will no longer be able to send messages while the channel is locked.

---

### `/unlock`

Unlock the current channel.

Restores the channel's ability to receive messages.

---

# 🔧 Utility Commands

### `/ping`

Checks whether the bot is online and responding.

Example:

```text
🏓 Pong!
```

---

### `/serverinfo`

Displays information about the current Discord server.

---

### `/userinfo`

Displays information about a selected Discord member.

---

### `/avatar`

Displays a user's Discord avatar.

---

### `/botinfo`

Displays information about the bot.

---

### `/help`

Displays the available bot commands and features.

---

# 📍 Channel-Based AutoMod

AutoMod can be configured to operate only in selected channels instead of monitoring every channel.

Configure the allowed AutoMod channels in:

```text
cogs/automod.py
```

Example:

```python
AUTOMOD_CHANNEL_IDS = {
    123456789012345678,
    987654321098765432,
}
```

Only messages inside the configured channels will be processed by the message-based AutoMod.

This allows the server to have different channels for:

* General discussion
* Trading
* Announcements
* Support
* Bot commands
* Moderation

without applying message AutoMod everywhere.

> Anti-Raid is different because it monitors member joins rather than messages, so it remains server-wide.

---

# 👑 Staff & Role Exceptions

The AutoMod system supports staff exceptions.

Currently, members with:

* Administrator
* Manage Messages

can bypass the message-based AutoMod.

Anti-Link also supports configurable immune roles.

Example:

```python
IMMUNE_ROLE_IDS = {
    1201483694507040768,
    1496721835277025351,
    1451247966533976194,
    1422198973598535680,
}
```

These roles are immune specifically to **Anti-Link**.

They are not automatically immune to:

* Anti-Spam
* Anti-Duplicate
* Anti-Raid
* Other AutoMod systems

---

# 📁 Project Structure

```text
DCBot/
│
├── cogs/
│   ├── automod.py
│   ├── profanity.py
│   ├── moderation.py
│   └── utility.py
│
├── data/
│   └── warnings.db
│
├── .env
├── .gitignore
├── bot.py
└── requirements.txt
```

## Cogs

### `automod.py`

Contains the automated security systems:

* Anti-Spam
* Anti-Raid
* Anti-Duplicate
* Anti-Link
* Warning database
* Automatic punishments

### `profanity.py`

Handles profanity detection and message removal.

### `moderation.py`

Contains administrator moderation commands:

* `/warn`
* `/kick`
* `/ban`
* `/unban`
* `/timeout`
* `/untimeout`
* `/clear`
* `/slowmode`
* `/lock`
* `/unlock`

### `utility.py`

Contains administrator utility commands:

* `/ping`
* `/serverinfo`
* `/userinfo`
* `/avatar`
* `/botinfo`
* `/help`

---

# ⚙️ Requirements

* Python 3.14+
* Discord Bot
* `discord.py`
* `python-dotenv`
* SQLite

Dependencies:

```text
discord.py==2.7.1
python-dotenv==1.2.3
```

---

# 🔐 Discord Permissions

The bot requires the appropriate Discord permissions for its moderation features.

Recommended permissions:

* View Channels
* Send Messages
* Manage Messages
* Ban Members
* Kick Members
* Moderate Members
* Manage Channels

## Gateway Intents

The following intents are required:

* Server Members Intent
* Message Content Intent

These must be enabled in the Discord Developer Portal.

---

# 🔑 Environment Variables

The bot token is stored inside `.env`.

Example:

```env
DISCORD_TOKEN=YOUR_BOT_TOKEN
```

Never commit the `.env` file to GitHub.

The repository should contain:

```text
.env
```

inside `.gitignore`.

---

# 🚀 Running the Bot

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the bot:

```bash
python bot.py
```

When successfully connected, the console should display:

```text
Slash commands synced!
Logged in as PaldoCryptoDAO#5888
Bot ID: 1554878356942487593
Bot is online!
```

---

# 🗄️ Database

The bot uses SQLite for persistent warning storage.

Database:

```text
data/warnings.db
```

The database stores warning counts using:

```text
guild_id
user_id
warning_count
```

The database file should not be uploaded to GitHub.

---

# 🔒 Security

Important security practices:

* Never expose the Discord bot token.
* Never commit `.env`.
* Keep `warnings.db` out of Git.
* Only give the bot the permissions it actually needs.
* Review administrator permissions regularly.
* Keep dependencies updated.
* Do not share bot credentials publicly.

If the bot token is accidentally exposed, immediately reset it through the Discord Developer Portal.

---

# 📌 Current Feature Status

| Feature               | Status      |
| --------------------- | ----------- |
| Anti-Spam             | ✅ Active    |
| Anti-Raid             | ✅ Active    |
| Anti-Duplicate        | ✅ Active    |
| Anti-Link             | ✅ Active    |
| Profanity Filter      | ✅ Active    |
| Warning System        | ✅ Active    |
| Automatic Punishment  | ✅ Active    |
| Channel-Based AutoMod | ✅ Supported |
| Admin Commands        | ✅ Active    |
| Anti-Mass Mention     | 🚧 Planned  |
| Anti-Invite           | 🚧 Planned  |
| Anti-Caps             | 🚧 Planned  |

---

# 🎯 Purpose

PaldoCryptoDAO Bot is designed to help maintain a safer, cleaner, and better-managed Discord community by automating repetitive moderation tasks while giving administrators direct control through slash commands.

Built for **PaldoCryptoDAO (PCD)**.
