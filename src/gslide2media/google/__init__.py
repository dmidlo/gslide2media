"""
Google Slides API and Drive API client for Python.

This module provides a client for interacting with Google Slides API and Drive API.
The GoogleClient class is the main interface for interacting with these APIs.
    The class provides methods for getting Google Slides presentation IDs from a
    Drive folder, getting Google Slides presentations by ID, getting the name of
    a Google Slides presentation, generating a slide image URL from a Google Slides
    slide ID, creating images from Google Slides slides, and converting Google
    Slides presentations to images or video.

Attributes:
    None.

Methods:
    GoogleClient:
        GoogleClient class to interact with Google Slides API and Drive API.
    get_presentations_from_drive_folder:
        Get Google Slides presentation IDs from the Drive folder.
    get_google_slides_presentation:
        Get Google Slides presentation by ID.
    get_presentation_name:
        Get the name of a Google Slides presentation.
    get_slides_data_from_presentation:
        Get a generator of slide data from a Google Slides presentation.
    get_svg_bytes_from_google_export_url:
        Get the SVG bytes from a Google Slides export URL.
    create_image_from_google_slide:
        Create an image from a Google Slides slide.
    generate_slide_image_url:
        Generate a slide image URL from a Google Slides slide ID.
    download_slides_as_images:
        Download Google Slides slides as images.
    convert_presentation:
        Convert a Google Slides presentation to images or video.
    create_images_from_slides:
        Create images from Google Slides slides.
    convert_presentations_in_google_folder:
        Convert Google Slides presentations in a Google Drive folder to images or video.
"""

from typing import Generator
from typing import Iterator
from typing import Optional

from pathlib import Path
from collections import namedtuple

from googleapiclient.errors import HttpError

from gslide2media.google.auth import AuthGoogle
from gslide2media.utils import save_image_to_file
from gslide2media.images import convert_svg_bytes_to_png_bytes
from gslide2media.images import convert_png_bytes_to_jpg_bytes
from gslide2media.video import convert_pngs_bytes_to_mp4
from gslide2media.options import Options
from gslide2media import config


class GoogleClient:
    """
    GoogleClient class to interact with Google Slides API and Drive API.

    Attributes:
        auth_google (AuthGoogle): An instance of the `AuthGoogle` class for authentication
            with Google services.
        presentations_from_drive_folder (Optional[str]): The ID of the Google Drive folder
            from which presentations are retrieved. If not set, the default value is `None`.

    Returns:
        None.

    Methods:
        get_presentations_from_drive_folder:
                Get Google Slides presentation IDs from the Drive folder.
        get_google_slides_presentation: Get Google Slides presentation by ID.
        get_presentation_name: Get the name of a Google Slides presentation.
        get_slides_data_from_presentation:
                Get a generator of slide data from a Google Slides presentation.
        get_svg_bytes_from_google_export_url: Get the SVG bytes from a Google Slides export URL.
        create_image_from_google_slide: Create an image from a Google Slides slide.
        generate_slide_image_url: Generate a slide image URL from a Google Slides slide ID.
        download_slides_as_images: Download Google Slides slides as images.
        convert_presentation: Convert a Google Slides presentation to images or video.
        create_images_from_slides: Create images from Google Slides slides.
        convert_presentations_in_google_folder:
                Convert Google Slides presentations in a Google Drive folder to images or video.
    """

    def __init__(self, options: Options) -> None:
        """Initialize a new instance of the GoogleClient class.

        Note: The `auth_google` and `presentations_from_drive_folder` attributes are set
        separately using the property decorators provided in this class.
        """
        self.options = options

        self.auth_google: AuthGoogle = AuthGoogle(
            config.API_SCOPES
        )
        self.presentations_from_drive_folder: list = (
            self.get_presentations_from_drive_folder(folder_id=self.options.folder_id)
        )
        self.root_folder_id = self.get_root_folder_id()

    @property
    def options(self) -> Options:
        """Get the `Options` instance for authentication with Google services.

        Returns:
            Options: An instance of the `Options` class used for authentication
                with Google services.
        """
        return self._options

    @options.setter
    def options(self, options: Options) -> None:
        """Set the `Options` instance for authentication with Google services.

        Args:
            options (Options): An instance of the `Options` class used for
                authentication with Google services.
        """
        self._options = options

    @options.deleter
    def options(self) -> None:
        """Delete the `Options` instance used for authentication with Google services."""
        del self._options

    @property
    def auth_google(self) -> AuthGoogle:
        """Get the `AuthGoogle` instance for authentication with Google services.

        Returns:
            AuthGoogle: An instance of the `AuthGoogle` class used for authentication
                with Google services.
        """
        return self._auth_google

    @auth_google.setter
    def auth_google(self, auth_google) -> None:
        """Set the `AuthGoogle` instance for authentication with Google services.

        Args:
            auth_google (AuthGoogle): An instance of the `AuthGoogle` class used for
                authentication with Google services.

        Returns:
            None
        """
        self._auth_google = auth_google

    @auth_google.deleter
    def auth_google(self) -> None:
        """Delete the `AuthGoogle` instance used for authentication with Google services."""
        del self._auth_google

    @property
    def presentations_from_drive_folder(self) -> Optional[list[dict]]:
        """Get the list of Google Slides presentations from the Drive folder.

        Returns:
            list[dict] | None: List of Google Slides presentations as dictionaries,
            where each dictionary contains metadata about a presentation. Returns
            `None` if no presentations are found or if the Drive folder has not
            been set.
        """
        return self._presentations_from_drive_folder

    @presentations_from_drive_folder.setter
    def presentations_from_drive_folder(self, presentations_from_drive_folder):
        """Set the list of Google Slides presentations from the Drive folder.

        Args:
            presentations_from_drive_folder (list[dict]): List of Google Slides
            presentations as dictionaries, where each dictionary contains metadata
            about a presentation.

        Returns: None
        """
        self._presentations_from_drive_folder = presentations_from_drive_folder

    @presentations_from_drive_folder.deleter
    def presentations_from_drive_folder(self):
        """Delete the list of Google Slides presentations from the Drive folder."""
        del self._presentations_from_drive_folder

    @property
    def root_folder_id(self) -> str:
        return self._root_folder_id

    @root_folder_id.setter
    def root_folder_id(self, root_folder_id: str):
        self._root_folder_id: str = root_folder_id

    @root_folder_id.deleter
    def root_folder_id(self):
        del self._root_folder_id

    def get_presentations_from_drive_folder(  # type:ignore
        self,
        folder_id,
    ) -> list | None:
        """Get the list of Google Slides presentations from a specified Drive folder.

        Returns:
            list or None: A list of dictionaries containing information about the Google Slides
                            presentations found in the specified folder. Each dictionary contains
                            'id' and 'name' fields for the presentation file, or None if an error
                            occurred.
        """

        if folder_id:
            try:
                # Query to get slides presentations in the specified folder
                query: str = (
                    f"'{folder_id}' in parents "
                    "and mimeType='application/vnd.google-apps.presentation' "
                    "and trashed = false"
                )

                results: dict = (
                    self.auth_google.drive_service.files()  # pylint: disable=no-member
                    .list(q=query, fields="nextPageToken, files(id, name)")
                    .execute()
                )

                return results.get("files", [])

            except HttpError as error:
                print(f"An error occurred: {error}")
                return None

    def get_root_folder_id(self) -> str:
        query = "'root' in parents"
        results = (
            self.auth_google.drive_service.files()
            .list(q=query, fields="files(id)")
            .execute()
        )
        return results.get("files", [])[0].get("id")

    def get_google_slides_presentation(self, presentation_id: str) -> dict:
        """Get a google slide presentation by id.

        Args:
            presentation_id (str): A presentation id from docs URL:
                https://docs.google.com/presentation/d/PRESENTATION_ID

        Returns:
            dict: Google Slide Presentation Dictionary
        """

        return (
            self.auth_google.slides_service.presentations()  # pylint: disable=no-member
            .get(presentationId=presentation_id)
            .execute()
        )

    def get_presentation_name(self, presentation_id: str) -> str:
        """Get the name of a Google Slides presentation based on its ID.

        Args:
            presentation_id (str): ID of the Google Slides presentation.

        Returns:
            str: The name of the Google Slides presentation with leading and trailing spaces
            removed, and spaces replaced with hyphens.
        """
        presentation: dict = self.get_google_slides_presentation(presentation_id)
        return presentation["title"].strip().replace(" ", "-")

    def get_slides_data_from_presentation(self, presentation_id: str) -> Generator:
        """Get slide data from a Google Slides presentation based on its ID.

        This method retrieves slide data, including the presentation name, presentation ID, and
        slide ID, from a Google Slides presentation based on its ID. It returns a generator that
        yields namedtuples with the slide data.

        Args:
            presentation_id (str): ID of the Google Slides presentation.

        Yields:
            namedtuple: A named tuple (SlideData) containing the presentation name, presentation ID,
            and slide ID.
        """

        presentation: dict = self.get_google_slides_presentation(presentation_id)
        presentation_name = presentation["title"].strip().replace(" ", "-")

        SlideData: namedtuple = namedtuple(
            "SlideData", ("presentation_name", "presentation_id", "slide_id")
        )

        return (
            SlideData(presentation_name, presentation_id, slide["objectId"])
            for slide in presentation.get("slides")  # type:ignore
        )

    def get_svg_bytes_from_google_export_url(self, slide_image_url: str) -> bytes:
        """Get SVG bytes from a Google export URL.

        This method retrieves SVG bytes from a Google export URL of an image, such as a slide
        thumbnail, using the authorized session of the authenticated Google client.

        Args:
            slide_image_url (str): URL of the image to download in SVG format.

        Returns:
            bytes: SVG bytes of the image.
        """
        return self.auth_google.google_authorized_session.get(slide_image_url).content

    def create_image_from_google_slide(
        self, image_path: Path, slide_image_url: str, img_format: str
    ) -> bytes | None:  # sourcery skip: merge-nested-ifs, move-assign
        # sourcery skip: remove-unnecessary-else, swap-if-else-branches
        """Create an image from a Google Slide.

        This method creates an image from a Google Slide by downloading the slide's image data in
        SVG format from the provided slide image URL, and then optionally converting it to PNG or
        JPEG format with the specified DPI and parent dimensions. The resulting image data can be
        saved to a file, and the image data in the desired format is returned as bytes.

        Args:
            image_path (Path):
                The path of the file to save the image to, if `save_to_file` is`True`.
            slide_image_url (str): The URL of the Google Slide image data to download.
            img_format (str):
                The desired format of the resulting image. Must be one of "svg", "png", or "jpeg".

        Returns:
            bytes | None: The image data in the desired format, as bytes. Returns `None` if the
                specified image format is not supported or an error occurred during image creation.

        Raises:
            ValueError: If the specified image format is not supported
                (not one of "svg", "png", or "jpeg").
        """

        fmt = img_format.lower()
        if fmt in {"svg", "png", "jpeg"}:
            svg_bytes = self.get_svg_bytes_from_google_export_url(slide_image_url)

            if fmt == "svg":
                if self.options.save_images_to_file:
                    save_image_to_file(image_path, svg_bytes)
                return svg_bytes

        else:
            raise ValueError("Invalid image format.  Must be jpeg, png, or svg.")

        if fmt in {"png", "jpeg"}:
            png_bytes: bytes = convert_svg_bytes_to_png_bytes(
                svg_bytes,
                self.options.dpi,
                self.options.screen_width,
                self.options.screen_height,
            )

            if fmt == "png":
                if self.options.save_images_to_file:
                    save_image_to_file(image_path, png_bytes)
                return png_bytes

        if fmt in {"jpeg"}:
            jpeg_bytes: bytes = convert_png_bytes_to_jpg_bytes(png_bytes)

            if self.options.save_images_to_file:
                save_image_to_file(image_path, jpeg_bytes)

            return jpeg_bytes
        return None

    @staticmethod
    def generate_slide_image_url(
        presentation_id: str, slide_id: str, img_format: str
    ) -> str:
        """Generate the URL for exporting a slide image from a Google Slides presentation.

        This static method generates the URL for exporting a slide image from a Google Slides
        presentation in the specified image format. The generated URL can be used to download
        the slide image data in the desired format from Google Slides.

        Args:
            presentation_id (str): The ID of the Google Slides presentation.
            slide_id (str): The ID of the slide to export as an image.
            img_format (str):
                The desired format of the exported slide image.
                Must be one of "jpeg", "png", or "svg".

        Returns:
            str: The URL for exporting the slide image in the specified format.

        Raises:
            ValueError: If the specified image format is not supported
                (not one of "jpeg", "png", or "svg").
        """
        img_format = img_format.lower()

        match img_format:
            case "jpeg":
                fmt = "jpeg"
            case "png":
                fmt = "png"
            case "svg":
                fmt = "svg"
            case _:
                raise ValueError("Invalid image format.  Must be jpeg, png, or svg.")

        return (
            f"https://docs.google.com/presentation/d/"
            f"{presentation_id}"
            f"/export/{fmt}?"
            f"id={presentation_id}"
            f"&pageid={slide_id}"
        )

    def download_slides_as_images(
        self, slides_data: Generator, img_format: str
    ) -> Generator:
        """Download slides from Google Slides as images in the specified format.

        This method downloads slides from Google Slides as images in the specified format and
        returns the image data as a generator. The downloaded images can optionally be saved to
        local files. The generator yields the image data for each downloaded slide in the order of
        the slides provided by the `slides_data` generator.

        Args:
            slides_data (Generator):
                A generator that provides SlideData objects, which contain information about the
                slides to download, including presentation ID, slide ID, and presentation name.
            img_format (str):
                The desired format of the downloaded slide images.
                Must be one of "jpeg", "png", or "svg".

        Yields:
            Generator: A generator that yields the image data for each downloaded slide as bytes.

        """
        for i, slide_data in enumerate(slides_data):
            presentation_name = slide_data.presentation_name
            presentation_directory: Path = (
                self.options.download_directory / "presentations" / presentation_name
            )

            if not presentation_directory.exists():
                presentation_directory.mkdir(parents=True)

            image_filename: str = f"{presentation_name}-slide_{i + 1}.{img_format}"
            image_path: Path = presentation_directory / image_filename

            if self.options.create_mp4s or not image_path.exists():
                presentation_id = slide_data.presentation_id

                slide_id = slide_data.slide_id

                slide_image_url: str = self.generate_slide_image_url(
                    presentation_id, slide_id, "svg"
                )

                yield self.create_image_from_google_slide(
                    image_path, slide_image_url, img_format
                )

    def convert_presentation(self, presentation_id: str) -> Generator:
        """Convert a Google Slides presentation to images or a video.

        This method converts a Google Slides presentation to images or a video, depending on the
        configuration settings. If images are selected, the method yields a generator that provides
        the image data for each slide in the presentation. If a video is selected, the method
        yields a generator that provides the bytes of the converted MP4 video.

        Args:
            presentation_id (str): The ID of the Google Slides presentation to convert.

        Yields:
            Generator: A generator that provides the image data for each slide in the presentation
            as bytes, if images are selected for conversion. A generator that provides the bytes of
            the converted MP4 video, if a video is selected for conversion.
        """
        slides_data: Generator = self.get_slides_data_from_presentation(presentation_id)

        presentation_images: Iterator[bytes] | None = None
        if self.options.create_images:
            yield from iter(
                self.download_slides_as_images(
                    slides_data, self.options.image_file_format
                )
            )

        elif self.options.create_mp4s:
            presentation_images = self.download_slides_as_images(
                slides_data, config.MP4_IMAGE_FILE_FORMAT
            )

            yield convert_pngs_bytes_to_mp4(
                self.get_presentation_name(presentation_id),
                presentation_images,
                self.options.mp4_slide_duration_secs,
                self.options.download_directory,
                self.options.save_mp4_to_file,
            )

    def create_images_from_slides(
        self,
        slides_data: Generator,
        img_format: str,
    ):
        """Create images from Google Slides.

        This method creates images from the slides of a Google Slides presentation. It yields a
        generator that provides the image data for each slide in the presentation, based on the
        specified image format, save-to-file setting, DPI resolution, and parent container
        dimensions.

        Args:
            slides_data (Generator):
                A generator that provides the data for each slide in the GoogleSlides presentation.
            img_format (str): The format of the images to create. This should be a valid image file
                format, such as "png", "jpeg", or "svg".

        Yields:
            Generator: A generator that provides the image data for each slide in the Google Slides
                presentation as bytes.
        """
        yield from iter(self.download_slides_as_images(slides_data, img_format))

    def convert_presentations_in_google_folder(self):
        """Convert Google Slides presentations in a Google Drive folder.

        This method converts Google Slides presentations in a specified Google Drive folder. The
        conversion can be done either by creating images from the slides or by creating an MP4 video
        from the slides. The generated images or MP4 video can be saved to local files, and various
        conversion options such as image format, DPI resolution, and parent container dimensions can
        be configured.

        Yields:
            Generator: If create_images is True, a generator that provides the image data for each
                slide in the Google Slides presentations as bytes. If create_mp4s is True, an MP4
                video file as bytes.

        """
        for _ in self.get_presentations_from_drive_folder(
            folder_id=self.options.folder_id
        ):  # type:ignore
            presentation_id: str = _["id"]
            slides_data: Generator = self.get_slides_data_from_presentation(
                presentation_id
            )

            presentation_images: Iterator[bytes] | None = None
            if self.options.create_images:
                yield from self.create_images_from_slides(
                    slides_data, self.options.image_file_format
                )

            elif self.options.create_mp4s:
                presentation_images = iter(
                    self.download_slides_as_images(
                        slides_data, config.MP4_IMAGE_FILE_FORMAT
                    )
                )

                yield convert_pngs_bytes_to_mp4(
                    self.get_presentation_name(presentation_id),
                    presentation_images,
                    self.options.mp4_slide_duration_secs,
                    self.options.download_directory,
                    self.options.save_mp4_to_file,
                )

            if not self.options.run_all:
                break
