from typing import Any
from pathlib import Path
from dataclasses import dataclass, asdict
from gslide2media.enums import OptionsSource
from gslide2media.enums import OptionsTimeAttrs
from datetime import datetime, timezone


@dataclass
class Options:
    presentation_id: list | None = None
    folder_id: list | None = None
    custom_presentation: list | None = None
    file_formats: Any = None
    run_all: bool = False
    download_directory: Path | str | None = None

    mp4_slide_duration_secs: int | None = None
    mp4_total_video_duration: int | None = None
    fps: int | None = None

    jpeg_quality: int | None = None

    aspect_ratio: str | None = None
    dpi: int | None = None
    screen_width: int | None = None
    screen_height: int | None = None

    # for api users; cli assumes "save to file", api assumes "yield <Generator>".
    save_to_file: bool = False
    import_client_secret: bool = False

    # Options History Args
    # excludes named option sets and generic commands that manipulate the options object.
    label: str | None = None
    set_label: bool | str | None = None
    options_set_name: str | None = None
    options_max_history: int | None = None
    remove_history_option: bool = False
    clear_history: bool = False
    clear_force: bool = False

    _interactive: bool = False
    from_api: bool = False
    _tool_auth_google_api_project: bool = False
    _tool_import_client_secret: bool = False
    options_source: OptionsSource | None = None
    _create_time_utc: int | None = None
    _modify_time_utc: int | None = None
    last_used_time_utc: int | None = None

    def __post_init__(self) -> None:
        if not self._create_time_utc:
            self.mark_time(OptionsTimeAttrs.CREATE)
        if not self._modify_time_utc:
            self.mark_time(OptionsTimeAttrs.MODIFY)
        if not self.last_used_time_utc:
            self.mark_time(OptionsTimeAttrs.LAST_USED)

        if not self.download_directory:
            self.download_directory = str(Path(".").resolve())

        # Class Attrs to ignore for __eq__ and __hash__
        self._comp_excluded_attrs = [
            "comp_excluded_attrs",
            "import_client_secret",
            "label",
            "set_label",
            "options_max_history",
            "remove_history_option",
            "clear_history",
            "clear_force",
            "_interactive",
            "from_api",
            "_tool_auth_google_api_project",
            "_tool_import_client_secret",
            "options_source",
            "_create_time_utc",
            "_modify_time_utc",
            "last_used_time_utc",
        ]

    def __call__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __hash__(self) -> int:
        # if it's a named option set, __eq__ and __hash__ are calculated on just the name,
        # whereas unnamed option sets are calculated on the hash
        # of self minus self._comp_excluded_attrs.

        if self.options_set_name:
            return hash(self.options_set_name)

        hash_attrs = []
        for attr, value in asdict(self).items():
            if attr not in self._comp_excluded_attrs:
                if isinstance(value, list):
                    value = tuple(value)
                hash_attrs.append(value)

        return hash(tuple(hash_attrs))

    def __eq__(self, other) -> bool:
        if self is other:
            return True

        if not isinstance(other, self.__class__):
            return False

        if self.options_set_name and self.options_set_name == other.options_set_name:
            return True

        return all(
            _self[1] == _other[1]
            for _self, _other in zip(asdict(self).items(), asdict(other).items())
            if _self[0] not in self._comp_excluded_attrs
        )

    def mark_time(self, action: OptionsTimeAttrs) -> None:
        utc_timestamp = int(datetime.now(timezone.utc).timestamp())
        match action:
            case OptionsTimeAttrs.CREATE:
                self._create_time_utc = utc_timestamp
            case OptionsTimeAttrs.MODIFY:
                self._modify_time_utc = utc_timestamp
            case OptionsTimeAttrs.LAST_USED:
                self.last_used_time_utc = utc_timestamp
            case _:
                raise AttributeError(f"invalid time action: {action}.")
