"""
Configuration settings for creating images and MP4 videos from Google Slides presentations.

Variables:
- MP4_IMAGE_FILE_FORMAT: str - file format for the images in the created MP4 video
- API_SCOPES: list[str] - list of API scopes for the Google Drive API

"""

MP4_IMAGE_FILE_FORMAT: str = "png"
API_SCOPES: list[str] = ["https://www.googleapis.com/auth/drive"]
