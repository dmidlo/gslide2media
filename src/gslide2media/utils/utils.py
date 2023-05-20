"""Write a set of bytes to a file path.

Functions:
    save_image_to_file(image_path: Path, image_bytes: bytes) -> None

        Write a set of bytes to a file path.
"""

import functools
from typing import NamedTuple
from typing import Callable
from typing import List
from dataclasses import dataclass, asdict, _process_class  # type:ignore


def partial_decorator(*args, **kwargs):
    def wrapper(func):
        partial_func = functools.partial(func, *args, **kwargs)
        functools.update_wrapper(partial_func, func)
        return partial_func

    return wrapper


def create_partial(func, *args, **kwargs):
    return partial_decorator(*args, **kwargs)(func)


@dataclass
class DataPartial:
    fmt_fnc: Callable
    key: str = "get"

    def __post_init__(self):
        self.partial_keys = [(self.key.lower(), type(functools.partial))]
        self.partial = NamedTuple("_DataPartial", self.partial_keys)

    def __call__(self, **kwargs):
        dict_data = {self.key: create_partial(self.fmt_fnc, **kwargs)}

        return self.partial(**dict_data)


def convert_partial_to_bytes(obj, key):
    if hasattr(obj[key], "_fields"):
        obj[key] = obj[key][0]()
    return obj[key]


def dataclass_unique_instance_cache(
    cls=None,
    /,
    *,
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
    match_args=True,
    kw_only=True,
    slots=True,
    weakref_slot=False,
    id_keys: List[str] | None = None,
):
    def wrap(cls):
        cls = _process_class(
            cls,
            init,
            repr,
            eq,
            order,
            unsafe_hash,
            frozen,
            match_args,
            kw_only,
            slots,
            weakref_slot,
        )

        id_keys_is_list_of_strings = (
            bool(id_keys)
            and isinstance(id_keys, list)
            and all(isinstance(_, str) for _ in id_keys)
        )
        id_keys_are_valid = all(
            _ if _ in set(cls.__dataclass_fields__) else False for _ in id_keys
        )

        if not id_keys_is_list_of_strings:
            raise ValueError(
                "dataclass_unique_instance_cache: requires [list] of 'params' to use as identifiers."
            )

        if not id_keys_are_valid:
            raise ValueError(
                "dataclass_unique_instance_cache: Invalid id_keys.  id_keys not dataclass field."
            )

        cls._instances = {}

        def new(cls, *args, **kwargs):
            # to make this decorator more generic.
            instance_id = tuple(kwargs[_] for _ in id_keys)

            if instance_id not in cls._instances:
                cls._instances[instance_id] = super(cls, cls).__new__(  # pylint: disable=no-value-for-parameter
                    cls
                )

            return cls._instances[instance_id]
        
        def to_dict(cls):
            return asdict(cls)

        setattr(cls, "__new__", new)
        setattr(cls, "to_dict", to_dict)
        return cls

    if cls is None:
        return wrap

    return wrap(cls)
