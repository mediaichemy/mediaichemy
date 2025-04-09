from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class Provider(ABC):
    """
    Base class for providers requiring an API key.

    :param api_key: str
        The API key for the provider.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def request(self, prompt, output_path, **kwargs):
        """
        Abstract method to handle requests.
        """
        pass
