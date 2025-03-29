from typing import Dict
from ..utils import validate_types
import logging

# Initialize logger
logger = logging.getLogger(__name__)


class PromptLibrary:
    """
    Represents a library of prompts for different content types.
    """
    def __init__(self) -> None:
        """
        Initializes the PromptLibrary with predefined prompts.
        """
        self.prompts: Dict[str, str] = {
            "short_video": (
                'Create {n_ideas} texts for social media.\n'
                'Dont include emojis\n\n'
                'Text details: {text_details}\n\n'
                'For each text write a prompt for creating an image that '
                'follows it. Image prompt should be in the following format: '
                'tag1, tag2, tag3, etc. First tags are: {img_tags}\n\n'
                'For each text and image write a caption that follows it.\n'
                'Don\'t include hashtags.\n\n'
                'Make a version of the text and caption to each of the '
                'following languages:\n {languages_names}\n\n'
                'The result should be given as a json in the following way:\n'
                'Languages should be represented by their respective codes:\n'
                ' {languages_codes}\n'
                '    {{\n'
                '        "texts": {{"language1": "the language1 text goes '
                'here",\n'
                '                "language2": "the language2 text goes here",'
                '\n                "etc..."}},\n'
                '        "image_prompt": "the image prompt goes here",\n'
                '        "captions": {{"language1": "the language1 caption '
                'goes here",\n'
                '                "language2": "the language2 caption goes '
                'here",\n'
                '                "etc..."}},\n'
                '        "languages": ["language1", "language2"],\n'
                '    }},\n'
                '    {{etc..}}\n'
                ']\n'
            ),
            "podcast": (
                'Generate {n_ideas} podcast episode ideas.\n'
                'Each idea should include:\n'
                '- A title\n'
                '- A brief description\n'
                '- Three key talking points\n\n'
                'Make sure the ideas are engaging and relevant to the '
                'following topic: {topic}\n\n'
                'The result should be displayed as a JSON array:\n'
                '[\n'
                '    {{\n'
                '        "title": "Podcast title goes here",\n'
                '        "description": "Brief description goes here",\n'
                '        "talking_points": ["Point 1", "Point 2", "Point 3"]\n'
                '    }},\n'
                '    {{etc...}}\n'
                ']\n'
            ),
            "single_image": (
                'Generate a image prompt based on the following details:\n'
                'Tags: {tags}\n'
                'Style: {style}\n'
                'Description: {description}\n\n'
                'The result should be a concise image prompt in the format:\n'
                '"tag1, tag2, tag3, style1, style2, description".\n'
            ),
            "carousel": (
                'Create {n_slides} carousel post ideas for social media.\n'
                'Each slide should include:\n'
                '- A title\n'
                '- A brief description\n'
                '- A call-to-action (CTA)\n\n'
                'Topic: {topic}\n\n'
                'The result should be displayed as a JSON array:\n'
                '[\n'
                '    {{\n'
                '        "slide_number": 1,\n'
                '        "title": "Slide title goes here",\n'
                '        "description": "Slide description goes here",\n'
                '        "cta": "CTA goes here"\n'
                '    }},\n'
                '    {{etc...}}\n'
                ']\n'
            ),
        }

    @validate_types
    def get_prompt(self, content_type: str) -> str:
        """
        Retrieves the prompt for a given content type.

        :param content_type: str
            The type of content (e.g., 'short_video', 'podcast').
        :return: str
            The prompt template for the specified content type.
        :raises KeyError:
            If the content type is not found in the library.
        """
        if content_type not in self.prompts:
            raise KeyError(f"Content type '{content_type}' not found in the "
                           "prompt library.")
        return self.prompts[content_type]

    def list_content_types(self) -> list:
        """
        Lists all available content types in the library.

        :return: list
            A list of content type keys.
        """
        return list(self.prompts.keys())
