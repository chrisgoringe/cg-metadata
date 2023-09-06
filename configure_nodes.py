import os, yaml
from common import Base_metadata, module_root_directory_metadata, AlwaysRerun, classproperty

config_file_metadata = os.path.join(module_root_directory_metadata,'configuration.yaml')

def _get_config_metadata(item, exception_if_missing_or_empty):
    if not os.path.exists(config_file_metadata):
        raise Exception(f"Configuration file not found at {config_file_metadata}")
    with open(config_file_metadata, 'r') as file:
        y:dict = yaml.safe_load(file)
        value = y.get(item,None)
        if value is None and exception_if_missing_or_empty:
            raise Exception(f"{item} in {config_file_metadata} was missing or empty and is required")
        return value
    
def get_config_metadata(item, exception_if_missing_or_empty=False):
    if item=='metadata_sources':
        return EditConfiguration.CONFIGURATION
    return _get_config_metadata(item, exception_if_missing_or_empty)

class EditConfiguration(Base_metadata, AlwaysRerun):
    CATEGORY = "metadata"
    @classproperty
    def REQUIRED(cls):
        return {"configuration": ("STRING", {"default":cls.display(cls.CONFIGURATION), "multiline":True})}
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("configuration", )
    OUTPUT_NODE = True
    CONFIGURATION = _get_config_metadata('metadata_sources', True)

    @classmethod
    def display(cls, thelist):
        return "\n- ".join(['metadata_sources',]+thelist)
    
    @classmethod
    def parse(cls, string):
        return list (s.strip() for s in string.split('- '))[1:]

    @classmethod
    def func(cls, configuration):
        cls.CONFIGURATION = cls.parse(configuration)
        return (configuration,)