import os

from discord import File
from discord.ext import commands
from loguru import logger

from usb.search import Appsearch
from usb.tasks import extract_thumbnail_id


TOKEN = os.getenv("DISCORD_TOKEN")
PREFIXES = ["!deal ", "what's the deal ", "whats the deal ", "what the deal "]


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super(Bot, self).__init__(guild_subscriptions=False, **kwargs)

    async def on_ready(self):
        logger.info("{} has connected to Discord!", self.user)

    async def on_message(self, message):
        logger.info("Message from {0.author}: {0.content}", message)
        await bot.process_commands(message)


bot = Bot(command_prefix=PREFIXES)
search = Appsearch()


@bot.command(name="with")
async def image(ctx, *, query):
    engine = "seinfeld"
    logger.info("{} called with command: {}", ctx.author, query)
    result = search.get(engine, query, rand=False)
    logger.debug(result)
    task = extract_thumbnail_id.delay(engine, result["id"]["raw"])
    logger.debug(task)

    file = task.get(timeout=10)

    with open(file, "rb") as f:
        picture = File(f)
        await ctx.send(file=picture)

    await logger.complete()


if __name__ == "__main__":
    bot.run(TOKEN)
