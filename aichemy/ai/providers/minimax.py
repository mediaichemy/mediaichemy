import httpx
import logging
from aichemy.ai.provider import Provider
import asyncio
import base64
import os
from aichemy.tools.filehandling import MP4File
from aichemy.configs import ConfigManager

logger = logging.getLogger(__name__)


class MinimaxProvider(Provider):
    """
    Provider for Minimax API.

    :ivar api_key: str
        The API key for the Minimax API.
    """
    def __init__(self):
        """
        Initializes the MinimaxProvider.

        :raises EnvironmentError:
            If the MINIMAX_API_KEY environment variable is not set.
        """
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
        :param prompt: str
            The text prompt for the video.
        :param output_path: str
            The path to save the generated video.
        :return: MP4File
            The generated video file.
        :raises Exception:
            If the video generation task fails.
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
        :raises httpx.HTTPStatusError:
            If the HTTP request fails.
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
        :raises Exception:
            If the video generation fails.
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
        :raises httpx.HTTPStatusError:
            If the HTTP request fails.
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
        :raises httpx.HTTPStatusError:
            If the HTTP request fails.
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
