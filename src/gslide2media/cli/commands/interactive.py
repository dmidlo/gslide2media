"""TODO: These menus are going to be brittle. Working to mitigate that where possible."""
from typing import Any
from typing import Optional
from typing import Callable
from typing import Generator

from abc import ABC, abstractmethod
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.prompts.input import InputPrompt

from InquirerPy.utils import (
    InquirerPyDefault,
    InquirerPyKeybindings,
    InquirerPyMessage,
    InquirerPySessionResult,
    InquirerPyStyle,
    InquirerPyValidate,
)

from prompt_toolkit.completion import Completer
from prompt_toolkit.completion import Completion
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.completion.base import ThreadedCompleter

from rich import print

from gslide2media.options import Options
from gslide2media.google import GoogleClient
from gslide2media.enums import DriveTypes
from gslide2media.enums import ExportFormats
from gslide2media import config


class Prompt(ABC):
    @abstractmethod
    def __init__(self, arg_namespace: Options):
        self.arg_namespace = arg_namespace

    @abstractmethod
    def __call__(self) -> Options:
        ...

    @staticmethod
    @abstractmethod
    def message():
        ...

    @abstractmethod
    def prompt(self) -> Options:
        ...


class PresentationIDs(Prompt):
    def __init__(self, arg_namespace: Options):
        self.arg_namespace = arg_namespace

    def __call__(self) -> Options:
        self.prompt()
        return self.arg_namespace

    @staticmethod
    def message():
        return "Add presentation by ID"

    def prompt(self):
        presentation_id = inquirer.text(message="Enter a presentation ID:").execute()

        if self.arg_namespace.presentation_id:
            self.arg_namespace.presentation_id.append(presentation_id)
        else:
            self.arg_namespace.presentation_id = [presentation_id]

        if inquirer.confirm(
            message="Would you like to add another presentation ID?"
        ).execute():
            self.prompt()


class FolderIDs(Prompt):
    def __init__(self, arg_namespace: Options):
        self.arg_namespace = arg_namespace

    def __call__(self) -> Options:
        self.prompt()
        return self.arg_namespace

    @staticmethod
    def message():
        return "Add folder by ID"

    def prompt(self):
        folder_id = inquirer.text(message="Enter a folder ID:").execute()

        if self.arg_namespace.folder_id:
            self.arg_namespace.folder_id.append(folder_id)
        else:
            self.arg_namespace.folder_id = [folder_id]

        if inquirer.confirm(
            message="Would you like to add another folder ID?"
        ).execute():
            self.prompt()


class RunAll(Prompt):
    def __init__(self, arg_namespace: Options):
        self.arg_namespace = arg_namespace

    def __call__(self) -> Options:
        self.prompt()
        return self.arg_namespace

    @staticmethod
    def message():
        return "Run All"

    def prompt(self):
        run_all = inquirer.confirm(
            message="Process all presentations?",
            default=True,
        ).execute()

        self.arg_namespace.run_all = run_all


class DrivePathCompleter(Completer):
    def __init__(self, only_folders: bool = False, only_presentations: bool = False):
        self._only_folders = only_folders
        self._only_presentations = only_presentations
        self._delimiter = "/"

    def get_completions(
        self, document, complete_event
    ) -> Generator[Completion, None, None]:
        if "/" not in document.text:
            base_paths = {"drive", "shared"}
            for _ in base_paths:
                yield Completion(
                    text=_,
                    start_position=-1 * len(document.text),
                    display=_,
                )

        if document.text == "drive/" and len(document.text) == len("drive/"):
            root_folders: list[dict] = config.GOOGLE.get_folders_in_root()
            root_presentations: list[dict] = config.GOOGLE.get_presentations_in_root()

            for _ in root_folders:
                yield Completion(
                    f"{document.text}{_['id']}",
                    start_position=-1 * len(document.text + _["id"]),
                    display=f"{_['name']}/",
                )

            for _ in root_presentations:
                yield Completion(
                    f"{document.text}{_['id']}",
                    start_position=-1 * len(document.text + _["id"]),
                    display=_["name"],
                )
        elif document.text == "shared/" and len(document.text) == len("shared/"):
            shared_folders: list[dict] = config.GOOGLE.get_shared_folders()
            shared_presentations: list[dict] = config.GOOGLE.get_shared_presentations()
            
            for _ in shared_folders:
                yield Completion(
                    f"{document.text}{_['id']}",
                    start_position=-1 * len(document.text + _["id"]),
                    display=f"{_['name']}/",
                )

            for _ in shared_presentations:
                yield Completion(
                    f"{document.text}{_['id']}",
                    start_position=-1 * len(document.text + _["id"]),
                    display=_["name"],
                )
        elif document.text.endswith("/"):
            split_doc = document.text.strip().split("/")
            folder_id = split_doc[-2].split("/")[0]

            folders: list[dict] = config.GOOGLE.get_folders_from_drive_folder(folder_id)
            presentations: list[dict] = config.GOOGLE.get_presentations_from_drive_folder(folder_id)

            for _ in folders:
                yield Completion(
                    f"{document.text}{_['id']}",
                    start_position=-1 * len(document.text + _["id"]),
                    display=f"{_['name']}/",
                )

            for _ in presentations:
                yield Completion(
                    f"{document.text}{_['id']}",
                    start_position=-1 * len(document.text + _["id"]),
                    display=_["name"],
                )


class DrivePathPrompt(InputPrompt):
    def __init__(
        self,
        message: InquirerPyMessage,
        style: Optional[InquirerPyStyle] = None,
        vi_mode: bool = False,
        default: InquirerPyDefault = "",
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        long_instruction: str = "",
        multicolumn_complete: bool = False,
        validate: Optional[InquirerPyValidate] = None,
        invalid_message: str = "Invalid input",
        only_directories: bool = False,
        only_files: bool = False,
        transformer: Optional[Callable[[str], Any]] = None,
        filter: Optional[Callable[[str], Any]] = None,
        keybindings: Optional[InquirerPyKeybindings] = None,
        wrap_lines: bool = True,
        raise_keyboard_interrupt: bool = True,
        mandatory: bool = True,
        mandatory_message: str = "Mandatory prompt",
        session_result: Optional[InquirerPySessionResult] = None,
        input: Optional["Input"] = None,
        output: Optional["Output"] = None,
    ) -> None:
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            default=default,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            long_instruction=long_instruction,
            completer=ThreadedCompleter(
                DrivePathCompleter(
                    only_folders=only_directories, only_presentations=only_files
                )
            ),
            multicolumn_complete=multicolumn_complete,
            validate=validate,
            invalid_message=invalid_message,
            transformer=transformer,
            filter=filter,
            keybindings=keybindings,
            wrap_lines=wrap_lines,
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
            session_result=session_result,
            input=input,
            output=output,
        )

    def _pre_run_prompt_autocomplete(self):
        buffer = self._session.app.current_buffer

        if buffer.complete_state:
            buffer.complete_next()
        else:
            buffer.start_completion(select_first=False)

    def _run(self) -> str:
        return self._session.prompt(
            default=self._default, pre_run=self._pre_run_prompt_autocomplete, complete_while_typing=True
        )

    async def _run_async(self) -> Any:
        return await self._session.prompt_async(
            default=self._default, pre_run=self._pre_run_prompt_autocomplete, complete_while_typing=True
        )


inquirer.drivepath = DrivePathPrompt


class Browse(Prompt):
    def __init__(self, arg_namespace: Options):
        if not config.GOOGLE:
            config.GOOGLE = GoogleClient()

        self.presentations: list = []
        self.folders: list = []
        self.arg_namespace = arg_namespace

    def __call__(self) -> Options:
        self.prompt()
        if not self.arg_namespace.folder_id:
            self.arg_namespace.folder_id = self.folders
        else:
            self.arg_namespace.folder_id.extend(self.folders)
        
        if not self.arg_namespace.presentation_id:
            self.arg_namespace.presentation_id = self.presentations
        else:
            self.arg_namespace.folder_id.extend(self.presentations)

        return self.arg_namespace

    @staticmethod
    def message():
        return "Browse Drive for Folders & Presentations"

    def prompt(self):
        path = inquirer.drivepath(
            message="Enter path to a folder or presentation:",
            instruction="'/' enables autocompletion for folders.",
        ).execute()

        resource_id = path.split("/")[-1] if path.split("/")[-1] != '' else path.split("/")[-2]
        resource_type = config.GOOGLE.get_resource_type(resource_id)

        if resource_type is DriveTypes.FOLDER:
            self.folders.append(resource_id)
        if resource_type is DriveTypes.PRESENTATION:
            self.presentations.append(resource_id)

        if inquirer.confirm(
            message="Would you like to add another Folder or Presentation?",
            default=True,
        ).execute():
            self.prompt()


class PresentationPrompt(Prompt):
    def __init__(self, arg_namespace: Options):
        self.arg_namespace = arg_namespace

        self.prompts: list = [Browse, RunAll, PresentationIDs, FolderIDs]

    def __call__(self):
        self.prompt()
        return self.arg_namespace

    @staticmethod
    def message():
        return "Presentation Sources"

    def prompt(self):
        exit_code = True

        choices = InteractivePrompt.get_subprompt_messages(self)
        additional_choices = ["back"]
        choices.extend(additional_choices)

        while exit_code:
            subprompt_select = inquirer.rawlist(
                message="Set Options Group:", choices=choices
            ).execute()

            prompt_index = (
                choices.index(subprompt_select)
                if subprompt_select not in additional_choices
                else None
            )

            if prompt_index is not None:
                self.arg_namespace = self.prompts[prompt_index](self.arg_namespace)()
            else:
                exit_code = False


class FormatsPrompt:
    def __init__(self, arg_namespace: Options):
        self.arg_namespace = arg_namespace

        self.file_formats: list = []

    def __call__(self):
        self.prompt()
        return self.arg_namespace

    @staticmethod
    def message():
        return "Export Formats"

    def prompt(self):
        export_formats = inquirer.select(
            message="Select Export Formats",
            instruction="[space] to multi-select. [enter] to confirm.",
            choices=ExportFormats.list_values(),
            multiselect=True
        ).execute()

        if not self.arg_namespace.file_formats:
            self.arg_namespace.file_formats = export_formats
        else:
            self.arg_namespace.file_formats.extend(export_formats)


class WorkDirPrompt:
    def __init__(self):
        self.download_directory: Path | str | None = None

    def __call__(self):
        return self.prompt()

    @staticmethod
    def message():
        return "Working Directory"

    def prompt(self):
        return


class VideoPrompt:
    def __init__(self):
        self.mp4_slide_duration_secs: int | None = None
        self.mp4_total_video_duration: int | None = None
        self.fps: int | None = None

    def __call__(self):
        return self.prompt()

    @staticmethod
    def message():
        return "Video Options"

    def prompt(self):
        return


class ImagePrompt:
    def __init__(self):
        self.jpeg_quality: int | None = None

    def __call__(self):
        return self.prompt()

    @staticmethod
    def message():
        return "Image Options"

    def prompt(self):
        return


class ScreenSettingsPrompt:
    def __init__(self):
        self.aspect_ratio: str | None = None
        self.dpi: int | None = None
        self.screen_width: int | None = None
        self.screen_height: int | None = None

    def __call__(self):
        return self.prompt()

    @staticmethod
    def message():
        return "Destination Screen Options"

    def prompt(self):
        return


class LabeledOptionsPrompt:
    def __init__(self):
        self.set_label: bool | str | None = None

    def __call__(self):
        return self.prompt()

    @staticmethod
    def message():
        return "Set Label for Options Set"

    def prompt(self):
        return


class InteractivePrompt:
    def __init__(self) -> None:
        self.prompts: list = [
            PresentationPrompt,
            FormatsPrompt,
            VideoPrompt,
            ImagePrompt,
            ScreenSettingsPrompt,
            LabeledOptionsPrompt,
            WorkDirPrompt,
        ]

    @staticmethod
    def get_subprompt_messages(obj: Prompt | Any):
        return [_.message() for _ in obj.prompts]

    def __call__(self, arg_namespace: Options) -> Options:
        exit_code = True

        choices = self.get_subprompt_messages(self)
        additional_choices = ["Run", "Quit"]
        choices.extend(additional_choices)

        while exit_code:
            subprompt_select = inquirer.rawlist(
                message="Set Options Group:", choices=choices
            ).execute()

            if subprompt_select == "Run":
                exit_code = False
            elif subprompt_select == "Quit":
                raise SystemExit

            exit_code = subprompt_select not in additional_choices

            prompt_index = (
                choices.index(subprompt_select)
                if subprompt_select not in additional_choices
                else None
            )

            if prompt_index is not None:
                arg_namespace = self.prompts[prompt_index](arg_namespace)()

        return arg_namespace