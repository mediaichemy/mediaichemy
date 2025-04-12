from mediaichemy.tools.filehandling import JPEGFile, MP4File, MP3File
from mediaichemy.content.short_video import ShortVideoPrompt, ShortVideo, ShortVideoCreator
import pytest
import logging
import os
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_short_video_prompt_initialization():
    """
    Test the initialization of the ShortVideoPrompt class.
    """
    prompt = ShortVideoPrompt(
        n_ideas=3,
        text_details="Details about the text",
        img_tags="tag1, tag2, tag3",
        languages=["english", "spanish"]
    )

    # Assert the attributes are correctly set
    assert prompt.n_ideas == 3
    assert prompt.text_details == "Details about the text"
    assert prompt.img_tags == "tag1, tag2, tag3"
    assert prompt.languages.get_names() == ["English", "Spanish"]
    assert prompt.languages.get_codes() == ["en", "es"]


def test_generate_prompt():
    """
    Test the generate_prompt method of the ShortVideoPrompt class.
    """
    prompt = ShortVideoPrompt(
        n_ideas=2,
        text_details="Details about the text",
        img_tags="tag1, tag2",
        languages=["en", "es"]
    )

    # Generate the prompt
    generated_prompt = prompt.generate_prompt()

    # Assert the generated prompt contains the expected content
    assert "Create 2 texts for social media." in generated_prompt
    assert "Don't include emojis" in generated_prompt
    assert "Text details: Details about the text" in generated_prompt
    assert "First tags are: tag1, tag2" in generated_prompt
    assert "Make a version of the text and caption to each of the following languages:" in generated_prompt
    assert "English, Spanish" in generated_prompt
    assert "Languages should be represented by their respective codes:" in generated_prompt
    assert "en, es" in generated_prompt


def test_short_video_initialization():
    """
    Test the initialization of the ShortVideo class with real data.
    """
    # Define input data
    input_data = {
        "texts": {
            "en": "This is a test text in English.",
            "es": "Este es un texto de prueba en español."
        },
        "image_prompt": "A beautiful sunset over the mountains.",
        "captions": {
            "en": "A breathtaking view of the sunset.",
            "es": "Una vista impresionante del atardecer."
        },
        "languages": ["en", "es"]
    }

    # Initialize the ShortVideo instance
    short_video = ShortVideo(input=input_data)

    # Assert that the attributes are correctly set
    assert short_video.texts.get_text("en") == "This is a test text in English."
    assert short_video.texts.get_text("es") == "Este es un texto de prueba en español."
    assert short_video.image_prompt == "A beautiful sunset over the mountains."
    assert short_video.captions.get_text("en") == "A breathtaking view of the sunset."
    assert short_video.captions.get_text("es") == "Una vista impresionante del atardecer."
    assert short_video.languages == ["en", "es"]


@pytest.mark.asyncio
async def test_short_video_states(copy_mock_content):
    """
    Test the STATES dictionary of the ShortVideo class.
    """
    # Create a ShortVideo object
    short_video = ShortVideo("tests/resources/temp_content/idea.json")

    # Assert the keys of the STATES dictionary
    assert list(short_video.STATES.keys()) == [
        "initialized",
        "image_created",
        "video_created",
        "speech_created",
        "video_edited",
        "subtitles_added"
    ]

    # Assert the values of the STATES dictionary
    states = short_video.STATES

    # Check "initialized" state
    assert states["initialized"] == [0, None]

    # Check "image_created" state
    assert states["image_created"][0] == 1
    assert isinstance(states["image_created"][1], JPEGFile)
    assert states["image_created"][1].filepath == f"{short_video.dir}/image.jpg"

    # Check "video_created" state
    assert states["video_created"][0] == 2
    assert isinstance(states["video_created"][1], MP4File)
    assert states["video_created"][1].filepath == f"{short_video.dir}/video.mp4"

    # Check "speech_created" state
    assert states["speech_created"][0] == 3
    assert isinstance(states["speech_created"][1], dict)
    for language, mp3_file in states["speech_created"][1].items():
        assert isinstance(mp3_file, MP3File)
        assert mp3_file.filepath == f"{short_video.dir}/{language}_speech.mp3"

    # Check "video_edited" state
    assert states["video_edited"][0] == 4
    assert isinstance(states["video_edited"][1], dict)
    for language, mp4_file in states["video_edited"][1].items():
        assert isinstance(mp4_file, MP4File)
        assert mp4_file.filepath == f"{short_video.dir}/{language}_edited_video.mp4"

    # Check "subtitles_added" state
    assert states["subtitles_added"] == [5, "Content created"]


def test_short_video_content(copy_mock_content):
    # Create a ShortVideo object
    short_video = ShortVideo("tests/resources/temp_content/idea.json")

    # Check if the ShortVideo object is created successfully
    assert isinstance(short_video, ShortVideo)
    assert short_video.dir == 'tests/resources/temp_content'

    # Assert that the attributes are correctly set
    assert short_video.texts.get_text("en") == ("Chase your dreams with relentless passion. Every step forward is a "
                                                "victory, no matter how small. Keep going.")
    assert short_video.texts.get_text("pt") == ("Persiga seus sonhos com paixão incansável. Cada passo à frente é "
                                                "uma vitória, não importa o quão pequeno. Continue seguindo.")
    assert short_video.image_prompt == ("determination, mountain summit, sunrise,"
                                        " hiker silhouette, golden light, vast horizon")
    assert short_video.captions.get_text("en") == "The climb may be tough, but the view from the top is worth it."
    assert short_video.captions.get_text("pt") == "A subida pode ser difícil, mas a vista do topo vale a pena."
    assert short_video.languages == ["en", "pt"]
    assert list(short_video.STATES.keys()) == ['initialized', 'image_created',
                                               'video_created', 'speech_created',
                                               'video_edited', 'subtitles_added']


@pytest.mark.asyncio
async def test_short_video_creator():
    """
    Test the ShortVideoCreator class.
    """
    creator = ShortVideoCreator()
    assert creator.configs == {'n_ideas': 2, 'languages': ['en', 'pt'], 'text_details': '', 'img_tags': '',
                               'extension_method': 'loop', 'video': {'creation_method': 'static_image'}}
    assert creator.content_type == 'short_video'
    assert creator.prompt == ('Create 2 texts for social media.\nDon\'t include emojis\n\nText details:'
                              ' \n\nFor each text write a prompt for creating an image that follows it.'
                              ' Image prompt should be in the following format: tag1, tag2, tag3, etc.'
                              ' First tags are: \n\nFor each text and image write a caption that'
                              ' follows it.\nDon\'t include hashtags.\n\nMake a version of the text and'
                              ' caption to each of the following languages:\n English, Portuguese\n\nThe'
                              ' result should be given as a json in the following way:\nLanguages'
                              ' should be represented by their respective codes:\n en, pt\n    {\n      '
                              '  "texts": {"language1": "the language1 text goes here",\n              '
                              '  "language2": "the language2 text goes here",\n                '
                              '"etc..."},\n        "image_prompt": "the image prompt goes here",\n    '
                              '    "captions": {"language1": "the language1 caption goes here",\n     '
                              '           "language2": "the language2 caption goes here",\n             '
                              '   "etc..."},\n        "languages": ["language1", "language2"],\n    },\n'
                              '    {etc..}\n]\n')
    ideas = await creator.generate_ideas()
    idea = ideas[0]
    assert isinstance(ideas, list)
    assert isinstance(ideas[0], dict)
    assert idea['texts'] == {'en': 'Chase your dreams with relentless passion. Every step forward is a victory,'
                             ' no matter how small. Keep going.',
                             'pt': 'Persiga seus sonhos com paixão incansável. Cada passo à frente é uma vitória,'
                             ' não importa o quão pequeno. Continue seguindo.'}
    assert idea['image_prompt'] == ('determination, mountain summit, sunrise, hiker silhouette, '
                                    'golden light, vast horizon')
    assert idea['captions'] == {'en': 'The climb may be tough, but the view from the top is worth it.',
                                'pt': 'A subida pode ser difícil, mas a vista do topo vale a pena.'}
    assert idea['languages'] == ['en', 'pt']
    content = ShortVideo(idea)
    assert content.state == 'initialized'
    # Construct the file path
    file_path = os.path.join(content.dir, "idea.json")

    # Assert that the file exists
    assert os.path.exists(file_path), f"File does not exist: {file_path}"

    # Delete the file and its containing folder
    shutil.rmtree(content.dir)

    # Assert that the directory no longer exists
    assert not os.path.exists(content.dir), f"Directory still exists: {content.dir}"
