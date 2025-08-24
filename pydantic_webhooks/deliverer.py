from typing import Any, Dict, List

import requests
from pydantic import BaseModel

from pydantic_webhooks.exceptions import InvalidWebhookFormatError, WebhookDeliveryError
from pydantic_webhooks.logger import logger
from pydantic_webhooks.options import create_config
from pydantic_webhooks.serializer import WebhookSerializer
from pydantic_webhooks.settings import settings


__all__ = ["HttpDeliverer"]


class WebhookDeliverer:

    _options: Dict[str, Any] = None

    class Config:
        formats: List[str]

    def __init__(self, serializer: WebhookSerializer):
        self._config = create_config(self.Config)
        self.serializer = serializer
        if serializer._config.format not in self._config.formats:
            raise InvalidWebhookFormatError(f"Invalid format: {serializer._config.format}. Supported formats are: {self._config.formats}")

    @property
    def options(self) -> Dict[str, Any]:
        return self._get_options()

    def _get_options(self) -> Dict[str, Any]:
        return {}

    def deliver(self, instance: BaseModel, **serialize_options) -> None:
        logger.info(f"Delivering webhook for instance: {instance}")
        data = self.serializer.serialize(instance, **serialize_options)
        self.deliver_data(data)

    def deliver_data(self, data: Any) -> None:
        raise NotImplementedError("Subclasses must implement deliver_data method.")


class HttpDeliverer(WebhookDeliverer):

    class Config(WebhookDeliverer.Config):
        formats = ['json']

    def _get_options(self) -> Dict[str, Any]:
        return {
            "url": settings.WEBHOOK_URL,
            "auth": (settings.HTTP_AUTH_USER, settings.HTTP_AUTH_PASSWORD),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    def deliver_data(self, data: Any) -> None:
        try:
            logger.info(f"Sending HTTP POST to {self.options['url']}")
            response = requests.post(self.options["url"], json=data, headers=self.options["headers"], auth=self.get_auth())
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to deliver webhook: {e}")
            raise WebhookDeliveryError(f"Failed to deliver webhook: {e}")

    def get_auth(self):
        user, password = self.options["auth"]
        return (user, password) if user and password else None
