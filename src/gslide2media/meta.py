from dataclasses import dataclass, field

import string
import random
import os
import pickle
import base64
import json

from pathlib import Path
from io import BytesIO

import yaml
from google.oauth2.credentials import Credentials
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from gslide2media.options import Options
from gslide2media.cli.tools import OptionsHistory
from gslide2media.cli.tools import options_name_dialog
from gslide2media.cli.tools import options_clear_confirm
from gslide2media.cli.modifiers import _fix_path_strings
from gslide2media.enums import OptionsTimeAttrs

from rich import print


@dataclass
class Metadata:
    _instance = None
    app_settings_path = Path.home() / ".gslide2media"
    app_metadata_path = Path.home() / ".gslide2media_meta"
    google_client_secret: dict = field(default_factory=dict)
    google_client_token: Credentials | None = None
    options_history: set[Options] = field(default_factory=set[Options])
    options_history_max_unnamed_sets = 10

    def __call__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.write()

    def __new__(cls):
        if cls.app_settings_path.exists() and cls.app_metadata_path.exists():
            return super().__new__(cls)

        cls.generate_settings(cls.app_settings_path)
        return super().__new__(cls)

    @classmethod
    def metadata_singleton_factory(cls):
        if not cls._instance:
            if cls.app_settings_path.exists() and cls.app_metadata_path.exists():
                cls._instance = Metadata.read(
                    cls.app_metadata_path,
                    Metadata.get_project_meta(cls.app_settings_path),
                )
            else:
                cls._instance = Metadata()
        return cls._instance

    @staticmethod
    def generate_settings(settings_path: Path):
        settings = Metadata.generate_yaml_dict()
        Metadata.write_settings(settings_path, settings)

    @staticmethod
    def generate_client_id():
        return "".join(
            random.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(1028)
        )

    @staticmethod
    def generate_project_id():
        return os.urandom(16)

    @staticmethod
    def generate_yaml_dict():
        yaml_dump = {
            "client_id": base64.urlsafe_b64encode(
                Metadata.generate_client_id().encode("ascii")
            ),
            "project_id": Metadata.generate_project_id(),
        }
        yaml_dump["project_meta"] = Metadata.generate_derived_key(
            yaml_dump["client_id"], yaml_dump["project_id"]
        )

        return yaml_dump

    @staticmethod
    def generate_derived_key(client_id, project_id):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=project_id, iterations=100000
        )

        return base64.urlsafe_b64encode(kdf.derive(client_id))

    @staticmethod
    def write_settings(settings_path: Path, settings: dict):
        if not settings_path.exists():
            settings_path.touch()

        with settings_path.open("w") as file:
            file.write(yaml.safe_dump(settings))

    @staticmethod
    def get_client_id(settings_path: Path):
        with settings_path.open("r") as file:
            settings = yaml.safe_load(file)
        return settings["client_id"]

    @staticmethod
    def get_project_id(settings_path: Path):
        with settings_path.open("r") as file:
            settings = yaml.safe_load(file)
        return settings["project_id"]

    @staticmethod
    def get_project_meta(meta_path: Path):
        if meta_path.exists():
            with meta_path.open("r") as file:
                settings = yaml.safe_load(file)
            return settings["project_meta"]

    @classmethod
    def read(cls, metadata_path: Path, project_meta):
        if metadata_path.exists():
            with metadata_path.open("rb") as file:
                data = file.read()
                decoder = Fernet(project_meta)
                decoded_data = BytesIO(decoder.decrypt(data))
                return pickle.load(decoded_data)
        return cls

    def write(self):
        dump = BytesIO()
        pickle.dump(self, dump)
        encoder = Fernet(Metadata.get_project_meta(self.app_settings_path))
        encoded_dump = encoder.encrypt(dump.getvalue())

        data = BytesIO(encoded_dump)

        if not self.app_metadata_path.exists():
            self.app_metadata_path.touch()

        with self.app_metadata_path.open("wb") as file:
            file.write(data.getvalue())

    def import_google_client_secret_json(self, file_path: str):
        path = Path(file_path)

        with Path.open(path, "r") as file:
            data = json.load(file)

        self(google_client_secret=data)

    def add_option_set(self, options_set: Options):
        terminate = isinstance(options_set.set_label, bool)

        if options_set != _fix_path_strings(Options()) or isinstance(options_set.set_label, bool):
            options_set = self.set_options_name(options_set)
            options_set.mark_time(OptionsTimeAttrs.LAST_USED)

            if options_set in self.options_history:
                self.options_history.remove(options_set)
            self.options_history.add(options_set)

        self.enforce_unnamed_option_sets_limit()

        self.write()
        if terminate:
            raise SystemExit

    def set_options_name(self, options_set: Options) -> Options:
        if options_set.set_label:
            if isinstance(options_set.set_label, bool):
                options_set = OptionsHistory()()
                self.options_history.remove(options_set)
                options_set.options_set_name = options_name_dialog(options_set)

            if isinstance(options_set.set_label, str):
                self.options_history.remove(options_set)
                options_set.options_set_name = options_set.set_label.strip().replace(" ", "-")

            options_set.set_label = None
            options_set.mark_time(OptionsTimeAttrs.MODIFY)
        return options_set

    def collate_named_and_unnamed_option_sets(self) -> tuple:
        named_sets: list = []
        unnamed_sets: list = []

        for _ in self.options_history:
            if _.options_set_name:
                named_sets.append(_)
            else:
                unnamed_sets.append(_)

        return named_sets, unnamed_sets

    def enforce_unnamed_option_sets_limit(self) -> None:
        named_sets, unnamed_sets = self.collate_named_and_unnamed_option_sets()

        unnamed_sets = sorted(unnamed_sets, key=lambda options_set: options_set._last_used_time_utc, reverse=True)[:self.options_history_max_unnamed_sets]

        self.options_history = set(named_sets) | set(unnamed_sets)

    def remove_options_set(self, options_set: Options) -> None:

        if options_set._remove_history_option:
            trash_option_set: Options | None = None

            if options_set.label:
                for _ in self.options_history:
                    if hash(options_set.label) == _.__hash__():
                        trash_option_set = _
                
                if not trash_option_set:
                    raise ValueError(f"No Option set with label found: {options_set.label}")

            else:
                trash_option_set = OptionsHistory()()

            if trash_option_set:
                self.options_history.remove(trash_option_set)
        self.write()
        raise SystemExit("options set removed.")
    
    def clear_options_history(self, options_set: Options) -> None:
        if len(self.options_history) > 0:
            if options_set.clear_force:
                self.options_history = set()
            else:
                if options_clear_confirm():
                    self.options_history = set()
                else:
                    raise SystemExit("aborted.")
            self.write()
        else:
            raise SystemExit("No records in options history.")
     
        raise SystemExit("reset options history.")
