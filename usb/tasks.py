import os
from pathlib import Path

from celery import Celery, group
from requests.exceptions import HTTPError
from elastic_app_search.exceptions import BadRequest
from invoke import task

from usb.logging import logger
from usb.utils import formatted_episodes, msecs
from usb.subtitle import Subtitles
from usb.video import VideoFile

app = Celery(
    "tasks",
    broker="pyamqp://celery:wh4tsth3d34l@{}/celery".format(
        os.getenv("SERVICE_NAME_BROKER", "broker")
    ),
    backend="redis://{}".format(os.getenv("SERVICE_NAME_RESULT", "result")),
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


def generate_thumbnail(id, path, seconds_middle, content):
    dest = "/thumbnails/{}.png".format(id)

    if not Path(dest).exists():
        video = VideoFile(path)
        video.thumbnail(float(seconds_middle), dest, content)
    return dest


@app.task
def extract_thumbnail_by_raw_document(document):
    return generate_thumbnail(
        document["id"]["raw"],
        document["path"]["raw"],
        document["seconds_middle"]["raw"],
        document["content"]["raw"],
    )


@app.task
def extract_thumbnail_by_document(document):
    return generate_thumbnail(
        document["id"],
        document["path"],
        document["seconds_middle"],
        document["content"],
    )


@task
def worker(c):
    c.run("celery -A usb.tasks worker")


@task
def flower(c):
    c.run("celery -A usb.tasks flower --port=5555")
