from abc import ABC, abstractmethod
from typing import Union
from mediaichemy.tools.filehandling import Directory, JSONFile
from ..tools.utils import validate_types
import logging

# Initialize logger
logger = logging.getLogger(__name__)


class Content(ABC):
    """
    Abstract base class for content ideas.

    :param input: Union[str, dict]
        A string representing the path to a JSON file or a dictionary containing idea data.
    :param name: str, optional
        The name of the content idea. Defaults to an empty string.
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
            self.load_state()
        elif isinstance(self.input, dict):
            data = self.input
            self.dir = Directory(path=name, create=True,
                                 random_subdir=True).path
            self.state = 'initialized'
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

        :param idea_path: str
            Path to the JSON file where the idea will be saved.
        :param idea_dict: dict
            Dictionary containing the idea data.
        """
        idea_path = self.dir + '/idea.json'
        idea_dict = self.input
        jsonfile = JSONFile(idea_path)
        jsonfile.save(data=idea_dict)
        logger.info(f"Saved idea to {idea_path}: {idea_dict}")

    def load(self, filepath: str) -> None:
        """
        Loads idea data from a JSON file.

        :param filepath: str
            Path to the JSON file.
        """
        jsonfile = JSONFile(filepath)
        self.__dict__.update(jsonfile.data)
        self.dir = jsonfile.dir
        logger.info(f"Loaded idea from {filepath}: {self.__dict__}")

    def load_state(self) -> None:
        """
        Loads the current state from a state file (.state) and updates the state attribute.
        """
        state_file = self.dir + '/.state'  # Path to the state file
        try:
            with open(state_file, 'r') as file:
                self.state = file.read().strip()  # Read and strip any extra whitespace
                logger.info(f"State loaded from {state_file}: {self.state}")
        except FileNotFoundError:
            logger.warning(f"State file not found: {state_file}. Defaulting to 'initialized'.")
            self.state = 'initialized'
        except Exception as e:
            logger.error(f"Failed to load state from {state_file}: {e}")
            raise
