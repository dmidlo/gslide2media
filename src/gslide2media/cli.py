from typing import Optional

import sys
import argparse
from pathlib import Path

from gslide2media.options import Options
from gslide2media.google.auth import AuthGoogle
from gslide2media.config import API_SCOPES
from gslide2media.tools.google_api_project import GoogleApiProject
from gslide2media import config

default_options = Options()


class ArgParser(argparse.ArgumentParser):
    def __init__(self, options: Options = default_options, prog="gslide2media"):
        self.formatter_width = 140
        self.max_help_position = 140
        super().__init__(
            prog=prog,
            usage="gslide2media {img, mp4} {presentation, folder} [options]",
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
        self._check_for_tools_and_run()
        self._sanitize_input()
        self._fix_path_strings()
        return self.arg_namespace

    def _build_parser(self):
        self.subparsers = self.add_subparsers(
            title="Available Commands", parser_class=argparse.ArgumentParser, metavar=""
        )

        self.img_parser = self.subparsers.add_parser(
            "img",
            help=(
                "command for exporting google slides presentation(s) as (an) image(s). "
                "svg, png, or jpeg"
            ),
            usage="gslide2media img {presentation, folder} [options]",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.img_parser.set_defaults(create_images=True)

        self.mp4_parser = self.subparsers.add_parser(
            "mp4",
            help=(
                "command for exporting google slides " "presentation(s) as (an) mp4(s)."
            ),
            usage="gslide2media mp4 {presentation, folder} [options]",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.mp4_parser.set_defaults(create_mp4s=True)

        self.img_subparsers = self.img_parser.add_subparsers(
            title="slide source", parser_class=argparse.ArgumentParser, metavar=""
        )
        self.mp4_subparsers = self.mp4_parser.add_subparsers(
            title="slide source", parser_class=argparse.ArgumentParser, metavar=""
        )

        self.img_folder_parser = self.img_subparsers.add_parser(
            "folder",
            help=(
                "command for exporting a all slides presentations from a google drive "
                "folder as directories of sorted images. svg, png, jpeg."
            ),
            usage=(
                "gslide2image img folder [-h] -i FOLDER_ID [-r] [--save-images-to-file] [-f "
                "{svg,png,jpeg}] [-d DOWNLOAD_DIRECTORY] [--aspect-ratio ASPECT_RATIO][--dpi DPI] "
                "[--screen-width SCREEN_WIDTH] [--screen-height SCREEN_HEIGHT] "
                "[--credentials-pattern CREDENTIALS_PATTERN][--credentials-file CREDENTIALS_FILE] "
                "[--token-pattern TOKEN_PATTERN] [--token-file TOKEN_FILE]"
            ),
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.img_presentation_parser = self.img_subparsers.add_parser(
            "presentation",
            help=(
                "command for exporting the slides of a goolge slides presentation as "
                "individual images. in svg, png, or jpeg"
            ),
            usage=(
                "gslide2media img presentation [-h] [-i, PRESENTATION_ID] "
                "[--save-images-to-file] [-f {svg,png,jpeg}] [-d DOWNLOAD_DIRECTORY] "
                "[--aspect-ratio ASPECT_RATIO] [--dpi DPI] [--screen-width SCREEN_WIDTH] "
                "[--screen-height SCREEN_HEIGHT] [--credentials-pattern CREDENTIALS_PATTERN] "
                "[--credentials-file CREDENTIALS_FILE] [--token-pattern TOKEN_PATTERN] "
                "[--token-file TOKEN_FILE]"
            ),
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.mp4_folder_parser = self.mp4_subparsers.add_parser(
            "folder",
            help=(
                "command for exporting a all slides presentations from a google drive "
                "folder as directories of sorted mp4s."
            ),
            usage=(
                "gslide2image mp4 folder [-h] -i FOLDER_ID [-r] [--save-images-to-file] "
                "[-s MP4_SLIDE_DURATION_SECS] [-t MP4_TOTAL_VIDEO_DURATION] [-d "
                "DOWNLOAD_DIRECTORY] [--aspect-ratio ASPECT_RATIO] [--dpi DPI] [--screen-width "
                "SCREEN_WIDTH] [--screen-height SCREEN_HEIGHT]"
            ),
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.mp4_presentation_parser = self.mp4_subparsers.add_parser(
            "presentation",
            help=(
                "command for exporting the slides of a goolge slides presentation as an mp4 video."
            ),
            usage=(
                "gslide2image mp4 presentation [-h] [-i, PRESENTATION_ID] "
                "[--save-images-to-file] [-s MP4_SLIDE_DURATION_SECS] [-t "
                "MP4_TOTAL_VIDEO_DURATION] [-d DOWNLOAD_DIRECTORY] [--aspect-ratio ASPECT_RATIO]"
                " [--dpi DPI] [--screen-width SCREEN_WIDTH] [--screen-height SCREEN_HEIGHT]"
            ),
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
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
        self.interactive_parser.set_defaults(interactive=True)

        self.generate_parser = self.subparsers.add_parser(
            "generate",
            help=("various generate helpful for the use of gslide2media."),
            usage="gslide2media generate [command]",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.generate_subparsers = self.generate_parser.add_subparsers(
            title="Categories", parser_class=argparse.ArgumentParser, metavar=""
        )
        self.generate_auth_google_api_project_parser = self.generate_subparsers.add_parser(
            "google-client-secret",
            help=(
                "Opens Instructions in default web browser on how to set up a google api project "
                "and download a client_secret*.json file."
            ),
            usage="gslide2media generate auth google-client-secret",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.generate_auth_google_api_project_parser.set_defaults(
            tool_auth_google_api_project=True
        )

        self.toots_auth_google_generate_and_refresh_token_parser = self.generate_subparsers.add_parser(
            "google-token",
            help=(
                "Generates a new or refreshes an existing token.json.  If one doesn't already "
                "exist, a google OAuth workflow is initiated using the default web browser."
            ),
            usage="gslide2media generate auth google-token",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.toots_auth_google_generate_and_refresh_token_parser.set_defaults(
            tool_google_auth_token=True
        )

        self.import_parser = self.subparsers.add_parser(
            "import",
            help="import google auth credentials.",
            usage="gslide2media import [command]",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )
        self.import_subparsers = self.import_parser.add_subparsers(
            title="import", parser_class=argparse.ArgumentParser, metavar=""
        )
        self.import_auth_google_api_project_parser = self.import_subparsers.add_parser(
            "google-client-secret",
            help=(
                "Opens Instructions in default web browser on how to set up a google api project "
                "and download a client_secret*.json file."
            ),
            usage="gslide2media generate auth google-client-secret",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog=prog,
                width=self.formatter_width,
                max_help_position=self.max_help_position,
            ),
        )

    def _set_args(self):
        self._add_folder_args(self.img_folder_parser)
        self._add_image_args(self.img_folder_parser)
        self._add_standard_args(self.img_folder_parser)

        self._add_presentation_args(self.img_presentation_parser)
        self._add_image_args(self.img_presentation_parser)
        self._add_standard_args(self.img_presentation_parser)

        self._add_folder_args(self.mp4_folder_parser)
        self._add_mp4_args(self.mp4_folder_parser)
        self._add_standard_args(self.mp4_folder_parser)

        self._add_presentation_args(self.mp4_presentation_parser)
        self._add_mp4_args(self.mp4_presentation_parser)
        self._add_standard_args(self.mp4_presentation_parser)

    def _prepare_from_api_args(self):
        """Build the args list from api Options.

        Returns:
            list: args
        """
        args = []
        if self.arg_namespace.create_images:
            args.append("img")
        elif self.arg_namespace.create_mp4s:
            args.append("mp4")
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
        self._check_should_print_help()

        self.check_allow_only_presentation_or_folder_not_both(
            self.arg_namespace.folder_id, self.arg_namespace.presentation_id
        )

        (
            self.arg_namespace.screen_width,
            self.arg_namespace.screen_height,
        ) = self.set_screen_dimensions(
            self.arg_namespace.aspect_ratio,
            self.arg_namespace.screen_width,
            self.arg_namespace.screen_height,
        )

        self.check_allow_only_create_images_or_mp4_not_both(
            self.arg_namespace.create_images, self.arg_namespace.create_mp4s
        )

        self.check_allow_only_mp4_slide_or_total_duration_not_both(
            self.arg_namespace.mp4_slide_duration_secs,
            self.arg_namespace.mp4_total_video_duration,
        )

        if "gslide2media" not in sys.argv[0] and self.arg_namespace.from_api:
            args = self._prepare_from_api_args()
            self.parse_args(args, namespace=self.arg_namespace)
        else:
            # Get the args from sys.argv
            self.parse_args(namespace=self.arg_namespace)

    def _check_for_tools_and_run(self):
        if len(sys.argv) >= 2 and len(sys.argv) <= 3:
            if sys.argv[1] == "generate":
                if len(sys.argv) == 3:
                    if sys.argv[2] == "google-client-secret":
                        self.arg_namespace.tool_auth_google_api_project = True
                        client_secret_path = GoogleApiProject()()
                        config.META.import_google_client_secret_json(client_secret_path)
                    elif sys.argv[2] == "google-token":
                        self.arg_namespace.tool_google_auth_token = True
                    raise SystemExit

    def _check_should_print_help(self):
        if not self.arg_namespace.from_api:
            if len(sys.argv) == 1:
                self.print_help(sys.stdout)
                raise SystemExit(0)

            if len(sys.argv) == 2:
                if sys.argv[1] == "img":
                    self.img_parser.print_help(sys.stdout)
                elif sys.argv[1] == "mp4":
                    self.mp4_parser.print_help(sys.stdout)
                elif sys.argv[1] == "generate":
                    self.generate_parser.print_help(sys.stdout)
                elif sys.argv[1] == "import":
                    self.import_parser.print_help(sys.stdout)
                raise SystemExit

            if len(sys.argv) >= 2 and len(sys.argv) <= 3:
                if sys.argv[1] == "img":
                    if sys.argv[2] == "folder":
                        self.img_folder_parser.print_help()
                    elif sys.argv[2] == "presentation":
                        self.img_presentation_parser.print_help()
                elif sys.argv[1] == "mp4":
                    if sys.argv[2] == "folder":
                        self.mp4_folder_parser.print_help()
                    elif sys.argv[2] == "presentation":
                        self.mp4_presentation_parser.print_help()
                raise SystemExit

    def _add_standard_args(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--download-directory",
            type=(lambda arg: self._validate_is_pathlike(arg)),
            help="Path to working directory. creates if not exist.",
        )

        dimensions = parser.add_argument_group("dimensions")

        dimensions.add_argument(
            "--aspect-ratio",
            type=str,
            default="16:9",
            help="Destination screen's aspect ratio, e.g. 16:9, delimited by ':'",
        )
        dimensions.add_argument(
            "--dpi",
            type=int,
            default=300,
            help="Dots Per Inch (DPI) of output image(s) or video(s).",
        )
        dimensions.add_argument(
            "--screen-width",
            type=int,
            default=3456,
            help="Screen width in Pixels of output image(s) or video(s).",
        )
        dimensions.add_argument(
            "--screen-height",
            type=int,
            default=2234,
            help="Screen height in Pixels of output image(s) or video(s).",
        )

    def _add_image_args(self, parser: argparse.ArgumentParser):
        images = parser.add_argument_group("images")

        images.add_argument(
            "--save-images-to-file",
            action="store_false",
            help="image format to use when exporting images.  svg, png, jpeg.",
        )

        parser.add_argument(
            "--image-file-format",
            type=str,
            default="svg",
            choices=["svg", "png", "jpeg"],
            help="image format to use when exporting images.  svg, png, jpeg.",
        )

    def _add_mp4_args(self, parser: argparse.ArgumentParser):
        images = parser.add_argument_group("images")

        images.add_argument(
            "--save-images-to-file",
            action="store_true",
            help="image format to use when exporting images.  svg, png, jpeg.",
        )

        mp4 = parser.add_argument_group("mp4")
        parser.add_argument(
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
            type=self._int_or_none,
            default=None,
            help=(
                "Amount of time in secs each slide should play when presentation "
                "is converted to video"
            ),
        )
        mp4.add_argument(
            "--save-mp4-to-file",
            action="store_false",
            help="image format to use when exporting images.  svg, png, jpeg.",
        )

    def _add_folder_args(self, parser: argparse.ArgumentParser):
        folder = parser.add_argument_group("folder")
        parser.add_argument(
            "--folder-id",
            type=str,
            required=True,
            help="Google Drive folder id to search for slides presentations.",
        )
        folder.add_argument(
            "--run-all",
            action="store_true",
            help=(
                "When converting a folder of presentations, run only on first discovered "
                "presentation.  Used for confirming workflow."
            ),
        )

    def _add_presentation_args(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--presentation-id",
            type=str,
            help="Google slides presentation id to convert.",
        )

    def _int_or_none(self, value):
        if value.lower() == "none":
            return None
        return int(value)

    def _validate_is_pathlike(self, string: str) -> None:
        try:
            path = Path(string)
        except (TypeError, ValueError) as err:
            raise ValueError("directory or file path is not pathlike.") from err

        return string

    def _fix_path_strings(self):
        # Fix --download-directory
        self.arg_namespace.download_directory = (
            Path(self.arg_namespace.download_directory)
            if self.arg_namespace.download_directory
            else Path(Path(".").resolve())
        )

        # Fix --token-file
        try:
            if (
                self.arg_namespace.token_file
                and Path(self.arg_namespace.token_file).is_dir()
            ):
                self.arg_namespace.token_file = next(
                    Path(self.arg_namespace.token_file).glob(
                        self.arg_namespace.token_pattern
                    ),
                    None,
                )

            self.arg_namespace.token_file = (
                Path(self.arg_namespace.token_file)
                if self.arg_namespace.token_file
                else next(
                    self.arg_namespace.download_directory.glob(
                        self.arg_namespace.token_pattern
                    )
                )
            )
        except StopIteration:
            print(
                (
                    "token.json file not found that matches the pattern in the directory provided."
                    f"  pattern: {self.arg_namespace.token_pattern}"
                    f"  directory: {self.arg_namespace.download_directory}\n"
                    "Attempting OAuth Flow.."
                )
            )

            auth = AuthGoogle(
                Path(self.arg_namespace.download_directory, "token.json"),
                API_SCOPES,
                self.arg_namespace.credentials_file,
            )

    @staticmethod
    def check_allow_only_presentation_or_folder_not_both(folder_id, presentation_id):
        if folder_id and presentation_id:
            raise ValueError(
                "Must Specify either 'folder_id' or 'presentation_id', but not both."
            )

    @staticmethod
    def set_screen_dimensions(aspect_ratio: str, input_width: int, input_height: int):
        aspect_ratio_tuple = tuple(aspect_ratio.split(":"))
        aspect_width: int | None = (
            int(
                input_height * (int(aspect_ratio_tuple[0]) / int(aspect_ratio_tuple[1]))
            )
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

    @staticmethod
    def check_allow_only_create_images_or_mp4_not_both(
        create_images: bool, create_mp4s: bool
    ) -> None:
        if create_images and create_mp4s:
            raise ValueError(
                "Must Specify either 'create_images' or 'create_mp4s', but not both."
            )

    @staticmethod
    def check_allow_only_mp4_slide_or_total_duration_not_both(
        mp4_slide_duration_secs: int, mp4_total_duration_secs: int
    ):
        if mp4_slide_duration_secs and mp4_total_duration_secs:
            raise ValueError(
                "Must Specify either 'mp4_slide_duration_secs' or 'mp4_total_video_duration', "
                "but not both."
            )

    @staticmethod
    def convert_options_to_string(options: Options) -> Options:
        for item in vars(options):
            if isinstance(getattr(options, item), int):
                setattr(options, item, str(getattr(options, item)))

            if isinstance(getattr(options, item), bool):
                setattr(options, item, str(getattr(options, item)))

            if isinstance(getattr(options, item), str):
                setattr(options, item, str(getattr(options, item)))

            if isinstance(getattr(options, item), Path):
                setattr(options, item, str(getattr(options, item)))

            if not getattr(options, item):
                setattr(options, item, "")

        return options
