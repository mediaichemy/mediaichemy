from abc import ABC, abstractmethod
import httpx
import logging
from runware import Runware, IImageInference
import asyncio
import base64
import os
from elevenlabs import ElevenLabs, VoiceSettings
from aichemy.filehandling import JPEGFile, MP4File, MP3File
from ..configs import ConfigManager

logger = logging.getLogger(__name__)


class Provider(ABC):
    """
    Base class for providers requiring an API key.
    """
    PROVIDERS = {
        "openrouter": "OpenRouterProvider",
        "runware": "RunwareProvider",
        "minimax": "MinimaxProvider",
        "elevenlabs": "ElevenLabsProvider",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def request(self, prompt, output_path, **kwargs):
        """
        Abstract method to handle requests.
        """
        pass

    @classmethod
    def create_provider(cls, provider_name: str) -> "Provider":
        """
        Factory method to create a provider instance.

        :param provider_name: str
            The name of the provider.
        :return: Provider
            An instance of the selected provider.
        """
        if provider_name not in cls.PROVIDERS:
            raise ValueError(f"Provider '{provider_name}' is not supported.")
        provider_class = globals()[cls.PROVIDERS[provider_name]]
        return provider_class()


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


class RunwareProvider(Provider):
    """
    Provider for Runware API.
    """
    def __init__(self):
        api_key = os.getenv("RUNWARE_API_KEY")
        if not api_key:
            raise EnvironmentError("RUNWARE_API_KEY is not set.")
        super().__init__(api_key)

    async def request(self, prompt: str,
                      output_path: str = "image.jpg") -> JPEGFile:
        """
        Requests image generation from Runware.

        :param prompt: str
            The text prompt.
        :param output_path: str
            The path to save the generated image.
        :return: JPEGFile
            The generated image file.
        """
        logger.info("Connecting to Runware API for image generation.")
        client = Runware(api_key=self.api_key)
        await client.connect()

        logger.info("Building inference for image generation.")
        inference = self.build_inference(prompt)
        images = await client.imageInference(requestImage=inference)
        image_url = images[0].imageURL

        logger.info(f"Downloading generated image to {output_path}.")
        JPEGFile._download_file(image_url, output_path)
        return JPEGFile(output_path)

    def build_inference(self, prompt: str) -> IImageInference:
        """
        Builds the IImageInference object for image generation.

        :param prompt: str
            The text prompt.
        :return: IImageInference
            The inference object.
        """
        config_manager = ConfigManager()
        model = config_manager.get("ai.image.runware").pop("model"),
        return IImageInference(positivePrompt=prompt,
                               numberResults=1,
                               model=model,
                               **config_manager.get("ai.image.runware"))


class MinimaxProvider(Provider):
    """
    Provider for Minimax API.
    """
    def __init__(self):
        api_key = os.getenv("MINIMAX_API_KEY")
        if not api_key:
            raise EnvironmentError("MINIMAX_API_KEY is not set.")
        super().__init__(api_key)
        self.base_url = "https://api.minimaxi.chat/v1"

    async def request(self,
                      prompt: str, img_filepath: str,
                      output_path: str = "video.mp4") -> MP4File:
        """
        Requests video generation from Minimax.

        :param img_filepath: str
            The path to the input image file.
        :param img_prompt: str
            The text prompt for the video.
        :param output_path: str
            The path to save the generated video.
        :param model: str
            The model to use.
        :return: MP4File
            The generated video file.
        """
        model = ConfigManager().get('ai.video.minimax.model')
        logger.info(
            f"Preparing video generation request with model '{model}'.")
        # Prepare the payload
        payload = self._prepare_payload(img_filepath, prompt, model)
        logger.debug(f"Payload: {payload}")
        logger.info("Submitting video generation task to Minimax.")
        # Submit the task
        task_id = await self._submit_task(payload)
        if not task_id:
            logger.error("Failed to generate video task.")
            raise Exception("Failed to generate video task")
        logger.info(f"Task submitted successfully. Task ID: {task_id}")

        # Poll for task status and download the video
        return await self._poll_and_download(task_id, output_path)

    def _prepare_payload(self, img_filepath: str,
                         img_prompt: str, model: str) -> dict:
        """
        Prepares the payload for video generation.

        :param img_filepath: str
            The path to the input image file.
        :param img_prompt: str
            The text prompt for the video.
        :param model: str
            The model to use.
        :return: dict
            The payload for the video generation request.
        """
        with open(img_filepath, "rb") as image_file:
            data = base64.b64encode(image_file.read()).decode("utf-8")
        return {
            "model": model,
            "prompt": img_prompt,
            "first_frame_image": f"data:image/jpeg;base64,{data}"
        }

    async def _submit_task(self, payload: dict) -> str:
        """
        Submits a video generation task.

        :param payload: dict
            The payload for the video generation request.
        :return: str
            The task ID.
        """
        headers = {"authorization": f"Bearer {self.api_key}",
                   "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/video_generation",
                                         headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get("task_id")

    async def _poll_and_download(self,
                                 task_id: str,
                                 output_path: str) -> MP4File:
        """
        Polls task status and downloads the video.

        :param task_id: str
            The task ID.
        :param output_path: str
            The path to save the generated video.
        :return: MP4File
            The generated video file.
        """
        logger.info(f"Polling status for task ID: {task_id}")
        while True:
            await asyncio.sleep(30)
            file_id, status = await self.check_status(task_id)
            if file_id:
                logger.info(
                    f"Task completed. Downloading video to {output_path}.")
                download_url = await self.get_download_url(file_id)
                MP4File._download_file(download_url, output_path)
                return MP4File(output_path)
            if status in {"Fail", "Unknown"}:
                logger.error("Video generation failed.")
                break

    async def check_status(self, task_id: str) -> tuple[str, str]:
        """
        Checks the status of a video generation task.

        :param task_id: str
            The task ID.
        :return: tuple[str, str]
            The file ID and status.
        """
        headers = {"authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/query/video_generation?task_id={task_id}",
                headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("file_id", ""), data.get("status", "Unknown")

    async def get_download_url(self, file_id: str) -> str:
        """
        Retrieves the download URL for the generated video.

        :param file_id: str
            The file ID.
        :return: str
            The download URL.
        """
        headers = {"authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/files/retrieve?file_id={file_id}",
                headers=headers)
            response.raise_for_status()
            download_url = response.json()["file"]["download_url"]
            logger.info(f"Video available at URL: {download_url}")
            return download_url


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
        voice_id = config_manager.get("ai.audio.elevenlabs.voice_id")
        voice_settings = config_manager.get("ai.audio.elevenlabs.voice_settings")

        # Calling the text_to_speech conversion API with detailed parameters
        response = self.client.text_to_speech.convert(
            voice_id=voice_id,  # Adam pre-made voice
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


PROVIDERS = {
    "text": {"openrouter": OpenRouterProvider},
    "image": {"runware": RunwareProvider},
    "video": {"minimax": MinimaxProvider},
    "speech": {"elevenlabs": ElevenLabsProvider},
}


async def ai_request(media: str, prompt, **kwargs):
    """
    Unified interface to make a request to a provider.

    :param provider_name: str
        The name of the provider to use.
    :param args: tuple
        Positional arguments for the provider's request method.
    :param kwargs: dict
        Keyword arguments for the provider's request method.
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

    # Call the provider's request method
    return await provider.request(prompt, **kwargs)
