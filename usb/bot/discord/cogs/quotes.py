import re
from pathlib import Path
import os

# noinspection PyPackageRequirements
from discord import File, Embed, DMChannel
# noinspection PyPackageRequirements
from discord.ext import commands
from sentry_sdk import configure_scope, capture_exception

from usb.logging import logger
from usb.search import Meilisearch
from usb.tasks import extract_thumbnail_by_document
from usb.utils import move_id
import usb


class Quotes(commands.Cog, name="Seinfeld Quotes"):
    reactions = ["whatsthedealwith", "seinfeld"]
    react_next = ["▶️", "➡️", "⏩", "⏭️"]
    react_previous = ["◀️", "⬅️", "⏪", "⏮️"]

    def __init__(self, bot, search: Meilisearch):
        self.bot = bot
        self.search = search
        self.base_url = os.getenv("BASE_URL", "https://seinfeld.ngrok.io")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("{} cog {} is ready", str(self.bot.user), str(self.qualified_name))
        await logger.complete()

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        logger.exception("Bot error: {}", event)
        capture_exception(event)
        await logger.complete()

    @commands.Cog.listener()
    async def on_command(self, ctx):
        logger.info(
            'Triggered command "{}" via guild "{}" user "{}" channel "{}"'.format(
                str(ctx.command), str(ctx.guild), str(ctx.author), str(ctx.channel)
            )
        )
        await logger.complete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        args = " ".join(exception.args)

        if isinstance(
            exception,
            (commands.errors.BadArgument, commands.errors.MissingRequiredArgument),
        ):
            await ctx.channel.send(
                f"\N{CROSS MARK} Bad argument: {args}",
                delete_after=10,
            )
            logger.info(f"Bad arguments: {args}")
            await logger.complete()

        elif isinstance(
            exception,
            commands.errors.CommandNotFound,
        ):
            await ctx.channel.send(
                f"\N{CROSS MARK} Command not found: {ctx.invoked_with}",
                delete_after=10,
            )
            logger.info(f"Command not found: {ctx.invoked_with}")
            await logger.complete()
        else:
            with configure_scope() as scope:
                scope.set_extra("username", str(ctx.author))
                scope.set_extra("invoked_with", ctx.invoked_with)
                scope.set_extra("args", ctx.args)
                scope.set_extra("kwargs", ctx.kwargs)
                capture_exception(exception)
                raise exception

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        logger.trace("reaction: {}", reaction)
        ctx = await self.bot.get_context(reaction.message)
        regex = r"\w+(?:\-\d+){3,4}$"

        if any(
            x in str(reaction) for x in Quotes.reactions
        ):  # TODO: use discord.py native emoji classes for comparison
            logger.info("sending image from reaction: {}", str(reaction))
            await self.image(
                ctx,
                query=reaction.message.content,
            )
        elif any(x in str(reaction) for x in Quotes.react_next):
            # check self
            footer = reaction.message.embeds[0].footer.text
            match = re.search(regex, footer)
            logger.trace(f"footer: {footer}")
            await self.id(ctx, move_id(match.group(), 1))
        elif any(x in str(reaction) for x in Quotes.react_previous):
            footer = reaction.message.embeds[0].footer.text
            match = re.search(regex, footer)
            logger.trace(f"footer: {footer}")
            await self.id(ctx, move_id(match.group(), -1))

        await logger.complete()

    @commands.command(aliases=["with"])
    async def image(self, ctx, *, query):
        """Returns a show image of the searched quote

        The with command takes show subtitle or quote to search and returns an image from that show
        moment. You can enclose the search in quotes to lookup specific phrases.

        The command also has an alias named "with" that is designed to be used with the "what's the deal with" prefix.

        Examples:

        what's the deal with "little Jerry"
        $ein image i carry a purse
        """
        engine = "seinfeld"

        logger.debug("context: {}", ctx.__dict__)
        logger.debug("query: {}", query)
        result = self.search.get(engine, query, rand=True)
        logger.debug("search result: {}", result)

        if result:
            await Quotes.send_result(ctx, result)

        await logger.complete()

    @commands.command()
    async def id(self, ctx, document_id):
        """Returns a specific image ID

        The with command takes a subtitle index ID in the format of: <show>-<season>-<episode>-<subtitle_index>

        You would usuall pair this with the "search" command.

        Example:

        $ein id seinfeld-4-3-4-50
        """

        engine = document_id.split("-")[0]
        document = self.search.get_document(engine, document_id)

        if document:
            await Quotes.send_result(ctx, document)
        else:
            logger.warning(f"Could not find document ID: {document_id}")

        await logger.complete()

    @staticmethod
    async def send_result(ctx, document):
        filename = f"{document.id}.png"
        path = Path(f"/thumbnails/{filename}")

        if not path.exists():
            logger.debug(f"Path {path} doesn't exist, attempting to create")
            logger.debug(f"Found document: {document}")
            task = extract_thumbnail_by_document.delay(document.to_dict())
            task.get(timeout=10)

        prefix = ctx.prefix if ctx.prefix else "$ein "

        with path.open("rb") as f:
            picture = File(f, filename=f"{filename}")
            embed = Embed(title=document.human_season_episode)
            embed.set_image(url=f"attachment://{filename}")
            embed.set_footer(text="{}id {}".format(prefix, document.id))
            await ctx.send(file=picture, embed=embed)

    @commands.command(name="search")
    async def search_subtitles(self, ctx: commands.Context, *, query):
        """Searches through subtitles and returns results

        The with command takes a query as the argument and sends results in a DM.
        Each search result has a command that can be used in a channel to directly reference an ID.

        Example:

        $ein search "my little jerry"
        """

        engine = "seinfeld"
        results = self.search.search(engine, query)

        if results:
            if not isinstance(ctx.channel, DMChannel):
                await ctx.send(f"Sending the top {len(results)} results to {ctx.author.name} in a private message.")
            for result in results:
                await Quotes.send_result(ctx, result)

    @commands.command()
    async def version(self, ctx):
        """Returns the bot version.

        Example:

        $ein version
        """

        await ctx.send("Universal Seinfeld Bus: **{}**".format(usb.__version__))
