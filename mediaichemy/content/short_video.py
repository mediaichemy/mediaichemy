from pydantic.dataclasses import dataclass
from typing import Dict, List, Union
from mediaichemy.tools.language import Languages, LanguageTexts
from mediaichemy.tools.utils import validate_types, extract_json
from mediaichemy.content.content import Content
from mediaichemy.ai.request import ai_request
from mediaichemy.content.creator import ContentCreator
from mediaichemy.configs import ConfigManager
from mediaichemy.tools.filehandling import JPEGFile, MP3File, MP4File


@dataclass
class ShortVideoPrompt:
    n_ideas: int
    text_details: str
    img_tags: str
    languages: List[str]

    def __post_init__(self):
        self.languages = Languages(self.languages)

    def generate_prompt(self) -> str:
        return (
            f"Create {self.n_ideas} texts for social media.\n"
            f"Don't include emojis\n\n"
            f"Text details: {self.text_details}\n\n"
            f"For each text write a prompt for creating an image that "
            f"follows it. Image prompt should be in the following format: "
            f"tag1, tag2, tag3, etc. First tags are: {self.img_tags}\n\n"
            f"For each text and image write a caption that follows it.\n"
            f"Don't include hashtags.\n\n"
            f"Make a version of the text and caption to each of the "
            f"following languages:\n {', '.join(self.languages.get_names())}\n\n"
            f"The result should be given as a json in the following way:\n"
            f"Languages should be represented by their respective codes:\n"
            f" {', '.join(self.languages.get_codes())}\n"
            f"    {{\n"
            f"        \"texts\": {{\"language1\": \"the language1 text goes here\",\n"
            f"                \"language2\": \"the language2 text goes here\",\n"
            f"                \"etc...\"}},\n"
            f"        \"image_prompt\": \"the image prompt goes here\",\n"
            f"        \"captions\": {{\"language1\": \"the language1 caption goes here\",\n"
            f"                \"language2\": \"the language2 caption goes here\",\n"
            f"                \"etc...\"}},\n"
            f"        \"languages\": [\"language1\", \"language2\"],\n"
            f"    }},\n"
            f"    {{etc..}}\n"
            f"]\n"
        )


class ShortVideo(Content):
    def __init__(self,
                 input: Union[str, dict],
                 name: str = '') -> None:
        name = name + '/short_video'
        super().__init__(input=input, name=name)
        self.STATES = {
             "initialized": [0, None],
             "image_created": [1, JPEGFile(self.dir + '/image.jpg')],
             "video_created": [2, MP4File(self.dir + '/video.mp4')],
             "speech_created": [3,
                                {language: MP3File(f'{self.dir}/{language}_speech.mp3')
                                 for language in self.languages}],
             "video_edited": [4,
                              {language: MP4File(f'{self.dir}/{language}_edited_video.mp4')
                               for language in self.languages}],
             "subtitles_added": [5, 'Content created']
             }

    @validate_types
    def initialize_specific_attributes(self, data: dict) -> None:
        self.texts: Dict[str, str] = LanguageTexts(data['texts'])
        self.image_prompt: str = data['image_prompt']
        self.captions: Dict[str, str] = LanguageTexts(data['captions'])
        self.languages: List[str] = Languages(data['languages']).codes


class ShortVideoCreator(ContentCreator):
    def __init__(self):
        self.configs = ConfigManager().get('content.short_video')

        self.prompt = ShortVideoPrompt(
            n_ideas=self.configs['n_ideas'],
            text_details=self.configs['text_details'],
            img_tags=self.configs['img_tags'],
            languages=self.configs['languages']
        ).generate_prompt()

        super().__init__(content_type="short_video")

    async def generate_ideas(self):
        raw_ideas = await ai_request(media="text", prompt=self.prompt)
        ideas = [dict(x) for x in extract_json(raw_ideas)]
        return ideas

    async def create(self, content: ShortVideo) -> None:
        config_manager = ConfigManager()
        image = await self.run_image_creation(content)
        video = await self.run_video_creation(content, image,
                                              creation_method=config_manager.get('video.creation_method'))
        speech = await self.run_speech_creation(content)
        edited_videos = await self.run_video_editing(content, video, speech,
                                                     extension_method=config_manager.get('video.extension_method'))
        subtitled_videos = await self.run_subtitling(content, edited_videos)
        return subtitled_videos
