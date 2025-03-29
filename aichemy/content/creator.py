from abc import ABC, abstractmethod
from .base_prompts import PromptLibrary
from ..utils import extract_json
from ..ai.providers import ai_request
from ..language import Languages
from .content import Content, ShortVideo
from ..configs import ConfigManager
from .tools.extend_video import ExtendVideo


class ContentCreator(ABC):
    """
    Abstract base class for content types.
    """
    def __init__(self, content_type: str):
        self.content_type = content_type

    @property
    def base_prompt(self) -> str:
        """
        Retrieves the base prompt for the given content type.

        :return: str
            The base prompt template.
        :raises KeyError:
            If the content type is not found in the registry.
        """
        try:
            return PromptLibrary().get_prompt(self.content_type)
        except KeyError:
            raise KeyError(f"Content type '{self.content_type}' not found in "
                           "the base prompt library.")

    def _format_prompt(self, **kwargs) -> str:
        """
        Formats the base prompt with the provided keyword arguments.

        :param kwargs: dict
            The values to format the prompt with.
        :return: str
            The formatted prompt.
        """
        return self.base_prompt.format(**kwargs)

    @abstractmethod
    async def generate_ideas(self, **kwargs):
        """
        Abstract method to generate ideas for the content type.
        This method should be implemented by subclasses.

        :param kwargs: dict
            The values to format the prompt with.
        :return: List[Dict]
            A list of generated ideas.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    async def create(self, idea: Content, **kwargs) -> None:
        """
        Abstract method to create content based on the generated idea.
        This method should be implemented by subclasses.

        :param idea: Content
            The content idea to create content from.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class ShortVideoCreator(ContentCreator):
    """
    Represents the 'short_video' content type.
    """

    def __init__(self):
        """
        Initializes the ShortVideo content type.
        """
        self.configs = ConfigManager().get('content.shortvideo')
        super().__init__(content_type="short_video")

    def format_prompt(self) -> str:
        # Convert the list of language codes to a Languages instance
        languages_obj = Languages(self.configs['languages'])
        return super()._format_prompt(
            n_ideas=self.configs['n_ideas'],
            text_details=self.configs['text_details'],
            img_tags=self.configs['img_tags'],
            languages_names=", ".join(languages_obj.names),
            languages_codes=", ".join(languages_obj.codes)
        )

    async def generate_ideas(self):
        # Step 1: Format the prompt
        prompt = self.format_prompt()

        # Step 2: Execute the request
        raw_ideas = await ai_request(media="text", prompt=prompt)

        # Step 3: Process the results
        ideas = [dict(x) for x in extract_json(raw_ideas)]
        return ideas

    async def create(self, content: ShortVideo) -> None:
        """
        Creates short video content based on the generated idea.

        :param idea: ShortVideo
            The content idea to create content from.
        """
        img = await ai_request(media="image",
                               output_path=content.dir + '/image.jpg',
                               prompt=content.image_prompt)

        video = await ai_request(media="video",
                                 prompt=content.image_prompt,
                                 output_path=content.dir + '/video.mp4',
                                 input_path=img.filepath)

        for language in content.languages:
            text = content.texts.get_text(language)
            speech = await ai_request(media="speech",
                                      prompt=text,
                                      output_path=content.dir + '/speech.mp3')
            duration = speech.get_duration()
            extender = ExtendVideo(video)
            extender.extend_to_duration(target_duration=duration,
                                        prompt=content.image_prompt,
                                        method=self.configs['extend_method'])

        print(video)
        print(duration)
