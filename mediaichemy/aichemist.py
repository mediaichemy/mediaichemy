from mediaichemy.content.short_video import ShortVideo, ShortVideoCreator
from mediaichemy.content.music_video import MusicVideo, MusicVideoCreator

CONTENT = {
    "short_video": {'creator': ShortVideoCreator,
                    'content': ShortVideo},
    "music_video": {'creator': MusicVideoCreator,
                    'content': MusicVideo}
}


class mediaAIChemist:
    def __init__(self, content_type: str):
        """
        Initialize the mediaAIChemist with the specified content type.
        :param content_type: str
            The type of content to be created (e.g., "short_video").
        """
        if content_type not in CONTENT:
            raise ValueError(f"Unsupported content type: {content_type}")
        self.content_type = content_type
        self.content_creator = CONTENT[content_type]['creator']()

    async def generate_ideas(self):
        """
        Generate ideas based on the content type.
        :return: list
            A list of generated ideas.
        """
        ideas = await self.content_creator.generate_ideas()
        return ideas

    def initialize_content(self, idea):
        """
        Initialize content based on the provided idea.
        :param idea: dict
            The idea to be used for content creation.
        :return: None
        """
        content = CONTENT[self.content_type]['content'](idea)
        return content

    async def create_content(self, content, purge: bool = False) -> None:
        """
        Create content based on the provided idea.
        :param idea: dict
            The idea to be used for content creation.
        :param purge: bool
            Whether to clean up the content creation files after completion.
        :return: None
        """
        media = await self.content_creator.create(content)
        if purge:
            content.purge()
        return media
