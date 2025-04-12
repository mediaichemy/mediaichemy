from mediaichemy.tools.filehandling import JPEGFile, MP4File, MP3File
from mediaichemy.content.short_video import ShortVideo, ShortVideoCreator
import pytest
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def standard_configs_assertions(videos):
    assert os.path.exists("tests/resources/temp_content/.state")
    assert os.path.exists("tests/resources/temp_content/en_speech_silence_background_random_part.mp3")
    assert os.path.exists("tests/resources/temp_content/en_speech_silence_background.mp3")
    assert os.path.exists("tests/resources/temp_content/en_speech_silence_mix.mp3")
    assert os.path.exists("tests/resources/temp_content/en_speech_silence.mp3")
    assert os.path.exists("tests/resources/temp_content/en_speech.mp3")
    assert os.path.exists("tests/resources/temp_content/en_video.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_speech_silence_mix.mp3")
    assert os.path.exists("tests/resources/temp_content/pt_speech_silence.mp3")
    assert os.path.exists("tests/resources/temp_content/pt_speech.mp3")
    assert os.path.exists("tests/resources/temp_content/pt_video.mp4")

    assert os.path.exists("tests/resources/temp_content/en_edited_video_2.mp4")
    assert os.path.exists("tests/resources/temp_content/en_edited_video_5.mp4")
    assert os.path.exists("tests/resources/temp_content/en_edited_video_8.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_boomerang_concat_trim_w_audio.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_boomerang_concat_trim.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_boomerang_concat.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_boomerang.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_edited_video_2.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_edited_video_5.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_edited_video_8.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_boomerang_concat_trim_w_audio.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_boomerang_concat_trim.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_boomerang_concat.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_boomerang.mp4")
    assert all([round(v.get_duration(), 1) == 15.7 for v in videos['en']])
    assert all([round(v.get_duration(), 1) == 19.3 for v in videos['pt']])


@pytest.mark.asyncio
async def test_short_video_creation_imagecreate_loopextend(copy_mock_content):

    content = ShortVideo("tests/resources/temp_content/idea.json")
    creator = ShortVideoCreator()
    image = await creator.run_image_creation(content)
    assert isinstance(image, JPEGFile)
    assert image.filepath == "tests/resources/temp_content/image.jpg"
    assert os.path.exists(image.filepath), f"Image file does not exist: {image.filepath}"

    video = await creator.run_video_creation(content, image, creation_method='static_image')
    assert isinstance(video, MP4File)
    assert video.filepath == "tests/resources/temp_content/image_video.mp4"
    assert os.path.exists(video.filepath), f"Video file does not exist: {video.filepath}"

    speechs = await creator.run_speech_creation(content)
    assert isinstance(speechs, dict)
    assert isinstance(speechs['en'], MP3File)
    assert speechs['en'].filepath == "tests/resources/temp_content/en_speech.mp3"
    assert os.path.exists(speechs['en'].filepath), f"Speech file does not exist: {speechs['en'].filepath}"

    assert isinstance(speechs, dict)
    assert isinstance(speechs['pt'], MP3File)
    assert speechs['pt'].filepath == "tests/resources/temp_content/pt_speech.mp3"
    assert os.path.exists(speechs['pt'].filepath), f"Speech file does not exist: {speechs['pt'].filepath}"

    videos = await creator.run_video_editing(content, video, speechs, extension_method='loop')
    assert isinstance(videos, dict)
    videos = await creator.run_subtitling(content, videos)
    standard_configs_assertions(videos)
    [v.copy_to(v.filepath.replace('tests/resources/temp_content/',
                                  'tests/resources/output/1_')) for v in videos['en']]
    [v.copy_to(v.filepath.replace('tests/resources/temp_content/',
                                  'tests/resources/output/1_')) for v in videos['pt']]

    content.purge()
    assert len([f for f in os.listdir(content.dir)
                if os.path.isfile(os.path.join(content.dir, f))]) == 11


@pytest.mark.asyncio
async def test_short_video_creation_aicreate_aiextend(copy_mock_content):
    content = ShortVideo("tests/resources/temp_content/idea.json")
    creator = ShortVideoCreator()
    image = await creator.run_image_creation(content)

    video = await creator.run_video_creation(content, image, creation_method='ai')
    assert isinstance(video, MP4File)
    assert video.filepath == "tests/resources/temp_content/video.mp4"
    assert os.path.exists(video.filepath), f"Video file does not exist: {video.filepath}"

    speechs = await creator.run_speech_creation(content)
    assert isinstance(speechs, dict)
    assert isinstance(speechs['en'], MP3File)
    assert speechs['en'].filepath == "tests/resources/temp_content/en_speech.mp3"
    assert os.path.exists(speechs['en'].filepath), f"Speech file does not exist: {speechs['en'].filepath}"

    videos = await creator.run_video_editing(content, video, speechs, extension_method='ai')
    assert isinstance(videos, dict)
    videos = await creator.run_subtitling(content, videos)
    assert os.path.exists("tests/resources/temp_content/en_video_ai_extension0_lastframe.jpg")
    assert os.path.exists("tests/resources/temp_content/en_video_ai_extension0.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_ai_extension1.mp4")
    assert os.path.exists("tests/resources/temp_content/en_edited_video_2.mp4")
    assert os.path.exists("tests/resources/temp_content/en_edited_video_5.mp4")
    assert os.path.exists("tests/resources/temp_content/en_edited_video_8.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_concat_trim_w_audio.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_concat_trim.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_concat.mp4")
    assert os.path.exists("tests/resources/temp_content/en_video_lastframe.jpg")
    assert os.path.exists("tests/resources/temp_content/en_video.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_ai_extension0_lastframe.jpg")
    assert os.path.exists("tests/resources/temp_content/pt_video_ai_extension0.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_ai_extension1.mp4")
    assert os.path.exists("tests/resources/temp_content/en_edited_video_2.mp4")
    assert os.path.exists("tests/resources/temp_content/en_edited_video_5.mp4")
    assert os.path.exists("tests/resources/temp_content/en_edited_video_8.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_concat_trim_w_audio.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_concat_trim.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_concat.mp4")
    assert os.path.exists("tests/resources/temp_content/pt_video_lastframe.jpg")
    assert os.path.exists("tests/resources/temp_content/pt_video.mp4")
    assert all([round(v.get_duration(), 1) == 15.7 for v in videos['en']])
    assert all([round(v.get_duration(), 1) == 19.3 for v in videos['pt']])
    [v.copy_to(v.filepath.replace('tests/resources/temp_content/',
                                  'tests/resources/output/2_')) for v in videos['en']]
    [v.copy_to(v.filepath.replace('tests/resources/temp_content/',
                                  'tests/resources/output/2_')) for v in videos['pt']]

    content.purge()
    assert len([f for f in os.listdir(content.dir)
                if os.path.isfile(os.path.join(content.dir, f))]) == 11


@pytest.mark.asyncio
async def test_short_video_create(copy_mock_content):
    content = ShortVideo("tests/resources/temp_content/idea.json")
    creator = ShortVideoCreator()

    videos = await creator.create(content)
    standard_configs_assertions(videos)
    [v.copy_to(v.filepath.replace('tests/resources/temp_content/',
                                  'tests/resources/output/3_')) for v in videos['en']]
    [v.copy_to(v.filepath.replace('tests/resources/temp_content/',
                                  'tests/resources/output/3_')) for v in videos['pt']]

    content.purge()
    assert len([f for f in os.listdir(content.dir)
                if os.path.isfile(os.path.join(content.dir, f))]) == 11
