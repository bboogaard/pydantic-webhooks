import os


class LazySettings:
    """A class to lazily load settings for the webhooks package."""

    def __init__(self):
        self._settings = None

    def __getattr__(self, item):
        """Get the setting value by its name."""
        if self._settings is None:
            self._settings = self._load_settings()
        if item not in self._settings:
            raise AttributeError(f"Setting '{item}' not found.")
        return self._settings[item]
    
    def _load_settings(self):
        """Load settings from the environment variables."""
        return {
            'WEBHOOK_URL': os.getenv('WEBHOOKS_WEBHOOK_URL'),
            'PRODUCER': os.getenv('WEBHOOKS_PRODUCER', 'default'),
            'DELIVERER': os.getenv('WEBHOOKS_DELIVERER', 'http'),
            'SERIALIZER': os.getenv('WEBHOOKS_SERIALIZER', 'json'),
            'HTTP_AUTH_USER': os.getenv('WEBHOOKS_HTTP_AUTH_USER', None),
            'HTTP_AUTH_PASSWORD': os.getenv('WEBHOOKS_HTTP_AUTH_PASSWORD', None)
        }
    

settings = LazySettings()