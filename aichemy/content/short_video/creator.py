
from aichemy.tools.utils import extract_json
from aichemy.ai.provider import ai_request
from aichemy.content.creator import ContentCreator
from aichemy.configs import ConfigManager
from aichemy.tools.extend_video import ExtendVideo
from aichemy.content.short_video.content import ShortVideo
from aichemy.content.short_video.prompt import ShortVideoPrompt


class ShortVideoCreator(ContentCreator):
    """
    Represents the 'short_video' content type.
    """

    def __init__(self):
        """
        Initializes the ShortVideo content type.
        """
        self.configs = ConfigManager().get('content.shortvideo')
        self.prompt = ShortVideoPrompt(
            n_ideas=self.configs['n_ideas'],
            text_details=self.configs['text_details'],
            img_tags=self.configs['img_tags'],
            languages=self.configs['languages']
        )
        super().__init__(content_type="short_video")

    async def generate_ideas(self):
        """
        Generates ideas for short video content.
        This method formats the prompt with the provided values and
        sends it to the AI provider to generate content ideas.
        :return: List[Dict]
            A list of generated ideas.
        """
        raw_ideas = await ai_request(media="text", prompt=self.prompt)

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
