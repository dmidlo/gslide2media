from enum import StrEnum, auto


class ImageExportFormats(StrEnum):
    JPEG = auto()
    PNG = auto()
    SVG = auto()


class GoogleSlideExportFormats(StrEnum):
    JPEG = auto()
    PNG = auto()
    SVG = auto()
    JSON = auto()


class GoogleSlideExportTypes(StrEnum):
    FILE = auto()
    IMAGE = auto()
    DATA = auto()


class GooglePresentationExportFormats(StrEnum):
    PPTX = auto()
    PDF = auto()
    TXT = auto()
    ODP = auto()
    JSON = auto()


class GooglePresentationExportTypes(StrEnum):
    FILE = auto()
    VIDEO = auto()
    DATA = auto()


class ExportFormats(StrEnum):
    PPTX = auto()
    PDF = auto()
    TXT = auto()
    ODP = auto()
    JPEG = auto()
    PNG = auto()
    SVG = auto()
    MP4 = auto()
    JSON = auto()
