class WebhookError(Exception):
    """Base class for all webhook-related exceptions."""
    pass


class InvalidWebhookDelivererError(WebhookError):
    """Exception raised for invalid webhook delivery."""
    pass


class InvalidWebhookSerializerError(WebhookError):
    """Exception raised for invalid webhook serializers."""
    pass


class InvalidWebhookProducerError(WebhookError):
    """Exception raised for invalid webhook producers."""
    pass


class InvalidWebhookFormatError(WebhookError):
    """Exception raised for invalid webhook formats."""
    pass


class WebhookDeliveryError(WebhookError):
    """Exception raised for errors during webhook delivery."""
    pass
