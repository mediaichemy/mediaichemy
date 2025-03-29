import logging
from aichemy.ai.provider import Provider
from runware import Runware, IImageInference
import os
from aichemy.tools.filehandling import JPEGFile
from aichemy.configs import ConfigManager

logger = logging.getLogger(__name__)


class RunwareProvider(Provider):
    """
    Provider for Runware API.

    :ivar api_key: str
        The API key for the Runware API.
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
