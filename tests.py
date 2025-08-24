from contextlib import contextmanager
from datetime import datetime
from unittest import mock

import pytest
import requests
from freezegun import freeze_time
from pydantic import BaseModel, field_serializer, PositiveInt

from pydantic_webhooks import get_webhook_producer
from pydantic_webhooks.exceptions import WebhookDeliveryError


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
