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

        # folder_id = "0B1M-9VPKe8ZnU0phUmFYNkNOaEU"
        # folder = Folder(folder_id=folder_id)
        # folder.recursive_save(set(ExportFormats))

        # presentation_id = "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ"
        # presentation = Presentation(presentation_id=presentation_id)
        # presentation.save(set(ExportFormats))

        # root_folder = Folder()
        # for _ in root_folder.presentations.get():
        #     print(_)

        presentation_ids = [
            "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ",
            "19cm7dFMa7SLCp0DdD8skOpEbLa8dO3QUB9r0vhzTcXA",
        ]
        folder_ids = ["1OotVomGB-_HvkgPO6nRQeJ5qQjR1yI-c", "0B7N3Xy--o-kQNkh0VkxKWVZueE0", "0B2uMDReI2FI0SlNKb3FZQmQxZWs", "0B7N3Xy--o-kQfkh5aV9iMnRic0lTeE1mS2x4MUFmc0xxekV5amVhMTY4RkUxYmRYWnZjclU"]
        custom_presentation_name = "hello_gen_pres"
        custom_presentation_ids = [("1odV-0NE1J1h9IBuh_t2lRY8n_-84fwJZOWwzRtddOtc", "g3fd1e2d0d3_2_18"), ("1u0En6FFIQjmySLo0PxSdnm-gDkwFG6XH2VvCfJZ5V00", "p"), ("1Me_TyonOhtFjHkP7Ju-kjdAPI4-kFqfoTxLzE_rtELE", "g1cb6702d99_1_0")]
        custom_presentation = Presentation(presentation_id=custom_presentation_name, presentation_name=custom_presentation_name, parent="batch", slide_ids=custom_presentation_ids, is_batch=True)

        # folder_list_of_folds = Folder(presentations=[custom_presentation])
        # folder_list_of_folds = Folder(folder_ids=folder_ids)
        # folder_list_of_folds = Folder(presentation_ids=presentation_ids)
        # folder_list_of_folds = Folder(presentations=[custom_presentation], folder_ids=folder_ids)
        # folder_list_of_folds = Folder(presentations=[custom_presentation], presentation_ids=presentation_ids)
        # folder_list_of_folds = Folder(folder_ids=folder_ids, presentation_ids=presentation_ids)
        folder_list_of_folds = Folder(presentations=[custom_presentation], folder_ids=folder_ids, presentation_ids=presentation_ids)
        files = folder_list_of_folds.recursive_to_file({"mp4"})

        for to_file in files:
            for _ in to_file:
                print(_)

        # folder_list_of_presentations = Folder(presentation_ids=presentation_ids)

        # folder_list_of_presentations.save(set(ExportFormats))

        # custom_presentation.save({"svg", "png", "jpeg", "json", "mp4"})

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
