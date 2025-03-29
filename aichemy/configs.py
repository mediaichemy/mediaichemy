import os
import toml
from typing import Any
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self):
        """
        Initialize the ConfigManager by searching for the "config.toml" file
        in the caller's directory and loading default configurations.
        """
        self.config_file_path = self._find_config_file()
        self.defaults = self._load_default_configs()
        self.config = self._load_config()

    def _find_config_file(self) -> str:
        """
        Locate the "config.toml" file in the caller's directory.

        Returns:
            str: The full path to the "config.toml" file.

        Raises:
            FileNotFoundError: If the "config.toml" file is not found.
        """
        caller_directory = os.getcwd()
        config_file_path = os.path.join(caller_directory, "config.toml")
        if not os.path.exists(config_file_path):
            logger.warning(
                "'config.toml' not found in directory: %s. "
                "Falling back to 'default_configs.toml'.",
                caller_directory
            )
            return os.path.join(os.path.dirname(__file__),
                                "default_configs.toml")
        return config_file_path

    def _load_config(self) -> dict:
        """
        Load the TOML configuration file and
        merge it with the default configurations.

        Returns:
            dict: Merged configuration data, prioritizing
            values from the config file.
        """
        with open(self.config_file_path, 'r') as file:
            user_config = toml.load(file)

        # Merge user_config into defaults, prioritizing user_config values
        return self._merge_dicts(self.defaults, user_config)

    def _merge_dicts(self, base: dict, override: dict) -> dict:
        """
        Recursively merge two dictionaries, prioritizing values
        from the override dictionary.

        Args:
            base (dict): The base dictionary (e.g., defaults).
            override (dict): The overriding dictionary (e.g., user config).

        Returns:
            dict: The merged dictionary.
        """
        merged = base.copy()
        for key, value in override.items():
            if isinstance(value,
                          dict) and key in merged and isinstance(merged[key],
                                                                 dict):
                merged[key] = self._merge_dicts(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _load_default_configs(self) -> dict:
        """
        Load default configurations from the "default_configs.toml" file.

        Returns:
            dict: Parsed default configuration data.

        Raises:
            FileNotFoundError: If the "default_configs.toml" file is not found.
        """
        default_config_path = os.path.join(os.path.dirname(__file__),
                                           "default_configs.toml")
        if not os.path.exists(default_config_path):
            raise FileNotFoundError("'default_configs.toml' not found in"
                                    f" directory: {os.path.dirname(__file__)}")
        with open(default_config_path, 'r') as file:
            return toml.load(file)

    def _resolve_keys(self, table: str = None, key: str = None) -> list:
        """
        Resolve the full key path based on the provided table and key.

        Args:
            table (str, optional): The name of the table.
            key (str, optional): The key or full key path.

        Returns:
            list: A list of keys representing the full path.
        """
        if table is None:
            return key.split('.')
        return table.split('.') + ([key] if key else [])

    def _traverse_config(self, keys: list) -> Any:
        """
        Traverse the configuration dictionary using the provided keys.

        Args:
            keys (list): A list of keys representing the path.

        Returns:
            Any: The value at the specified path.

        Raises:
            ValueError: If the path does not exist in the configuration.
        """
        table = self.config
        for k in keys:
            table = table.get(k)
            if table is None:
                raise ValueError(f"Key or table '{'.'.join(keys)}' "
                                 "not found in the configuration file.")
        return table

    def _apply_defaults(self, table: str) -> None:
        """
        Apply default values to a specific table if they are not already set.

        Args:
            table (str): The name of the table to apply defaults to.
        """
        keys = table.split('.')
        table_ref = self.config
        for key in keys:
            if key not in table_ref:
                table_ref[key] = {}
            table_ref = table_ref[key]

        defaults = self.defaults.get(table)
        if defaults:
            for k, v in defaults.items():
                if k not in table_ref:
                    table_ref[k] = v

    def get(self, table: str = None, key: str = None) -> Any:
        """
        Retrieve configuration data. If only `table` is provided,
        return all key-value pairs in the table as kwargs.
        If both `table` and `key` are provided, or if `key` is a full
        key path, return the specific value.

        Args:
            table (str, optional): The name of the table (e.g. "image.runware")
            key (str, optional): The key to retrieve. If `table` is None,
                                 `key should be the full key path
                                 (e.g., "image.runware.height").

        Returns:
            Any: A dictionary of key-value pairs if a table is requested,
            or a specific value if a key is requested.
        """
        if table:
            self._apply_defaults(table)

        keys = self._resolve_keys(table, key)
        result = self._traverse_config(keys)

        if key is None and isinstance(result, dict):
            return result

        return result
