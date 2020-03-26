from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

sentry_sdk.init(integrations=[CeleryIntegration(), AioHttpIntegration()])


def breadcrumb_sink(message):
    record = message.record
    sentry_sdk.add_breadcrumb(
        category=record["name"],
        message=record["message"],
        level=record["level"].name,
    )


logger.add(breadcrumb_sink)
