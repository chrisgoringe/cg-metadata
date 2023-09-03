import os, yaml, random
import folder_paths

module_root_directory_metadata = os.path.dirname(os.path.realpath(__file__))
config_file_metadata = os.path.join(module_root_directory_metadata,'configuration.yaml')
module_js_directory_metadata = os.path.join(module_root_directory_metadata, "js")

application_root_directory = os.path.dirname(folder_paths.__file__)
application_web_extensions_directory = os.path.join(application_root_directory, "web", "extensions", "cg-nodes", "metadata")

def get_config_metadata(item, exception_if_missing_or_empty=False):
    if not os.path.exists(config_file_metadata):
        raise Exception(f"Configuration file not found at {config_file_metadata}")
    with open(config_file_metadata, 'r') as file:
        y:dict = yaml.safe_load(file)
        value = y.get(item,None)
        if value is None and exception_if_missing_or_empty:
            raise Exception(f"{item} in {config_file_metadata} was missing or empty and is required")
        return value

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