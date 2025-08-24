from dotenv import load_dotenv
load_dotenv('.env')


import logging  # noqa: E402

import typer  # noqa: E402
from pydantic import BaseModel  # noqa: E402


from pydantic_webhooks import get_webhook_producer  # noqa: E402


logger = logging.getLogger("command")


class MyModel(BaseModel):
    id: int
    name: str
    description: str
    number: float
    

def start_app():
    app = typer.Typer()
    return app


app = start_app()


@app.command(hidden=True)
def info():
    print("Command line tools for the pydantic-webhooks package")


@app.command()
def send_webhook():
    producer = get_webhook_producer()
    # Create a sample Pydantic model instance
    instance = MyModel(id=1, name="Test", description="This is a test", number=42.0)
    producer.send_webhook(instance)


if __name__ == "__main__":
    app()
