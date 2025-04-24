import pytest
import os
import shutil
from unittest.mock import patch, AsyncMock


with open('tests/resources/mocks/short_video/idea.json', 'r') as f:
    mock_idea = f.read()


@pytest.fixture(scope="function", autouse=True)
def set_env_variables():
    """
    Set environment variables for the entire test function.
    """
    env_vars = {
        "MINIMAX_API_KEY": "mocked_minimax_api_key",
        "RUNWARE_API_KEY": "mocked_runware_api_key",
        "OPENROUTER_API_KEY": "mocked_openrouter_api_key",
        "ELEVENLABS_API_KEY": "mocked_elevenlabs_api_key",
    }
    for key, value in env_vars.items():
        os.environ[key] = value


@pytest.fixture(scope="function")
def copy_mock_short_video():
    """
    Copy all content from 'tests/resources/mocks/short_video' to 'tests/resources/temp_content'.
    """
    source_dir = 'tests/resources/mocks/short_video'
    target_dir = 'tests/resources/temp_content'

    # Remove the target directory if it already exists to ensure a clean copy
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    # Copy the source directory to the target directory
    shutil.copytree(source_dir, target_dir)
    print(f"Copied content from {source_dir} to {target_dir}")

    # Yield to allow tests to run
    yield

    # Cleanup after tests are done
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
        print(f"Cleaned up temporary content directory: {target_dir}")


@pytest.fixture(scope="function")
def copy_mock_music_video():
    """
    Copy all content from 'tests/resources/mocks/music_video' to 'tests/resources/temp_content'.
    """
    source_dir = 'tests/resources/mocks/music_video'
    target_dir = 'tests/resources/temp_content'

    # Remove the target directory if it already exists to ensure a clean copy
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    # Copy the source directory to the target directory
    shutil.copytree(source_dir, target_dir)
    print(f"Copied content from {source_dir} to {target_dir}")

    # Yield to allow tests to run
    yield

    # Cleanup after tests are done
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
        print(f"Cleaned up temporary content directory: {target_dir}")


@pytest.fixture(scope="function", autouse=True)
def mock_providers():
    """
    Mock all provider request methods for the entire test function.
    """
    mock_dir = 'tests/resources/temp_content'
    # Mock OpenRouterProvider.request
    mock_openrouter_request = AsyncMock(return_value=mock_idea)

    # Mock RunwareProvider.request
    mock_runware_request = AsyncMock(return_value=mock_dir + "/image.jpg")

    # Mock MinimaxProvider.request
    mock_minimax_request = AsyncMock(return_value=mock_dir + "/test_video.mp4")

    # Mock ElevenLabsProvider.request
    mock_elevenlabs_request = AsyncMock(return_value=mock_dir + "/test_en_speech.mp3")

    # Patch all providers
    with patch("mediaichemy.ai.providers.openrouter.OpenRouterProvider.request",
               mock_openrouter_request) as mock_openrouter, \
         patch("mediaichemy.ai.providers.runware.RunwareProvider.request",
               mock_runware_request) as mock_runware, \
         patch("mediaichemy.ai.providers.minimax.MinimaxProvider.request",
               mock_minimax_request) as mock_minimax, \
         patch("mediaichemy.ai.providers.elevenlabs.ElevenLabsProvider.request",
               mock_elevenlabs_request) as mock_elevenlabs:
        yield {
            "mock_openrouter": mock_openrouter,
            "mock_runware": mock_runware,
            "mock_minimax": mock_minimax,
            "mock_elevenlabs": mock_elevenlabs,
        }


@pytest.fixture
def temporary_configs_file():
    """
    Fixture to create a temporary configs.toml file in the working directory.
    The file will exist only during the test execution and will be deleted afterward.
    :return: Function to create the configs.toml file with raw TOML content.
    """
    def _create_configs(raw_toml: str):
        # Define the path for the temporary configs.toml file
        config_file_path = os.path.join(os.getcwd(), "configs.toml")

        # Write the raw TOML content to the file
        with open(config_file_path, "w") as config_file:
            config_file.write(raw_toml)

        # Return the path to the created file
        return config_file_path

    # Yield the function to allow the test to create the file
    yield _create_configs

    # Cleanup: Delete the file after the test
    config_file_path = os.path.join(os.getcwd(), "configs.toml")
    if os.path.exists(config_file_path):
        os.remove(config_file_path)
