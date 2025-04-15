import logging
from configparser import ConfigParser
from os import environ
from pathlib import Path
from threading import Lock
from typing import Optional


class StateManager:
    _instance = None
    _initialized = False

    def __new__(cls, package_name: str, testing: Optional[bool] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        # python will automatically call __init__ after __new__
        return cls._instance

    def __init__(self, package_name: str, testing: Optional[bool] = None):
        # Skip initialization if already done
        if StateManager._initialized:
            return

        if testing is None:
            testing = environ.get("TESTING", "") == "1"

        state_file_dir = "/tmp" if testing else "/var/lib"
        self.state_file_path = f"{state_file_dir}/{package_name}/state.cfg"
        self.config_parser = ConfigParser()
        self.lock = Lock()

        # Initialize state file
        path = Path(self.state_file_path)
        if not path.exists():
            logging.info(
                f"State file {self.state_file_path} does not exist, creating it..."
            )
            Path(path.parent).mkdir(parents=True, exist_ok=True)
            path.touch()

        self.config_parser.read(self.state_file_path)
        StateManager._initialized = True

    def get(self, section: str, key: str, fallback=None):
        with self.lock:
            val = fallback
            try:
                val = self.config_parser.get(section, key)
            except Exception:
                if fallback is None:
                    raise
            return val

    def set(self, section: str, key: str, value):
        with self.lock:
            try:
                if not self.config_parser.has_section(section):
                    self.config_parser.add_section(section)
                self.config_parser.set(section, key, value)
            except Exception:
                raise
            self._save()

    def remove(self, section: str, key: str = ""):
        with self.lock:
            try:
                if key and self.config_parser.has_option(section, key):
                    self.config_parser.remove_option(section, key)
                elif len(key) == 0 and self.config_parser.has_section(section):
                    self.config_parser.remove_section(section)
            except Exception:
                raise
            self._save()

    def _save(self):
        with open(self.state_file_path, "w") as f:
            self.config_parser.write(f)

    @classmethod
    def exists(cls, package_name: str, testing: Optional[bool] = None):
        state_file_dir = "/tmp" if testing else "/var/lib"
        state_file_path = f"{state_file_dir}/{package_name}/state.cfg"
        return Path(state_file_path).exists()
