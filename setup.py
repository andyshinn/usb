from setuptools import setup

from usb import __version__

setup(
    name="usb",
    version=__version__,
    packages=["usb"],
    install_requires=[
        "aiohttp",
        "celery",
        "discord.py",
        "elastic-app-search",
        "flower",
        "fsspec",
        "gcsfs",
        "guessit",
        "inflect",
        "loguru",
        "moviepy",
        "pytest",
        "redis",
        "requests",
        "sentry-sdk",
        "sh",
        "srt",
    ],
    entry_points={"console_scripts": ["usb = usb:program.run"]},
)
