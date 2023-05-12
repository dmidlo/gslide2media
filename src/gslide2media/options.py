from dataclasses import dataclass

import os
from pathlib import Path


@dataclass
class Options:
    create_images: bool = False
    create_mp4s: bool = False
    folder_id: str | None = None
    presentation_id: str | None = None

    run_all = False
    max_walk_depth = 10
    # folder_id = "0B9ytToO3rm0mVW43MmttZTRJc2c"
    # presentation_id = "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ"

    dpi: int = 0
    fps: int = 10
    aspect_ratio: str = ""
    screen_width: int | None = 0
    screen_height: int | None = 0

    mp4_slide_duration_secs: int | None = 20
    mp4_total_video_duration: int | None = None
    save_mp4_to_file = False

    image_file_format = "svg"
    save_images_to_file = False
    jpeg_quality: int = 90

    download_directory: Path | str | None = None

    from_api: bool = False
    tool_auth_google_api_project: bool = False
    tool_google_auth_token: bool = False
    tool_import_client_secret: bool = False

    def __post_init__(self) -> None:
        if not self.download_directory:
            self.download_directory = str(Path(".").resolve())

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
