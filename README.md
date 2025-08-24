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
