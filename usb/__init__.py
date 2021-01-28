import sentry_sdk
from invoke import Collection, Program
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from usb import cli, server, tasks
from usb.bot import discord

__version__ = "0.0.12"

sentry_sdk.init(
    integrations=[CeleryIntegration(), AioHttpIntegration()],
    release=f"usb@{__version__}",
)

program = Program(namespace=Collection(cli, server, tasks, discord), version=__version__)
