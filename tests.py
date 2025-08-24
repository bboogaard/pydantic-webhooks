import os
from contextlib import contextmanager
from datetime import datetime
from unittest import mock

import pytest
import requests
from dict2xml import dict2xml
from freezegun import freeze_time
from pydantic import BaseModel, field_serializer, PositiveInt

from pydantic_webhooks import get_webhook_producer, register_webhook_deliverer, register_webhook_serializer
from pydantic_webhooks.deliverer import WebhookDeliverer
from pydantic_webhooks.exceptions import InvalidWebhookDelivererError, InvalidWebhookFormatError, WebhookDeliveryError
from pydantic_webhooks.serializer import WebhookSerializer


default_time = '2024-01-01T00:00:00'


@contextmanager
def override_settings(**kwargs):
    from pydantic_webhooks.settings import settings as pydantic_settings
    old_settings = pydantic_settings._settings.copy()
    pydantic_settings._settings.update(**kwargs)
    yield
    pydantic_settings._settings.clear()
    pydantic_settings._settings.update(**old_settings)


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]

    @field_serializer('signup_ts')
    def serialize_signup_ts(self, v: datetime | None) -> str | None:
        return v.isoformat()[:19] if v else None
    

class XMLFileDeliverer(WebhookDeliverer):

    data_dir: str

    class Config(WebhookDeliverer.Config):
        formats = ["xml"]

    def deliver_data(self, data: str) -> None:
        with open(os.path.join(self.data_dir, "webhook.xml"), "w") as f:
            f.write(data)


class XMLSerializer(WebhookSerializer):
    
    class Config(WebhookSerializer.Config):
        format = "xml"
        mode = "json"

    def format_data(self, data: dict) -> str:
        return dict2xml(data, wrap="webhook", indent="  ")


@pytest.fixture
def user_data():
    with freeze_time(default_time):
        return {
            'id': 1,
            'name': 'John Doe',
            'signup_ts': datetime.now(),
            'tastes': {
            'spicy': 5,
            'sweet': 3
        }
    }


@pytest.fixture
def user(user_data):
    return User(**user_data)


@pytest.fixture
def file_deliverer():
    data_dir = './data'
    os.makedirs(data_dir, exist_ok=True)
    deliver_class = type('XMLFileDeliverer', (XMLFileDeliverer,), {'data_dir': data_dir})
    register_webhook_deliverer('file', deliver_class)
    register_webhook_serializer('xml', XMLSerializer)
    yield deliver_class
    for filename in os.listdir(data_dir):
        os.remove(os.path.join(data_dir, filename))
    os.rmdir(data_dir)


def test_send_webhook(user):
    with mock.patch('requests.post') as mock_post:
        producer = get_webhook_producer()
        producer.send_webhook(user)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == 'http://example.com/webhook'
        assert 'json' in kwargs
        assert kwargs['json']['id'] == 1
        assert kwargs['json']['name'] == 'John Doe'
        assert kwargs['json']['signup_ts'] == '2024-01-01T00:00:00'
        assert kwargs['json']['tastes'] == {'spicy': 5, 'sweet': 3}
        assert kwargs['headers']['Content-Type'] == 'application/json'
        assert kwargs['auth'] is None


def test_send_webhook_with_error(user):
    with mock.patch('requests.post') as mock_post:
        mock_post.side_effect = requests.RequestException("Network error")
        producer = get_webhook_producer()
        with pytest.raises(WebhookDeliveryError):
            producer.send_webhook(user)


def test_send_webhook_with_auth(user):
    with override_settings(HTTP_AUTH_USER='user', HTTP_AUTH_PASSWORD='pass'):
        with mock.patch('requests.post') as mock_post:
            producer = get_webhook_producer()
            producer.send_webhook(user)
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert kwargs['auth'] == ('user', 'pass')


def test_send_webhook_with_serialization_options(user):
    with mock.patch('requests.post') as mock_post:
        producer = get_webhook_producer()
        producer.send_webhook(user, exclude={'tastes'})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert 'json' in kwargs
        assert 'tastes' not in kwargs['json']


def test_custom_components(user, file_deliverer):
    with override_settings(DELIVERER='file', SERIALIZER='xml'):
        producer = get_webhook_producer()
        producer.send_webhook(user)
        with open(os.path.join(file_deliverer.data_dir, "webhook.xml")) as f:
            xml_data = f.read()
        assert "<webhook>" in xml_data
        assert "<id>1</id>" in xml_data
        assert "<name>John Doe</name>" in xml_data
        assert "<signup_ts>2024-01-01T00:00:00</signup_ts>" in xml_data
        assert "<tastes>" in xml_data
        assert "<spicy>5</spicy>" in xml_data
        assert "<sweet>3</sweet>" in xml_data


def test_invalid_deliverer():
    with override_settings(DELIVERER='invalid'):
        with pytest.raises(InvalidWebhookDelivererError):
            get_webhook_producer()


def test_invalid_format(file_deliverer):
    with override_settings(DELIVERER='file'):
        with pytest.raises(InvalidWebhookFormatError):
            get_webhook_producer()
