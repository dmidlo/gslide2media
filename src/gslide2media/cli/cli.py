import sys
import argparse

from gslide2media.options import Options
from gslide2media.enums import OptionsSource
from gslide2media import config

from .validators import _check_int_or_none
from .validators import _check_string_is_pathlike
from .validators import _check_allow_only_mp4_slide_or_total_duration_not_both
from .validators import _check_should_print_help
from .modifiers import _check_for_tools_and_run
from .modifiers import _fix_path_strings
from .modifiers import _set_screen_dimensions

default_options = Options(_options_source=OptionsSource.DEFAULT)


class ArgParser(argparse.ArgumentParser):
    def __init__(self, options: Options = default_options, prog="gslide2media"):
        self.formatter_width = 140
        self.max_help_position = 140
        super().__init__(
            prog=prog,
            usage="\n  gslide2media [options]\n  gslide2media interactive [options]\n  gslide2media history [args|command]\n  gslide2media auth [command]",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.arg_namespace = options
        self._default_args = self.arg_namespace.__dict__
        self.set_defaults(**self._default_args)
        self._build_parser()

    def __call__(self) -> Options:
        """Collect and process settings from CLI or API.

        Returns:
            Options: arg_namespace for config.ARGS
        """

        self._set_args()
        _check_should_print_help(self)
        self.arg_namespace = _check_for_tools_and_run(self.arg_namespace)
        self._sanitize_input()

        self.arg_namespace.options_set_name = "c"

        # update_options_history()  this will be in meta.
        if self.arg_namespace._remove_history_option:
            config.META.remove_options_set(self.arg_namespace)
        elif self.arg_namespace._clear_history:
            config.META.clear_options_history(self.arg_namespace)
        elif self.arg_namespace.label:
            self.arg_namespace = config.META.get_options_set_by_label(self.arg_namespace.label)
        config.META.add_option_set(self.arg_namespace)

        return self.arg_namespace

    def _build_parser(self):
        self.subparsers = self.add_subparsers(
            title="Available Commands", parser_class=argparse.ArgumentParser, metavar=""
        )

        self.interactive_parser = self.subparsers.add_parser(
            "interactive",
            help="start gslide2media in interactive mode",
            usage="gslide2media interactive",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.interactive_parser.set_defaults(_interactive=True)

        self.history_parser = self.subparsers.add_parser(
            "history",
            help="start gslide2media with a previously used options set",
            usage=(
                "\n  gslide2media history"
                "\n  gslide2media history --label <NamedOptionSet>"
                "\n  gslide2media history set-label"
                "\n  gslide2media history remove"
                "\n  gslide2media history remove --label <NamedOptionSet>"
                "\n  gslide2media history clear"
                "\n  gslide2media history clear --force"
            ),
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )

        self.history_subparsers = self.history_parser.add_subparsers(title="commands", parser_class=argparse.ArgumentParser, metavar="")

        self.history_set_label = self.history_subparsers.add_parser(
            "set-label",
            help=(
                "Add a label to to an options set to create a named option set using an interactive prompt."
            ),
            usage="\n  gslide2media history set-label",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),

        )
        self.history_set_label.set_defaults(set_label=True)

        self.history_remove = self.history_subparsers.add_parser(
            "remove",
            help=(
                "Remove an Options Set from history."
            ),
            usage="\n  gslide2media history remove\n  gslide2media history remove --label <NamedOptionSet>\n accepts --force to skip confirm.",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),

        )
        self.history_remove.set_defaults(_remove_history_option=True)

        self.history_clear = self.history_subparsers.add_parser(
            "clear",
            help=(
                "Clears Options history."
            ),
            usage="\n  gslide2media history clear\n  gslide2media history clear --force",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),

        )
        self.history_clear.set_defaults(_clear_history=True)

        self.auth_parser = self.subparsers.add_parser(
            "auth",
            help=("Configure authorization for Google APIs."),
            usage="gslide2media auth [command]",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )

        self.auth_subparsers = self.auth_parser.add_subparsers(
            title="Auth Tools", parser_class=argparse.ArgumentParser, metavar=""
        )
        self.tool_auth_google_api_project_parser = self.auth_subparsers.add_parser(
            "wizard",
            help=(
                "A CLI-based walk-through for the process of creating a Google Developer project, generating a client_secret*.json, and importing it to gslide2media."
            ),
            usage="gslide2media auth wizard",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.tool_auth_google_api_project_parser.set_defaults(
            _tool_auth_google_api_project=True
        )

        self.tool_import_client_secret_parser = self.auth_subparsers.add_parser(
            "import",
            help=(
                "Import a Google Developer project's client_secret*.json."
            ),
            usage="gslide2media auth import",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.tool_import_client_secret_parser.set_defaults(
            _tool_import_client_secret=True
        )

    def _set_args(self):
        self._add_standard_args(self)
        self._add_options_history_args(self.history_parser)
        self._add_options_history_args(self.history_remove)
        self._add_clear_force_arg(self.history_clear)

    def _prepare_from_api_args(self):
        """Build the args list from api Options.

        Returns:
            list: args
        """
        args = []
        if self.arg_namespace.folder_id:
            args.append("folder")
            args.extend(["--folder-id", self.arg_namespace.folder_id])

            if self.arg_namespace.run_all:
                args.append("--run-all")

        elif self.arg_namespace.presentation_id:
            args.append("presentation")
            args.extend(["--presentation-id", self.arg_namespace.presentation_id])

        if self.arg_namespace.image_file_format:
            args.extend(["--image-file-format", self.arg_namespace.image_file_format])

        if self.arg_namespace.dpi:
            args.extend(["--dpi", str(self.arg_namespace.dpi)])

        if self.arg_namespace.aspect_ratio:
            args.extend(["--aspect-ratio", self.arg_namespace.aspect_ratio])

        if self.arg_namespace.screen_width:
            args.extend(["--screen-width", str(self.arg_namespace.screen_width)])

        if self.arg_namespace.screen_height:
            args.extend(["--screen-height", str(self.arg_namespace.screen_height)])

        if self.arg_namespace.download_directory:
            args.extend(["--download-directory", self.arg_namespace.download_directory])

        if self.arg_namespace.credentials_pattern:
            args.extend(
                ["--credentials-pattern", self.arg_namespace.credentials_pattern]
            )

        if self.arg_namespace.credentials_file:
            args.extend(["--credentials-file", self.arg_namespace.credentials_file])

        if self.arg_namespace.token_pattern:
            args.extend(["--token-pattern", self.arg_namespace.token_pattern])

        if self.arg_namespace.token_file:
            args.extend(["--token-file", self.arg_namespace.token_file])

        if self.arg_namespace.mp4_slide_duration_secs:
            args.extend(
                [
                    "--mp4-slide-duration-secs",
                    str(self.arg_namespace.mp4_slide_duration_secs),
                ]
            )

        if self.arg_namespace.mp4_total_video_duration:
            args.extend(
                [
                    "--mp4-total-video-duration",
                    str(self.arg_namespace.mp4_total_video_duration),
                ]
            )

        if self.arg_namespace.save_images_to_file:
            args.append("--save-images-to-file")

        if self.arg_namespace.save_mp4_to_file:
            args.append("--save-mp4-to-file")
        return args

    def _sanitize_input(self):

        # Pre-parse
        _check_allow_only_mp4_slide_or_total_duration_not_both(
            self.arg_namespace.mp4_slide_duration_secs,
            self.arg_namespace.mp4_total_video_duration,
        )

        # Parse
        if "gslide2media" not in sys.argv[0] and self.arg_namespace._from_api:
            args = self._prepare_from_api_args()
            self.parse_args(args, namespace=self.arg_namespace)
        else:
            # Get the args from sys.argv
            self.parse_args(namespace=self.arg_namespace)

        # Post-Parse
        (
            self.arg_namespace.screen_width,
            self.arg_namespace.screen_height,
        ) = _set_screen_dimensions(
            self.arg_namespace.aspect_ratio,
            self.arg_namespace.screen_width,
            self.arg_namespace.screen_height,
        )

        self.arg_namespace = _fix_path_strings(self.arg_namespace)

    def _add_standard_args(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--presentation-id",
            nargs="+",
            type=str,
            help=(
                "Space-separated Google slides presentation ids to convert. "
                "e.g. --presentation-id presentation_id ... ..."
            ),
        )

        parser.add_argument(
            "--folder-id",
            nargs="+",
            type=str,
            help=(
                "Space-separated Google Drive folder ids to search for slides presentations. "
                "e.g. --folder-id folder_id ... ..."
            ),
        )

        parser.add_argument(
            "--custom-presentation",
            nargs="+",
            type=str,
            help=(
                "Build custom mp4s from a JSON encoded list of lists. "
                "(a single slide is a comma separated string of a presentation_id and slide_id) "
                "e.g. --custom-presentation "
                " \"[['presentation_id,slide_id', '...,...', '...,...'], [...], [...]]\""
            ),
        )

        parser.add_argument(
            "--file-formats",
            nargs="+",
            type=str,
            default="svg",
            choices=["svg", "png", "jpeg"],
            help="Image format to use when exporting images.  svg, png, jpeg.",
        )

        parser.add_argument(
            "--run-all",
            action="store_true",
            help=(
                "When converting a folder of presentations, run only on first discovered "
                "presentation.  Used for confirming workflow."
            ),
        )

        self._add_set_label_arg(parser)

        parser.add_argument(
            "--download-directory",
            type=(lambda arg: _check_string_is_pathlike(arg)),
            help="Path to working directory. creates if not exist.",
        )

        mp4 = parser.add_argument_group("mp4")
        mp4.add_argument(
            "--mp4-slide-duration-secs",
            type=int,
            default=20,
            help=(
                "Amount of time in secs each slide should play when presentation "
                "is converted to video"
            ),
        )
        mp4.add_argument(
            "--mp4-total-video-duration",
            type=_check_int_or_none,
            default=None,
            help=(
                "Total duration of mp4 video.  Subject to system modification based on "
                "--mp4-slide-duration-secs or if presentation has transitions or embedded video."
            ),
        )
        mp4.add_argument(
            "--fps",
            type=int,
            default=10,
            help=(
                "Base frames-per-second. Subject to system modification if presentation has "
                "transitions or embedded video."
            ),
        )

        image = parser.add_argument_group("image")

        image.add_argument(
            "--jpeg-quality",
            type=int,
            default=90,
            help=(
                "Quality level of exported jpeg images."
            ),
        )

        screen = parser.add_argument_group("screen")

        screen.add_argument(
            "--aspect-ratio",
            type=str,
            default="16:9",
            help="Destination screen's aspect ratio, e.g. 16:9, delimited by ':'",
        )
        screen.add_argument(
            "--dpi",
            type=int,
            default=300,
            help="Dots Per Inch (DPI) of output image(s) or video(s).",
        )
        screen.add_argument(
            "--screen-width",
            type=int,
            default=3456,
            help="Screen width in Pixels of output image(s) or video(s).",
        )
        screen.add_argument(
            "--screen-height",
            type=int,
            default=2234,
            help="Screen height in Pixels of output image(s) or video(s).",
        )

    def _add_set_label_arg(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--set-label",
            action="store_true",
            help=(
                "Save Options as a labeled option set."
            ),
        )

    def _add_options_history_args(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--label",
            type=str,
            help=(
                "call gslide2media with a Named Option Set."
            ),
        )

    def _add_clear_force_arg(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "call gslide2media with a Named Option Set."
            ),
            dest="clear_force"
        )

