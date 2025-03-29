from abc import ABC, abstractmethod
from aichemy.content.content import Content


class ContentCreator(ABC):
    """
    Abstract base class for content types.
    """
    def __init__(self, content_type: str):
        self.content_type = content_type

    @abstractmethod
    async def generate_ideas(self, **kwargs):
        """
        Abstract method to generate ideas for the content type.
        This method should be implemented by subclasses.

        :param kwargs: dict
            The values to format the prompt with.
        :return: List[Dict]
            A list of generated ideas.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    async def create(self, idea: Content, **kwargs) -> None:
        """
        Abstract method to create content based on the generated idea.
        This method should be implemented by subclasses.

        :param idea: Content
            The content idea to create content from.
        """
        raise NotImplementedError("Subclasses must implement this method.")
