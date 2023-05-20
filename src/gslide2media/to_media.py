# sourcery skip: hoist-statement-from-if, introduce-default-else
from typing import Generator

from gslide2media.cli import ArgParser
from gslide2media.google import GoogleClient
from gslide2media.options import Options

from gslide2media import config
from gslide2media.meta import Metadata
from gslide2media.enums import OptionsSource


class ToMedia:
    def __init__(self, options: Options) -> None:
        config.META = Metadata.metadata_singleton_factory()

        config.ARGS = ArgParser(options)()

        config.GOOGLE = GoogleClient()

    def __call__(self) -> None | Generator:
        if not config.ARGS.download_directory.exists():  # type:ignore
            config.ARGS.download_directory.mkdir(parents=True)  # type:ignore

        if config.ARGS.from_api:
            ...


def main(options: Options | None = None) -> Generator | None:
    if not options:
        options = Options(options_source=OptionsSource.CLI)

        ToMedia(options)()

        return None

    options.from_api = True
    options.options_source = OptionsSource.API
    return ToMedia(options)()
