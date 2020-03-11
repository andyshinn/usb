from celery import Celery, group
from loguru import logger

from usb.utils import parse_episodes, formatted_episodes
from usb.subtitle import index_subtitle
from usb.video import VideoFile

app = Celery('tasks', broker='pyamqp://celery:wh4tsth3d34l@broker/celery')


@app.task
def get_episodes(title):
    return parse_episodes(title)


@app.task
def process_subtitle(file):
    index_subtitle(file)


@app.task
def finish_indexing(count):
    logger.info("finished indexing {} episodes".format(count))


@app.task
def process_video(file):
    video = VideoFile(file)
    subs = video.extract_subs()
    extract_task = group(extract_thumbnail.s(
        file,
        sub.start.total_seconds() * 1000,
        "/thumbnails/{}-{}-{}-{}.png".format(video.show, video.season, formatted_episodes(video.episode), sub.index),
        sub.content
    ) for sub in subs)
    extract_task.apply_async()


@app.task
def extract_thumbnail(file, msecs, dest, text):
    video = VideoFile(file)
    video.thumbnail(msecs, dest, text)
