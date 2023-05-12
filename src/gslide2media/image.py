from io import BytesIO

import cairosvg
from PIL import Image as PILImage

from gslide2media.enums import ImageExportFormats
from gslide2media.utils import dataclass_unique_instance_cache
from gslide2media.file import File
from gslide2media import config


@dataclass_unique_instance_cache(id_keys=["img_format", "presentation_id", "slide_id"])
class Image:
    img_format: ImageExportFormats
    img_data: bytes | list
    presentation_id: str
    slide_id: str
    presentation_order: int = 0
    is_composite: bool = False

    def to_file(self):
        return File(extension=self.img_format, file_data=self.img_data, presentation_id=self.presentation_id, slide_id=self.slide_id, presentation_order=self.presentation_order)

    def to_png(self):
        match self.img_format:
            case ImageExportFormats.SVG:
                image_data = cairosvg.svg2png(
                    self.img_data,
                    dpi=config.ARGS.dpi,
                    parent_width=config.ARGS.screen_width,
                    parent_height=config.ARGS.screen_height,
                    output_width=config.ARGS.screen_width,
                    output_height=config.ARGS.screen_height,
                    unsafe=True,
                )

                return Image(
                    img_format=ImageExportFormats.PNG,
                    img_data=image_data,
                    presentation_id=self.presentation_id,
                    slide_id=self.slide_id,
                    presentation_order=self.presentation_order,
                    is_composite=self.is_composite,
                )
            case ImageExportFormats.JPEG:
                with PILImage.open(BytesIO(self.img_data)) as img:
                    with BytesIO() as buffer:
                        img.resize((config.ARGS.screen_width, config.ARGS.screen_height))
                        img.save(buffer, format="PNG")
                        image_data = buffer.getvalue()
                return Image(
                    img_format=ImageExportFormats.PNG,
                    img_data=image_data,
                    presentation_id=self.presentation_id,
                    slide_id=self.slide_id,
                    presentation_order=self.presentation_order,
                    is_composite=self.is_composite,
                )

            case ImageExportFormats.PNG:
                return self
            case _:
                raise ValueError("Invalid Image Format")

    def to_jpeg(self):
        match self.img_format:
            case ImageExportFormats.SVG:
                png_image = self.to_png()
                return self._to_jpeg(png_image.img_data)
            case ImageExportFormats.PNG:
                return self._to_jpeg(self.img_data)
            case ImageExportFormats.JPEG:
                return self
            case _:
                raise ValueError("Invalid Image Format")

    def _to_jpeg(self, image_data: bytes):
        with PILImage.open(BytesIO(image_data)) as img:
            with BytesIO() as buffer:
                img = img.convert("RGB")
                img.resize((config.ARGS.screen_width, config.ARGS.screen_height))
                img.save(buffer, format="JPEG", quality=config.ARGS.jpeg_quality)
                bytes_data = buffer.getvalue()
        return Image(
            img_format=ImageExportFormats.JPEG,
            img_data=bytes_data,
            presentation_id=self.presentation_id,
            slide_id=self.slide_id,
            presentation_order=self.presentation_order,
            is_composite=self.is_composite,
        )
