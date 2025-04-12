from abc import ABC, abstractmethod
from mediaichemy.content.content import Content
from mediaichemy.ai.request import ai_request
from mediaichemy.content.checkpoint import checkpoint
from mediaichemy.tools import edit_audio, edit_text, edit_video


class ContentCreator(ABC):
    def __init__(self, content_type: str):
        self.content_type = content_type

    @abstractmethod
    async def generate_ideas(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")

    async def create(self, idea: Content, **kwargs) -> None:
        raise NotImplementedError("Subclasses must implement this method.")

    @staticmethod
    @checkpoint('image_created')
    async def run_image_creation(content):
        image = await ai_request(media="image",
                                 output_path=content.dir + '/image.jpg',
                                 prompt=content.image_prompt)
        return image

    @staticmethod
    @checkpoint('video_created')
    async def run_video_creation(content, image, creation_method):
        if creation_method == 'static_image':
            video = edit_video.create_video_from_image(image=image,
                                                       duration=5)
        if creation_method == 'ai':
            video = await ai_request(media="video",
                                     prompt=content.image_prompt,
                                     output_path=content.dir + '/video.mp4',
                                     input_path=image.filepath)
        return video

    @staticmethod
    @checkpoint('speech_created')
    async def run_speech_creation(content):
        lang_speechs = {}
        for language in content.languages:
            text = content.texts.get_text(language)
            speech = await ai_request(media="speech",
                                      prompt=text,
                                      output_path=f'{content.dir}/{language}_speech.mp3')
            lang_speechs[language] = speech
        return lang_speechs

    @staticmethod
    @checkpoint('video_edited')
    async def run_video_editing(content, video, speechs, extension_method):
        edited_videos = {}
        for language in content.languages:
            speech = speechs[language]
            speech_s = edit_audio.add_silence(speech)
            lang_video = video.copy_to(f'{content.dir}/{language}_video.mp4')
            lang_video = await edit_video.extend_to_duration(lang_video,
                                                             target_duration=speech_s.get_duration(),
                                                             prompt=content.image_prompt,
                                                             method=extension_method)
            background = edit_audio.add_audio_background(speech_s)
            audio_video = edit_video.add_audio_to_video(lang_video, background)
            edited_video = audio_video.copy_to(f'{content.dir}/{language}_edited_video.mp4')
            edited_videos[language] = edited_video
        return edited_videos

    @staticmethod
    @checkpoint('subtitles_added')
    async def run_subtitling(content, videos):
        subtitled_videos = {}
        for language in content.languages:
            video = videos[language]
            text = content.texts.get_text(language)
            text_editor = edit_text.Subtitles(text=text, video=video)
            langsub_videos = text_editor.add_text_to_video()
            subtitled_videos[language] = langsub_videos
        return subtitled_videos
