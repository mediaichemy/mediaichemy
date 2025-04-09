import os
import subprocess
import re
import logging
from mediaichemy.tools.filehandling import MP4File
from mediaichemy.configs import ConfigManager
import pysubs2

logger = logging.getLogger(__name__)


subtitle_alignments = {
                "bottom_left": pysubs2.Alignment.BOTTOM_LEFT,
                "bottom_center": pysubs2.Alignment.BOTTOM_CENTER,
                "bottom_right": pysubs2.Alignment.BOTTOM_RIGHT,
                "middle_left": pysubs2.Alignment.MIDDLE_LEFT,
                "middle_center": pysubs2.Alignment.MIDDLE_CENTER,
                "middle_right": pysubs2.Alignment.MIDDLE_RIGHT,
                "top_left": pysubs2.Alignment.TOP_LEFT,
                "top_center": pysubs2.Alignment.TOP_CENTER,
                "top_right": pysubs2.Alignment.TOP_RIGHT,
            }


class Subtitles:
    """
    Handles text editing operations, including generating and adding subtitles to a video.

    :param text: The input text to be processed.
    :type text: str
    :param video: The video file to which subtitles will be added.
    :type video: MP4File, optional
    """
    def __init__(self, text: str, video: MP4File = None):
        if not text:
            raise ValueError("Text must be provided.")
        self.text = text
        self.video = video

    # @log
    def add_text_to_video(self, output_path: str = None) -> MP4File:
        """
        Generates subtitles from the text and adds them to the video.

        :param output_path: The path to save the video with subtitles.
        If not provided, the input file will be overwritten.
        :type output_path: str, optional
        :return: The video file with subtitles added.
        :rtype: MP4File
        :raises ValueError: If no video file is provided.
        """
        if not self.video:
            raise ValueError("No video file provided to add subtitles to.")

        # Get the video duration
        print(self.video)
        duration = self.video.get_duration() - ConfigManager().get(key='audio.silence.duration')

        # Generate subtitles from the text
        subtitles = self.generate_subtitles(duration=duration)

        # Add subtitles to the video
        subtitled_videos = self.add_subtitles(subtitles=subtitles)

        logger.info("Text successfully added to the video as subtitles.")
        return subtitled_videos

    # @log
    def generate_subtitles(self, duration: float) -> list[dict[str, float | str]]:
        """
        Generates subtitles by dividing the text into sentences and distributing them over the video duration.

        :param duration: The total duration of the video in seconds.
        :type duration: float
        :return: A list of subtitle dictionaries with start, end, and text keys.
        :rtype: list[dict[str, float | str]]
        :raises ValueError: If the duration is less than or equal to 0.
        """
        if duration <= 0:
            raise ValueError("Duration must be greater than 0.")

        letter_duration = duration / len(self.text)

        sentences = self._punctuation_split(self.text)
        subtitles = []
        start = 0

        for sentence in sentences:
            end = start + letter_duration * len(sentence)
            subtitles.append({"start": start, "end": end, "text": sentence})
            start = end

        logger.info(f"Generated {len(subtitles)} subtitles.")
        return subtitles

    # @log
    def add_subtitles(self, subtitles: list[dict[str, float | str]]) -> MP4File:
        """
        Adds subtitles to the video.

        :param subtitles: A list of subtitle dictionaries with start, end, and text keys.
        :type subtitles: list[dict[str, float | str]]
        :param output_path: The path to save the video with subtitles.
        If not provided, the input file will be overwritten.
        :type output_path: str, optional
        :return: The video file with subtitles added.
        :rtype: MP4File
        :raises ValueError: If no video file or subtitles are provided.
        """
        if not self.video:
            raise ValueError("No video file provided to add subtitles to.")
        if not subtitles:
            raise ValueError("No subtitles provided to add to the video.")

        # Create a temporary .ass subtitle file
        subtitle_path = f"{os.path.splitext(self.video.filepath)[0]}.ass"
        sub_paths = self._create_ass_subtitles(subtitles, subtitle_path)
        subtitled_videos = []
        for subtitle_path in sub_paths:
            temp_output_path = subtitle_path.replace(".ass", ".mp4")
            try:
                # Use ffmpeg to add subtitles to the video
                command = [
                    "ffmpeg",
                    "-i", self.video.filepath,  # Input video
                    "-vf", f"subtitles={subtitle_path}",  # Add subtitles
                    "-c:a", "copy",  # Copy the audio stream without re-encoding
                    temp_output_path
                ]
                subprocess.run(command, check=True)
                logger.info(f"Subtitles added successfully. Output saved to: {temp_output_path}")
                subtitled_videos.append(MP4File(filepath=temp_output_path))
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to add subtitles to video: {e}")
                raise
            finally:
                # Clean up the temporary subtitle file
                if os.path.exists(subtitle_path):
                    os.remove(subtitle_path)
        return subtitled_videos

    # @log
    def save_subtitles_as_ass(self, output_path: str) -> list[str]:
        """
        Saves the generated subtitles as .ass files.

        :param output_path: The base path to save the .ass subtitle files.
        :type output_path: str
        :return: A list of paths to the saved .ass files.
        :rtype: list[str]
        :raises ValueError: If no text is provided or the output path is not specified.
        """
        if not self.text:
            raise ValueError("No text provided to generate subtitles.")
        if not output_path:
            raise ValueError("Output path must be specified.")

        # Generate subtitles for the full text
        duration = self.video.get_duration() - ConfigManager().get(key='audio.silence.duration')
        subtitles = self.generate_subtitles(duration)
        sub_paths = self._create_ass_subtitles(subtitles, output_path)
        logger.info(f"Subtitles saved as .ass file at: {output_path}")
        return sub_paths

    # @log
    @staticmethod
    def _punctuation_split(text: str) -> list[str]:
        """
        Splits a text into sentences based on punctuation.

        :param text: The input text to split.
        :type text: str
        :return: A list of sentences.
        :rtype: list[str]
        """
        sentences = re.split(r'(?<=[.,!?]) +', text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    # @log
    @staticmethod
    def _load_subtitle_configs() -> dict[int, pysubs2.SSAFile]:
        """
        Loads subtitle configuration settings from the configs.toml file and applies them to pysubs2.SSAFile objects.

        :return: A dictionary mapping alignments to configured SSAFile objects.
        :rtype: dict[int, pysubs2.SSAFile]
        """
        configs = ConfigManager().get(table='subtitles')
        # Fetch alignment from configs and map it using the subtitle_alignments dictionary
        alignment_list = configs.get('alignment')
        alignments = [subtitle_alignments[alignment_str] for alignment_str in alignment_list]
        subs = {}
        for alignment in alignments:
            # Create and configure the SSAFile object
            sub = pysubs2.SSAFile()
            sub.styles["Default"].fontname = configs['fontname']
            sub.styles["Default"].fontsize = configs['fontsize']
            sub.styles["Default"].primarycolor = pysubs2.Color(*map(int, configs['primarycolor'].split(',')))
            sub.styles["Default"].secondarycolor = pysubs2.Color(*map(int, configs['secondarycolor'].split(',')))
            sub.styles["Default"].outlinecolor = pysubs2.Color(*map(int, configs['outlinecolor'].split(',')))
            sub.styles["Default"].backcolor = pysubs2.Color(*map(int, configs['backcolor'].split(',')))
            sub.styles["Default"].bold = configs['bold']
            sub.styles["Default"].italic = configs['italic']
            sub.styles["Default"].underline = configs['underline']
            sub.styles["Default"].strikeout = configs['strikeout']
            sub.styles["Default"].scalex = configs['scalex']
            sub.styles["Default"].scaley = configs['scaley']
            sub.styles["Default"].spacing = configs['spacing']
            sub.styles["Default"].angle = configs['angle']
            sub.styles["Default"].borderstyle = configs['borderstyle']
            sub.styles["Default"].outline = configs['outline']
            sub.styles["Default"].shadow = configs['shadow']
            sub.styles["Default"].alignment = alignment
            sub.styles["Default"].margin_l = configs['margin_l']
            sub.styles["Default"].margin_r = configs['margin_r']
            sub.styles["Default"].margin_v = configs['margin_v']
            subs[alignment] = sub
        return subs

    # @log
    @staticmethod
    def _create_ass_subtitles(subtitles: list[dict[str, float | str]], output_path: str) -> list[str]:
        """
        Creates .ass subtitle files from a list of subtitles.

        :param subtitles: A list of subtitle dictionaries with start, end, and text keys.
        :type subtitles: list[dict[str, float | str]]
        :param output_path: The base path to save the .ass subtitle files.
        :type output_path: str
        :return: A list of paths to the created .ass files.
        :rtype: list[str]
        """
        # Load and configure the SSAFile object
        subs = Subtitles._load_subtitle_configs()
        print(subs)
        sub_paths = []
        for alignment in subs.keys():
            # Add subtitles to the SSAFile
            sub = subs[alignment]
            for subtitle in subtitles:
                sub.append(
                    pysubs2.SSAEvent(
                        start=subtitle["start"] * 1000,
                        end=subtitle["end"] * 1000,
                        text=subtitle["text"]
                    )
                )
            print(f'Alignment is: {alignment}')
            print(f'Subs are : {subs}')
            print(f'Sub is : {sub}')
            # Save the .ass file
            sub_filepath = output_path.replace(".ass", f'_{alignment}.ass')
            sub.save(sub_filepath)
            logger.info(f"Subtitle file created at: {sub_filepath}")
            sub_paths.append(sub_filepath)
        return sub_paths
