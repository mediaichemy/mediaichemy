from pydantic.dataclasses import dataclass
import langcodes
from typing import List, Dict
import logging

# Initialize logger
logger = logging.getLogger(__name__)


@dataclass
class Language:
    """
    Represents a single language with its code and name.
    """
    language: str

    def __post_init__(self):
        """
        Initializes the Language object by resolving
        the input as a language code or name.
        """
        if langcodes.tag_is_valid(self.language):
            self.code = self.language
            self.name = langcodes.Language.get(self.code).display_name()
        else:
            resolved_language = langcodes.find(self.language)
            if not resolved_language:
                raise ValueError(f"Invalid language input: {self.language}")
            self.code = resolved_language.language
            self.name = resolved_language.display_name()


@dataclass
class Languages:
    """
    Represents a collection of languages.
    """
    languages: List[str]

    def __post_init__(self):
        """
        Initializes the Languages object by
        creating Language instances for each input.
        """
        self.languages = [Language(language) for language in self.languages]
        self.names = self.get_names()
        self.codes = self.get_codes()

    def get_names(self):
        """
        Retrieves the names of all languages.

        :return: List[str]
            A list of language names.
        """
        names = []
        for language in self.languages:
            names.append(language.name)
        return names

    def get_codes(self):
        """
        Retrieves the codes of all languages.

        :return: List[str]
            A list of language codes.
        """
        codes = []
        for language in self.languages:
            codes.append(language.code)
        return codes


@dataclass
class LanguageTexts:
    """
    Represents text content in multiple languages.
    """
    texts: Dict[str, str]

    def __post_init__(self):
        self.texts = self._validate_text_dicts(self.texts)

    def get_text(self, language: str):
        """
        Retrieves the text for a specific language.

        :param language: str
            The language code.
        :return: str
            The text in the specified language.
        """
        texts = [txt for txt in self.texts if language in txt]
        if not texts:
            raise ValueError(f"Language '{language}' not found in texts.")
        return texts[0][language]

    def _validate_text_dicts(self, text_dicts):
        return [{Language(k).code: text_dicts[k]}for k in text_dicts.keys()]
