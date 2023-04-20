# pylint: disable=invalid-name
"""gslide2media.

Allows gslide2media to be run as a module with
as >>> python -m gslide2media
"""

from . import to_media


def main() -> None:  # noqa:DAR401
    """Run to_media.main and raise SystemExit on completion.

    Raises:
        SystemExit: Exit when finished.
    """
    raise SystemExit(to_media.main())


if __name__ == "__main__":
    main()
