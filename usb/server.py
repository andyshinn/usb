from aiohttp import web
import fsspec
from invoke import task

from usb.tasks import extract_thumbnail_by_raw_document, extract_thumbnail_by_document
from usb.search import Appsearch
from usb.logging import logger

app = web.Application()
routes = web.RouteTableDef()

routes.static("/thumbnails", "/thumbnails", show_index=True)


@routes.get("/search/{show}/{query}")
async def image_search(request):
    search = Appsearch()
    show = request.match_info["show"]
    query = request.match_info["query"]
    engine = show.lower()

    random = bool(request.query.get("random", False))
    result = search.get(engine, query, random)

    logger.debug("Result from query: {}", result)

    if not result:
        raise web.HTTPNotFound(reason=f"Could not find any image for query: {query}")

    of = fsspec.open(f"/thumbnails/{id}.png")

    if not of.fs.isfile(of.path):
        task = extract_thumbnail_by_raw_document.delay(result)
        of.path = task.get(timeout=10)

    logger.complete()

    raise web.HTTPFound(of.path)


@routes.get("/get/{file}")
async def image_id(request):
    file = request.match_info["file"]

    of = fsspec.open(f"/thumbnails/{file}")

    if of.fs.isfile(of.path):
        return web.FileResponse(of.path)
    else:
        search = Appsearch()
        engine = file.split("-")[0].lower()
        id = file.strip(".png").lower()
        logger.debug(engine, id)
        result = search.get_document(engine, id)

        if result:
            task = extract_thumbnail_by_document.delay(result)
            task.get(timeout=10)
            return web.FileResponse(of.path)
        else:
            raise web.HTTPNotFound(reason=f"Could not find any image ID: {id}")

    logger.complete()


@task
def run(c):
    app.add_routes(routes)
    web.run_app(app, port=5000)
