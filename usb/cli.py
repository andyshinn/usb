from invoke import task

from usb.logging import logger
from usb.search import Meilisearch
from usb.tasks import process_subtitle, process_video
from usb.utils import get_mkvs


def mkv_task(index: str, folder: str, task_name):
    for file in get_mkvs(folder):
        task_job = task_name.delay(index, file.path)
        logger.info("submitting {} task: {}", task_name, task_job)


@task
def index_subs(c, index_name, folder):
    client = Meilisearch()
    index = client.get_or_create_index(index_name, {"primaryKey": "id"})
    index.update_settings({"searchableAttributes": ["content"]})
    mkv_task(index_name, folder, process_subtitle)


@task
def extract_thumbs(c, index, folder):
    mkv_task(index, folder, process_video)


@task
def list_files(c, folder):
    for file in get_mkvs(folder):
        logger.info("found file: {}", file)
