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

    return arg_namespace


def _fix_path_strings(arg_namespace: Options):
    # Fix --download-directory
    arg_namespace.download_directory = (
        Path(arg_namespace.download_directory)
        if arg_namespace.download_directory
        else Path(Path(".").resolve())
    )

    return arg_namespace


def _check_numeric_one_or_the_other_not_both(**kwargs):
    arg1_name, arg2_name, _ = kwargs.keys()
    arg1, arg2, instance_type = kwargs.values()

    if (isinstance(arg1, str) and arg1.isnumeric()) or isinstance(arg1, (int, float)):
        if int(arg1) == 0:
            arg1 = None
        else:
            if isinstance(instance_type, int):
                arg1 = int(arg1)
            if isinstance(instance_type, float):
                arg1 = float(arg1)

    if (isinstance(arg2, str) and arg2.isnumeric()) or isinstance(arg2, (int, float)):
        if int(arg2) == 0:
            arg2 = None
        else:
            if isinstance(instance_type, int):
                arg2 = int(arg2)
            if isinstance(instance_type, float):
                arg2 = float(arg2)

    if arg1 is not None and arg2 is not None:
        raise ValueError(
            f"Must Specify either '{arg1_name}' or '{arg2_name}', "
            "but not both."
        )
    
    return arg1, arg2

    raise SystemExit
