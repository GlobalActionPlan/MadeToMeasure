from repoze.folder import Folder
from zope.interface import implements

from madetomeasure.interfaces import IBaseFolder


class BaseFolder(Folder):
    __doc__ = IBaseFolder.__doc__
    implements(IBaseFolder)

    @property
    def content_type(self):
        raise NotImplementedError("Must be implemented by subclass")
    display_name = allowed_contexts = content_type
    

    def get_title(self):
        return getattr(self, '__title__', '')
    
    def set_title(self, value):
        self.__title__ = value
