import logging
import re
from typing import Any, Union

import discord
from discord import Embed, Message
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashCommandOptionType as SCType
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv
from von import api

load_dotenv()

MAX_EMBED_LENGTH = 1000

SOURCE_REGEX = re.compile(
    r"(USAMO|JMO|IMO|Shortlist|ELMO|USA TST|TSTST|RMM|EGMO|USEMO) [0-9]{4}[ \/][ACGN]?[0-9]+"
)

# https://stackoverflow.com/questions/61150145/remove-line-breaks-but-not-double-line-breaks-python
SINGLE_NEWLINE_DELETER = re.compile(r"(?<=[A-Za-z.:,\$ ]{2})\n(?!\n)")


async def post_problem(source: str, trigger: Union[SlashContext, Message]):
    if isinstance(trigger, SlashContext):
        target = trigger
    else:
        target = trigger.channel

    entry = api.get(source)
    statement = entry.bodies[0]
    statement = SINGLE_NEWLINE_DELETER.sub(" ", statement)
    if len(statement) > MAX_EMBED_LENGTH:
        statement = statement[:MAX_EMBED_LENGTH]
        if " " in statement[:MAX_EMBED_LENGTH]:
            i = statement.rindex(" ")
            statement = statement[:i] + "..."
        else:
            statement += "..."

    kwargs: dict[str, Any] = {
        "title": source,
        "description": "```latex" + "\n" + statement + "\n" + "```",
    }
    if entry.url is not None:
        shortlink = entry.url
        if shortlink.startswith("http://"):
            shortlink = shortlink[7:]
        if shortlink.startswith("https://"):
            shortlink = shortlink[8:]
        if shortlink.startswith("www."):
            shortlink = shortlink[4:]
        if len(shortlink) > 32:
            shortlink = shortlink[:29] + "..."
        kwargs["url"] = entry.url
    else:
        shortlink = None

    embed = Embed(**kwargs)

    if shortlink is not None:
        embed.add_field(
            name="Link",
            value=f"[{shortlink}]({entry.url})",
            inline=True,
        )
    if entry.author is not None:
        embed.add_field(name="Author", value=entry.author, inline=True)

    await target.send(embed=embed)  # type: ignore


class EvenChanBot(commands.Bot):
    def startup(self):
        logging.info("Even Chan started up successfully")

    async def on_ready(self):
        logging.info(f"{self.user} is alive")
        self.startup()

    async def on_message(self, message: Message):
        if message.author == self.user:
            return
        haystack = message.content.strip()
        if (m := SOURCE_REGEX.search(haystack)) is not None:
            source = m.group(0)
            if api.has(source):
                await post_problem(source, message)


bot = EvenChanBot(command_prefix="&", intents=discord.Intents.default())
slash = SlashCommand(bot, sync_commands=True)


@slash.slash(
    name="yank",
    description="Look up a certain source",
    options=[
        create_option(
            name="source",
            description="The source to look up",
            option_type=SCType.STRING,
            required=True,
        )
    ],
)
async def slash_yank(ctx: SlashContext, source: str):
    if not SOURCE_REGEX.fullmatch(source):
        await ctx.send(f"{source} is not in a supported contest", hidden=True)
    elif not api.has(source):
        await ctx.send(f"Could not find {source} in Evan's von database", hidden=True)
    else:
        await post_problem(source, ctx)


@slash.slash(
    name="refresh",
    description="Admin command to refresh Evil Chin database",
    options=[],
)
async def slash_refresh(ctx: SlashContext):
    if context_by_admin(ctx):
        await ctx.send(":ok:", hidden=True)
        bot.startup()
    else:
        await ctx.send(":x:", hidden=True)


@slash.slash(
    name="puppet",
    description="Puppet a message as Even Chan",
    options=[
        create_option(
            name="text",
            description="The text you would like to send",
            option_type=SCType.STRING,
            required=True,
        ),
    ],
)
async def slash_puppet(ctx: SlashContext, text: str):
    if context_by_admin(ctx):
        if ctx.channel is None:
            await ctx.send(text)
        else:
            await ctx.send(":socks:", hidden=True)
            await ctx.channel.send(text)
    else:
        await ctx.send("Not authorized", hidden=True)


def context_by_admin(ctx: SlashContext) -> bool:
    author = ctx.author
    if isinstance(author, discord.Member):
        return author.guild_permissions.administrator
    return False
