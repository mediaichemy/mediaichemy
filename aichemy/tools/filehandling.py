from abc import ABC, abstractmethod
import json
import logging
import os
import random
import requests
import string
from PIL import Image
from typing import Any, Dict, Tuple
import subprocess
from mutagen.mp3 import MP3

# Initialize logger
logger = logging.getLogger(__name__)


class Directory:
    """
    Handles directory operations.

    :param path: str
        The directory path.
    :param create: bool, optional
        Whether to create the directory if it doesn't exist. Defaults to False.
    :param random_subdir: bool, optional
        Whether to create a random subdirectory. Defaults to False.
    """
    def __init__(self, path: str,
                 create: bool = False,
                 random_subdir: bool = False) -> None:
        self.path = path
        self.create = create
        self.random_subdir = random_subdir

        if self.create:
            self.path = self.create_dir()
        elif not os.path.isdir(self.path):
            raise ValueError(f"Invalid directory path: {self.path}")

    def create_dir(self) -> str:
        """
        Creates the directory if it does not exist.

        :return: str
            The created directory path.
        """
        if self.random_subdir:
            dirname = ''.join(random.choices(string.ascii_lowercase +
                                             string.digits, k=10))
            self.path = os.path.join(self.path, dirname)
        os.makedirs(self.path, exist_ok=True)
        logger.info(f"Created directory: {self.path}")
        return self.path


class File(ABC):
    """
    Abstract base class for file operations.

    :param filepath: str
        The file path.
    :param output_path: str, optional
        The output path for downloaded files.
    """
    def __init__(self, filepath: str, output_path: str = None) -> None:
        self.filepath = filepath
        self.output_path = output_path

        if self._is_url(filepath):
            if not output_path:
                raise ValueError(
                    "An output_path must be provided when the input is a URL.")
            self._download_file(filepath, output_path)
            self.filepath = output_path

        dir, self.name, self.extension = self.split_name(self.filepath)
        self.dir = Directory(dir).path
        self.data = self.load() if os.path.isfile(self.filepath) else None

    @staticmethod
    def _is_url(path: str) -> bool:
        """
        Checks if a path is a URL.

        :param path: str
            The path to check.
        :return: bool
            True if the path is a URL, False otherwise.
        """
        return path.startswith(("http://", "https://"))

    @staticmethod
    def _download_file(url: str, destination: str) -> None:
        """
        Downloads a file from a URL to the specified destination.

        :param url: str
            The URL of the file to download.
        :param destination: str
            The path where the file will be saved.
        """
        response = requests.get(url)
        response.raise_for_status()
        with open(destination, 'wb') as handler:
            handler.write(response.content)
        logger.info(f"Downloaded file from {url} to {destination}")

    @staticmethod
    def split_name(filepath: str) -> Tuple[str, str, str]:
        """
        Splits the filename into directory, name, and extension.

        :param filepath: str
            The full path of the file.
        :return: Tuple[str, str, str]
            A tuple containing the directory, name, and extension of the file.
        """
        dir, name = os.path.split(filepath)
        name, ext = os.path.splitext(name)
        return dir, name, ext

    @staticmethod
    def validate_extension(filepath: str, expected_extension: str) -> None:
        """
        Validates that the filename has the specified extension.

        :param filepath: str
            The full path of the file.
        :param expected_extension: str
            The expected file extension (e.g., ".txt", ".json").
        :raises ValueError:
            If the filename does not end with the specified extension.
        """
        if not filepath.endswith(expected_extension):
            raise ValueError(f"Invalid file extension for '{filepath}'."
                             " Expected '{expected_extension}'.")

    @abstractmethod
    def save(self, data: Any) -> None:
        """
        Saves data to the file.
        """
        pass

    @abstractmethod
    def load(self) -> Any:
        """
        Loads data from the file.
        """
        pass


class JSONFile(File):
    """
    Handles JSON file operations.
    """
    def __init__(self, filepath: str, output_path: str = None) -> None:
        super().__init__(filepath, output_path)
        self.validate_extension(self.filepath, ".json")

    def save(self, data: Dict[str, Any]) -> None:
        """
        Saves a dictionary as a JSON file.

        :param data: Dict[str, Any]
            The data to save.
        """
        os.makedirs(self.dir, exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved JSON file: {self.filepath}")

    def load(self) -> Dict[str, Any]:
        """
        Loads a JSON file.

        :return: Dict[str, Any]
            The loaded data.
        """
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded JSON file: {self.filepath}")
        return data


class JPEGFile(File):
    """
    Handles JPEG file operations.
    """
    def __init__(self, filepath: str, output_path: str = None) -> None:
        super().__init__(filepath, output_path)
        self.validate_extension(self.filepath, ".jpg")

    def save(self, data: Image.Image) -> None:
        """
        Saves an image as a JPEG file.

        :param data: Image.Image
            The image data to save.
        """
        os.makedirs(self.dir, exist_ok=True)
        data.save(self.filepath, format='JPEG')
        logger.info(f"Saved JPEG file: {self.filepath}")

    def load(self) -> Image.Image:
        """
        Loads a JPEG file.

        :return: Image.Image
            The loaded image.
        """
        image = Image.open(self.filepath)
        logger.info(f"Loaded JPEG file: {self.filepath}")
        return image


class MP4File(File):
    """
    Handles MP4 file operations.

    :param filepath: str
        The full path of the MP4 file.
    """
    def __init__(self, filepath: str, output_path: str = None) -> None:
        super().__init__(filepath, output_path)
        self.validate_extension(self.filepath, ".mp4")

    def save(self, data: bytes) -> None:
        """
        Saves binary data as an MP4 file.

        :param data: bytes
            The binary data to save.
        """
        os.makedirs(self.dir, exist_ok=True)
        with open(self.filepath, 'wb') as f:
            f.write(data)
        logger.info(f"Saved MP4 file: {self.filepath}")

    def load(self) -> bytes:
        """
        Loads an MP4 file.

        :return: bytes
            The loaded data.
        """
        with open(self.filepath, 'rb') as f:
            data = f.read()
        logger.info(f"Loaded MP4 file: {self.filepath}")
        return data

    def get_duration(self) -> float:
        """
        Gets the length of the video in seconds.

        :return: float
            The video length in seconds.
        """
        try:
            # Use ffprobe to get the video duration
            result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    self.filepath
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Parse the duration from the output
            duration = float(result.stdout.strip())
            return duration
        except Exception as e:
            logger.error(f"Error getting video length: {e}")
            raise


class MP3File(File):
    """
    Handles MP3 file operations.

    :param filepath: str
        The full path of the MP3 file.
    """
    def __init__(self, filepath: str, output_path: str = None) -> None:
        super().__init__(filepath, output_path)
        self.validate_extension(self.filepath, ".mp3")

    def save(self, data: bytes) -> None:
        """
        Saves binary data as an MP3 file.

        :param data: bytes
            The binary data to save.
        """
        os.makedirs(self.dir, exist_ok=True)
        with open(self.filepath, 'wb') as f:
            f.write(data)
        logger.info(f"Saved MP3 file: {self.filepath}")

    def load(self) -> bytes:
        """
        Loads an MP3 file.

        :return: bytes
            The loaded data.
        """
        with open(self.filepath, 'rb') as f:
            data = f.read()
        logger.info(f"Loaded MP3 file: {self.filepath}")
        return data

    def get_duration(self) -> float:
        """
        Gets the duration of the MP3 file in seconds.

        :return: float
            The MP3 duration in seconds.
        """
        try:
            audio = MP3(self.filepath)
            return audio.info.length
        except ImportError:
            logger.error("Mutagen library is required to get MP3 duration.")
            raise
        except Exception as e:
            logger.error(f"Error getting MP3 duration: {e}")
            raise
