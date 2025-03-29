import json
from PIL import Image, ImageDraw, ImageFont
import IPython
import matplotlib.font_manager as font_manager
from io import StringIO
import logging
import sys
from functools import wraps
from inspect import signature
from typing import get_type_hints, get_origin, get_args, Union

# Initialize logger
logger = logging.getLogger(__name__)


def validate_types(func):
    """
    Decorator to validate function argument types.

    :param func: Callable
        The function to validate.
    :return: Callable
        The wrapped function with type validation.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Get the function's signature and type hints
        sig = signature(func)
        type_hints = get_type_hints(func)

        # Bind the arguments to the signature
        bound_args = sig.bind(self, *args, **kwargs)
        bound_args.apply_defaults()

        # Validate each argument against its type hint
        for arg_name, arg_value in bound_args.arguments.items():
            if arg_name in type_hints:
                expected_type = type_hints[arg_name]
                if not _validate_type(arg_value, expected_type):
                    raise TypeError(
                        f"Argument '{arg_name}' must be of "
                        f"type {expected_type}, but got {type(arg_value)}."
                    )

        return func(self, *args, **kwargs)
    return wrapper


def _validate_type(value, expected_type):
    """
    Validates a value against an expected type.

    :param value: Any
        The value to validate.
    :param expected_type: Any
        The expected type.
    :return: bool
        True if the value matches the expected type, False otherwise.
    """
    origin = get_origin(expected_type)  # Get the base type (e.g., list, dict)
    args = get_args(expected_type)  # Get the type arguments (e.g., str, int)

    if origin is None:
        # If there's no origin, it's a simple type (e.g., int, str)
        return isinstance(value, expected_type)

    if origin in {list, tuple}:
        # Validate list or tuple elements
        if not isinstance(value, origin):
            return False
        if args:
            return all(_validate_type(item, args[0]) for item in value)

    if origin is dict:
        # Validate dictionary keys and values
        if not isinstance(value, origin):
            return False
        if args:
            key_type, value_type = args
            return all(
                _validate_type(k, key_type) and _validate_type(v, value_type)
                for k, v in value.items()
            )

    if origin is Union:
        # Validate Union types (e.g., Union[int, str])
        return any(_validate_type(value, arg) for arg in args)

    # Add more cases for other generic types if needed
    return isinstance(value, origin)


def RawJSONDecoder(index):
    """
    Creates a custom JSON decoder starting at a specific index.

    :param index: int
        The starting index for decoding.
    :return: JSONDecoder
        A custom JSON decoder class.
    """
    class _RawJSONDecoder(json.JSONDecoder):
        end = None

        def decode(self, s, *_):
            data, self.__class__.end = self.raw_decode(s, index)
            return data
    return _RawJSONDecoder


def extract_json(s, index=0):
    """
    Extracts JSON objects from a string starting at a given index.

    :param s: str
        The string to extract JSON from.
    :param index: int, optional
        The starting index for extraction. Defaults to 0.
    :return: Generator[dict]
        A generator yielding JSON objects.
    """
    while (index := s.find('{', index)) != -1:
        try:
            yield json.loads(s, cls=(decoder := RawJSONDecoder(index)))
            index = decoder.end
        except json.JSONDecodeError:
            index += 1


def display_fonts(starting_at=2):
    """
    Displays system fonts starting from a given index.

    :param starting_at: int, optional
        The index to start displaying fonts. Defaults to 2.
    """
    fonts = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    for i in range(starting_at, len(fonts)):
        image = Image.new("RGB", (500, 100), "white")
        font = ImageFont.truetype(fonts[i], 40)
        draw = ImageDraw.Draw(image)
        position = (10, 10)
        text = "Example to display fonts"
        draw.text(position, text, font=font, fill="black")
        IPython.display(image)
        print(fonts[i].replace('/System/Library/Fonts/',
                               '').replace('Supplemental/', ''))


class Capturing(list):
    """
    Captures stdout output during execution.

    Methods:
        __enter__: Starts capturing stdout.
        __exit__: Stops capturing and stores the output.
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout
