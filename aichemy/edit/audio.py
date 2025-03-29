import os
import subprocess
from aichemy.tools.filehandling import MP3File, MP4File
import logging

logger = logging.getLogger(__name__)


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
