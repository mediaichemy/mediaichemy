import httpx
import logging
from aichemy.ai.provider import Provider
import os
from aichemy.configs import ConfigManager

logger = logging.getLogger(__name__)


class OpenRouterProvider(Provider):
    """
    Provider for OpenRouter API.
    """
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENROUTER_API_KEY is not set.")
        super().__init__(api_key)
        self.model_dicts = {'auto': 'openrouter/auto',
                            'deepseek': 'deepseek/deepseekr1'}
        self.base_url = "https://openrouter.ai/api/v1"

    async def request(self, prompt: str) -> str:
        """
        Requests text generation from OpenRouter.

        :param prompt: str
            The text prompt.
        :param model: str
            The model to use.
        :return: str
            The generated text.
        """
        logger.info("Sending text generation"
                    " request to OpenRouter with model '{model}'")
        model = ConfigManager().get("ai.text.openrouter.model")
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
