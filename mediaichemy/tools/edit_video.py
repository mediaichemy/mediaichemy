import os
import subprocess
from math import ceil
import logging
from mediaichemy.tools.filehandling import JPEGFile, MP4File
from mediaichemy.tools.utils import log
from mediaichemy.ai.request import ai_request

logger = logging.getLogger(__name__)


@log
def add_audio_to_video(video, audio) -> MP4File:
    if not video:
        raise ValueError("No video file provided to add audio to.")

    video_w_audio_path = video.filepath.replace(".mp4", "_w_audio.mp4")
    # Use ffmpeg to combine audio and video
    command = [
        "ffmpeg",
        "-i", video.filepath,  # Input video
        "-i", audio.filepath,  # Input audio
        "-map", "0",  # Map all streams from the video
        "-map", "1:a",  # Map only the audio stream from the audio file
        "-c:v", "copy",  # Copy the video stream without re-encoding
        "-shortest",  # Ensure the output duration matches the shortest input
        video_w_audio_path
    ]
    subprocess.run(command, check=True)
    return MP4File(video_w_audio_path)


@log
def apply_boomerang(video) -> MP4File:
    boom_path = video.filepath.replace(".mp4", "_boomerang.mp4")
    subprocess.run(
        [
            'ffmpeg',
            '-ss', '0',
            '-an',
            '-i', video.filepath,
            '-y',
            '-filter_complex', "[0]split[b][c];[c]reverse[r];[b][r]concat",
            boom_path
        ],
        check=True
    )
    return MP4File(boom_path)


@log
def concat_videos(video, n: int = 0, videos_to_add=None) -> MP4File:
    combined_path = video.filepath.replace(".mp4", "_concat.mp4")
    if (n > 0 and videos_to_add) or (n == 0 and not videos_to_add):
        raise ValueError("You must provide either 'n' or 'videos_to_add', but not both.")
    concat_list_path = os.path.join(video.dir, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        if n > 0:
            for _ in range(n):
                f.write(f"file '{os.path.abspath(video.filepath)}'\n")
        elif videos_to_add:
            f.write(f"file '{os.path.abspath(video.filepath)}'\n")
            for video in videos_to_add:
                f.write(f"file '{os.path.abspath(video.filepath)}'\n")
    subprocess.run(
        [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list_path,
            '-c', 'copy',
            combined_path
        ],
        check=True
    )
    os.remove(concat_list_path)
    return MP4File(combined_path)


@log
def trim_video(video, duration: int) -> str:
    if duration <= 0:
        raise ValueError("The length must be greater than 0 seconds.")
    trim_path = video.filepath.replace(".mp4", "_trim.mp4")

    subprocess.run(
        [
            'ffmpeg',
            '-i', video.filepath,
            '-t', str(duration),
            '-c', 'copy',
            '-y',
            trim_path
        ],
        check=True
    )
    return MP4File(trim_path)


@log
def extract_last_frame(video) -> JPEGFile:
    last_frame_path = video.filepath.replace(".mp4", "_lastframe.jpg")
    try:
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


@log
async def extend_to_duration(video, target_duration: float,
                             method: str = "loop",
                             prompt: str = None) -> None:
    if target_duration <= 0:
        raise ValueError("Target duration must be greater than 0 seconds.")

    if method == "loop":
        boom = apply_boomerang(video)
        # Calculate the number of repetitions needed to match or exceed the target duration
        n_repeat = ceil(target_duration / boom.get_duration())
        # Repeat the video
        if n_repeat > 1:
            extended_video = concat_videos(boom, n=n_repeat)
        if n_repeat <= 1:
            extended_video = boom
    if method == "ai":
        extended_video = await add_ai_videos(video, target_duration, prompt)

    # Trim the video to exactly match the target duration
    trimd = trim_video(extended_video, duration=target_duration)

    return trimd


@log
async def add_ai_videos(video, target_duration, prompt=""):
    if prompt == "":
        logger.warning("No prompt provided for AI video generation.")
    current_video = video
    videos_to_add = []
    while sum([v.get_duration() for v in [video] + videos_to_add]) < target_duration:
        n = len(videos_to_add)
        n_path = video.filepath.replace(".mp4", f"_ai_extension{n}.mp4")
        lastframe = extract_last_frame(current_video)
        video_continue = await ai_request(media="video",
                                          prompt=prompt,
                                          img_filepath=lastframe.filepath,
                                          output_path=n_path)
        videos_to_add.append(video_continue)
        current_video = video_continue
    if len(videos_to_add) > 0:
        extended_video = concat_videos(video, videos_to_add=videos_to_add)
    if len(videos_to_add) == 0:
        extended_video = video
    return extended_video


@log
def create_video_from_image(image: JPEGFile, duration: int) -> MP4File:
    if duration <= 0:
        raise ValueError("Duration must be greater than 0 seconds.")

    video_path = image.filepath.replace(".jpg", "_video.mp4")

    # Use ffmpeg to create a video from the image
    command = [
        "ffmpeg",
        "-loop", "1",  # Loop the image
        "-i", image.filepath,  # Input image
        "-c:v", "libx264",  # Use H.264 codec
        "-t", str(duration),  # Set the duration
        "-pix_fmt", "yuv420p",  # Ensure compatibility with most players
        "-y",  # Overwrite output file if it exists
        video_path
    ]
    subprocess.run(command, check=True)

    return MP4File(video_path)
