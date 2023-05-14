"""
Configuration settings for creating images and MP4 videos from Google Slides presentations.

Variables:
- META: Storage class for meta information.
- MP4_IMAGE_FILE_FORMAT: str - file format for the images in the created MP4 video
- API_SCOPES: list[str] - list of API scopes for the Google Drive API

"""
from gslide2media.meta import Metadata
from gslide2media.options import Options
from gslide2media.google import GoogleClient

META: Metadata
ARGS: Options
GOOGLE: GoogleClient
MP4_IMAGE_FILE_FORMAT: str = "png"
API_SCOPES: list[str] = ["https://www.googleapis.com/auth/drive"]
