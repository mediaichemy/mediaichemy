from pydantic.dataclasses import dataclass
from typing import Dict, List, Union
from mediaichemy.tools.edit_text import YoutubeCaption
from mediaichemy.tools.utils import validate_types, extract_json
from mediaichemy.content.content import Content
from mediaichemy.ai.request import ai_request
from mediaichemy.content.creator import ContentCreator
from mediaichemy.configs import ConfigManager
from mediaichemy.tools.filehandling import JPEGFile, MP4File
import gc


@dataclass
class MusicVideoPrompt:
    n_ideas: int
    video_url: str
    img_tags: str = ''
    n_subtitles: int = 5

    def __post_init__(self):
        yt_captions = YoutubeCaption(self.video_url)
        self.subtitles = yt_captions.get_subtitles()

    def generate_prompt(self) -> str:
        return (f"Extract {self.n_ideas} interesting sections from the subtitles I'm about to give you. "
                f"Each section will be used to make one video for social media. "
                "Each section is made of multiple subtitles, with start, end, and text.\n"
                "Along with each section, create a caption that goes along it on social media\n"
                "The caption should be in the same language as the subtitles and can contain emojis.\n"
                "Along with each section, create a prompt for creating a video that goes along it."
                "The prompt should be in english"
                f"The image prompt should start with: {self.img_tags}\n"
                "The subtitles should be in order and should not overlap each other."
                "Keep start and end the same as provided below. "
                "It is okay if the sections intersect with each other, but this is not preferred. "
                f"Each section should have around {self.n_subtitles} subtitles.\n"
                "Return them as a JSON in the following format \n"
                "   {'section': [{'end':..., 'start':..., 'text': ...},"
                "                {'end':..., 'start':..., 'text': ...}],"
                "    'caption': '...',"
                "    'image_prompt': '...'},"
                "   {'section': [{'end':..., 'start':..., 'text': ...},"
                "                {'end':..., 'start':..., 'text': ...}],"
                "    'caption': '...'}"
                "   {'section': [{'end':..., 'start':..., 'text': ...},"
                "                {'end':..., 'start':..., 'text': ...}],"
                "    'caption': '...',"
                "    'image_prompt': '...'}\n"
                f"These are the subtitles: \n{self.subtitles}")


class MusicVideo(Content):
    def __init__(self,
                 input: Union[str, dict],
                 name: str = '') -> None:
        name = name + '/music_video'
        super().__init__(input=input, name=name)
        self.STATES = {
             "initialized": [0, None],
             "image_created": [1, JPEGFile(self.dir + '/image.jpg')],
             "video_created": [2, MP4File(self.dir + '/video.mp4')],
             "video_edited": [4, MP4File(f'{self.dir}/edited_video.mp4')],
             "subtitles_added": [5, 'Content created']
             }

    @validate_types
    def initialize_specific_attributes(self, data: dict) -> None:
        self.subtitles: List[dict] = data['section']
        self.image_prompt: str = data['image_prompt']
        self.captions: Dict[str, str] = data['caption']
        self.start = min([sub['start'] for sub in self.subtitles])
        self.end = max([sub['end'] for sub in self.subtitles])
        self.duration = self.end - self.start
        for subtitle in self.subtitles:
            subtitle['start'] -= self.start
            subtitle['end'] -= self.start
            subtitle['text'] = subtitle['text'].replace('\n', '\\N')


class MusicVideoCreator(ContentCreator):
    def __init__(self):
        self.configs = ConfigManager().get('content.music_video')
        prompt = MusicVideoPrompt(
            n_ideas=self.configs['n_ideas'],
            img_tags=self.configs['img_tags'],
            video_url=self.configs['video_url'],
            n_subtitles=self.configs['n_subtitles']
        )
        self.prompt = prompt.generate_prompt()
        self.subtitles = prompt.subtitles

        super().__init__(content_type="music_video")

    async def generate_ideas(self):
        raw_ideas = await ai_request(media="text", prompt=self.prompt)
        ideas = [dict(x) for x in extract_json(raw_ideas)]
        return ideas

    async def create(self, content: MusicVideo) -> None:
        config_manager = ConfigManager()
        image = await self.run_image_creation(content)
        video = await self.run_video_creation(content, image,
                                              creation_method=config_manager.get('video.creation_method'))
        edited_videos = await self.run_video_editing2(content, video, self.configs['video_url'],
                                                      extension_method=config_manager.get('video.extension_method'))
        subtitled_videos = await self.run_subtitling2(content, edited_videos)
        gc.collect()
        return subtitled_videos
