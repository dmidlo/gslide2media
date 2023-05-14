from typing import Iterator
import functools
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.parse import urlunparse
from urllib.parse import ParseResult as UrlParseResult

from gslide2media.enums import GoogleSlideExportFormats
from gslide2media.enums import ImageExportFormats
from gslide2media.enums import GoogleSlideExportTypes
from gslide2media.utils import DataPartial
from gslide2media.utils import convert_partial_to_bytes
from gslide2media.utils import dataclass_unique_instance_cache
from gslide2media import config

from .image import Image
from .file import File


@dataclass
class SlideExportUrls:
    slide_id: str
    presentation_id: str
    presentation_order: int = 0
    parent: str | None = None
    presentation_name: str | None = None
    is_composite: bool = False
    is_batch: bool = False

    def __post_init__(self):
        self.set_resource_export_url_attributes()

    @staticmethod
    def create_slide_export_url(
        presentation_id: str, slide_id: str, export_format: GoogleSlideExportFormats
    ) -> UrlParseResult:
        # slide_id should be: g201d5ec49f_1_0
        #    NOT with a leading 'id.', like this: id.g201d5ec49f_1_0

        return urlparse(
            "https://docs.google.com/presentation/d/"
            f"{presentation_id}"
            "/export/"
            f"{export_format}?"
            f"id={presentation_id}"
            f"&pageid={slide_id}"
        )

    def set_resource_export_url_attributes(self):
        for _ in GoogleSlideExportFormats:
            setattr(
                self,
                _,
                self.create_slide_export_url(self.presentation_id, self.slide_id, _),
            )
            self.__annotations__[
                _.lower()
            ] = UrlParseResult  # pylint: disable=no-member

    def __iter__(self):
        self.index = 0
        self.attributes = [x.lower() for x in GoogleSlideExportFormats]
        return self

    def __next__(self):
        if self.index >= len(self.attributes):
            raise StopIteration

        attr_name = self.attributes[self.index]
        attr_value = getattr(self, attr_name)
        self.index += 1
        return (attr_name, urlunparse(attr_value))

    def __getitem__(self, key):
        if key.lower() not in set(GoogleSlideExportFormats):
            raise KeyError(f"'{key}' is not a valid export format")

        if key.lower() in set(ImageExportFormats):
            return DataPartial(self.get_image_bytes_from_url)(key=key)
        raise ValueError(f"{key} not a valid export format.")

    def get_image_bytes_from_url(self, key: ImageExportFormats) -> Image:
        if key.lower() not in set(ImageExportFormats):
            raise KeyError(f"'{key}' is not a valid image format")

        url_obj = getattr(self, key)

        bytes_content = (
            config.GOOGLE.auth_google.google_authorized_session.get(  # type:ignore
                urlunparse(url_obj)
            ).content
        )

        return Image(  # type:ignore
            img_format=key,
            img_data=bytes_content,
            presentation_id=self.presentation_id,
            slide_id=self.slide_id,
            presentation_order=self.presentation_order,
            parent=self.parent,
            presentation_name=self.presentation_name,
            is_batch=self.is_batch,
        )


@dataclass
class FetchSlideData:
    slide_id: str
    presentation_id: str
    slide_image_urls: SlideExportUrls
    export_type: GoogleSlideExportTypes
    presentation_order: int = 0
    parent: str | None = None
    presentation_name: str | None = None
    is_composite: bool = False
    is_batch: bool = False

    def __post_init__(self):
        self.create_self_attributes(self.export_type)

    def __iter__(self):
        match self.export_type:
            case GoogleSlideExportTypes.IMAGE:
                self.attributes = list(ImageExportFormats)
            case GoogleSlideExportTypes.DATA:
                self.attributes = ["json"]

        self.index = 0
        return self

    def __next__(self):
        if self.index >= len(self.attributes):
            raise StopIteration

        attr_name = self.attributes[self.index]
        attr_value = getattr(self, attr_name)
        self.index += 1
        return (attr_name, attr_value)

    def __getitem__(self, key: GoogleSlideExportFormats):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get_json_slide_data(self):
        def func(obj):
            presentation = config.GOOGLE.get_google_slides_presentation(
                obj.presentation_id
            )
            slides = presentation.get("slides")

            [slide_data] = [_ for _ in slides if _["objectId"] == obj.slide_id]

            return File(
                extension="json",
                file_data=slide_data,
                presentation_id=obj.presentation_id,
                slide_id=obj.slide_id,
                presentation_order=obj.presentation_order,
                parent=self.parent,
                presentation_name=self.presentation_name,
                is_batch=self.is_batch,
            )

        return DataPartial(func)(obj=self)

    def create_self_attributes(self, export_type: GoogleSlideExportTypes):
        if export_type is GoogleSlideExportTypes.IMAGE:
            for _ in set(ImageExportFormats):
                setattr(self, _, self.slide_image_urls[_])
                self.__annotations__[_.lower()] = type(
                    functools.partial
                )  # pylint: disable=no-member
        elif export_type is GoogleSlideExportTypes.DATA:
            setattr(self, "json", self.get_json_slide_data())
            self.__annotations__["json"] = dict  # pylint: disable=no-member


@dataclass
class SlideData:
    slide_id: str
    presentation_id: str
    presentation_order: int
    parent: str | None = None
    presentation_name: str | None = None
    is_composite: bool = False
    is_batch: bool = False

    def __post_init__(self) -> None:
        self.slide_image_urls: SlideExportUrls = SlideExportUrls(
            self.slide_id,
            self.presentation_id,
            self.presentation_order,
            self.parent,
            self.presentation_name,
            self.is_composite,
            self.is_batch,
        )
        self.image_data = FetchSlideData(
            self.slide_id,
            self.presentation_id,
            self.slide_image_urls,
            GoogleSlideExportTypes.IMAGE,
            self.presentation_order,
            self.parent,
            self.presentation_name,
            self.is_composite,
            self.is_batch,
        )
        self.json_data = FetchSlideData(
            self.slide_id,
            self.presentation_id,
            self.slide_image_urls,
            GoogleSlideExportTypes.DATA,
            self.presentation_order,
            self.parent,
            self.presentation_name,
            self.is_composite,
            self.is_batch,
        )

    def __iter__(self):
        self.index = 0
        self.attributes = ["image_data", "json_data"]
        return self

    def __next__(self):
        if self.index >= len(self.attributes):
            raise StopIteration

        attr_name = self.attributes[self.index]
        attr_value = getattr(self, attr_name)
        self.index += 1
        return (attr_name, attr_value)

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def image_data(self) -> Iterator[Image]:
        return self._image_data

    @image_data.setter
    def image_data(self, image_data: Iterator[Image]):
        self._image_data = image_data

    @image_data.deleter
    def image_data(self):
        del self._image_data

    @property
    def json_data(self) -> dict:
        return self._json_data

    @json_data.setter
    def json_data(self, json_data: dict):
        self._json_data = json_data

    @json_data.deleter
    def json_data(self):
        del self._json_data


@dataclass_unique_instance_cache(id_keys=["slide_id", "presentation_id"])
class Slide:
    slide_id: str
    presentation_id: str
    presentation_order: int
    slide_duration_secs: int = 0
    slide_data: SlideData | None = None
    parent: str | None = None
    presentation_name: str | None = None
    is_composite: bool = False
    is_batch: bool = False

    def __post_init__(self) -> None:
        self.slide_data: SlideData = SlideData(
            self.slide_id,
            self.presentation_id,
            self.presentation_order,
            self.parent,
            self.presentation_name,
            self.is_composite,
            self.is_batch,
        )

    def __call__(self, presentation_order: int | None = None):
        if presentation_order:
            self.presentation_order = presentation_order
        return self

    def to_file(self, key):
        match key:
            case key if key in set(ImageExportFormats):
                svg_image = convert_partial_to_bytes(self.slide_data.image_data, key)

                if key == ImageExportFormats.SVG:
                    file = svg_image.to_file()
                elif key == ImageExportFormats.PNG:
                    self.slide_data.image_data.png = svg_image.to_png()
                    file = self.slide_data.image_data.png.to_file()
                elif key == ImageExportFormats.JPEG:
                    self.slide_data.image_data.jpeg = svg_image.to_jpeg()
                    file = self.slide_data.image_data.jpeg.to_file()

            case key if key in {"json"}:
                file = convert_partial_to_bytes(self.slide_data.json_data, key)
            case _:
                raise ValueError(f"{_} is an invalid file type.")

        return file

    def save(self, key):
        self.to_file(key).save()

    def get_bytes(self, key):
        match key:
            case key if key in set(ImageExportFormats):
                svg_image = convert_partial_to_bytes(self.slide_data.image_data, key)

                if key == ImageExportFormats.SVG:
                    return svg_image.img_data
                elif key == ImageExportFormats.PNG:
                    self.slide_data.image_data.png = svg_image.to_png()
                    return self.slide_data.image_data.png.img_data
                elif key == ImageExportFormats.JPEG:
                    self.slide_data.image_data.jpeg = svg_image.to_jpeg()
                    return self.slide_data.image_data.jpeg.img_data

            case key if key in {"json"}:
                return convert_partial_to_bytes(
                    self.slide_data.json_data, key
                ).file_data
            case _:
                raise ValueError(f"{_} is an invalid file type.")
