import os
import glob

from invoke import task
from loguru import logger
from guessit import guessit


from usb.utils import get_files
from usb.tasks import process_subtitle, process_video
from usb.extract import Extractor
from usb.video import VideoFile

@task
def index_subs(c, path='subs/*.srt'):
    for file in get_files(path):
        task = process_subtitle.delay(file)
        logger.info("submitting task: {}", task)


@task
def guess_it(c, path):
    file = os.path.basename(path)
    logger.info(file)
    logger.info(guessit(file))


@task
def extract_sub(c, file):
    video = VideoFile(file)
    video.extract_subs()
    logger.info('Extracted subtitles for {}', video)


@task
def extract_thumbs(c, path):
    for file in get_files(path):
        task = process_video.delay(file)
        logger.info("submitting task: {}", task)
