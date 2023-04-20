from dataclasses import dataclass

import os
from pathlib import Path


@dataclass
class Options:
    create_images: bool = False
    create_mp4s: bool = False
    folder_id: str | None = None
    presentation_id: str | None = None

    run_on_only_first_in_folder: bool = True
    # folder_id = "0B9ytToO3rm0mVW43MmttZTRJc2c"
    # presentation_id = "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ"

    dpi: int = 0
    aspect_ratio: str = ""
    screen_width: int | None = 0
    screen_height: int | None = 0

    mp4_slide_duration_secs: int | None = 0
    mp4_total_video_duration: int | None = None
    save_mp4_to_file = False

    image_file_format = "svg"
    save_images_to_file = False

    download_directory: Path | str | None = None

    credentials_pattern: str = "client_secret*.json"
    credentials_file: Path | str | os.PathLike[str] = None  # type:ignore
    token_pattern: str = "token.json"
    token_file: Path | str | os.PathLike[str] = None  # type:ignore

    from_api: bool = False

    def __post_init__(self) -> None:
        if not self.download_directory:
            self.download_directory = str(Path(".").resolve())

        if not self.credentials_file:
            self.credentials_file = next(
                Path(self.download_directory).glob(self.credentials_pattern), None
            )
            self.credentials_file = str(self.credentials_file)

        if not self.token_file:
            self.token_file = str(
                next(Path(self.download_directory).glob(self.token_pattern), None)
            ) or str(Path(self.download_directory, self.token_file))

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
