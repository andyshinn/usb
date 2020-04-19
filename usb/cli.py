from invoke import task

from usb.logging import logger
from usb.utils import get_mkvs
from usb.tasks import process_subtitle, process_video


def mkv_task(folder, task_name):
    for file in get_mkvs(folder):
        task = task_name.delay(file.path)
        logger.info("submitting {} task: {}", task_name, task)


@task
def index_subs(c, folder):
    mkv_task(folder, process_subtitle)


@task
def extract_thumbs(c, folder):
    mkv_task(folder, process_video)


@task
def list_files(c, folder):
    for file in get_mkvs(folder):
        logger.info("found file: {}", file)
