from dataclasses import dataclass

import json

from io import BytesIO
from pathlib import Path

from rich import print

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
    parent: str | None = None

    _path: Path | None = None
    _working_dir: Path | None = None
    _instances = {}  # type:ignore

    def __new__(
        cls,
        extension=None,
        file_data=None,
        presentation_id=None,
        slide_id=None,
        presentation_order=0,
        presentation_name=None,
        parent=None,
    ):
        instance_id = extension, presentation_id, slide_id, parent
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
                / config.GOOGLE.resolve_drive_file_path_to_root(
                    self.presentation_id
                ).name_path
                / self.presentation_name
                / f"{self.presentation_name}_slide_{self.presentation_order + 1:02}_{self.slide_id}.{self.extension}"
            )
        else:
            self.path = (
                self.working_dir
                / "presentations"
                / config.GOOGLE.resolve_drive_file_path_to_root(
                    self.presentation_id
                ).name_path
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

    @classmethod
    def get_instance_count(cls) -> int:
        return len(cls._instances)

    def __repr__(self):
        return f"""
            "extension": {self.extension}
            "file_data": {"True" if self.file_data else "False"}
            "presentation_id": {self.presentation_id}
            "slide_id": {self.slide_id}
            "presentation_order": {self.presentation_order}
            "presentation_name": {self.presentation_name}
            "parent": {self.parent}
            "_path": {self._path}
            "_working_dir": {self._working_dir}
        """

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
