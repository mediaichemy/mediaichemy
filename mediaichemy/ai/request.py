from mediaichemy.ai.providers.elevenlabs import ElevenLabsProvider
from mediaichemy.ai.providers.openrouter import OpenRouterProvider
from mediaichemy.ai.providers.runware import RunwareProvider
from mediaichemy.ai.providers.minimax import MinimaxProvider
from mediaichemy.configs import ConfigManager
import logging
from mediaichemy.tools.filehandling import JPEGFile, MP3File, MP4File
import os

logger = logging.getLogger(__name__)

PROVIDERS = {
    "text": {"openrouter": OpenRouterProvider},
    "image": {"runware": RunwareProvider},
    "video": {"minimax": MinimaxProvider},
    "speech": {"elevenlabs": ElevenLabsProvider},
}


TYPES = {
    "text": str,
    "image": JPEGFile,
    "video": MP4File,
    "speech": MP3File,
}


async def ai_request(media: str, prompt, output_path=None, **kwargs):
    """
    Unified interface to make a request to a provider.

    :param media: str
        The type of media to generate (e.g., "text", "image").
    :param prompt: str
        The prompt for the AI provider.
    :param kwargs: dict
        Additional arguments for the provider's request method.
    :return: Any
        The result of the provider's request.
    """
    config_manager = ConfigManager()
    provider_name = config_manager.get(table=f'ai.{media}', key='provider')
    logger.debug(f"Using provider '{provider_name}' for media '{media}'")
    logger.debug(f"Arguments: {kwargs}")
    if provider_name not in PROVIDERS[media]:
        raise ValueError(f"Provider '{provider_name}' is not supported.")

    # Instantiate the provider using the factory pattern
    provider = PROVIDERS[media][provider_name]()

    response = await provider.request(prompt, output_path=output_path, **kwargs)

    if 'test' in response:
        logger.debug(f"Test mode: {response}")
        if output_path is None and media == 'text':
            logger.debug("Text response might include the test word, and not need to be saved.")
            return response
        if not os.path.exists(output_path):
            TYPES[media](response.replace('test_', '')).copy_to(output_path)
        response = output_path

    # Call the provider's request method
    return TYPES[media](response)
