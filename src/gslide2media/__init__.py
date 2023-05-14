"""Entry point for gslide2media api.

gslide2media(options)

Returns:
    data: returns a generator.
"""
from typing import Generator

import sys

from gslide2media.options import Options
from gslide2media.models import File
from gslide2media.models import Folder
from gslide2media.models import Image
from gslide2media.models import Presentation
from gslide2media.models import Slide

from . import to_media

__all__ = ["Options"]


__version__ = "0.0.50"
__author__ = "David Midlo"


class APICaller(sys.modules[__name__].__class__):  # type: ignore # noqa:H601
    """APICaller. A Masquerade class.

    A class that extends sys.modules[__name__].__class__ (the gslide2media class)
    extends/overwrites with a __call__ method to allow the module to be callable.

    Returns:
        data: returns a generator.
    """

    def __call__(self, options: Options) -> Generator | None:  # noqa:BLK001
        """ """
        return to_media.main(options)


sys.modules[__name__].__class__ = APICaller
