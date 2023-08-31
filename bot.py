import logging
import os

import discord
from discord import Message
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashCommandOptionType as SCType
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv

load_dotenv()

GUILD_ID = int(os.getenv("GUILD_ID") or -1)
assert GUILD_ID != -1
GUILDS = [
    GUILD_ID,
]


class EvenChanBot(commands.Bot):
    def startup(self):
        logging.info("Even Chan started up successfully")

    async def on_ready(self):
        logging.info(f"{self.user} is alive")
        self.startup()

    async def on_message(self, message: Message):
        if message.author == self.user:
            return
        # TODO


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
    pass  # TODO: source


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
