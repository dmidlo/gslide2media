from typing import Tuple
from typing import NamedTuple

from pathlib import Path

from googleapiclient.errors import HttpError

from gslide2media import config
from gslide2media.enums import DriveTypes

from .auth import AuthGoogle


# TODO: Should make this a singleton as well.
#  making this a singleton will allow the None checks for config.GOOGLE to be removed.
#  presently AuthGoogle is only used here in the client and therefore would be encapsulated
#  in this singleton and would not need be one itself.
class GoogleClient:
    def __init__(self) -> None:
        self.auth_google: AuthGoogle = AuthGoogle(config.API_SCOPES)

    @property
    def auth_google(self) -> AuthGoogle:
        return self._auth_google

    @auth_google.setter
    def auth_google(self, auth_google) -> None:
        self._auth_google = auth_google

    @auth_google.deleter
    def auth_google(self) -> None:
        del self._auth_google

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

    def get_folders_in_root(self) -> list[dict]:
        query = "'root' in parents and mimeType='application/vnd.google-apps.folder' and trashed = false"
        results = (
            self.auth_google.drive_service.files()  # pylint: disable=no-member
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_presentations_in_root(self) -> list[dict]:
        query = "'root' in parents and mimeType='application/vnd.google-apps.presentation' and trashed = false"
        results = (
            self.auth_google.drive_service.files()  # pylint: disable=no-member
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_shared_folders(self) -> list[dict]:
        query = "mimeType='application/vnd.google-apps.folder' and sharedWithMe"
        results = (
            self.auth_google.drive_service.files()  # pylint: disable=no-member
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def get_shared_presentations(self) -> list[dict]:
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

    def resolve_drive_file_path_to_root(
        self, file_resource_id: str
    ) -> Tuple[Path, Path] | None:
        try:
            file_metadata = (
                self.auth_google.drive_service.files()  # pylint: disable=no-member
                .get(fileId=file_resource_id, fields="name, parents")
                .execute()
            )

            parent = file_metadata.get("parents")

            parent_id_list, parent_name_list = [], []

            if parent:
                parent_id_list.append(parent[0])

            while parent:
                parent_metadata = (
                    self.auth_google.drive_service.files()  # pylint: disable=no-member
                    .get(fileId=parent[0], fields="name, parents")
                    .execute()
                )

                parent_name = parent_metadata.get("name").strip().replace(" ", "-")
                parent_parent = parent_metadata.get("parents")

                if parent_name == "My-Drive":
                    parent_id_list.pop()
                else:
                    parent_name_list.append(parent_name)
                    if parent_parent:
                        parent_id_list.append(parent_parent[0])

                parent = parent_parent

            root_id_path = Path()
            root_name_path = Path()

            for _ in zip(reversed(parent_id_list), reversed(parent_name_list)):
                root_id_path = root_id_path / _[0]
                root_name_path = root_name_path / _[1]

            return ResolvedDrivePath(root_name_path, root_id_path)

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

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
        
    def get_resource_type(self, resource_id: str) -> DriveTypes:
        file = self.auth_google.drive_service.files().get(fileId=resource_id, fields='mimeType').execute()
        mime_type = file['mimeType']

        if mime_type == 'application/vnd.google-apps.folder':
            return DriveTypes.FOLDER
        elif mime_type == 'application/vnd.google-apps.presentation':
            return DriveTypes.PRESENTATION

class ResolvedDrivePath(NamedTuple):
    name_path: Path
    id_path: Path
