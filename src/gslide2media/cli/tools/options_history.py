
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.exceptions import InvalidArgument

from rich import print

from gslide2media.options import Options
from gslide2media import config


class OptionsHistory:
    def __init__(self) -> None:
        self.choices: list
        self.sort_named_sets_to_top()
        self.sort_most_recently_used_to_top()
        self.pack_options_as_inquirer_choices()

    def __call__(self) -> Options:
        try:
            return Options(**inquirer.fuzzy(
                message="Previous Option Sets. Choose One.",
                choices=self.choices,
                match_exact=True,
            ).execute())
        except InvalidArgument as err:
            raise SystemExit("gslide2media: no history available.") from err
        except KeyboardInterrupt as err:
            raise SystemExit("gslide2media: user exited.") from err

    def sort_named_sets_to_top(self) -> None:
        named_sets, unnamed_sets = config.META.collate_named_and_unnamed_option_sets()
        self.choices = [*named_sets, *unnamed_sets]
    
    def sort_most_recently_used_to_top(self) -> None:
        self.choices = sorted(self.choices, key=lambda options_set: options_set._last_used_time_utc, reverse=True)

    def pack_options_as_inquirer_choices(self) -> None:
        self.choices = [Choice(value=_, name=self.get_options_view(_)) for _ in self.choices]

    def get_options_view(self, options_set: Options) -> str:

        return (
            f"Label: {options_set._options_set_name}\n"
            f"    Sources:  presentation_id(s): {options_set.presentation_id}\n"
            f"              folder_id(s): {options_set.folder_id}\n"
            f"              custom_presentation(s): {options_set.custom_presentation}\n"
            f"    System:   file_format(s): {options_set.file_formats}\n"
            f"              download_directory: {options_set.download_directory}\n"
            f"              run_all: {options_set.run_all}\n"
            f"    Screen:   aspect_ratio: {options_set.aspect_ratio}\n"
            f"              dpi: {options_set.dpi}\n"
            f"              screen_width: {options_set.screen_width}\n"
            f"              screen_height: {options_set.screen_height}\n"
            f"    Video:    mp4_slide_duration_secs: {options_set.mp4_slide_duration_secs}\n"
            f"              mp4_total_video_duration: {options_set.mp4_total_video_duration}\n"
            f"              fps: {options_set.fps}\n"
            f"    Image:    jpeg_quality: {options_set.jpeg_quality}\n"
            f"    API:      save_to_file: {options_set.save_to_file}\n"
        )
