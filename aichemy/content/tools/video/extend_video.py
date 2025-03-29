import os
import subprocess
from math import ceil
from aichemy.filehandling import MP4File
import logging

logger = logging.getLogger(__name__)


class ExtendVideo:
    """
    A class to extend a video to a specified duration by applying effects,
    repeating, and trimming.
    """

    def __init__(self, video: MP4File):
        """
        Initializes the ExtendVideo class.

        :param video: MP4File
            The video file object.
        """
        self.video = video

    def extend_to_duration(self, target_duration: float, apply_boomerang_effect: bool = True) -> None:
        """
        Extends a video to match a specified target duration by optionally applying
        a boomerang effect, repeating the video, and trimming it to the target duration.

        :param target_duration: float
            The target duration in seconds to which the video should be extended.
        :param apply_boomerang_effect: bool
            Whether to apply the boomerang effect to the video. Default is True.
        """
        if target_duration <= 0:
            raise ValueError("Target duration must be greater than 0 seconds.")

        # Optionally apply the boomerang effect
        if apply_boomerang_effect:
            self.apply_boomerang()

        # Calculate the number of repetitions needed to match or exceed the target duration
        n_repeat = ceil(target_duration / self.video.get_duration())

        # Repeat the video
        self.repeat_video(n=n_repeat)

        # Trim the video to exactly match the target duration
        self.trim_video(duration=target_duration)

    def apply_boomerang(self, overwrite: bool = True) -> str:
        """
        Applies a boomerang effect to the video.

        :param overwrite: bool
            Whether to overwrite the original file with the boomerang effect.
        :return: str
            The path to the boomerang video file.
        """
        video_path = self.video.filepath
        video_dir = self.video.dir
        boom_path = os.path.join(video_dir, 'boomerang.mp4')

        # Run the ffmpeg command to apply the boomerang effect
        subprocess.run(
            [
                'ffmpeg',
                '-ss', '0',
                '-an',
                '-i', video_path,
                '-y',
                '-filter_complex', "[0]split[b][c];[c]reverse[r];[b][r]concat",
                boom_path
            ],
            check=True
        )

        if overwrite:
            os.remove(video_path)
            os.rename(boom_path, video_path)
            return video_path
        else:
            return boom_path

    def repeat_video(self, n: int, overwrite: bool = True) -> str:
        """
        Repeats a video file n times.

        :param n: int
            The number of times to repeat the video.
        :param overwrite: bool
            Whether to overwrite the original file with the repeated video.
        :return: str
            The path to the repeated video file.
        """
        if n < 1:
            raise ValueError("The number of repetitions (n) must be at least 1.")

        video_path = self.video.filepath
        video_dir = self.video.dir
        video_name, video_ext = os.path.splitext(os.path.basename(video_path))
        repeated_path = os.path.join(video_dir, f"{n}repeated{video_ext}")

        # Create a temporary text file listing the input video n times
        concat_list_path = os.path.join(video_dir, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for _ in range(n):
                f.write(f"file '{os.path.abspath(video_path)}'\n")

        # Use ffmpeg to concatenate the video n times
        subprocess.run(
            [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',
                repeated_path
            ],
            check=True
        )

        # Clean up the temporary file
        os.remove(concat_list_path)

        if overwrite:
            os.remove(video_path)
            os.rename(repeated_path, video_path)
            return video_path
        else:
            return repeated_path

    def trim_video(self, duration: int, overwrite: bool = True) -> str:
        """
        Trims a video to a specified length in seconds.

        :param duration: int
            The length in seconds to which the video should be trimmed.
        :param overwrite: bool
            Whether to overwrite the original file with the trimmed video.
        :return: str
            The path to the trimmed video file.
        """
        if duration <= 0:
            raise ValueError("The length must be greater than 0 seconds.")

        video_path = self.video.filepath
        video_dir = self.video.dir
        video_name, video_ext = os.path.splitext(os.path.basename(video_path))
        cut_path = os.path.join(video_dir, f"cut_{duration}s{video_ext}")

        # Use ffmpeg to cut the video to the specified length
        subprocess.run(
            [
                'ffmpeg',
                '-i', video_path,
                '-t', str(duration),
                '-c', 'copy',
                '-y',  # Overwrite the output file if it exists
                cut_path
            ],
            check=True
        )

        if overwrite:
            os.remove(video_path)
            os.rename(cut_path, video_path)
            return video_path
        else:
            return cut_path

    def extract_last_frame(self) -> str:
        """
        Extracts the last frame of the video and saves it as a JPEG file.

        :return: str
            The path to the saved JPEG file.
        """
        last_frame_path = os.path.join(self.video.dir, "last_frame.jpg")
        try:
            # Use ffmpeg to extract the last frame based on time
            subprocess.run(
                [
                    "ffmpeg", "-y", "-sseof", "-3", "-i", self.video.filepath,
                    "-vsync", "0", "-q:v", "0", "-update", "true", last_frame_path
                ],
                check=True
            )
            return last_frame_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract the last frame: {e}")
            raise
