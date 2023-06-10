from typing import Optional

import sys
from pathlib import Path

from gslide2media.options import Options
from gslide2media import config

from .commands.auth import GoogleApiProject
from .commands.auth import ImportClientSecret
from .commands import OptionsHistory
from .commands import InteractivePrompt

from rich import print


def _check_for_tools_and_run(arg_namespace: Options):
    # TODO: Move this back to cli.py.
    # sourcery skip: merge-duplicate-blocks, merge-nested-ifs
    if sys.argv[1] == "auth":
        if len(sys.argv) == 3:
            if sys.argv[2] == "wizard":
                if client_secret_path := GoogleApiProject()():
                    config.META.import_google_client_secret_json(
                        client_secret_path
                    )  # type:ignore
                    Path(client_secret_path).unlink()

            elif sys.argv[2] == "import":
                if client_secret_path := ImportClientSecret()():
                    config.META.import_google_client_secret_json(client_secret_path)
                    Path(client_secret_path).unlink()

            raise SystemExit

    if sys.argv[1] == "history":
        if len(sys.argv) == 2:
            if history_set := OptionsHistory()():
                return history_set
            raise ValueError("No Options Chosen.")

    if sys.argv[1] == "interactive":
        arg_namespace._interactive = True
        arg_namespace = InteractivePrompt()(arg_namespace)

    return arg_namespace


def _fix_path_strings(arg_namespace: Options):
    # Fix --download-directory
    arg_namespace.download_directory = (
        Path(arg_namespace.download_directory)
        if arg_namespace.download_directory
        else Path(Path(".").resolve())
    )

    return arg_namespace


def _set_screen_dimensions(aspect_ratio: str, input_width: int, input_height: int):
    aspect_ratio_tuple = (
        tuple(aspect_ratio.split(":")) if aspect_ratio else "".split(":")
    )  # TODO: HACK until screen_types enum is implemented.
    aspect_width: int | None = (
        int(input_height * (int(aspect_ratio_tuple[0]) / int(aspect_ratio_tuple[1])))
        if input_height
        else None
    )
    aspect_height: Optional[int] | None = (
        int(input_width * (int(aspect_ratio_tuple[1]) / int(aspect_ratio_tuple[0])))
        if input_width
        else None
    )
    screen_width: Optional[int] = input_width or aspect_width
    screen_height: Optional[int] = input_height or aspect_height

    return screen_width, screen_height
