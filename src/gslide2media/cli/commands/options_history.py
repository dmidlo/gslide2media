from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.exceptions import InvalidArgument

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
            return Options(
                **inquirer.fuzzy(
                    message="Previous Option Sets. Choose One.",
                    choices=self.choices,
                    match_exact=True,
                ).execute()
            )
        except InvalidArgument as err:
            raise SystemExit("gslide2media: no history available.") from err
        except KeyboardInterrupt as err:
            raise SystemExit("gslide2media: user exited.") from err

    def sort_named_sets_to_top(self) -> None:
        named_sets, unnamed_sets = config.META.collate_named_and_unnamed_option_sets()
        self.choices = [*named_sets, *unnamed_sets]

    def sort_most_recently_used_to_top(self) -> None:
        self.choices = sorted(
            self.choices,
            key=lambda options_set: options_set.last_used_time_utc,
            reverse=True,
        )

    def pack_options_as_inquirer_choices(self) -> None:
        self.choices = [
            Choice(value=_, name=_.get_options_view()) for _ in self.choices
        ]

def options_name_dialog() -> str:
    return (
        inquirer.text(
            message="Enter a label name:",
            # TODO:  completer={}
        )
        .execute()
        .strip()
        .lower()
        .replace(" ", "-")
    )


def options_clear_confirm():
    return inquirer.confirm(
        message="Reset options history?",
        default=True,
    ).execute()
