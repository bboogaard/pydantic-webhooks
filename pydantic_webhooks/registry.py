from typing import Dict, Type

from pydantic_webhooks.deliverer import HttpDeliverer, WebhookDeliverer
from pydantic_webhooks.exceptions import InvalidWebhookDelivererError, InvalidWebhookProducerError, InvalidWebhookSerializerError
from pydantic_webhooks.producer import DefaultProducer, WebhookProducer
from pydantic_webhooks.serializer import JsonSerializer, WebhookSerializer
from pydantic_webhooks.settings import settings


class WebhookRegistry:

    _producers: Dict[str, Type[WebhookProducer]] = {}
    _deliverers: Dict[str, Type[WebhookDeliverer]] = {}
    _serializers: Dict[str, Type[WebhookSerializer]] = {}

    @classmethod
    def register_producer(cls, name: str, producer: Type[WebhookProducer]) -> None:
        cls._producers[name] = producer

    @classmethod
    def get_producer(cls, name: str) -> Type[WebhookProducer]:
        if name not in cls._producers:
            raise InvalidWebhookProducerError(f"Producer '{name}' is not registered.")
        return cls._producers[name]

    @classmethod
    def register_deliverer(cls, name: str, deliverer: Type[WebhookDeliverer]) -> None:
        cls._deliverers[name] = deliverer

    @classmethod
    def get_deliverer(cls, name: str) -> Type[WebhookDeliverer]:
        if name not in cls._deliverers:
            raise InvalidWebhookDelivererError(f"Deliverer '{name}' is not registered.")
        return cls._deliverers[name]
    
    @classmethod
    def register_serializer(cls, name: str, serializer: Type[WebhookSerializer]) -> None:
        cls._serializers[name] = serializer

    @classmethod
    def get_serializer(cls, name: str) -> Type[WebhookSerializer]:
        if name not in cls._serializers:
            raise InvalidWebhookSerializerError(f"Serializer '{name}' is not registered.")
        return cls._serializers[name]
    

def register_webhook_producer(name: str, producer: Type[WebhookProducer]) -> None:
    WebhookRegistry.register_producer(name, producer)


def get_webhook_producer() -> WebhookProducer:
    serializer = get_webhook_serializer()
    deliverer = get_webhook_deliverer(serializer)
    return WebhookRegistry.get_producer(settings.PRODUCER)(deliverer)


def register_webhook_deliverer(name: str, deliverer: Type[WebhookDeliverer]) -> None:
    WebhookRegistry.register_deliverer(name, deliverer)


def get_webhook_deliverer(serializer: WebhookSerializer) -> WebhookDeliverer:
    return WebhookRegistry.get_deliverer(settings.DELIVERER)(serializer)


def register_webhook_serializer(name: str, serializer: Type[WebhookSerializer]) -> None:
    WebhookRegistry.register_serializer(name, serializer)


def get_webhook_serializer() -> WebhookSerializer:
    return WebhookRegistry.get_serializer(settings.SERIALIZER)()


def register_webhook_components():
    register_webhook_producer("default", DefaultProducer)
    register_webhook_deliverer("http", HttpDeliverer)
    register_webhook_serializer("json", JsonSerializer)


register_webhook_components()
