import os

from discord import File
from discord.ext import commands
from sentry_sdk import configure_scope, capture_exception

from usb.logging import logger
from usb.search import Appsearch
from usb.tasks import extract_thumbnail_id

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIXES = ["what's the deal ", "what’s the deal ", "whats the deal ", "what the deal "]
REACTIONS = ["whatsthedealwith", "seinfeld"]

search = Appsearch()


class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        capture_exception(event)

    @commands.Cog.listener()
    async def on_command_error(self, context, exception):
        with configure_scope() as scope:
            scope.user = {"username": str(context.author)}
            scope.set_extra("invoked_with", context.invoked_with)
            scope.set_extra("args", context.args)
            scope.set_extra("kwargs", context.kwargs)
            capture_exception(exception)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        logger.debug("reaction: {}", str(reaction))
        if any(
            x in str(reaction) for x in REACTIONS
        ):  # TODO: use discord.py native emoji classes for comparison
            logger.info("sending image from reaction: {}", str(reaction))
            await self.image(
                await self.bot.get_context(reaction.message),
                query=reaction.message.content,
            )

        await logger.complete()

    @commands.command(name="with")
    async def image(self, ctx, *, query):
        engine = "seinfeld"
        logger.info("{} called with command: {}", ctx.author, query)
        result = search.get(engine, query, rand=True)
        logger.debug(result)
        task = extract_thumbnail_id.delay(engine, result["id"]["raw"])
        logger.debug(task)

        file = task.get(timeout=10)

        with open(file, "rb") as f:
            picture = File(f)
            await ctx.send(file=picture)

        await logger.complete()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super(Bot, self).__init__(guild_subscriptions=False, **kwargs)

    async def on_ready(self):
        logger.info("{} has connected to Discord!", self.user)

    async def on_message(self, message):
        logger.debug("Message from {0.author}: {0.content}", message)
        await bot.process_commands(message)


bot = Bot(command_prefix=PREFIXES)
bot.add_cog(Quotes(bot))

if __name__ == "__main__":
    bot.run(TOKEN)
