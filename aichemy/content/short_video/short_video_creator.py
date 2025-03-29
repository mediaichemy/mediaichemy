from aichemy.tools.utils import extract_json
from aichemy.ai.request import ai_request
from aichemy.content.creator import ContentCreator
from aichemy.configs import ConfigManager
from aichemy.edit.video import VideoEdit
from aichemy.edit.audio import AudioEdit
from aichemy.content.short_video.short_video import ShortVideo
from aichemy.content.short_video.short_video_prompt import ShortVideoPrompt


class ShortVideoCreator(ContentCreator):
    """
    Represents the 'short_video' content type.

    :ivar configs: dict
        Configuration settings for short video content.
    :ivar prompt: ShortVideoPrompt
        The prompt object for generating ideas.
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
        ).generate_prompt()
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

        :param content: ShortVideo
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
            video_editor = VideoEdit(video)
            video_editor.extend_to_duration(target_duration=duration,
                                            prompt=content.image_prompt,
                                            method=self.configs['extend_method'])
            speech_editor = AudioEdit(speech)
            speech_editor.add_audio_background()

        print(video)
        print(duration)
