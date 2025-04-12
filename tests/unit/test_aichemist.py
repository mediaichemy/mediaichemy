from mediaichemy.aichemist import mediaAIChemist
from mediaichemy.content.short_video import ShortVideoCreator
import pytest


def test_initialization():
    # Test initialization with a valid content type
    aichemist = mediaAIChemist(content_type="short_video")
    assert aichemist.content_type == "short_video"
    assert aichemist.content_creator is not None
    assert isinstance(aichemist.content_creator, ShortVideoCreator)


def test_invalid_content_type():
    # Test initialization with an invalid content type
    try:
        mediaAIChemist("invalid_content_type")
    except ValueError as e:
        assert str(e) == "Unsupported content type: invalid_content_type"
    else:
        assert False, "Expected ValueError not raised"


@pytest.mark.asyncio
async def test_idea_generation():
    aichemist = mediaAIChemist(content_type="short_video")

    ideas = await aichemist.generate_ideas()
    assert isinstance(ideas, list), "Ideas should be a list"
    assert all(isinstance(idea, dict) for idea in ideas), "All ideas should be dictionaries"
