from dataclasses import dataclass

import json

from io import BytesIO
from pathlib import Path

from gslide2media.enums import ExportFormats
from gslide2media import config


@dataclass(slots=True, kw_only=True)
class File:
    extension: ExportFormats
    file_data: bytes | BytesIO
    presentation_id: str
    slide_id: str | None = None
    presentation_order: int = 0
    presentation_name: str | None = None

    _path: Path | None = None
    _working_dir: Path | None = None
    _instances = {}

    def __new__(cls, *args, **kwargs):
        instance_id = tuple(
            kwargs[_] if hasattr(kwargs, _) else "None"
            for _ in {"extension", "presentation_id", "slide_id"}
        )
        if instance_id not in cls._instances:
            cls._instances[instance_id] = super(cls, cls).__new__(cls)

        return cls._instances[instance_id]

    def __post_init__(self):
        self.working_dir = config.ARGS.download_directory

        if self.presentation_name is None:
            self.presentation_name = config.GOOGLE.get_presentation_name(
                self.presentation_id
            )

        if self.slide_id:
            self.path = (
                self.working_dir
                / "presentations"
                / self.presentation_name
                / f"{self.presentation_name}_slide_{self.presentation_order + 1:02}_{self.slide_id}.{self.extension}"
            )
        else:
            self.path = (
                self.working_dir
                / "presentations"
                / self.presentation_name
                / f"{self.presentation_name}.{self.extension}"
            )

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.extension == ExportFormats.JSON and isinstance(self.file_data, dict):
            data = json.dumps(self.file_data).encode("UTF-8")
        elif self.extension == ExportFormats.MP4:
            data = self.file_data.getbuffer()
        else:
            data = self.file_data

        with self.path.open("wb") as file:
            file.write(data)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: Path):
        self._path = path

    @path.deleter
    def path(self):
        del self._path

    @property
    def working_dir(self):
        return self._working_dir

    @working_dir.setter
    def working_dir(self, working_dir: Path):
        self._working_dir = working_dir

    @working_dir.deleter
    def working_dir(self):
        del self._working_dir
