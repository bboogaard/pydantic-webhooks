from pydantic import BaseModel

from pydantic_webhooks.deliverer import WebhookDeliverer
from pydantic_webhooks.logger import logger


__all__ = ["DefaultProducer"]


class WebhookProducer:

    def __init__(self, deliverer: WebhookDeliverer):
        self.deliverer = deliverer

    def send_webhook(self, instance: BaseModel, **serialize_options) -> None:
        # Send the serialized data to the webhook
        logger.info(f"Producing webhook for instance: {instance}")
        self.deliverer.deliver(instance, **serialize_options)


class DefaultProducer(WebhookProducer):
    ...
