from pydantic.dataclasses import dataclass
from typing import List
from aichemy.tools.language import Languages


@dataclass
class ShortVideoPrompt:
    n_ideas: int
    text_details: str
    img_tags: List[str]
    languages: List[str]

    def __post_init__(self):
        """
        Initializes the ShortVideoPrompt object by creating
        Language instances for each input.
        """
        self.languages = Languages(self.languages)

    def generate_prompt(self) -> str:
        """
        Generates the prompt based on the provided arguments.

        :return: str
            The formatted prompt string.
        """
        return (
            f"Create {self.n_ideas} texts for social media.\n"
            f"Don't include emojis\n\n"
            f"Text details: {self.text_details}\n\n"
            f"For each text write a prompt for creating an image that "
            f"follows it. Image prompt should be in the following format: "
            f"tag1, tag2, tag3, etc. First tags are: {', '.join(self.img_tags)}\n\n"
            f"For each text and image write a caption that follows it.\n"
            f"Don't include hashtags.\n\n"
            f"Make a version of the text and caption to each of the "
            f"following languages:\n {', '.join(self.languages_names)}\n\n"
            f"The result should be given as a json in the following way:\n"
            f"Languages should be represented by their respective codes:\n"
            f" {', '.join(self.languages_codes)}\n"
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
