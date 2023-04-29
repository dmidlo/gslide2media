import pytest

from sh import gslide2media
from pathlib import Path

import gslide2media
from gslide2media.options import Options


@pytest.fixture
def default_options() -> Options:
    return Options()


@pytest.mark.parametrize(
    "options_set, options_obj",
    [
        (
            "img_with_presentation_id",
            {
                "presentation_id": "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ",
                "create_images": True,
                "image_file_format": "svg",
                "save_images_to_file": True,
                "dpi": 300,
                "aspect_ratio": "16:10",
                "screen_width": 3456,
                "screen_height": 2234,
            },
        ),
        (
            "img_with_presentation_id",
            {
                "presentation_id": "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ",
                "create_images": True,
                "image_file_format": "png",
                "save_images_to_file": True,
                "dpi": 300,
                "aspect_ratio": "16:10",
                "screen_width": 3456,
                "screen_height": 2234,
            },
        ),
        (
            "img_with_presentation_id",
            {
                "presentation_id": "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ",
                "create_images": True,
                "image_file_format": "jpeg",
                "save_images_to_file": True,
                "dpi": 300,
                "aspect_ratio": "16:10",
                "screen_width": 3456,
                "screen_height": 2234,
            },
        ),
        (
            "img_with_folder_id",
            {
                "folder_id": "0B9ytToO3rm0mVW43MmttZTRJc2c",
                "run_all": False,
                "create_images": True,
                "image_file_format": "svg",
                "save_images_to_file": True,
                "dpi": 300,
                "aspect_ratio": "16:10",
                "screen_width": 3456,
                "screen_height": 2234,
            },
        ),
    ],
)
def test_gslide2media_API(options_set, options_obj, default_options):
    options = default_options
    options(**options_obj)

    to_media = gslide2media(options)

    for _ in to_media:
        ...

    assert True
