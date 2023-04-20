"""Converts a series of PNG images to an MP4 video.

Functions:
    convert_pngs_bytes_to_mp4(
            presentation_name: str,
            presentation_images: Iterator[bytes]
        ) -> BytesIO

        Given a presentation name and a series of PNG images in bytes format, converts them
        to an MP4 video.

        Returns the MP4 video in bytes format.
"""

from typing import Iterator
from typing import Optional

from io import BytesIO
from pathlib import Path

import imageio


def convert_pngs_bytes_to_mp4(
    presentation_name: str,
    presentation_images: Iterator[bytes],
    mp4_slide_duration_secs: Optional[int],
    download_directory: Path,
    save_mp4_to_file: bool,
):
    """Converts a sequence of PNG images represented as bytes to an MP4 video.

    Args:
        presentation_name (str): The name of the presentation.
        presentation_images (Iterator[bytes]): An iterator of PNG images represented as bytes.

    Returns:
        BytesIO: A bytes buffer containing the MP4 video."""
    presentation_directory: Path = (
        download_directory / "presentations" / presentation_name
    )
    video_path: Path = presentation_directory / f"{presentation_name}.mp4"

    fps = 10.0
    number_of_repetitions = int(mp4_slide_duration_secs * fps)  # type: ignore

    video_frames = []

    for image_bytes in presentation_images:
        for _ in range(number_of_repetitions):
            image = imageio.imread(image_bytes)
            video_frames.append(image)

    output_params = {"fps": fps, "extension": ".mp4"}

    if save_mp4_to_file:
        imageio.v3.imwrite(
            str(video_path.resolve()), video_frames, **output_params
        )  # type:ignore

    video_bytes = BytesIO()
    return imageio.v3.imwrite(video_bytes, video_frames, **output_params)  # type:ignore
