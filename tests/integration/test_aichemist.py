from mediaichemy import mediaAIChemist
import pytest
from tests.helpers import compare_video_files


@pytest.mark.asyncio
async def test_short_video(copy_mock_short_video, temporary_configs_file):
    raw_toml = """
    [audio.background]
    urls = []
    """

    # Create the temporary configs.toml file
    temporary_configs_file(raw_toml)
    aichemist = mediaAIChemist(content_type="short_video")

    # Initialize content based on the first idea
    content = aichemist.initialize_content("tests/resources/temp_content/idea.json")
    assert content is not None, "Content should be initialized"

    # Create content
    media = await aichemist.create_content(content)
    assert media is not None, "Media should be created"

    content.purge()
    for video in content.list_files('mp4'):
        expected_video = video.replace('tests/resources/temp_content/',
                                       'tests/resources/expected/short_video/')
        assert compare_video_files([video, expected_video])


@pytest.mark.asyncio
async def test_music_video(copy_mock_music_video, temporary_configs_file):
    raw_toml = """
    [audio.background]
    urls = []
    """

    # Create the temporary configs.toml file
    temporary_configs_file(raw_toml)
    aichemist = mediaAIChemist(content_type="music_video")

    # Initialize content based on the first idea
    content = aichemist.initialize_content("tests/resources/temp_content/idea.json")
    assert content is not None, "Content should be initialized"

    # Create content
    media = await aichemist.create_content(content)
    assert media is not None, "Media should be created"

    content.purge()
    for video in content.list_files('mp4'):
        expected_video = video.replace('tests/resources/temp_content/',
                                       'tests/resources/expected/music_video/')
        assert compare_video_files([video, expected_video])
