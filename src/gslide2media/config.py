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
GOOGLE: GoogleClient | None = None
MP4_IMAGE_FILE_FORMAT: str = "png"
API_SCOPES: list[str] = ["https://www.googleapis.com/auth/drive"]

_default_file_formats = "mp4 svg"
_default_slide_duration_secs = 20
_default_mp4_total_video_duration = 0
_default_fps = 10
_default_jpeg_quality = 90
_default_aspect_ratio = "16:9"
_default_dpi = 300
_default_screen_width = 3456
_default_screen_height = 2234
