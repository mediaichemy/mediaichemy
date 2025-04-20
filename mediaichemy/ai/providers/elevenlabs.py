import logging
from mediaichemy.ai.provider import Provider
import os
from elevenlabs import ElevenLabs, VoiceSettings
from mediaichemy.configs import ConfigManager

logger = logging.getLogger(__name__)


class ElevenLabsProvider(Provider):
    """
    Provider for ElevenLabs API.

    :ivar api_key: str
        The API key for the ElevenLabs API.
    """
    def __init__(self):
        """
        Initializes the ElevenLabsProvider.

        :raises EnvironmentError:
            If no API key is found in the configs or the ELEVENLABS_API_KEY environment variable.
        """
        api_key = ConfigManager().get("ai.speech.elevenlabs.api_key") or os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise EnvironmentError("No API key found in configs or ELEVENLABS_API_KEY environment variable.")
        super().__init__(api_key)
        self.client = ElevenLabs(api_key=api_key)

    async def request(self, prompt: str, output_path) -> str:
        """
        Converts text to speech and saves the output as an MP3 file.

        This function uses a specific client for
        text-to-speech conversion. It configures
        various parameters for the voice output
        and saves the resulting audio stream to an
        MP3 file with a unique name.

        :param prompt: str
            The text content to convert to speech.
        :param output_path: str
            The file path where the audio file will be saved.
        :return: str
            The file path where the audio file has been saved.
        """
        config_manager = ConfigManager()
        voice_id = config_manager.get("ai.speech.elevenlabs.voice_id")
        voice_settings = config_manager.get(table="ai.speech.elevenlabs.voice_settings")
        logger.debug(f"Voice settings: {voice_settings}")
        # Calling the text_to_speech conversion API with detailed parameters
        response = self.client.text_to_speech.convert(
            voice_id=voice_id,
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=prompt,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                **voice_settings
            ),
        )

        # Save the audio stream to a file
        with open(output_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        logger.info(f"Audio saved to {output_path}")

        # Return the path of the saved audio file
        return output_path
