# sourcery skip: hoist-statement-from-if, introduce-default-else
from typing import Generator

from rich import print

from gslide2media.cli import ArgParser
from gslide2media.google import GoogleClient
from gslide2media.options import Options

from gslide2media import config
from gslide2media.meta import Metadata
from gslide2media.drive import Folder
from gslide2media.presentation import Presentation

from gslide2media.enums import ExportFormats


class ToMedia:
    def __init__(self, options: Options) -> None:
        config.META = Metadata.metadata_singleton_factory()
        config.ARGS = ArgParser(options)()
        config.GOOGLE = GoogleClient(config.ARGS)

        # folder_id = "0B9ytToO3rm0mVW43MmttZTRJc2c"
        # folder = Folder(folder_id=folder_id)
        # folder.save_to_file(set(ExportFormats)

        # presentation_id = "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ"
        # presentation = Presentation(presentation_id=presentation_id)
        # presentation.save_to_file(set(ExportFormats))

        # root_folder = Folder()
        # for _ in root_folder.presentations.get():
        #     print(_)

        # folder_ids = ["1OotVomGB-_HvkgPO6nRQeJ5qQjR1yI-c", "0B7N3Xy--o-kQNkh0VkxKWVZueE0", "0B2uMDReI2FI0SlNKb3FZQmQxZWs"]
        # folder_list_of_folds = Folder(folder_ids=folder_ids)

        presentation_ids = [
            "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ",
            "19cm7dFMa7SLCp0DdD8skOpEbLa8dO3QUB9r0vhzTcXA",
        ]
        folder_list_of_presentations = Folder(presentation_ids=presentation_ids)

        folder_list_of_presentations.save(set(ExportFormats))

        if config.ARGS.presentation_id:
            ...
        elif config.ARGS.folder_id:
            ...

    def __call__(self) -> None | Generator:
        if not config.ARGS.download_directory.exists():
            config.ARGS.download_directory.mkdir(parents=True)

        if config.ARGS.from_api:
            if config.ARGS.presentation_id:
                ...

            elif config.ARGS.folder_id:
                ...


def main(options: Options | None = None) -> Generator | None:
    if not options:
        options = Options()

        ToMedia(options)()

        return None
    options.from_api = True
    return ToMedia(options)()
