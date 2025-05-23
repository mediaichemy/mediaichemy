import httpx
import logging
from mediaichemy.ai.provider import Provider
import os
from mediaichemy.configs import ConfigManager

logger = logging.getLogger(__name__)


class OpenRouterProvider(Provider):
    """
    Provider for OpenRouter API.

    :ivar api_key: str
        The API key for the OpenRouter API.
    """
    def __init__(self):
        """
        Initializes the OpenRouterProvider.

        :raises EnvironmentError:
            If no API key is found in the configs or the OPENROUTER_API_KEY environment variable.
        """
        api_key = ConfigManager().get("ai.text.openrouter.api_key") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise EnvironmentError("No API key found in configs or OPENROUTER_API_KEY environment variable.")
        super().__init__(api_key)
        self.model_dicts = {'auto': 'openrouter/auto', 'deepseek': 'deepseek/deepseekr1'}
        self.base_url = "https://openrouter.ai/api/v1"

    async def request(self, prompt: str, output_path=None,) -> str:
        """
        Requests text generation from OpenRouter.

        :param prompt: str
            The text prompt.
        :param model: str
            The model to use.
        :return: str
            The generated text.
        """
        if output_path:
            raise ValueError("Output path is not yet supported for text generation.")

        model = ConfigManager().get("ai.text.openrouter.model")
        logger.info("Sending text generation"
                    f" request to OpenRouter with model '{model}'")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_dicts[model],
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                response.raise_for_status()
                completion = response.json()
                logger.info("Text generation request completed successfully.")
                return completion["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error occurred:"
                         f" {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error requesting text completion: {e}")
            raise
