from invoke import task
from loguru import logger

from usb.utils import get_mkvs
from usb.tasks import process_subtitle, process_video


def mkv_task(folder, task_name):
    for file in get_mkvs(folder):
        task = eval(task_name).delay(str(file))
        logger.info("submitting {} task: {}", task_name, task)


@task
def index_subs(c, folder):
    mkv_task(folder, 'process_subtitle')


@task
def extract_thumbs(c, folder):
    mkv_task(folder, 'process_video')
