from invoke import task
from loguru import logger

from usb.subtitle import get_subtitle_files
from usb.tasks import process_subtitle

@task
def index_subs(c, path='subs/*.srt'):
    for file in get_subtitle_files(path):
        task = process_subtitle.delay(file)
        logger.info("submitting task: {}", task)
