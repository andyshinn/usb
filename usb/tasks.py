from celery import Celery, group
from loguru import logger
from requests.exceptions import HTTPError

from usb.utils import formatted_episodes, msecs
from usb.subtitle import Subtitles
from usb.video import VideoFile

app = Celery('tasks', broker='pyamqp://celery:wh4tsth3d34l@broker/celery')


@app.task(bind=True)
def process_subtitle(self, path):
    video = VideoFile(path)
    subtitles = Subtitles(video)
    try:
        subtitles.index()
    except HTTPError as e:
        self.retry(countdown=10, exc=e)


@app.task
def finish_indexing(count):
    logger.info("finished indexing {} episodes".format(count))


@app.task
def process_video(file):
    video = VideoFile(file)
    subs = video.extract_subs()
    extract_task = group(extract_thumbnail.s(
        file,
        msecs(sub.start, sub.end),
        "/thumbnails/{}-{}-{}-{}.png".format(video.show, video.season, formatted_episodes(video.episodes), sub.index),
        sub.content
    ) for sub in subs)
    extract_task.apply_async()


@app.task
def extract_thumbnail(file, milliseconds, dest, text):
    video = VideoFile(file)
    video.thumbnail(milliseconds, dest, text)
