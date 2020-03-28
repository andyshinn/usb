from aiohttp import web
import fsspec

from usb.tasks import extract_thumbnail_id
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

    if result:
        id = result["id"]["raw"]
    else:
        raise web.HTTPNotFound(reason=f"Could not find any image for query: {query}")

    of = fsspec.open(f"/thumbnails/{id}.png")

    if not of.fs.isfile(of.path):
        task = extract_thumbnail_id.delay(engine, id)
        of.path = task.get(timeout=10)

    logger.complete()

    raise web.HTTPFound(of.path)


app.add_routes(routes)
web.run_app(app, port=5000)
