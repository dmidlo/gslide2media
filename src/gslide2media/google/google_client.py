from typing import Generator
from typing import Iterator
from typing import Optional

from pathlib import Path
from collections import namedtuple

from googleapiclient.errors import HttpError

from gslide2media.google.auth import AuthGoogle
from gslide2media.options import Options
from gslide2media import config


class GoogleClient:
    def __init__(self, options: Options) -> None:
        self.options = options

        self.auth_google: AuthGoogle = AuthGoogle(config.API_SCOPES)
        self.presentations_from_drive_folder: list = (
            self.get_presentations_from_drive_folder(folder_id=self.options.folder_id)
        )
        self.root_folder_id = self.get_folders_in_root()

    @property
    def options(self) -> Options:
        return self._options

    @options.setter
    def options(self, options: Options) -> None:
        self._options = options

    @options.deleter
    def options(self) -> None:
        del self._options

    @property
    def auth_google(self) -> AuthGoogle:
        return self._auth_google

    @auth_google.setter
    def auth_google(self, auth_google) -> None:
        self._auth_google = auth_google

    @auth_google.deleter
    def auth_google(self) -> None:
        del self._auth_google

    @property
    def presentations_from_drive_folder(self) -> Optional[list[dict]]:
        return self._presentations_from_drive_folder

    @presentations_from_drive_folder.setter
    def presentations_from_drive_folder(self, presentations_from_drive_folder):
        self._presentations_from_drive_folder = presentations_from_drive_folder

    @presentations_from_drive_folder.deleter
    def presentations_from_drive_folder(self):
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

    def get_google_drive_folder(self, folder_id: str) -> dict:
        return (
            self.auth_google.drive_service.files()  # pylint: disable=no-member
            .get(fileId=folder_id, fields="id, name")
            .execute()
        )

    def get_folder_name(self, folder_id: str) -> str:
        folder: dict = self.get_google_drive_folder(folder_id)
        return folder["name"].strip().replace(" ", "-")

    def get_presentations_from_drive_folder(  # type:ignore
        self,
        folder_id,
    ) -> list | None:
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

    def get_folders_from_drive_folder(self, folder_id) -> list | None:
        if folder_id:
            try:
                # Query to get folders in the specified folder
                query: str = (
                    f"'{folder_id}' in parents "
                    "and mimeType='application/vnd.google-apps.folder' "
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

    def get_folders_in_root(self) -> str:
        query = "'root' in parents and mimeType='application/vnd.google-apps.folder' and trashed = false"
        results = (
            self.auth_google.drive_service.files()
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_presentations_in_root(self) -> str:
        query = "'root' in parents and mimeType='application/vnd.google-apps.presentation' and trashed = false"
        results = (
            self.auth_google.drive_service.files()
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])
    
    def get_shared_folders(self):
        query = "mimeType='application/vnd.google-apps.folder' and sharedWithMe"
        results = (
            self.auth_google.drive_service.files()
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_shared_presentations(self):
        query = "mimeType='application/vnd.google-apps.presentation' and sharedWithMe"
        results = (
            self.auth_google.drive_service.files()
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_google_slides_presentation(self, presentation_id: str) -> dict:
        return (
            self.auth_google.slides_service.presentations()  # pylint: disable=no-member
            .get(presentationId=presentation_id)
            .execute()
        )

    def get_presentation_name(self, presentation_id: str) -> str:
        presentation: dict = self.get_google_slides_presentation(presentation_id)
        return presentation["title"].strip().replace(" ", "-")
    
    def get_parent_folder_of_google_file(self, file_resource_id: str) -> str | None:
        try:
            # Call the Drive API to get the metadata of the presentation file
            file_metadata = self.auth_google.drive_service.files().get(
                fileId=file_resource_id,
                fields="parents"
            ).execute()

            # Extract the IDs of the parent folders
            parent_folder_ids = file_metadata.get("parents", [])

            if len(parent_folder_ids) == 1:
                return parent_folder_ids[0]
            elif len(parent_folder_ids) > 1:
                return parent_folder_ids[0]
            else:
                return None

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_slides_data_from_presentation(self, presentation_id: str) -> Generator:
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
        return self.auth_google.google_authorized_session.get(slide_image_url).content

    def create_image_from_google_slide(
        self, image_path: Path, slide_image_url: str, img_format: str
    ) -> bytes | None:  # sourcery skip: merge-nested-ifs, move-assign
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

            convert_pngs_bytes_to_mp4_opts = {
                "presentation_name": self.get_presentation_name(presentation_id),
                "presentation_images": presentation_images,
                "mp4_slide_duration_secs": self.options.mp4_slide_duration_secs,
                "download_directory": self.options.download_directory,
                "save_mp4_to_file": self.options.save_mp4_to_file,
            }

            yield convert_pngs_bytes_to_mp4(**convert_pngs_bytes_to_mp4_opts)

    def create_images_from_slides(
        self,
        slides_data: Generator,
        img_format: str,
    ):
        yield from iter(self.download_slides_as_images(slides_data, img_format))

    def convert_presentations_in_google_folder(self):
        for _ in self.get_presentations_from_drive_folder(
            folder_id=self.options.folder_id
        ):  # type:ignore
            presentation_id: str = _["id"]
            slides_data: Generator = self.get_slides_data_from_presentation(
                presentation_id
            )

            presentation_images: Iterator[bytes] | None = None
            if self.options.create_images:
                yield from self.download_slides_as_images(
                    slides_data, self.options.image_file_format
                )

            elif self.options.create_mp4s:
                presentation_images = iter(
                    self.download_slides_as_images(
                        slides_data, config.MP4_IMAGE_FILE_FORMAT
                    )
                )

                convert_pngs_bytes_to_mp4_opts = {
                    "presentation_name": self.get_presentation_name(presentation_id),
                    "presentation_images": presentation_images,
                    "mp4_slide_duration_secs": self.options.mp4_slide_duration_secs,
                    "download_directory": self.options.download_directory,
                    "save_mp4_to_file": self.options.save_mp4_to_file,
                }

                yield convert_pngs_bytes_to_mp4(**convert_pngs_bytes_to_mp4_opts)

            if not self.options.run_all:
                break
