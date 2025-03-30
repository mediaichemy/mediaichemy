import pysubs2
import subprocess
import re


def punctuation_split(text: str) -> list[str]:
    """
    Divide a text into multiple sentences based on punctuation.

    :param text: The input text to be divided.
    :type text: str

    :return: List of sentences divided by punctuation.
    :rtype: list[str]
    """
    sentences = re.split(r'(?<=[.,!?]) +', text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def generate_subtitles(text, duration):
    letter_duration = duration / len(text)
    sentences = punctuation_split(text)
    sentences = [{'text': sentence} for sentence in sentences]
    start = 0
    for sentence in sentences:
        sentence['start'] = start
        sentence['end'] = start + letter_duration * len(sentence['text'])
        start = sentence['end']
    return sentences


def create_ass_subtitles(subtitles: list, output_path: str):
    """
    
    """
    subs = pysubs2.SSAFile()
    subs.styles["Default"].fontname = "Arial"
    subs.styles["Default"].fontsize = 24
    subs.styles["Default"].alignment = pysubs2.Alignment.BOTTOM_CENTER
    subs.styles["Default"].margin_v = 20

    for subtitle in subtitles:
        subs.append(
            pysubs2.SSAEvent(
                start=subtitle["start"] * 1000,
                end=subtitle["end"] * 1000,
                text=subtitle["text"]
            )
        )

    subs.save(output_path)


def add_subtitles_ffmpeg(video_path: str, subtitle_path: str, output_path: str):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={subtitle_path}",
        "-c:a", "copy",
        output_path
    ]
    subprocess.run(command, check=True)
