from typing import Iterator
from dataclasses import dataclass
from gslide2media.presentation import Presentation
from gslide2media.utils import DataPartial
from gslide2media.utils import convert_partial_to_bytes
from gslide2media import config

@dataclass(slots=True)
class Folder:
    folder_id: str | None = None
    folder_name: str | None = None
    parent: str | None = None

    _root_instance = None
    _instances = {}
    _folders: Iterator | None = None
    _presentations: Iterator | None = None
    _drive_folder_tree: dict | None = None
    _attributes: list | None = None
    _index: int | None = None

    def __new__(cls, folder_id=None, folder_name=None, parent=None):
        if folder_id is None:
            if cls._root_instance is None:
                cls._root_instance = super(cls, cls).__new__(cls)
            return cls._root_instance
        else:
            if folder_id not in cls._instances:
                cls._instances[folder_id] = super(cls, cls).__new__(cls)
                cls._instances[folder_id].folder_id = folder_id
                cls._instances[folder_id].folder_name = folder_name
                cls._instances[folder_id].parent = parent
            return cls._instances[folder_id]
        
    def __post_init__(self):
        if self is self.get_root_folder():
            self.folder_id = "root"
            self.folder_name = "root"
            self.folders = self.get_folders_in_root_partial()
            self.presentations = self.get_presentations_in_root_partial()
            self.drive_folder_tree = self.walk()
        else:
            if not self.folder_name:
                self.folder_name = config.GOOGLE.get_folder_name(self.folder_id)
            if not self.parent:
                self.parent = config.GOOGLE.get_parent_folder_of_google_file(self.folder_id)
            self.folders = self.get_folders_partial()
            self.presentations = self.get_presentations_partial()

    def __iter__(self):
        self.attributes = ["folders", "presentations"]
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

            return (Folder(_["id"], _["name"], obj.folder_id) for _ in folders_list)
        return DataPartial(func)(obj=self)
    
    def get_presentations_partial(self):
        def func(obj):
            presentations_list = config.GOOGLE.get_presentations_from_drive_folder(obj.folder_id)

            return (Presentation(presentation_id=_["id"], parent=obj.folder_id) for _ in presentations_list)
        return DataPartial(func)(obj=self)

    def get_folders_in_root_partial(self):
        def func():
            folders_list = config.GOOGLE.get_folders_in_root()
            folders_list.extend(config.GOOGLE.get_shared_folders())
            
            return (Folder(_["id"], _["name"], "root") for _ in folders_list)
        
        return DataPartial(func)()
    
    def get_presentations_in_root_partial(self):
        def func():
            presentation_list = config.GOOGLE.get_presentations_in_root()
            presentation_list.extend(config.GOOGLE.get_shared_presentations())

            return (Presentation(presentation_id=_["id"], parent="root") for _ in presentation_list)
        
        return DataPartial(func)()

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

    def save_to_file(self, key_formats: set):
        for _ in convert_partial_to_bytes(self, "presentations"):
            _.save_to_file(key_formats)

    @property
    def folders(self) -> Iterator:
        return self._folders
    
    @folders.setter
    def folders(self, folders: Iterator):
        self._folders = folders

    @folders.deleter
    def folders(self):
        del self._folders

    @property
    def presentations(self) -> Iterator:
        return self._presentations
    
    @presentations.setter
    def presentations(self, presentations: Iterator):
        self._presentations = presentations

    @presentations.deleter
    def presentations(self):
        del self._presentations

    @property
    def drive_folder_tree(self) -> Iterator:
        return self._drive_folder_tree
    
    @drive_folder_tree.setter
    def drive_folder_tree(self, drive_folder_tree: Iterator):
        self._drive_folder_tree = drive_folder_tree

    @drive_folder_tree.deleter
    def drive_folder_tree(self):
        del self._drive_folder_tree

    @property
    def attributes(self) -> Iterator:
        return self._attributes
    
    @attributes.setter
    def attributes(self, attributes: Iterator):
        self._attributes = attributes

    @attributes.deleter
    def attributes(self):
        del self._attributes

    @property
    def index(self) -> Iterator:
        return self._index
    
    @index.setter
    def index(self, index: Iterator):
        self._index = index

    @index.deleter
    def index(self):
        del self._index
