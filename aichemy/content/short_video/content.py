
from typing import Dict, List, Union
from aichemy.tools.language import Languages, LanguageTexts
from aichemy.tools.utils import validate_types
from aichemy.content.content import Content


class ShortVideo(Content):
    """
    Represents a content idea for short videos.
    """
    def __init__(self,
                 input: Union[str, dict],
                 name: str = '') -> None:
        """
        Initializes a ShortVideo instance.

        :param input: Union[str, dict]
            A string representing the path to a JSON file or
            a dictionary containing idea data.
        :param name: str
            The name of the content idea (default: 'short_video').
        """
        name = name + '/short_video'
        super().__init__(input=input, name=name)

    @validate_types
    def initialize_specific_attributes(self, data: dict) -> None:
        """
        Initializes attributes specific to short video content.

        :param data: dict
            The data dictionary containing idea-specific information.
        """

        self.texts: Dict[str, str] = LanguageTexts(data['texts'])
        self.image_prompt: str = data['image_prompt']
        self.captions: Dict[str, str] = LanguageTexts(data['captions'])
        self.languages: List[str] = Languages(data['languages']).codes
