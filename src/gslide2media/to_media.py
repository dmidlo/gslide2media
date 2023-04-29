"""_summary_

Returns:
    _type_: _description_
"""

# sourcery skip: hoist-statement-from-if, introduce-default-else
from typing import Generator

from pathlib import Path

from gslide2media.cli import ArgParser
from gslide2media.google import GoogleClient
from gslide2media.options import Options

from gslide2media import config
from gslide2media.meta import Metadata


class ToMedia:
    """
    A class that converts a Google Slides presentation to media files.

    Attributes:
        google (GoogleClient): An instance of the GoogleClient class.
        presentation (Presentation): An instance of the Presentation class.
        presentations_in_google_folder (List[Presentation]):
                                            A list of instances of the Presentation class.

    Args:
        token_file (Path | None): The path to the token file or None.
        credentials_file (Path | None): The path to the credentials file or None.
        api_scopes (list[str]): A list of API scopes.
        create_images (bool): Whether to create images or not.
        create_mp4s (bool): Whether to create mp4 files or not.
        dpi (int): The resolution of the images.
        parent_width (Optional[int]): The width of the parent container or None.
        parent_height (Optional[int]): The height of the parent container or None.
        presentation_id (str | None): The ID of the Google Slides presentation or None.
        folder_id (str | None): The ID of the Google Drive folder or None.

    Returns:
        None
    """

    def __init__(self, options: Options) -> None:
        config.META = Metadata.metadata_singleton_factory()
        self.ARGS = ArgParser(options)()
        print(config.META)
        print(self.ARGS)
        raise SystemExit
        self.GOOGLE = GoogleClient(self.ARGS)


        if self.ARGS.presentation_id:
            self.presentations_in_google_folder = None
            self.presentation = self.GOOGLE.convert_presentation(
                self.ARGS.presentation_id
            )
        elif self.ARGS.folder_id:
            self.presentations_in_google_folder = (
                self.GOOGLE.convert_presentations_in_google_folder()
            )
            self.presentation = None

    def __call__(self) -> None | Generator:
        if not self.ARGS.download_directory.exists():
            self.ARGS.download_directory.mkdir(parents=True)

        if self.ARGS.presentation_id:
            for _ in self.presentation:
                if self.ARGS.from_api:
                    yield _

        elif self.ARGS.folder_id:
            for _ in self.presentations_in_google_folder:
                if self.ARGS.from_api:
                    yield _

    # Getters and Setters for class attributes
    @property
    def ARGS(self):
        """
        Get the ARGs from either the CLI argparser or API Dictionary.

        Returns:
            Args: the ARGs from either the CLI argparser or API Dictionary.
        """
        return self._ARGS

    @ARGS.setter
    def ARGS(self, ARGS):
        """
        Sets the ARGs from either the CLI argparser or API Dictionary.

        Args:
            Args: the ARGs from either the CLI argparser or API Dictionary.

        Returns:
            None
        """
        self._ARGS = ARGS

    @ARGS.deleter
    def ARGS(self):
        """
        Delete ARGS instance from either the CLI argparser or API Dictionary.
        """
        del self._ARGS

    @property
    def GOOGLE(self):
        """
        Get the GoogleClient instance used for authentication and interacting with the Google API.

        Returns:
            GoogleClient: The GoogleClient instance.
        """
        return self._google

    @GOOGLE.setter
    def GOOGLE(self, google):
        """
        Set the GoogleClient instance used for authentication and interacting with the Google API.

        Args:
            google (GoogleClient): The GoogleClient instance.

        Returns:
            None
        """
        self._google = google

    @GOOGLE.deleter
    def GOOGLE(self):
        """
        Delete GoogleClient instance used for authentication and interacting with the Google API.
        """
        del self._google

    @property
    def presentation(self):
        """
        Get the Presentation instance representing the Google Slides presentation
            being converted to media files.

        Returns:
            Presentation: The Presentation instance.
        """
        return self._presentation

    @presentation.setter
    def presentation(self, presentation):
        """
        Set the Presentation instance representing the Google Slides presentation being
            converted to media files.

        Args:
            presentation (Presentation): The Presentation instance.

        Returns:
            None
        """
        self._presentation = presentation

    @presentation.deleter
    def presentation(self):
        """
        Delete the Presentation instance representing the Google Slides presentation being
            converted to media files.

        Returns:
            None
        """
        del self._presentation

    @property
    def presentations_in_google_folder(self):
        """
        Get the list of Presentation instances representing Google Slides presentations in
            the specified Google Drive folder.

        Returns:
            List[Presentation]: A list of Presentation instances.
        """
        return self._presentations_in_google_folder

    @presentations_in_google_folder.setter
    def presentations_in_google_folder(self, presentations_in_google_folder):
        """
        Set the list of Presentation instances representing Google Slides presentations in
            the specified Google Drive folder.

        Args:
            presentations_in_google_folder (List[Presentation]): A list of Presentation instances.

        Returns:
            None
        """
        self._presentations_in_google_folder = presentations_in_google_folder

    @presentations_in_google_folder.deleter
    def presentations_in_google_folder(self):
        """
        Delete the list of Presentation instances representing Google Slides presentations in
            the specified Google Drive folder.

        Returns:
            None
        """
        del self._presentations_in_google_folder


def main(options: Options | None = None) -> Generator | None:
    if not options:
        options = Options()
        for _ in ToMedia(options)():
            ...
        return None
    options.from_api = True
    return ToMedia(options)()
