from celery import Celery
from loguru import logger

from usb.utils import parse_episodes
from usb.subtitle import index_subtitle

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
