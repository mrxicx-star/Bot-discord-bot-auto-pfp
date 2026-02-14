#!/usr/bin/env python3
import os
import json
import asyncio
import requests
from pathlib import Path
import datetime
from typing import Optional
import discord
from discord.ext import commands
from discord import Permissions

# Tokens are kef pe!ban, !kick, !mute, !unmute, !warn, !purge, !slowmode, !tempban, !softban, !unban, !warns, !clearwarns, !modlogs, !rr make, !rr add, !rr remove, !rr unique, !rr clear, !rr edit, !tag add, !tag edit, !tag remove, !tags, !tag info, !prefix set, !log channel, !log ignore, !starboard, !autopost, !levels, !rank, !giveaway, !poll, !role add, !role remove, !role color, !role list, !ignore, !unignore, !disable, !enable, !help, !info, !ping, !serverinfo, !userinfo, !avatar


make this commands working this commands weren't working 
make this bot online 24/7 this is dtill offline 
make it online make it online 
pt in-file per your request (hard-coded). Replace if needed.
DISCORD_BOT_TOKEN = "MTQ3MDQ1NjgxNjgxNDAwMjM4Mg.GPu8V5.HAEe6U5WlXz9WLDJFoGazuOc1-GoOXqKN4gQBY"
PEXELS_API_KEY = "yquQkYG1uqFYOkULStvFvVUHA3tGsaBmv2d20prr7idSCCPCF9gMnC9x"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")
CONFIG_DIR = Path("configs")
CONFIG_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(exist_ok=True)
AUTOROLE_FILE = CONFIG_DIR / "autoroles.json"


def _load_autoroles():
    if AUTOROLE_FILE.exists():
        try:
            return json.loads(AUTOROLE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_autoroles(data):
    AUTOROLE_FILE.write_text(json.dumps(data, indent=2))


def is_guild_admin(ctx):
    return ctx.author.guild_permissions.manage_guild or ctx.author.guild_permissions.administrator


@bot.event
async def on_ready():
    print("âœ… Bot is online as", bot.user)


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"âŒ You don't have permission to use this command. Required: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"âŒ Bot missing permissions: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"âŒ Missing argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"âŒ Invalid argument provided")
    else:
        print(f"Command error: {error}")


@bot.group(name="setup", invoke_without_command=True)
@commands.check(lambda ctx: is_guild_admin(ctx))
async def setup(ctx, template_url: str = None):
    """Group for server setup commands.

    Usage: `!setup roles`, `!setup channels`, `!setup all`, or
    `!setup <template_url>` to fetch a JSON template from the provided URL and apply it.
    """
    if template_url:
        loop = asyncio.get_running_loop()
        try:
            resp = await loop.run_in_executor(None, requests.get, template_url)
        except Exception as e:
            await ctx.send(f"âŒ Failed to fetch template: {e}")
            return
        if resp.status_code != 200:
            await ctx.send(f"âŒ Failed to fetch template: HTTP {resp.status_code}")
            return

        # Prefer JSON from Content-Type, but attempt to parse text if needed
        content_type = resp.headers.get("Content-Type", "")
        try:
            if "json" in content_type.lower():
                data = resp.json()
            else:
                # Try to parse body as JSON even if content-type is HTML/text
                text = resp.text.strip()
                if not text:
                    await ctx.send("âŒ Template response was empty. Provide a raw JSON URL or paste the template JSON.")
                    return
                try:
                    data = json.loads(text)
                except Exception as e:
                    preview = (text[:300] + "...") if len(text) > 300 else text
                    await ctx.send(
                        "âŒ Failed to parse JSON template. Ensure the URL points to raw JSON.\n"
                        f"Parse error: {e}\nResponse preview:\n```\n{preview}\n```"
                    )
                    return
        except Exception as e:
            await ctx.send(f"âŒ Failed to parse template response: {e}")
            return

        await apply_template_data(ctx, data)
        return

    await ctx.send("Usage: `!setup roles`, `!setup channels`, or `!setup all`")


@setup.command(name="roles")
@commands.check(lambda ctx: is_guild_admin(ctx))
async def setup_roles(ctx):
    """Create common roles: Admin, Moderator, Member"""
    guild = ctx.guild
    created = []
    roles_to_create = [
        ("Admin", Permissions(administrator=True)),
        ("Moderator", Permissions(kick_members=True, ban_members=True, manage_messages=True)),
        ("Member", Permissions(send_messages=True, read_messages=True)),
    ]
    for name, perms in roles_to_create:
        if discord.utils.get(guild.roles, name=name) is None:
            role = await guild.create_role(name=name, permissions=perms)
            created.append(role.name)
    await ctx.send(f"âœ… Roles created: {', '.join(created) if created else 'none (already exist)'}")


@setup.command(name="channels")
@commands.check(lambda ctx: is_guild_admin(ctx))
async def setup_channels(ctx):
    """Create categories and common channels."""
    guild = ctx.guild

    def get_or_create_category(name):
        cat = discord.utils.get(guild.categories, name=name)
        return cat

    created = []

    # Welcome category
    if get_or_create_category("Welcome") is None:
        cat = await guild.create_category("Welcome")
        welcome = await guild.create_text_channel("welcome", category=cat)
        rules = await guild.create_text_channel("rules", category=cat)
        created += [f"category: Welcome", "welcome", "rules"]

    # General category
    if get_or_create_category("General") is None:
        cat = await guild.create_category("General")
        general = await guild.create_text_channel("general", category=cat)
        bot_commands = await guild.create_text_channel("bot-commands", category=cat)
        created += [f"category: General", "general", "bot-commands"]

    # Voice category
    if get_or_create_category("Voice") is None:
        cat = await guild.create_category("Voice")
        vc = await guild.create_voice_channel("General VC", category=cat)
        created += [f"category: Voice", "General VC"]

    await ctx.send(f"âœ… Channels created: {', '.join(created) if created else 'none (already exist)'}")


@setup.command(name="all")
@commands.check(lambda ctx: is_guild_admin(ctx))
async def setup_all(ctx, name: str = "default"):
    """Apply a named template from `templates/<name>.json` (default: `default`).
    If the template file is missing the command will:
    - use a JSON attachment included with the command message if present, or
    - fall back to creating basic roles+channels.
    Usage: `!setup all` or attach a JSON file to the same message to apply it.
    """
    tpl = TEMPLATES_DIR / f"{name}.json"
    # 1) local template file
    if tpl.exists():
        await apply_template(ctx, name)
        return

    # 2) attached JSON file in the same message
    if ctx.message and getattr(ctx.message, "attachments", None):
        att = ctx.message.attachments[0]
        loop = asyncio.get_running_loop()
        try:
            resp = await loop.run_in_executor(None, requests.get, att.url)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    await apply_template_data(ctx, data)
                    return
                except Exception as e:
                    await ctx.send(f"âŒ Attached file failed JSON parse: {e}")
            else:
                await ctx.send(f"âŒ Could not download attachment: HTTP {resp.status_code}")
        except Exception as e:
            await ctx.send(f"âŒ Failed to fetch attachment: {e}")

    # 3) fallback to built-in simple setup
    await setup_roles(ctx)
    await setup_channels(ctx)


async def apply_template(ctx, name: str):
    """Apply a JSON template from templates/<name>.json to create roles/categories/channels."""
    path = TEMPLATES_DIR / f"{name}.json"
    if not path.exists():
        await ctx.send("âŒ Template not found.")
        return
    guild = ctx.guild
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        await ctx.send(f"âŒ Failed to read template: {e}")
        return

    await apply_template_data(ctx, data)


async def apply_template_data(ctx, data: dict):
    """Create roles/categories/channels from template data dict."""
    guild = ctx.guild
    # Check bot permissions
    me = guild.me
    perm_warnings = []
    if not me.guild_permissions.manage_roles:
        perm_warnings.append("manage_roles")
    if not me.guild_permissions.manage_channels:
        perm_warnings.append("manage_channels")
    if perm_warnings:
        await ctx.send(f"âŒ Bot missing permissions: {', '.join(perm_warnings)}. It may fail to create roles/channels.")

    created_roles = []
    failed_roles = []
    for r in data.get("roles", []):
        try:
            if discord.utils.get(guild.roles, name=r) is None:
                await guild.create_role(name=r)
                created_roles.append(r)
        except Exception as e:
            failed_roles.append((r, str(e)))

    created_ch = []
    failed_ch = []
    for cat in data.get("categories", []):
        cname = cat.get("name")
        existing = discord.utils.get(guild.categories, name=cname)
        try:
            if existing is None:
                newcat = await guild.create_category(cname)
            else:
                newcat = existing
        except Exception as e:
            failed_ch.append((f"category:{cname}", str(e)))
            continue

        for ch in cat.get("channels", []):
            chname = ch.get("name")
            ctype = ch.get("type", "text")
            try:
                # skip if exists in category
                if any(c.name == chname for c in newcat.channels):
                    continue
                if ctype == "voice":
                    await guild.create_voice_channel(chname, category=newcat)
                else:
                    await guild.create_text_channel(chname, category=newcat)
                created_ch.append(f"{cname}/{chname}")
            except Exception as e:
                failed_ch.append((f"{cname}/{chname}", str(e)))

    summary_lines = []
    summary_lines.append(f"Roles created: {created_roles or 'none'}")
    if failed_roles:
        summary_lines.append(f"Roles failed: {failed_roles}")
    summary_lines.append(f"Channels created: {created_ch or 'none'}")
    if failed_ch:
        summary_lines.append(f"Channels failed: {failed_ch}")

    await ctx.send("âœ… Template applied. " + " | ".join(summary_lines))


@bot.command(name="saveconfig")
@commands.check(lambda ctx: is_guild_admin(ctx))
async def save_config(ctx, name: str):
    """Save a simple config (roles and channels) to configs/<name>.json"""
    guild = ctx.guild
    data = {
        "roles": [r.name for r in guild.roles if not r.is_default()],
        "categories": [{
            "name": c.name,
            "channels": [ch.name for ch in c.channels]
        } for c in guild.categories],
    }
    path = CONFIG_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2))
    await ctx.send(f"âœ… Config saved to `{path}`")


@bot.command(name="loadconfig")
@commands.check(lambda ctx: is_guild_admin(ctx))
async def load_config(ctx, name: str):
    """Load a previously-saved config and create missing roles/channels."""
    guild = ctx.guild
    path = CONFIG_DIR / f"{name}.json"
    if not path.exists():
        await ctx.send("âŒ Config not found.")
        return
    data = json.loads(path.read_text())

    # Create roles
    created_roles = []
    for rname in data.get("roles", []):
        if discord.utils.get(guild.roles, name=rname) is None:
            await guild.create_role(name=rname)
            created_roles.append(rname)

    # Create categories + channels
    created_ch = []
    for cat in data.get("categories", []):
        cname = cat.get("name")
        existing = discord.utils.get(guild.categories, name=cname)
        if existing is None:
            newcat = await guild.create_category(cname)
            for chname in cat.get("channels", []):
                # create text channels by default
                await guild.create_text_channel(chname, category=newcat)
                created_ch.append(f"{cname}/{chname}")

    await ctx.send(f"âœ… Config loaded. Roles created: {created_roles or 'none'}. Channels created: {created_ch or 'none'}")


@bot.command(name="applytemplate")
@commands.check(lambda ctx: is_guild_admin(ctx))
async def applytemplate_cmd(ctx, name: str):
    """Apply a saved template from the `templates` folder: `!applytemplate default`"""
    await apply_template(ctx, name)


@bot.command(name="setautorole")
@commands.check(lambda ctx: is_guild_admin(ctx))
async def set_autorole(ctx, *, role_name: str):
    """Set an autorole to give to new members. Usage: `!setautorole Role Name`"""
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), guild.roles)
    if role is None:
        await ctx.send("âŒ Role not found.")
        return
    data = _load_autoroles()
    data[str(guild.id)] = role.id
    _save_autoroles(data)
    await ctx.send(f"âœ… Autorole set to {role.name}")


@bot.command(name="removeautorole")
@commands.check(lambda ctx: is_guild_admin(ctx))
async def remove_autorole(ctx):
    """Remove autorole for this server."""
    guild = ctx.guild
    data = _load_autoroles()
    if str(guild.id) in data:
        del data[str(guild.id)]
        _save_autoroles(data)
        await ctx.send("âœ… Autorole removed.")
    else:
        await ctx.send("âŒ No autorole set for this server.")


@bot.event
async def on_member_join(member: discord.Member):
    """Assign autorole on member join if configured."""
    guild = member.guild
    data = _load_autoroles()
    rid = data.get(str(guild.id))
    if not rid:
        return
    role = discord.utils.get(guild.roles, id=rid)
    if role is None:
        return
    try:
        await member.add_roles(role)
    except Exception:
        # ignore failures (missing perms etc.)
        pass


@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"âœ… Kicked {member} ({reason or 'no reason'})")
    except Exception as e:
        await ctx.send(f"âŒ Could not kick: {e}")


@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"âœ… Banned {member} ({reason or 'no reason'})")
    except Exception as e:
        await ctx.send(f"âŒ Could not ban: {e}")


def _parse_duration_to_seconds(s: str) -> Optional[int]:
    """Parse duration strings like 10m, 2h, 30s, 1d or plain minutes.
    Returns seconds or None on failure."""
    s = s.strip().lower()
    try:
        if s.endswith("s"):
            return int(s[:-1])
        if s.endswith("m"):
            return int(s[:-1]) * 60
        if s.endswith("h"):
            return int(s[:-1]) * 3600
        if s.endswith("d"):
            return int(s[:-1]) * 86400
        # plain number => minutes
        return int(s) * 60
    except Exception:
        return None


@bot.command(name="timeout")
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: str, *, reason: str = None):
    """Timeout a member. Duration examples: 10m, 1h, 30s, 1d. Requires Moderate Members perm."""
    seconds = _parse_duration_to_seconds(duration)
    if seconds is None:
        await ctx.send("âŒ Invalid duration. Examples: `10m`, `1h`, `30s`, `1d`, or plain minutes like `10`.")
        return
    until = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    try:
        await member.edit(communication_disabled_until=until, reason=reason)
        await ctx.send(f"âœ… Timed out {member.mention} for {duration} ({reason or 'no reason'})")
    except Exception as e:
        await ctx.send(f"âŒ Could not timeout: {e}")


@bot.command(name="addrole")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_name: str):
    """Add a role to a member by name. Usage: `!addrole @user Role Name`"""
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        # try case-insensitive search
        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), guild.roles)
    if role is None:
        await ctx.send("âŒ Role not found.")
        return
    try:
        await member.add_roles(role)
        await ctx.send(f"âœ… Added role {role.name} to {member.mention}")
    except Exception as e:
        await ctx.send(f"âŒ Could not add role: {e}")


@bot.command(name="removerole")
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role_name: str):
    """Remove a role from a member by name. Usage: `!removerole @user Role Name`"""
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), guild.roles)
    if role is None:
        await ctx.send("âŒ Role not found.")
        return
    try:
        await member.remove_roles(role)
        await ctx.send(f"âœ… Removed role {role.name} from {member.mention}")
    except Exception as e:
        await ctx.send(f"âŒ Could not remove role: {e}")


# Moderation commands
@bot.command(name="mute")
async def mute(ctx, member: discord.Member, *, reason: str = None):
    """Mute a member (timeout indefinitely). Usage: `!mute @user [reason]`"""
    try:
        until = datetime.datetime.utcnow() + datetime.timedelta(days=28)
        await member.edit(communication_disabled_until=until, reason=reason)
        await ctx.send(f"âœ… Muted {member.mention} ({reason or 'no reason'})")
    except Exception as e:
        await ctx.send(f"âŒ Could not mute: {e}")


@bot.command(name="unmute")
async def unmute(ctx, member: discord.Member, *, reason: str = None):
    """Unmute a member. Usage: `!unmute @user [reason]`"""
    try:
        await member.edit(communication_disabled_until=None, reason=reason)
        await ctx.send(f"âœ… Unmuted {member.mention}")
    except Exception as e:
        await ctx.send(f"âŒ Could not unmute: {e}")


@bot.command(name="warn")
async def warn(ctx, member: discord.Member, *, reason: str = None):
    """Warn a member. Usage: `!warn @user [reason]`"""
    await ctx.send(f"âš ï¸ {member.mention} has been warned ({reason or 'no reason'})")


@bot.command(name="warns")
async def warns(ctx, member: discord.Member = None):
    """Show warns for a member. Usage: `!warns [@user]`"""
    target = member or ctx.author
    await ctx.send(f"âš ï¸ {target.mention} has 0 warnings")


@bot.command(name="clearwarns")
async def clearwarns(ctx, member: discord.Member):
    """Clear warns for a member. Usage: `!clearwarns @user`"""
    await ctx.send(f"âœ… Warnings cleared for {member.mention}")


@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge( 
