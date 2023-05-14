from typing import Iterator
from typing import Generator
from dataclasses import dataclass
from itertools import chain
from gslide2media.presentation import Presentation
from gslide2media.utils import DataPartial
from gslide2media.utils import convert_partial_to_bytes
from gslide2media import config

from rich import print


@dataclass(slots=True, kw_only=True)
class Folder:
    folder_id: str | None = None
    folder_name: str | None = None
    parent: str | None = None
    presentation_ids: list[str] | None = None
    presentations: Iterator | list[Presentation] | None = None
    folder_ids: list[str] | None = None

    _root_instance = None
    _instances = {}  # type:ignore
    _folders: Iterator | None = None
    _custom_presentations: list[Presentation] | None = None
    _drive_folder_tree: dict | None = None
    _attributes: list[str] | None = None
    _index: int | None = None

    def __new__(
        cls,
        folder_id=None,
        folder_name=None,
        parent=None,
        presentation_ids=None,
        presentations=None,
        folder_ids=None,
    ):
        if folder_id is None and presentation_ids is None and folder_ids is None:
            if cls._root_instance is None:
                cls._root_instance = super(cls, cls).__new__(cls)
            return cls._root_instance
        else:
            instance_id = "batch" if presentation_ids or folder_ids else folder_id

            if folder_id not in cls._instances:
                cls._instances[instance_id] = super(cls, cls).__new__(cls)
                cls._instances[instance_id].folder_id = folder_id
                cls._instances[instance_id].folder_name = folder_name
                cls._instances[instance_id].parent = parent
                cls._instances[instance_id].presentation_ids = presentation_ids
            return cls._instances[instance_id]

    def __post_init__(self):
        if self is self.get_root_folder() and not self.presentation_ids and not self.folder_ids and not self.presentations:
            self.folder_id = "root"
            self.folder_name = "root"
            self.folders = self.get_folders_in_root_partial()
            self.presentations = self.get_presentations_in_root_partial()
            self.drive_folder_tree = self.walk()
        elif self.presentation_ids or self.folder_ids or self.presentations:
            if not self.folder_id:
                self.folder_id = "batch"
            if not self.folder_name:
                self.folder_name = "batch"
            if not self.parent:
                self.parent = "batch"

            self.folders = self.get_folders_from_ids_list()
            if self.presentations:
                self.custom_presentations = self.presentations
            self.presentations = self.get_presentations_from_ids_list()
        else:
            if not self.folder_name:
                self.folder_name = config.GOOGLE.get_folder_name(self.folder_id)
            if not self.parent:
                self.parent = config.GOOGLE.get_parent_folder_of_google_file(
                    self.folder_id
                )
            self.folders = self.get_folders_partial()
            self.presentations = self.get_presentations_partial()

    def __iter__(self) -> "Folder":
        self.attributes: list[str] = ["folders", "presentations"]
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

    def get_folders_partial(self):
        def func(obj):
            folders_list = config.GOOGLE.get_folders_from_drive_folder(obj.folder_id)

            return (
                Folder(folder_id=_["id"], folder_name=_["name"], parent=obj.folder_id)
                for _ in folders_list
            )

        return DataPartial(func)(obj=self)

    def get_presentations_partial(self):
        def func(obj):
            presentations_list = config.GOOGLE.get_presentations_from_drive_folder(
                obj.folder_id
            )

            return (
                Presentation(presentation_id=_["id"], parent=obj.folder_id)
                for _ in presentations_list
            )

        return DataPartial(func)(obj=self)

    def get_folders_in_root_partial(self):
        def func():
            folders_list = config.GOOGLE.get_folders_in_root()
            folders_list.extend(config.GOOGLE.get_shared_folders())

            return (
                Folder(folder_id=_["id"], folder_name=_["name"], parent="root")
                for _ in folders_list
            )

        return DataPartial(func)()

    def get_presentations_in_root_partial(self):
        def func():
            presentation_list = config.GOOGLE.get_presentations_in_root()
            presentation_list.extend(config.GOOGLE.get_shared_presentations())

            return (
                Presentation(presentation_id=_["id"], parent="root")
                for _ in presentation_list
            )

        return DataPartial(func)()

    def get_folders_from_ids_list(self):
        def func(obj):
            return (
                Folder(
                    folder_id=_,
                    folder_name=config.GOOGLE.get_folder_name(_),
                    parent=config.GOOGLE.get_parent_folder_of_google_file(_),
                )
                for _ in obj.folder_ids
            )

        return DataPartial(func)(obj=self)

    def get_presentations_from_ids_list(self):
        def func(obj):
            if obj.presentation_ids:
                presentations_from_ids = (
                    Presentation(
                        presentation_id=_,
                        parent=config.GOOGLE.get_parent_folder_of_google_file(_),
                    )
                    for _ in obj.presentation_ids
                )

                if self.custom_presentations:
                    presentations_from_ids = chain(presentations_from_ids, iter(self.custom_presentations))
                return presentations_from_ids
            
            elif self.custom_presentations:
                return iter(self.custom_presentations)

            return None

        return DataPartial(func)(obj=self)

    @classmethod
    def walk(cls):
        def func(folder=None, visited=None, level=0):
            if visited is None:
                visited = {}
            if folder is None:
                folder = Folder._root_instance

            fields = (folder.folder_id, folder.folder_name)
            current_dict = visited.setdefault(fields, {})

            for child in folder.folders.get():
                func(child, current_dict, level + 1)

            if level == 0:
                return visited

        return DataPartial(func)()

    @classmethod
    def get_root_folder(cls):
        return cls._root_instance

    def to_file(self, key_formats: set):
        for _ in convert_partial_to_bytes(self, "presentations"):
            yield from _.to_file(key_formats)

    def recursive_to_file(self, key_formats: set) -> Generator:
        def func(folder=None, presentations=None, level=0) -> Generator:
            if presentations is None:
                presentations = []
            if folder is None:
                folder = self

            if convert_partial_to_bytes(folder, "presentations"):
                yield from (_.to_file(key_formats) for _ in folder.presentations)

            for child in folder.folders.get():
                func(child, presentations, level + 1)

            if level == 0:
                return

        yield from func()
            

    def save(self, key_formats: set):
        for _ in convert_partial_to_bytes(self, "presentations"):
            _.save(key_formats)

    def recursive_save(self, key_formats: set):

        def func(folder=None, level=0):
            if folder is None:
                folder = self

            if convert_partial_to_bytes(folder, "presentations"):
                for _ in folder.presentations:
                    _.save(key_formats)

            for child in folder.folders.get():
                func(child, level + 1)

            if level == 0:
                return True
            
        return func()

    @property
    def folders(self) -> Iterator | None:
        return self._folders

    @folders.setter
    def folders(self, folders: Iterator):
        self._folders = folders

    @folders.deleter
    def folders(self):
        del self._folders

    @property
    def custom_presentations(self) -> list[Presentation] | None:
        return self._custom_presentations

    @custom_presentations.setter
    def custom_presentations(self, custom_presentations: list[Presentation]):
        self._custom_presentations = custom_presentations

    @custom_presentations.deleter
    def custom_presentations(self):
        del self._custom_presentations

    @property
    def drive_folder_tree(self) -> dict | None:
        return self._drive_folder_tree

    @drive_folder_tree.setter
    def drive_folder_tree(self, drive_folder_tree: dict | None):
        self._drive_folder_tree = drive_folder_tree

    @drive_folder_tree.deleter
    def drive_folder_tree(self):
        del self._drive_folder_tree

    @property
    def attributes(self) -> list[str] | None:
        return self._attributes

    @attributes.setter
    def attributes(self, attributes: list[str] | None):
        self._attributes = attributes

    @attributes.deleter
    def attributes(self):
        del self._attributes

    @property
    def index(self) -> int | None:
        return self._index

    @index.setter
    def index(self, index: int | None):
        self._index = index

    @index.deleter
    def index(self):
        del self._index
