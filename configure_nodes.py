import os, yaml
from custom_nodes.cg_custom_core.base import BaseNode, classproperty
from common import module_root_directory_metadata, AlwaysRerun

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
        return ConfigureMetadataSources.CONFIGURATION
    return _get_config_metadata(item, exception_if_missing_or_empty)

class ConfigureMetadataSources(BaseNode, AlwaysRerun):
    CATEGORY = "metadata"
    @classproperty
    def REQUIRED(cls):
        return { "active": (["yes","no"],{}), "configuration": ("STRING", {"default":cls.display(cls.CONFIGURATION), "multiline":True})}
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("configuration", )
    OPTIONAL = { "trigger": ("*",{}) }
    OUTPUT_NODE = True
    CONFIGURATION = _get_config_metadata('metadata_sources', True)

    @classmethod
    def display(cls, thelist):
        return "\n- ".join(['metadata_sources',]+thelist)
    
    @classmethod
    def parse(cls, string):
        return list (s.strip() for s in string.split('- '))[1:]

    @classmethod
    def func(cls, active, configuration, trigger=None):
        if active=="yes":
            cls.CONFIGURATION = cls.parse(configuration)
        return (configuration,)