from invoke import Collection, Program
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from usb import cli, server, tasks, bot

__version__ = "0.0.6"

sentry_sdk.init(
    integrations=[CeleryIntegration(), AioHttpIntegration()], release=__version__
)

program = Program(namespace=Collection(cli, server, tasks, bot), version=__version__)
