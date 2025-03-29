import os
import subprocess
from aichemy.tools.filehandling import MP3File, MP4File
import logging
import random
from aichemy.configs import ConfigManager

logger = logging.getLogger(__name__)


def download_random_from_youtube_urls(urls: list, output_path: str) -> MP3File:
    """
    Downloads a random audio file from a list of YouTube URLs as an MP3 file.

    :param urls: list
        A list of YouTube video URLs.
    :param output_path: str
        The path to save the downloaded MP3 file.
    :return: MP3File
        The downloaded MP3 file object.
    :raises ValueError:
        If the URL list is empty or invalid.
    """
    if not urls:
        raise ValueError("The URL list is empty. Provide at least one URL.")

    # Select a random URL from the list
    selected_url = random.choice(urls)
    logger.info(f"Selected URL for download: {selected_url}")

    try:
        # Use yt-dlp to download the audio
        command = [
            "yt-dlp",
            "-x",  # Extract audio
            "--audio-format", "mp3",  # Convert to MP3
            "-o", output_path,  # Output file path
            selected_url
        ]
        subprocess.run(command, check=True)
        logger.info(f"Audio downloaded successfully to: {output_path}")

        # Return the MP3File object
        return MP3File(filepath=output_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download audio from URL {selected_url}: {e}")
        raise


class AudioEdit:
    """
    Handles audio editing operations, including adding MP3 audio to an MP4 video.

    :param audio: MP3File
        The MP3 file to be used for audio editing.
    :param video: MP4File, optional
        The MP4 file to which the audio will be added.
    """
    def __init__(self, audio: MP3File, video: MP4File = None):
        self.audio = audio
        self.video = video

    def add_audio_to_video(self, output_path: str = None, overwrite: bool = True) -> str:
        """
        Adds the MP3 audio to the MP4 video.

        :param output_path: str, optional
            The path to save the output video with the added audio.
            If not provided and overwrite is True, the input video will be overwritten.
        :param overwrite: bool
            Whether to overwrite the original video file. Default is True.
        :return: str
            The path to the output video file.
        :raises ValueError:
            If no video file is provided.
        """
        if not self.video:
            raise ValueError("No video file provided to add audio to.")

        # Determine the output path
        if output_path is None:
            if not overwrite:
                raise ValueError("Output path must be specified if overwrite is False.")
            temp_output_path = f"{os.path.splitext(self.video.filepath)[0]}_temp.mp4"
        if output_path is not None:
            temp_output_path = f"{self.video.dir}/{output_path.replace('.mp4', '')}.mp4"
            overwrite = False

        try:
            # Use ffmpeg to combine audio and video
            command = [
                "ffmpeg",
                "-i", self.video.filepath,  # Input video
                "-i", self.audio.filepath,  # Input audio
                "-map", "0",  # Map all streams from the video
                "-map", "1:a",  # Map only the audio stream from the audio file
                "-c:v", "copy",  # Copy the video stream without re-encoding
                "-shortest",  # Ensure the output duration matches the shortest input
                temp_output_path
            ]
            subprocess.run(command, check=True)

            # If overwriting, replace the original file with the new one
            if overwrite:
                os.replace(temp_output_path, self.video.filepath)
                logger.info("Audio added to video successfully. Original file overwritten.")
                return self.video
            if not overwrite:
                logger.info(f"Audio added to video successfully. Output saved at: {output_path}")
                return MP4File(temp_output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add audio to video: {e}")
            raise

    def extract_random_section(self, duration: int, output_path: str = None, overwrite: bool = True) -> MP3File:
        """
        Extracts a random section from the MP3 file with the specified duration.

        :param duration: int
            The duration of the section to extract, in seconds.
        :param output_path: str, optional
            The path to save the extracted MP3 file.
            If not provided and overwrite is True, the input file will be overwritten.
        :param overwrite: bool
            Whether to overwrite the original MP3 file. Default is True.
        :return: MP3File
            The extracted MP3 file object.
        :raises ValueError:
            If the duration is longer than the MP3 file's total duration.
        """
        if not self.audio:
            raise ValueError("No MP3 file provided to extract a section from.")

        # Get the total duration of the MP3 file
        total_duration = self.audio.get_duration()
        if duration > total_duration:
            raise ValueError(
                f"Specified duration ({duration}s) is longer than the MP3 file's total duration ({total_duration}s).")

        # Determine the output path
        if output_path is None:
            if not overwrite:
                raise ValueError("Output path must be specified if overwrite is False.")
            temp_output_path = f"{os.path.splitext(self.audio.filepath)[0]}_temp.mp3"
        else:
            temp_output_path = output_path

        # Calculate a random start time
        start_time = random.randint(0, int(total_duration - duration))
        logger.info(f"Extracting a section from {start_time}s to {start_time + duration}s.")

        try:
            # Use ffmpeg to extract the section
            command = [
                "ffmpeg",
                "-i", self.audio.filepath,  # Input MP3 file
                "-ss", str(start_time),  # Start time
                "-t", str(duration),  # Duration
                "-c", "copy",  # Copy the audio stream without re-encoding
                temp_output_path
            ]
            subprocess.run(command, check=True)

            # If overwriting, replace the original file with the new one
            if overwrite:
                os.replace(temp_output_path, self.audio.filepath)
                logger.info("Extracted section saved and original file overwritten.")
                return self.audio
            else:
                logger.info(f"Extracted section saved to: {temp_output_path}")
                return MP3File(filepath=temp_output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract audio section: {e}")
            raise

    def mix_with_audio(self, other_audio: MP3File, output_path: str = None,
                       overwrite: bool = True, relative_volume: float = 1.0) -> MP3File:
        """
        Mixes the current audio with another MP3 file, adjusting their relative volumes.

        :param other_audio: MP3File
            The MP3 file to mix with the current audio.
        :param output_path: str, optional
            The path to save the mixed MP3 file.
            If not provided and overwrite is True, the input file will be overwritten.
        :param overwrite: bool
            Whether to overwrite the original MP3 file. Default is True.
        :param relative_volume: float
            The relative volume of the two audio files. Ranges from 0 to 2:
            - 1.0: Both files retain their original volume.
            - 2.0: The original file retains its volume, and the new file is muted.
            - 0.0: The new file retains its volume, and the original file is muted.
            Values in between represent a gradient between these extremes.
        :return: MP3File
            The mixed MP3 file object.
        :raises ValueError:
            If no other audio file is provided or if relative_volume is out of range.
        """
        if not self.audio:
            raise ValueError("No MP3 file provided to mix with.")
        if not other_audio:
            raise ValueError("No other MP3 file provided to mix with.")
        if not (0.0 <= relative_volume <= 2.0):
            raise ValueError("relative_volume must be between 0 and 2.")

        # Determine the output path
        if output_path is None:
            if not overwrite:
                raise ValueError("Output path must be specified if overwrite is False.")
            temp_output_path = f"{os.path.splitext(self.audio.filepath)[0]}_mix.mp3"
        if output_path is not None:
            temp_output_path = output_path
            overwrite = False

        # Calculate volume adjustments
        original_volume = 2.0 - relative_volume  # Volume for the original file
        new_volume = relative_volume  # Volume for the new file

        try:
            # Use ffmpeg to overlay the audio files with adjusted volumes
            command = [
                "ffmpeg",
                "-i", self.audio.filepath,  # Input first MP3 file
                "-i", other_audio.filepath,  # Input second MP3 file
                "-filter_complex", (f"[0:a]volume={original_volume}"
                                    f"[a0];[1:a]volume={new_volume}"
                                    "[a1];[a0][a1]amix=inputs=2:duration=longest:dropout_transition=2"),
                "-c:a", "libmp3lame",  # Encode to MP3
                temp_output_path
            ]
            subprocess.run(command, check=True)

            # If overwriting, replace the original file with the new one
            if overwrite:
                os.replace(temp_output_path, self.audio.filepath)
                logger.info("Audio files mixed successfully with relative volume. Original file overwritten.")
                return self.audio
            else:
                logger.info(
                    f"Audio files mixed successfully with relative volume. Output saved to: {temp_output_path}")
                return MP3File(filepath=temp_output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mix audio files: {e}")
            raise

    def add_audio_background(self, relative_volume: float = 0.8, overwrite: bool = True):
        """
        Adds a random audio background to the current MP3 file.
        :param relative_volume: float
            The relative volume of the background audio. Ranges from 0 to 2.
        :param overwrite: bool
            Whether to overwrite the original MP3 file. Default is True.
        :return: MP3File
            The mixed MP3 file object.
        """
        background_urls = ConfigManager().get(key='audio.background.urls')
        if not background_urls:
            logger.warning("No audio.background.urls provided in the configs.toml.")
            return self.audio
        background = download_random_from_youtube_urls(background_urls,
                                                       output_path=self.audio.dir + '/background.mp3')
        self.extract_random_section(duration=self.audio.get_duration())
        mixed_audio = self.mix_with_audio(other_audio=background,
                                          relative_volume=relative_volume,
                                          overwrite=overwrite)
        os.remove(background.filepath)
        return mixed_audio
