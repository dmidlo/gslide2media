from pathlib import Path
import sys

from typing import TYPE_CHECKING
from gslide2media.enums import OptionsSource

if TYPE_CHECKING:
    from .cli import ArgParser


def _check_should_print_help(obj: "ArgParser"):
    if not obj.arg_namespace.options_source is OptionsSource.API:
        if len(sys.argv) == 1:
            obj.print_help(sys.stdout)
            raise SystemExit(0)

        if sys.argv[1] == "auth":
            if len(sys.argv) == 2:
                obj.auth_parser.print_help()
                raise SystemExit

            if sys.argv[2] == "-h" or sys.argv[2] == "--help":
                obj.auth_parser.print_help()
                raise SystemExit


def _check_for_at_least_one_source():
    ...


def _check_int_or_none(value) -> int | None:
    return None if value.lower() == "none" else int(value)


def _check_string_is_pathlike(string: str) -> None | str:
    try:
        Path(string)  # noqa:F841
    except (TypeError, ValueError) as err:
        raise ValueError("directory or file path is not pathlike.") from err

    return string  # type:ignore
