import os, random

module_root_directory_metadata = os.path.dirname(os.path.realpath(__file__))
config_file_metadata = os.path.join(module_root_directory_metadata,'configuration.yaml')
  
class AlwaysRerun():
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return random.random()