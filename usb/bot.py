import os

from discord import File
from discord.ext import commands
from sentry_sdk import configure_scope, capture_exception
from invoke import task

from usb.logging import logger
from usb.search import Appsearch
from usb.tasks import extract_thumbnail_id

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIXES = ["what's the deal ", "what’s the deal ", "whats the deal ", "what the deal "]
REACTIONS = ["whatsthedealwith", "seinfeld"]

search = Appsearch()


class Quotes(commands.Cog, name="Seinfeld Quotes"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        logger.exception("Bot error: {}", event)
        capture_exception(event)
        await logger.complete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(
            exception,
            (commands.errors.BadArgument, commands.errors.MissingRequiredArgument),
        ):
            await ctx.channel.send(
                f"\N{CROSS MARK} Bad argument: {' '.join(exception.args)}",
                delete_after=10,
            )

        with configure_scope() as scope:
            scope.user = {"username": str(ctx.author)}
            scope.set_extra("invoked_with", ctx.invoked_with)
            scope.set_extra("args", ctx.args)
            scope.set_extra("kwargs", ctx.kwargs)
            capture_exception(exception)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        logger.trace("reaction: {}", str(reaction))
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
        """Returns a show image of the searched quote

        The with command takes show subtitle or quote to search and returns an image from that show
        moment. You can enclose the search in quotes to lookup specific phrases.

        For example:

          what's the deal with "little Jerry"
          what's the deal with i carry a purse
        """
        engine = "seinfeld"
        logger.info(
            "Guild {} user {} channel {} querying: {}".format(
                str(ctx.guild), str(ctx.author), str(ctx.channel), query
            )
        )
        logger.debug("context: {}", ctx.__dict__)
        logger.debug("query: {}", query)
        result = search.get(engine, query, rand=True)
        logger.debug("search result: {}", result)

        if result:
            task = extract_thumbnail_id.delay(engine, result)
            file = task.get(timeout=10)

            with open(file, "rb") as f:
                picture = File(f)
                await ctx.send(file=picture)

        await logger.complete()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super(Bot, self).__init__(**kwargs)

    async def on_ready(self):
        logger.info("{} has connected to Discord!", self.user)


bot = Bot(command_prefix=PREFIXES, description="A Seinfeld related Discord bot.")
bot.add_cog(Quotes(bot))

if __name__ == "__main__":
    bot.run(TOKEN)


@task
def run(c):
    bot.run(TOKEN)
