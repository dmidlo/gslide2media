# sourcery skip: hoist-statement-from-if, introduce-default-else
from typing import Generator

from gslide2media.cli import ArgParser
from gslide2media.google import GoogleClient
from gslide2media.options import Options
from gslide2media.screen import Screen

from gslide2media import config
from gslide2media.meta import Metadata
from gslide2media.enums import OptionsSource

from rich import print


class ToMedia:
    def __init__(self, options: Options) -> None:
        config.META = Metadata.metadata_singleton_factory()

        config.ARGS = ArgParser(options)()

        if not config.SCREEN:
            config.SCREEN = config._default_screen

        if not config.GOOGLE:
            config.GOOGLE = GoogleClient()

        print(config.ARGS)
        raise SystemExit

    def __call__(self) -> None | Generator:
        if not config.ARGS.download_directory.exists():  # type:ignore
            config.ARGS.download_directory.mkdir(parents=True)  # type:ignore

        if config.ARGS.options_source is OptionsSource.API:
            ...


def main(options: Options | None = None) -> Generator | None:
    if not options:
        options = Options(options_source=OptionsSource.CLI)

        ToMedia(options)()

        return None

    options.options_source = OptionsSource.API
    return ToMedia(options)()
