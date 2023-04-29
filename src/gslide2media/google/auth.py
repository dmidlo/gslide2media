"""This module provides classes and functions for authenticating with Google APIs.

Classes:
    AuthGoogle -- A class for managing Google authentication credentials and services.

Functions:
    None

"""


from typing import Optional

from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import Resource
from googleapiclient.discovery import build

from gslide2media import config


class AuthGoogle:
    """Class for authenticating Google API requests.

    Args:
        token_file (Path, optional): Path to Google API token file. Defaults to None.
        api_scopes (list[str]): List of Google API scopes.
        credentials_file (Path, optional): Path to Google API credentials file. Defaults to None.

    Attributes:
        creds (google.oauth2.credentials.Credentials): Google API credentials object.
        slides_service (googleapiclient.discovery.Resource): Google Slides API service object.
        drive_service (googleapiclient.discovery.Resource): Google Drive API service object.
        google_authorized_session (google.auth.transport.requests.AuthorizedSession):
                Authorized session object.

    Methods:
        __call__(): Not yet implemented.

    Returns:
        None
    """

    def __init__(self, token_file: Path | None, api_scopes: list[str]) -> None:
        """Initialize AuthGoogle class.

        Args:
            token_file (Path, optional): Path to Google API token file. Defaults to None.
            api_scopes (list[str]): List of Google API scopes.
            credentials_file (Path, optional):
                    Path to Google API credentials file. Defaults to None.

        """
        self.refresh_token_json_file(token_file, api_scopes)

        self.slides_service: Resource = self.create_slides_service()
        self.drive_service: Resource = self.create_drive_service()
        self.google_authorized_session: AuthorizedSession = (
            self.create_google_authorized_session()
        )

    def __call__(self):
        """Callable class that raises a NotImplementedError.

        Raises:
            NotImplementedError: When called, this method will always raise a NotImplementedError
                with a message indicating that the '__call__' method of 'AuthGoogle' class
                is not yet implemented.
        """
        raise NotImplementedError("AuthGoogle.__call__() not yet implemented")

    @property
    def creds(self):
        """Getter method for accessing the credentials of the object.

        Returns:
            Any: The credentials associated with the object.
        """
        return self._creds

    @creds.setter
    def creds(self, creds):
        """Setter method for 'creds' attribute.

        Args:
            creds (Any): The new value to set for the 'creds' attribute.

        Raises:
            TypeError: If 'creds' is not of the expected data type.
        """
        self._creds = creds

    @creds.deleter
    def creds(self):
        """Deleter method for 'creds' attribute.

        Raises:
            AttributeError: If 'creds' attribute is not present.
        """
        del self._creds

    @property
    def slides_service(self):
        """Getter method for 'slides_service' attribute.

        Returns:
            googleapiclient.discovery.Resource: The slides service object.

        """
        return self._slides_service

    @slides_service.setter
    def slides_service(self, slides_service):
        """Setter method for 'slides_service' attribute.

        Args:
            slides_service (googleapiclient.discovery.Resource): The slides service object.

        """
        self._slides_service = slides_service

    @slides_service.deleter
    def slides_service(self):
        """Deleter method for 'slides_service' attribute.

        Deletes the slides service object associated with this instance.
        """
        del self._slides_service

    @property
    def drive_service(self):
        """Getter method for 'drive_service' attribute.

        Returns the Google Drive service object associated with this instance.

        Returns:
            The Google Drive service object associated with this instance.
        """
        return self._drive_service

    @drive_service.setter
    def drive_service(self, drive_service):
        """Setter method for 'drive_service' attribute.

        Sets the Google Drive service object associated with this instance.

        Args:
            drive_service (googleapiclient.discovery.Resource): The Google Drive service
                object to be associated with this instance.
        """
        self._drive_service = drive_service

    @drive_service.deleter
    def drive_service(self):
        """Deleter method for 'drive_service' attribute.

        Deletes the Google Drive service object associated with this instance.
        """
        del self._drive_service

    @property
    def google_authorized_session(self):
        """Get the authorized Google session.

        Returns:
            AuthorizedSession: The authorized Google session object associated with this instance.
        """
        return self._google_authorized_session

    @google_authorized_session.setter
    def google_authorized_session(self, google_authorized_session):
        """Set the authorized Google session.

        Args:
            google_authorized_session (AuthorizedSession):
                    The authorized Google session object to set.
        """
        self._google_authorized_session = google_authorized_session

    @google_authorized_session.deleter
    def google_authorized_session(self):
        """Delete the authorized Google session.

        Deletes the authorized Google session associated with the instance, effectively revoking the
        authorization.
        """
        del self._google_authorized_session

    @staticmethod
    def load_google_auth_creds_from_file(
        token_file: Optional[Path], api_scopes: list[str]
    ) -> Credentials | None:
        """Load Google authorization credentials from a file.

        Loads Google authorization credentials from the specified token file, which stores the
        user's access and refresh tokens. If the token file does not exist, None is returned. The
        loaded credentials can be used to authenticate requests to Google APIs.

        Args:
            token_file (Optional[Path]): Path to the token file that stores the authorization
                credentials. If None, no credentials will be loaded and None will be returned.
            api_scopes (list[str]): List of API scopes that the authorization credentials should
                be granted access to.

        Returns:
            Credentials | None: The loaded authorization credentials as a `Credentials` object, or
            None if the token file does not exist.
        """

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_file_path = Path(token_file)

        return (
            Credentials.from_authorized_user_file(token_file, api_scopes)
            if token_file_path.exists()  # type:ignore
            else None
        )

    @staticmethod
    def refresh_google_auth_creds(creds: Credentials) -> Credentials | None:
        """Refresh Google authorization credentials.

        Refreshes the provided Google authorization credentials if they are expired and a refresh
        token is available. The refreshed credentials are returned. If the provided credentials are
        already valid and not expired, or if a refresh token is not available, the same credentials
        are returned without modification.

        Args:
            creds (Credentials): The Google authorization credentials to refresh.

        Returns:
            Credentials | None: The refreshed authorization credentials as a `Credentials` object,
            or None if the provided credentials are already valid and not expired, or if a refresh
            token is not available.
        """
        # Using short-circuiting
        if creds and not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    @staticmethod
    def initiate_google_oauth_flow(
        creds: Credentials, api_scopes: list[str]
    ) -> Credentials:
        """Initiate Google OAuth flow for authorization.

        Initiates the Google OAuth flow to obtain authorization credentials for a user. If the
        provided credentials (`creds`) are not available or invalid, the flow is started using the
        client secrets file (`credentials_file`) and the requested API scopes (`api_scopes`). The
        user is prompted to authenticate and authorize the application using a local server flow
        with a dynamically allocated port. Once the user completes the authorization flow, the
        obtained credentials are returned.

        a path to a client_secret.json for {credentials_file (Path | None)} can be downloaded from
            https://console.cloud.google.com/apis/credentials?project=YOUR_PROJECT

        Args:
            creds (Credentials): The Google authorization credentials, which may be None or invalid.
            credentials_file (Path | None): The path to the client secrets file, or None if not
            available. api_scopes (list[str]): The list of requested Google API scopes.

        Returns:
            Credentials: The obtained Google authorization credentials as a `Credentials` object.
        """
        if not creds:
            flow: "InstalledAppFlow" = InstalledAppFlow.from_client_config(
                config.META.google_client_secret, api_scopes
            )
            creds = flow.run_local_server(port=0)
        return creds

    @staticmethod
    def save_token_file_to_disk(creds: Credentials, token_file: Optional[Path]) -> None:
        """Save Google authorization credentials to a token file on disk.

        Saves the provided Google authorization credentials (`creds`) to a token file on disk
        located at the specified path (`token_file`). The credentials are serialized to JSON format
        using the `to_json()` method, and the resulting JSON string is written to the token file.

        Args:
            creds (Credentials): The Google authorization credentials to save.
            token_file (Path | None): The path to the token file on disk, or None if not available.

        Returns:
            None
        """
        with token_file.open("w") as token:  # type:ignore
            token.write(creds.to_json())

    def create_slides_service(self) -> build:
        """Create and return an instance of Google Slides service.

        Creates and returns an instance of the Google Slides service (`build`) from the
        `google-auth` and `google-api-python-client` libraries, using the `slides` API version 1,
        and the stored credentials (`self.creds`) for authentication.

        Returns:
            build: An instance of the Google Slides service (`build`) for making API requests.
        """
        return build("slides", "v1", credentials=self.creds)

    def create_drive_service(self) -> build:
        """Create and return an instance of Google Drive service.

        Creates and returns an instance of the Google Drive service (`build`) from the
        `google-auth` and `google-api-python-client` libraries, using the `drive` API version 3,
        and the stored credentials (`self.creds`) for authentication.

        Returns:
            build: An instance of the Google Drive service (`build`) for making API requests.
        """
        return build("drive", "v3", credentials=self.creds)

    def create_google_authorized_session(self) -> AuthorizedSession:
        """Create and return an authorized session using Google credentials.

        Creates and returns an instance of the `AuthorizedSession` class from the `google-auth`
        library, using the stored credentials (`self.creds`) for authorization.

        Returns:
            AuthorizedSession: An authorized session with Google services.
        """
        return AuthorizedSession(self.creds)

    def refresh_token_json_file(self, token_file, api_scopes):
        self.creds: Credentials | None = self.load_google_auth_creds_from_file(
            token_file, api_scopes
        )
        self.creds = self.refresh_google_auth_creds(self.creds)
        self.creds = self.initiate_google_oauth_flow(self.creds, api_scopes)

        # needs to be twice to fill out creds attributes.
        self.creds = self.refresh_google_auth_creds(self.creds)

        self.save_token_file_to_disk(self.creds, token_file)
