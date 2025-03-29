from abc import ABC, abstractmethod
from typing import Union
from aichemy.tools.filehandling import Directory, JSONFile
from ..tools.utils import validate_types
import logging

# Initialize logger
logger = logging.getLogger(__name__)


class Content(ABC):
    """
    Abstract base class for content ideas.
    """
    @validate_types
    def __init__(self, input: Union[str, dict], name: str = '') -> None:
        """
        Initializes a Content instance.

        :param input: Union[str, dict]
            A string representing the path to a JSON file or
            a dictionary containing idea data.
        :param name: str
            The name of the content idea.
        """
        name = 'content/' + name
        self.input = input
        if isinstance(input, str):
            jsonfile = JSONFile(self.input)
            data = jsonfile.data
            self.dir = jsonfile.dir
        elif isinstance(self.input, dict):
            data = self.input
            self.dir = Directory(path=name, create=True,
                                 random_subdir=True).path
            self.save()

        # Call the subclass-specific method to initialize specific attributes
        self.initialize_specific_attributes(data)

    @abstractmethod
    def initialize_specific_attributes(self, data: dict) -> None:
        """
        Initializes attributes specific to the subclass.

        :param data: dict
            The data dictionary containing idea-specific information.
        """
        pass

    def save(self) -> None:
        """
        Saves the idea as a JSON file.
        """
        idea_path = self.dir + '/idea.json'
        idea_dict = self.input
        jsonfile = JSONFile(idea_path)
        jsonfile.save(data=idea_dict)

    def load(self, filepath: str) -> None:
        """
        Loads idea data from a JSON file.

        :param filepath: str
            Path to the JSON file.
        """
        jsonfile = JSONFile(filepath)
        self.__dict__.update(jsonfile.data)
        self.dir = jsonfile.dir
