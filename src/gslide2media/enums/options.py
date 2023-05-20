from enum import StrEnum, auto


class OptionsSource(StrEnum):
    CLI = auto()
    API = auto()
    DEFAULT = auto()


class OptionsTimeAttrs(StrEnum):
    CREATE = auto()
    MODIFY = auto()
    LAST_USED = auto()
