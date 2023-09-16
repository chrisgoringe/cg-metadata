import os, yaml
from common import module_root_directory_metadata

config_file_metadata = os.path.join(module_root_directory_metadata,'configuration.yaml')

def get_config_metadata(item, exception_if_missing_or_empty=True):
    if not os.path.exists(config_file_metadata):
        raise Exception(f"Configuration file not found at {config_file_metadata}")
    with open(config_file_metadata, 'r') as file:
        y:dict = yaml.safe_load(file)
        value = y.get(item,None)
        if value is None and exception_if_missing_or_empty:
            raise Exception(f"{item} in {config_file_metadata} was missing or empty and is required")
        return value
    