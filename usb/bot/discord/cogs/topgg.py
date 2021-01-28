import os

from dbl import DBLClient
# noinspection PyPackageRequirements
from discord.ext import commands

from usb.logging import logger


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = os.getenv("DBL_TOKEN", "unset")
        self.dblpy = DBLClient(self.bot, self.token, autopost=True)  # Autopost will post your guild count every 30
        # minutes

    @commands.Cog.listener()
    async def on_guild_post(self):
        logger.info("Server count posted successfully")
