import os
import subprocess
from math import ceil
import logging
from aichemy.tools.filehandling import JPEGFile, MP4File
from aichemy.ai.provider import ai_request

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

    async def extend_to_duration(self, target_duration: float,
                                 method: str = "loop",
                                 prompt: str = None) -> None:
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

        if method == "loop":
            self.apply_boomerang()
            # Calculate the number of repetitions needed to match or exceed the target duration
            n_repeat = ceil(target_duration / self.video.get_duration())
            # Repeat the video
            self.repeat_video(n=n_repeat)
        if method == "ai":
            await self.add_ai_videos(target_duration, prompt)

        # Trim the video to exactly match the target duration
        self.trim_video(duration=target_duration)

        return self.video.filepath

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
            return MP4File(boom_path)

    def repeat_video(self, n: int = 0, videos_to_add=None, overwrite: bool = True) -> str:
        """
        Repeats a video file n times or appends additional videos.

        :param n: int
            The number of times to repeat the video. Default is 0.
        :param videos_to_add: list
            List of additional video file paths to append to the original video. Default is None.
        :param overwrite: bool
            Whether to overwrite the original file with the repeated or appended video.
        :return: str
            The path to the repeated or appended video file.
        """
        if (n > 0 and videos_to_add) or (n == 0 and not videos_to_add):
            raise ValueError("You must provide either 'n' or 'videos_to_add', but not both.")

        video_path = self.video.filepath
        video_dir = self.video.dir
        video_name, video_ext = os.path.splitext(os.path.basename(video_path))
        output_path = os.path.join(video_dir, f"{n}repeated{video_ext}" if n > 0 else f"appended{video_ext}")

        # Create a temporary text file listing the videos to concatenate
        concat_list_path = os.path.join(video_dir, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            if n > 0:
                for _ in range(n):
                    f.write(f"file '{os.path.abspath(video_path)}'\n")
            elif videos_to_add:
                f.write(f"file '{os.path.abspath(video_path)}'\n")
                for video in videos_to_add:
                    f.write(f"file '{os.path.abspath(video.filepath)}'\n")

        # Use ffmpeg to concatenate the videos
        subprocess.run(
            [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',
                output_path
            ],
            check=True
        )

        # Clean up the temporary file
        os.remove(concat_list_path)

        if overwrite:
            os.remove(video_path)
            os.rename(output_path, video_path)
            return video_path
        else:
            return MP4File(output_path)

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
            return MP4File(cut_path)

    def extract_last_frame(self, video=None) -> str:
        """
        Extracts the last frame of the video and saves it as a JPEG file.

        :return: str
            The path to the saved JPEG file.
        """
        if video is None:
            video = self.video
        last_frame_path = os.path.join(video.dir, "last_frame.jpg")
        try:
            # Use ffmpeg to extract the last frame based on time
            subprocess.run(
                [
                    "ffmpeg", "-y", "-sseof", "-3", "-i", video.filepath,
                    "-vsync", "0", "-q:v", "0", "-update", "true", last_frame_path
                ],
                check=True
            )
            return JPEGFile(last_frame_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract the last frame: {e}")
            raise

    async def add_ai_videos(self, target_duration, prompt=""):
        if prompt == "":
            logger.warning("No prompt provided for AI video generation.")
        current_video = self.video
        videos_to_add = []
        while sum([v.get_duration() for v in videos_to_add]) < target_duration:
            n = len(videos_to_add)
            lastframe = self.extract_last_frame(current_video)
            video_continue = await ai_request(media="video",
                                              prompt=prompt,
                                              img_filepath=lastframe.filepath,
                                              output_path=self.video.dir + f'/video_continue{n}.mp4')
            videos_to_add.append(video_continue)
            current_video = video_continue
        extended_video = self.repeat_video(videos_to_add=videos_to_add)
        return extended_video
