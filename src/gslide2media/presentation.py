from typing import Iterator
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.parse import urlunparse
from urllib.parse import ParseResult as UrlParseResult
from io import BytesIO
import functools

import imageio

from gslide2media.slide import Slide
from gslide2media.file import File
from gslide2media.enums import GooglePresentationExportFormats
from gslide2media.enums import GooglePresentationExportTypes
from gslide2media.enums import ImageExportFormats
from gslide2media.enums import ExportFormats
from gslide2media.utils import DataPartial
from gslide2media.utils import convert_partial_to_bytes
from gslide2media.utils import dataclass_unique_instance_cache
from gslide2media import config


@dataclass
class PresentationExportUrls:
    presentation_id: str
    parent: str | None = None
    presentation_name: str | None = None
    is_batch: bool = False

    def __post_init__(self):
        self.set_resource_export_url_attributes()

    @staticmethod
    def create_presentation_export_url(
        presentation_id: str, export_format: GooglePresentationExportFormats
    ) -> UrlParseResult:
        return urlparse(
            "https://docs.google.com/presentation/d/"
            f"{presentation_id}"
            "/export/"
            f"{export_format}?"
            f"id={presentation_id}"
        )

    def set_resource_export_url_attributes(self):
        for _ in GooglePresentationExportFormats:
            setattr(
                self,
                _,
                self.create_presentation_export_url(self.presentation_id, _),
            )
            self.__annotations__[
                _.lower()
            ] = UrlParseResult  # pylint: disable=no-member

    def __iter__(self):
        self.index = 0
        self.attributes = [x.lower() for x in GooglePresentationExportFormats]
        return self

    def __next__(self):
        if self.index >= len(self.attributes):
            raise StopIteration

        attr_name = self.attributes[self.index]
        attr_value = getattr(self, attr_name)
        self.index += 1
        return (attr_name, urlunparse(attr_value))

    def __getitem__(self, key):
        if key.lower() not in set(GooglePresentationExportFormats):
            raise KeyError(f"'{key}' is not a valid export format")

        if key.lower() in set(GooglePresentationExportFormats):
            return DataPartial(self.get_file_bytes_from_url)(key=key)
        raise ValueError(f"{key} not a valid export format.")

    def get_file_bytes_from_url(self, key: GooglePresentationExportFormats) -> File:
        if key.lower() not in set(GooglePresentationExportFormats):
            raise KeyError(f"'{key}' is not a valid image format")

        url_obj = getattr(self, key)

        bytes_content = (
            config.GOOGLE.auth_google.google_authorized_session.get(  # type:ignore
                urlunparse(url_obj)
            ).content
        )

        return File(
            extension=key,
            file_data=bytes_content,
            presentation_id=self.presentation_id,
            parent=self.parent,
            presentation_name=self.presentation_name,  # type:ignore
            is_batch=self.is_batch,
        )


@dataclass
class FetchPresentationData:
    presentation_id: str
    presentation_urls: PresentationExportUrls
    export_type: GooglePresentationExportTypes
    parent: str | None = None
    presentation_name: str | None = None
    is_batch: bool = False

    def __post_init__(self):
        self.create_self_attributes(self.export_type)

    def __iter__(self):
        match self.export_type:
            case GooglePresentationExportTypes.FILE:
                self.attributes = list(
                    set(GooglePresentationExportFormats)
                    - {GooglePresentationExportFormats.JSON}
                )
            case GooglePresentationExportTypes.DATA:
                self.attributes = [GooglePresentationExportFormats.JSON]
            case GooglePresentationExportTypes.VIDEO:
                self.attributes = [ExportFormats.MP4]
        self.index = 0
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

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get_json_presentation_data(self):
        def func(obj):
            if not self.is_batch:
                presentation_data = config.GOOGLE.get_google_slides_presentation(
                    obj.presentation_id
                )
                return File(
                    extension="json",
                    file_data=presentation_data,
                    presentation_id=obj.presentation_id,
                    parent=obj.parent,
                    presentation_name=obj.presentation_name,
                    is_batch=self.is_batch,
                )

        return DataPartial(func)(obj=self)

    def get_mp4_bytes(self, slides: list | None | None = None):
        def func(obj, slides: list | None = None):
            output_params = {
                "fps": config.ARGS.fps,
                "extension": ".mp4",
                "format_hint": ".mp4",
                "plugin": "pyav",
                "codec": "h264",
            }

            frame_count = int(
                config.ARGS.mp4_slide_duration_secs * config.ARGS.fps
            )  # type:ignore
            video_frames = []

            for slide in slides:  # type: ignore
                for _ in range(frame_count):
                    image = imageio.imread(slide.get_bytes(ImageExportFormats.PNG))
                    video_frames.append(image)

            mp4_bytes = BytesIO()
            imageio.v3.imwrite(mp4_bytes, video_frames, **output_params)  # type:ignore
            return File(
                extension=ExportFormats.MP4,
                file_data=mp4_bytes,
                presentation_id=obj.presentation_id,
                parent=self.parent,
                presentation_name=self.presentation_name,
                is_batch=self.is_batch
            )

        return DataPartial(func)

    def create_self_attributes(self, export_type: GooglePresentationExportTypes):
        if export_type is GooglePresentationExportTypes.FILE:
            for _ in set(GooglePresentationExportFormats) - {
                GooglePresentationExportFormats.JSON
            }:
                setattr(self, _, self.presentation_urls[_])
                self.__annotations__[_.lower()] = type(
                    functools.partial
                )  # pylint: disable=no-member
        elif export_type is GooglePresentationExportTypes.DATA:
            setattr(self, "json", self.get_json_presentation_data())
            self.__annotations__["json"] = dict  # pylint: disable=no-member
        elif export_type is GooglePresentationExportTypes.VIDEO:
            setattr(self, "mp4", self.get_mp4_bytes())


@dataclass
class PresentationData:
    presentation_id: str
    parent: str | None = None
    presentation_name: str | None = None
    is_batch: bool = False

    def __post_init__(self):
        self.presentation_urls = PresentationExportUrls(
            self.presentation_id, self.parent, self.presentation_name, self.is_batch
        )
        self.file_data = FetchPresentationData(
            self.presentation_id,
            self.presentation_urls,
            GooglePresentationExportTypes.FILE,
            self.parent,
            self.presentation_name,
            self.is_batch,
        )
        self.json_data = FetchPresentationData(
            self.presentation_id,
            self.presentation_urls,
            GooglePresentationExportTypes.DATA,
            self.parent,
            self.presentation_name,
            self.is_batch
        )
        self.mp4_data = FetchPresentationData(
            self.presentation_id,
            self.presentation_urls,
            GooglePresentationExportTypes.VIDEO,
            self.parent,
            self.presentation_name,
            self.is_batch
        )

    def __iter__(self):
        self.index = 0
        self.attributes = ["file_data", "json_data", "mp4_data"]
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

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @property
    def file_data(self):
        return self._file_data

    @file_data.setter
    def file_data(self, file_data):
        self._file_data = file_data

    @file_data.deleter
    def file_data(self):
        del self._file_data

    @property
    def json_data(self):
        return self._json_data

    @json_data.setter
    def json_data(self, json_data):
        self._json_data = json_data

    @json_data.deleter
    def json_data(self):
        del self._json_data

    @property
    def mp4_data(self):
        return self._mp4_data

    @mp4_data.setter
    def mp4_data(self, mp4_data):
        self._mp4_data = mp4_data

    @mp4_data.deleter
    def mp4_data(self):
        del self._mp4_data


@dataclass_unique_instance_cache(id_keys=["presentation_id", "parent"])
class Presentation:
    presentation_id: str | None = None
    parent: str | None = None
    slide_ids: list[tuple[str, str]] | None = None
    presentation_name: str | None = None
    is_batch: bool = False

    _slides: list | None = None
    _presentation_data: PresentationData | None = None
    _instances = {}  # type:ignore

    def __new__(cls, *args, **kwargs):
        instance_id = tuple(
            kwargs[_] if hasattr(kwargs, _) else "batch"
            for _ in ["presentation_id", "parent"]
        )
        if instance_id not in cls._instances:
            cls._instances[instance_id] = super(cls, cls).__new__(cls)

        return cls._instances[instance_id]

    def __post_init__(self):
        if not self.is_batch and self.presentation_id and not self.slide_ids:
            self.presentation_name = config.GOOGLE.get_presentation_name(self.presentation_id)
            self.presentation_data = PresentationData(self.presentation_id, self.parent, self.presentation_name)
        else:
            self.presentation_data = PresentationData(self.presentation_id, self.parent, self.presentation_name, self.is_batch)

        self.populate_slides()
        self.presentation_data.mp4_data.mp4 = self.presentation_data.mp4_data.mp4(
            obj=self.presentation_data.mp4_data, slides=self.slides
        )

    def populate_slides(self):
        if self.slide_ids is None:
            self.presentation_data.json_data.json = convert_partial_to_bytes(self.presentation_data.json_data, GooglePresentationExportFormats.JSON)
            self.slides = [
                Slide(
                    slide_id=slide["objectId"],
                    presentation_id=self.presentation_id,
                    presentation_order=i,
                    slide_duration_secs=config.ARGS.mp4_slide_duration_secs,
                    parent=self.parent,
                    presentation_name=self.presentation_name,
                )
                for i, slide in enumerate(
                    self.presentation_data.json_data.json.file_data.get("slides")
                )
            ]
        else:
            self.slides = [
                Slide(
                    slide_id=_[1],
                    presentation_id=_[0],
                    presentation_order=i,
                    slide_duration_secs=config.ARGS.mp4_slide_duration_secs,
                    parent=self.parent,
                    presentation_name=self.presentation_name,
                    is_batch=True,
                )
                for i, _ in enumerate(self.slide_ids)
            ]

    def save(self, key_formats: set):
        file = None
        for key in key_formats:
            match key:
                case key if key in set(ImageExportFormats):
                    for _ in self.slides:  # type:ignore
                        _.save(key)
                case key if key in set(GooglePresentationExportFormats) - {
                    GooglePresentationExportFormats.JSON
                }:
                    file = convert_partial_to_bytes(
                        self.presentation_data.file_data, key  # type:ignore
                    )
                case key if key == ExportFormats.JSON:
                    if not self.slide_ids:
                        file = convert_partial_to_bytes(
                            self.presentation_data.json_data, key  # type:ignore
                        )
                    for _ in self.slides:  # type:ignore
                        _.save(key)
                case key if key == ExportFormats.MP4:
                    file = convert_partial_to_bytes(
                        self.presentation_data.mp4_data, key  # type:ignore
                    )
                case _:
                    raise ValueError(f"{key} is not a valid file type.")
            if file:
                file.save()

    def get_bytes(self, key):
        match key:
            case key if key in set(ImageExportFormats):
                return (slide.get_bytes(key) for slide in self.slides)
            case key if key in set(GooglePresentationExportFormats) - {
                GooglePresentationExportFormats.JSON
            }:
                return convert_partial_to_bytes(
                    self.presentation_data.file_data, key
                ).file_data
            case key if key == ExportFormats.JSON:
                return convert_partial_to_bytes(
                    self.presentation_data.json_data, key
                ).file_data
            case key if key == ExportFormats.MP4:
                return convert_partial_to_bytes(
                    self.presentation_data.mp4_data, key
                ).file_data.getbuffer()
            case _:
                raise ValueError(f"{key} is not a valid file type.")

    @property
    def slides(self) -> list | None:
        return self._slides

    @slides.setter
    def slides(self, slides: list | None):
        self._slides = slides

    @slides.deleter
    def slides(self):
        del self._slides

    @property
    def presentation_data(self) -> PresentationData | None:
        return self._presentation_data

    @presentation_data.setter
    def presentation_data(self, presentation_data: PresentationData | None):
        self._presentation_data = presentation_data

    @presentation_data.deleter
    def presentation_data(self):
        del self._presentation_data
