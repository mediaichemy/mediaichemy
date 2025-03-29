from aichemy.ai.providers.elevenlabs import ElevenLabsProvider
from aichemy.ai.providers.openrouter import OpenRouterProvider
from aichemy.ai.providers.runware import RunwareProvider
from aichemy.ai.providers.minimax import MinimaxProvider
from aichemy.configs import ConfigManager
import logging
from aichemy.tools.filehandling import MP4File

logger = logging.getLogger(__name__)

PROVIDERS = {
    "text": {"openrouter": OpenRouterProvider},
    "image": {"runware": RunwareProvider},
    "video": {"minimax": MinimaxProvider},
    "speech": {"elevenlabs": ElevenLabsProvider},
}


async def ai_request(media: str, prompt, **kwargs):
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
    if media == 'test_video':
        return MP4File("content/short_video/0w9m9n67ws/video.mp4")
    config_manager = ConfigManager()
    provider_name = config_manager.get(table=f'ai.{media}', key='provider')
    logger.debug(f"Using provider '{provider_name}' for media '{media}'")
    logger.debug(f"Arguments: {kwargs}")
    if provider_name not in PROVIDERS[media]:
        raise ValueError(f"Provider '{provider_name}' is not supported.")

    # Instantiate the provider using the factory pattern
    provider = PROVIDERS[media][provider_name]()

    # Call the provider's request method
    return await provider.request(prompt, **kwargs)
