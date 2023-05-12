from typing import Optional

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
            self.auth_google.drive_service.files()  # pylint: disable=no-member
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_presentations_in_root(self) -> str:
        query = "'root' in parents and mimeType='application/vnd.google-apps.presentation' and trashed = false"
        results = (
            self.auth_google.drive_service.files()  # pylint: disable=no-member
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_shared_folders(self):
        query = "mimeType='application/vnd.google-apps.folder' and sharedWithMe"
        results = (
            self.auth_google.drive_service.files()  # pylint: disable=no-member
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_shared_presentations(self):
        query = "mimeType='application/vnd.google-apps.presentation' and sharedWithMe"
        results = (
            self.auth_google.drive_service.files()  # pylint: disable=no-member
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
            file_metadata = (
                self.auth_google.drive_service.files()  # pylint: disable=no-member
                .get(fileId=file_resource_id, fields="parents")
                .execute()
            )

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
