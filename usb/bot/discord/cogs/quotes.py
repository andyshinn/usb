from pathlib import Path
import os

from discord import File, Embed, DMChannel
from discord.ext import commands
from sentry_sdk import configure_scope, capture_exception

from usb.logging import logger
from usb.tasks import extract_thumbnail_by_raw_document, extract_thumbnail_by_document
from usb.utils import move_id
import usb


class Quotes(commands.Cog, name="Seinfeld Quotes"):
    reactions = ["whatsthedealwith", "seinfeld"]
    react_next = ["▶️", "➡️", "⏩", "⏭️"]
    react_previous = ["◀️", "⬅️", "⏪", "⏮️"]

    def __init__(self, bot, search):
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
        logger.trace("reaction: {}", reaction)
        ctx = await self.bot.get_context(reaction.message)

        if any(
            x in str(reaction) for x in Quotes.reactions
        ):  # TODO: use discord.py native emoji classes for comparison
            logger.info("sending image from reaction: {}", str(reaction))
            await self.image(
                ctx,
                query=reaction.message.content,
            )
        elif any(
            x in str(reaction) for x in Quotes.react_next
        ):
            # check self
            footer = reaction.message.embeds[0].footer.text
            logger.trace(f"footer: {footer}")
            await self.id(ctx, move_id(footer, 1))
        elif any(
            x in str(reaction) for x in Quotes.react_previous
        ):
            footer = reaction.message.embeds[0].footer.text
            logger.trace(f"footer: {footer}")
            await self.id(ctx, move_id(footer, -1))

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
            task = extract_thumbnail_by_raw_document.delay(result)
            task.get(timeout=10)
            id = result["id"]["raw"]

            await self.send_result(ctx, id)

        await logger.complete()

    @commands.command()
    async def id(self, ctx, id):
        """Returns a specific image ID

        The with command takes a subtitle index ID in the format of: <show>-<season>-<episode>-<subtitle_index>

        You would usuall pair this with the "search" command.

        Example:

        $ein id seinfeld-4-3-4-50
        """

        engine = id.split("-")[0]
        filename = f"{id}.png"
        path = Path(f"/thumbnails/{filename}")

        if not path.exists():
            logger.debug(f"Path {path} doesn't exist, attempting to create")
            document = self.search.get_document(engine, id)

            if document:
                logger.debug(f"Found document: {document}")
                task = extract_thumbnail_by_document.delay(document)
                task.get(timeout=10)
            else:
                logger.warn(f"Could not find document ID: {id}")

        await self.send_result(ctx, id)
        await logger.complete()

    async def send_result(self, ctx, id):
        filename = f"{id}.png"
        path = Path(f"/thumbnails/{filename}")

        with path.open("rb") as f:
            picture = File(f, filename=f"{filename}")
            embed = Embed()
            embed.set_image(url=f"attachment://{filename}")
            embed.set_footer(text=f"{id}")
            await ctx.send(file=picture, embed=embed)

    @commands.command(name="search")
    async def search_subtitles(self, ctx, *, query):
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
                await ctx.send(
                    "Sending the top {} results to {} in a private message.".format(
                        len(results["results"]), ctx.author
                    )
                )

            for result in results["results"]:
                id = result["id"]["raw"]
                task = extract_thumbnail_by_raw_document.delay(result)
                task.get(timeout=10)
                embed = Embed(description=result["content"]["raw"])
                embed.add_field(
                    name="Title", value=result["episode_title"]["raw"], inline=True
                )
                embed.add_field(
                    name="Episode",
                    value=", ".join(result["episode"]["raw"]),
                    inline=True,
                )
                embed.add_field(
                    name="Season", value=int(result["season"]["raw"]), inline=True
                )
                embed.set_image(url=f"{self.base_url}/get/{id}.png")
                embed.set_footer(text="{}id {}".format(ctx.prefix, id))
                await ctx.author.send(embed=embed)

        await logger.complete()

    @commands.command()
    async def version(self, ctx):
        """Returns the bot version.

        Example:

        $ein version
        """

        await ctx.send("Universal Seinfeld Bus: **{}**".format(usb.__version__))
