from repoze.folder import Folder

class BaseFolder(Folder):

    def get_title(self):
        return getattr(self, '__title__', '')
    
    def set_title(self, value):
        self.__title__ = value