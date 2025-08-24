# Pydantic Webhooks

## Installation

Install the wheel file from the dist folder in your own virtual environment:

`pip install pydantic_webhooks-0.1.0-py3-none-any.whl`


## Quickstart

**Set environment variables**

To use the default settings, to send webhook data to a public http endpoint, assign the
value of this url to the environment variable `WEBHOOKS_WEBHOOK_URL`.

**Instantiate the Pydantic model**

```python
from pydantic import BaseModel


class MyModel(BaseModel):
    name: str
    value: str


instance = MyModel(name='foo', value='bar')
```

**Import the webhook producer and send the data**

```python
from pydantic_webhooks import get_webhook_producer


producer = get_webhook_producer()
producer.send_webhook(instance)
```

**Register a custom serializer**

```python
from pydantic_webhooks import register_webhook_serializer
from pydantic_webhooks.serializer import WebhookSerializer


class XMLSerializer(WebhookSerializer):
    
    class Config(WebhookSerializer.Config):
        format = "xml"
        mode = "json"

    def format_data(self, data: dict) -> str:
        return dict2xml(data, wrap="webhook", indent="  ")


register_webhook_serializer('xml', XMLSerializer)
```

**Register a custom deliverer**

```python
from pydantic_webhooks import register_webhook_deliverer
from pydantic_webhooks.deliverer import WebhookDeliverer


class FileDeliverer(WebhookDeliverer):

    data_dir: str

    class Config(WebhookDeliverer.Config):
        formats = ["json"]

    def deliver_data(self, data: str) -> None:
        with open(os.path.join(self.data_dir, "webhook.json"), "w") as f:
            f.write(data)


register_webhook_deliverer('file', FileDeliverer)
```
