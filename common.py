import os, random

module_root_directory_metadata = os.path.dirname(os.path.realpath(__file__))
config_file_metadata = os.path.join(module_root_directory_metadata,'configuration.yaml')

class Base_metadata:
    def __init__(self):
        pass
    FUNCTION = "func"
    CATEGORY = "metadata"
    REQUIRED = {}
    OPTIONAL = None
    HIDDEN = None
    @classmethod    
    def INPUT_TYPES(s):
        types = {"required": s.REQUIRED}
        if s.OPTIONAL:
            types["optional"] = s.OPTIONAL
        if s.HIDDEN:
            types["hidden"] = s.HIDDEN
        return types
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    
class AlwaysRerun():
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return random.random()
    
class classproperty(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, owner):
        return self.f(owner)

