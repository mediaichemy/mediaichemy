import pytest
from mediaichemy.ai.request import ai_request
from mediaichemy.tools.filehandling import MP4File, JPEGFile, MP3File


@pytest.mark.asyncio
async def test_ai_request_text(mock_providers, copy_mock_content):
    """
    Test ai_request for text generation using OpenRouterProvider.
    """

    with open('tests/resources/mocks/short_video/idea.json', 'r') as f:
        mock_idea = f.read()

    result = await ai_request(media="text", prompt="Generate some text")
    mock_providers["mock_openrouter"].assert_called_once_with("Generate some text",
                                                              output_path=None)
    assert isinstance(result, str)
    assert result == mock_idea


@pytest.mark.asyncio
async def test_ai_request_image(mock_providers, copy_mock_content):
    """
    Test ai_request for image generation using RunwareProvider.
    """
    result = await ai_request(media="image", prompt="Generate an image",
                              output_path="tests/resources/temp_content/image.jpg")
    mock_providers["mock_runware"].assert_called_once_with("Generate an image",
                                                           output_path="tests/resources/temp_content/image.jpg")
    assert isinstance(result, JPEGFile)
    assert result.filepath == "tests/resources/temp_content/image.jpg"


@pytest.mark.asyncio
async def test_ai_request_video(mock_providers, copy_mock_content):
    """
    Test ai_request for video generation using MinimaxProvider.
    """
    result = await ai_request(media="video", prompt="Generate a video",
                              output_path="tests/resources/temp_content/video.mp4",
                              input_path="tests/resources/temp_content/image.jpg")
    mock_providers["mock_minimax"].assert_called_once_with("Generate a video",
                                                           output_path="tests/resources/temp_content/video.mp4",
                                                           input_path="tests/resources/temp_content/image.jpg")
    assert isinstance(result, MP4File)
    assert result.filepath == "tests/resources/temp_content/video.mp4"


@pytest.mark.asyncio
async def test_ai_request_speech(mock_providers, copy_mock_content):
    """
    Test ai_request for speech generation using ElevenLabsProvider.
    """
    result = await ai_request(media="speech", prompt="Generate speech",
                              output_path="tests/resources/temp_content/speech.mp3")
    mock_providers["mock_elevenlabs"].assert_called_once_with(
        "Generate speech",
        output_path="tests/resources/temp_content/speech.mp3")
    assert isinstance(result, MP3File)
    assert result.filepath == "tests/resources/temp_content/speech.mp3"
