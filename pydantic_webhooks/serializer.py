from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from pydantic_webhooks.logger import logger
from pydantic_webhooks.options import create_config


__all__ = ["JsonSerializer"]


class WebhookSerializer:

    class Config:
        format: str
        mode: str

    def __init__(self):
        self._config = create_config(self.Config)

    def serialize(self, instance: BaseModel, include: Optional[List[str]] = None, exclude: Optional[List[str]] = None, 
                  aliases: Optional[Dict[str, str]] = None, exclude_none: bool = False) -> Any:
        logger.info(f"Serializing instance: {instance}")
        serialized = instance.model_dump(
            mode=self._config.mode, 
            include=include, 
            exclude=exclude, 
            exclude_none=exclude_none
        )
        if aliases:
            serialized = {aliases.get(k, k): v for k, v in serialized.items()}
        return self.format_data(serialized)
    
    def format_data(self, data: Dict[str, Any]) -> Any:
        raise NotImplementedError("Subclasses must implement format_data method.")
    

class JsonSerializer(WebhookSerializer):
    
    class Config(WebhookSerializer.Config):
        format = "json"
        mode = "json"

    def format_data(self, data: Dict[str, Any]) -> Any:
        return data
