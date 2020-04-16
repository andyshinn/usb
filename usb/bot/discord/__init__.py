import os

from discord.ext import commands
from invoke import task

from usb.logging import logger
from usb.search import Appsearch
from usb.bot.discord.cogs.quotes import Quotes

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIXES = [
    "$ein ",
    "$sein ",
    "what's the deal ",
    "what’s the deal ",
    "whats the deal ",
    "what the deal ",
]


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super(Bot, self).__init__(**kwargs)

    async def on_ready(self):
        logger.info("{} has connected to Discord!", self.user)


search = Appsearch()
bot = Bot(command_prefix=PREFIXES, description="A Seinfeld related Discord bot.")
bot.add_cog(Quotes(bot, search))


@task
def run(c):
    bot.run(TOKEN)


if __name__ == "__main__":
    bot.run(TOKEN)
