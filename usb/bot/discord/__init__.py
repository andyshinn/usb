import os

# noinspection PyPackageRequirements
from discord import Intents
# noinspection PyPackageRequirements
from discord.ext import commands
from invoke import task

from usb.logging import logger
from usb.search import Meilisearch
from usb.bot.discord.cogs.quotes import Quotes
from usb.bot.discord.cogs.topgg import TopGG
from usb.bot.discord.cogs.health import Health

TOKEN = os.getenv("DISCORD_TOKEN")
PING_URL = os.getenv("PING_URL", None)
PREFIXES = [
    "$ein ",
    "$sein ",
    "what's the deal ",
    "what’s the deal ",
    "whats the deal ",
    "What's the deal ",
    "What’s the deal ",
    "Whats the deal ",
    "what the deal ",
]


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super(Bot, self).__init__(**kwargs)

    async def on_ready(self):
        logger.info("{} has connected to Discord!", self.user)


intents = Intents(messages=True, reactions=True, guilds=True)
search = Meilisearch()
bot = Bot(
    command_prefix=PREFIXES, case_insensitive=True, intents=intents, description="A Seinfeld related Discord bot."
)
bot.add_cog(Quotes(bot, search))
bot.add_cog(TopGG(bot))
if PING_URL:
    bot.add_cog(Health(bot, PING_URL))


@task
def run(c):
    bot.run(TOKEN)


if __name__ == "__main__":
    bot.run(TOKEN)
