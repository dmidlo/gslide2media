import math

from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from gslide2media.enums import OptionsTimeAttrs

METRIC_CONVERSION_RATIO: float = 2.54


@dataclass(slots=True, kw_only=True)
class Screen:
    name: str
    pixel_width: int | None = None
    pixel_height: int | None = None
    _diagonal: float | None = None
    _diagonal_cm: float | None = None

    _create_time_utc: int | None = None
    _modify_time_utc: int | None = None
    last_used_time_utc: int | None = None

    def __post_init__(self) -> None:
        if not self._create_time_utc:
            self.mark_time(OptionsTimeAttrs.CREATE)
        if not self._modify_time_utc:
            self.mark_time(OptionsTimeAttrs.MODIFY)
        if not self.last_used_time_utc:
            self.mark_time(OptionsTimeAttrs.LAST_USED)

    def __hash__(self) -> int:
        if self.name:
            return hash(self.name)

        hash_attrs = [value for _, value in asdict(self).items()]
        return hash(tuple(hash_attrs))

    def __eq__(self, other) -> bool:
        if self is other:
            return True

        if not isinstance(other, self.__class__):
            return False

        if self.name and self.name == other.name:
            return True

        return all(
            _self[1] == _other[1]
            for _self, _other in zip(asdict(self).items(), asdict(other).items())
        )
    
    def mark_time(self, action: OptionsTimeAttrs) -> None:
        utc_timestamp = int(datetime.now(timezone.utc).timestamp())
        match action:
            case OptionsTimeAttrs.CREATE:
                self._create_time_utc = utc_timestamp
            case OptionsTimeAttrs.MODIFY:
                self._modify_time_utc = utc_timestamp
            case OptionsTimeAttrs.LAST_USED:
                self.last_used_time_utc = utc_timestamp
            case _:
                raise AttributeError(f"invalid time action: {action}.")

    @property
    def diagonal(self) -> float | None:
        if isinstance(self._diagonal, (float, int)):
            return self._diagonal
        return self.diagonal_cm / METRIC_CONVERSION_RATIO

    @diagonal.setter
    def diagonal(self, diagonal: float | None):
        self._diagonal = diagonal

    @diagonal.deleter
    def diagonal(self):
        del self._diagonal

    @property
    def diagonal_cm(self) -> float | None:
        if isinstance(self._diagonal_cm, (float, int)):
            return self._diagonal_cm
        return self._diagonal * METRIC_CONVERSION_RATIO

    @diagonal_cm.setter
    def diagonal_cm(self, diagonal_cm: float | None):
        self._diagonal_cm = diagonal_cm

    @diagonal_cm.deleter
    def diagonal_cm(self):
        del self._diagonal_cm

    @property
    def width_inch(self) -> float:
        return math.sqrt(self.diagonal**2 / (1 + self.ratio**2))
    
    @property
    def height_inch(self) -> float:
        return self.width_inch * self.ratio

    @property
    def width_cm(self) -> float:
        return self.width_inch * METRIC_CONVERSION_RATIO

    @property
    def height_cm(self) -> float:
        return self.height_inch * METRIC_CONVERSION_RATIO

    @property
    def area_inch(self) -> float:
        return self.height_inch * self.width_inch

    @property
    def area_cm(self) -> float:
        return self.height_cm * self.width_cm

    @property
    def width_ppi(self) -> float:
        return self.pixel_width / self.width_inch

    @property
    def height_ppi(self) -> float:
        return self.pixel_height / self.width_inch

    @property
    def dpi(self) -> int:
        return min([self.height_ppi, self.width_ppi])
    
    @property
    def ratio(self) -> float:
        return self.pixel_width / self.pixel_height

    @property
    def megapixels(self) -> float:
        return round((self.pixel_width * self.pixel_height) / 1000000, 2)
