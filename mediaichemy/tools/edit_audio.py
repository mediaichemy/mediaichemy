import subprocess
from mediaichemy.tools.filehandling import MP3File
import logging
import random
from mediaichemy.configs import ConfigManager
from mediaichemy.tools.utils import log

logger = logging.getLogger(__name__)


@log
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
        result = subprocess.run(command, check=True,
                                capture_output=True,
                                text=True
                                )
        if "ERROR" in result.stderr:
            logger.error("Error downloading background music")
            logger.error("If you are using a VPN consider disabling it")
            logger.error(result.stderr)
        logger.info(f"Audio downloaded successfully to: {output_path}")

        # Return the MP3File object
        return MP3File(output_path)

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download audio from URL {selected_url}: {e}")
        raise


# @log
def add_silence(audio, duration: int = None) -> MP3File:
    silence_path = audio.filepath.replace(".mp3", "_silence.mp3")

    if duration is None:
        duration = ConfigManager().get('audio.silence.duration')
    if not audio:
        raise ValueError("No MP3 file provided to add silence to.")
    if duration <= 0:
        raise ValueError("Duration of silence must be greater than 0.")

    try:
        # Use ffmpeg to add silence to the end of the audio file
        command = [
            "ffmpeg",
            "-i", audio.filepath,  # Input MP3 file
            "-f", "lavfi",  # Use lavfi to generate silence
            "-t", str(duration),  # Duration of silence
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",  # Generate silence
            "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",  # Concatenate audio and silence
            "-map", "[out]",  # Map the output
            silence_path
        ]
        subprocess.run(command, check=True)
        return MP3File(silence_path)

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add silence to audio file: {e}")
        raise


@log
def extract_random_section(audio, duration: int) -> MP3File:
    section_path = audio.filepath.replace(".mp3", "_random_part.mp3")

    # Get the total duration of the MP3 file
    total_duration = audio.get_duration()
    if duration > total_duration:
        raise ValueError(
            f"Specified duration ({duration}s) is longer than the MP3 file's total duration ({total_duration}s).")

    # Calculate a random start time
    start_time = random.randint(0, int(total_duration - duration))
    logger.info(f"Extracting a section from {start_time}s to {start_time + duration}s.")

    try:
        # Use ffmpeg to extract the section
        command = [
            "ffmpeg",
            "-i", audio.filepath,  # Input MP3 file
            "-ss", str(start_time),  # Start time
            "-t", str(duration),  # Duration
            "-c", "copy",  # Copy the audio stream without re-encoding
            section_path
        ]
        subprocess.run(command, check=True)

        return MP3File(section_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to extract audio section: {e}")
        raise


@log
def mix_audio(audio: MP3File, audio2: MP3File, relative_volume: float = 1.0) -> MP3File:
    mix_path = audio.filepath.replace(".mp3", "_mix.mp3")

    if not audio:
        raise ValueError("No MP3 file provided to mix with.")
    if not audio2:
        raise ValueError("No other MP3 file provided to mix with.")
    if not (0.0 <= relative_volume <= 2.0):
        raise ValueError("relative_volume must be between 0 and 2.")

    # Calculate volume adjustments
    original_volume = 2.0 - relative_volume  # Volume for the original file
    new_volume = relative_volume  # Volume for the new file

    try:
        # Use ffmpeg to overlay the audio files with adjusted volumes
        command = [
            "ffmpeg",
            "-i", audio.filepath,  # Input first MP3 file
            "-i", audio2.filepath,  # Input second MP3 file
            "-filter_complex", (f"[0:a]volume={original_volume}"
                                f"[a0];[1:a]volume={new_volume}"
                                "[a1];[a0][a1]amix=inputs=2:duration=longest:dropout_transition=2"),
            "-c:a", "libmp3lame",  # Encode to MP3
            mix_path
        ]
        subprocess.run(command, check=True)
        logger.info("Audio files mixed successfully. Original file overwritten.")
        return MP3File(mix_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to mix audio files: {e}")
        raise


@log
def add_audio_background(audio, background: MP3File = None) -> MP3File:
    background_path = audio.filepath.replace(".mp3", "_background.mp3")

    configs = ConfigManager().get(table='audio.background')
    background_urls = configs.get('urls')
    relative_volume = configs.get('relative_volume')

    if not background and not background_urls:
        logger.warning("No background audio provided or available. Returning original audio.")
        return audio
    if not background:
        if background_urls:
            background = download_random_from_youtube_urls(background_urls,
                                                           output_path=background_path)
    background_section = extract_random_section(background, duration=audio.get_duration())
    mixed_audio = mix_audio(audio=audio,
                            audio2=background_section, relative_volume=relative_volume)

    return mixed_audio
