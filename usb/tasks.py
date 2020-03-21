from celery import Celery, group
from loguru import logger
from requests.exceptions import HTTPError
from elastic_app_search.exceptions import BadRequest

from usb.utils import formatted_episodes, msecs
from usb.subtitle import Subtitles
from usb.video import VideoFile
from usb.search import Appsearch

app = Celery(
    "tasks",
    broker="pyamqp://celery:wh4tsth3d34l@broker/celery",
    backend="redis://result",
)


@app.task(bind=True)
def process_subtitle(self, path):
    video = VideoFile(path)
    subtitles = Subtitles(video)

    if video.ignored:
        logger.warning("video {} ignored, skipping processing")
        return "video ignored, skipping processing"
    else:
        try:
            subtitles.index()
        except (HTTPError, BadRequest) as e:
            self.retry(countdown=10, exc=e)


@app.task
def finish_indexing(count):
    logger.info("finished indexing {} episodes".format(count))


@app.task
def process_video(file):
    video = VideoFile(file)
    subs = video.extract_subs()
    extract_task = group(
        extract_thumbnail.s(
            file,
            msecs(sub.start, sub.end),
            "/thumbnails/{}-{}-{}-{}.png".format(
                video.show.lower(),
                video.season,
                formatted_episodes(video.episode),
                sub.index,
            ),
            sub.content,
        )
        for sub in subs
    )
    extract_task.apply_async()


@app.task
def extract_thumbnail(file, milliseconds, dest, text):
    video = VideoFile(file)
    video.thumbnail(milliseconds, dest, text)


@app.task
def extract_thumbnail_id(engine, id):
    search = Appsearch()
    document = search.get_document(engine, id)

    dest = "/thumbnails/{}.png".format(id)

    video = VideoFile(document["path"])
    video.thumbnail(float(document["seconds_middle"]), dest, document["content"])

    return dest
