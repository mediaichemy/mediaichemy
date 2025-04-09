from abc import ABC, abstractmethod
from mediaichemy.content.content import Content


class ContentCreator(ABC):
    def __init__(self, content_type: str):
        self.content_type = content_type

    @abstractmethod
    async def generate_ideas(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")

    async def create(self, idea: Content, **kwargs) -> None:
        raise NotImplementedError("Subclasses must implement this method.")
