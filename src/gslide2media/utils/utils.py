"""Write a set of bytes to a file path.

Functions:
    save_image_to_file(image_path: Path, image_bytes: bytes) -> None

        Write a set of bytes to a file path.
"""

from pathlib import Path


def save_image_to_file(image_path: Path, image_bytes: bytes) -> None:
    """Write a set of bytes to a file path.

    Args:
        image_path (Path): The file path to write the image to.
        image_bytes (bytes): The set of bytes to write to the file path.

    Returns:
        None
    """
    with image_path.open("wb") as image:
        image.write(image_bytes)
