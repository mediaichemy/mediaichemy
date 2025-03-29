import logging
from aichemy.ai.provider import Provider
import os
from aichemy.ai.providers.elevenlabs import ElevenLabs, VoiceSettings
from aichemy.tools.filehandling import MP3File
from aichemy.configs import ConfigManager

logger = logging.getLogger(__name__)


class ElevenLabsProvider(Provider):
    """
    Provider for ElevenLabs API.
    """
    def __init__(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise EnvironmentError("ELEVENLABS_API_KEY is not set.")
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

        Args:
            text (str): The text content to convert to speech.

        Returns:
            str: The file path where the audio file has been saved.
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
        mp3file = MP3File(output_path)
        logger.info(f"Audio saved to {output_path}")

        # Return the path of the saved audio file
        return mp3file
