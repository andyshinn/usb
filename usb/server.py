import fsspec
from aiohttp import web
from invoke import task

from usb.logging import logger
from usb.search import Meilisearch
from usb.tasks import extract_thumbnail_by_document

app = web.Application()
routes = web.RouteTableDef()
search = Meilisearch()

routes.static("/thumbnails", "/thumbnails", show_index=True)


@routes.get("/search/{show}/{query}")
async def image_search(request):
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
        celery_task = extract_thumbnail_by_document.delay(result.to_dict())
        of.path = celery_task.get(timeout=10)

    await logger.complete()

    raise web.HTTPFound(of.path)


@routes.get("/get/{file}")
async def image_id(request):
    file = request.match_info["file"]

    of = fsspec.open(f"/thumbnails/{file}")

    if of.fs.isfile(of.path):
        return web.FileResponse(of.path)
    else:
        engine = file.split("-")[0].lower()
        document_id = file.strip(".png").lower()
        logger.debug(engine, document_id)
        result = search.get_document(engine, document_id)

        await logger.complete()

        if result:
            celery_task = extract_thumbnail_by_document.delay(result.to_dict())
            celery_task.get(timeout=10)
            return web.FileResponse(of.path)
        else:
            raise web.HTTPNotFound(reason=f"Could not find any image ID: {document_id}")


@task
def run(c):
    app.add_routes(routes)
    web.run_app(app, port=5000)
