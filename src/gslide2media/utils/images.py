"""
Converts SVG images to PNG and JPEG formats.

Dependencies:
    - cairosvg
    - PIL

Functions:
    - convert_svg_bytes_to_png_bytes(
            svg_bytes: bytes,
            dpi: int,
            parent_width: Optional[int],
            parent_height: Optional[int]
        ) -> bytes
        Converts SVG bytes to PNG bytes.
        Returns:
            bytes: The PNG bytes.
    - convert_png_bytes_to_jpg_bytes(png_bytes: bytes) -> bytes
        Converts PNG bytes to JPEG bytes.
        Returns:
            bytes: The JPEG bytes.
"""
from typing import Optional

from io import BytesIO

from cairosvg import svg2png
from PIL import Image


def convert_svg_bytes_to_png_bytes(
    svg_bytes: bytes,
    dpi: int,
    parent_width: Optional[int],
    parent_height: Optional[int],
) -> bytes:
    """Converts SVG bytes to PNG bytes.

    Args:
        svg_bytes (bytes): The SVG bytes to convert.
        dpi (int): The resolution in dots per inch for the output PNG image.
        parent_width (Optional[int]): The optional width of the parent container for the SVG image.
        parent_height (Optional[int]):
                                The optional height of the parent container for the SVG image.

    Returns:
        bytes: The PNG bytes of the converted image.
    """
    return svg2png(
        svg_bytes,
        dpi=dpi,
        parent_width=parent_width,
        parent_height=parent_height,
        output_width=parent_width,
        output_height=parent_height,
        unsafe=True,
    )


def convert_png_bytes_to_jpg_bytes(png_bytes: bytes) -> bytes:
    """Converts PNG bytes to JPEG bytes.

    Args:
        png_bytes (bytes): The PNG bytes to convert to JPEG.

    Returns:
        bytes: The JPEG bytes of the converted image.
    """
    image = Image.open(BytesIO(png_bytes))
    rgb_image = image.convert("RGB")
    jpeg_data = BytesIO()
    rgb_image.save(jpeg_data, format="JPEG")

    return jpeg_data.getvalue()
