import pysubs2
import subprocess

def create_ass_subtitles(subtitles: list, output_path: str):
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

# Example usage
video_path = "input_video.mp4"
output_video_path = "output_video.mp4"
subtitle_path = "subtitles.ass"

subtitles = [
    {"start": 0, "end": 5, "text": "Hello, world!"},
    {"start": 6, "end": 10, "text": "This is a subtitle example."}
]

create_ass_subtitles(subtitles, subtitle_path)
add_subtitles_ffmpeg(video_path, subtitle_path, output_video_path)