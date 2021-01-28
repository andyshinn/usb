import os
from pathlib import Path

from celery import Celery, group, Task
from requests.exceptions import HTTPError
from elastic_app_search.exceptions import BadRequest
from invoke import task

from usb.document import Document
from usb.logging import logger
from usb.utils import formatted_episodes, msecs
from usb.subtitle import Subtitles
from usb.video import VideoFile

app = Celery(
    "tasks",
    broker="pyamqp://celery:wh4tsth3d34l@{}/celery".format(os.getenv("SERVICE_NAME_BROKER", "broker")),
    backend="redis://{}".format(os.getenv("SERVICE_NAME_RESULT", "result")),
)


@app.task(bind=True, ignore_result=True)
def process_subtitle(self: Task, index_name, path):
    video = VideoFile(path)
    subtitles = Subtitles(video)

    if video.ignored:
        logger.warning("video {} ignored, skipping processing")
        return "video ignored, skipping processing"
    else:
        try:
            subtitles.index(index_name)
        except (HTTPError, BadRequest) as error:
            self.retry(countdown=10, exc=error, max_retries=3)


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


def generate_thumbnail(document: Document):
    dest = "/thumbnails/{}.png".format(document.id)

    if not Path(dest).exists():
        video = VideoFile(document.path)
        video.thumbnail(float(document.seconds_middle), dest, document.content)
    return dest


@app.task
def extract_thumbnail_by_document(document: dict):
    return generate_thumbnail(Document.from_dict(document))


@task
def worker(c):
    c.run("celery -A usb.tasks worker")


@task
def flower(c):
    c.run("celery -A usb.tasks flower --port=5555")
