import sys, os, shutil
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from .metadata import *
from .string_nodes import *
from .metadata_nodes import *
from .common import *

NODE_CLASS_MAPPINGS = { 
                        "Clear Metadata at Start" : ClearMetadataAtStart,
                        "Store Metadata in Image" : AddMetadataToImage,
                        "Load Image and Metadata" : LoadImageWithMetadata,
                        "Get Metadata" : GetMetadata,
                        "Get Metadata String" : GetMetadataString,
                        "Set Metadata String" : SetMetadataString,
                        "Show Metadata" : ShowMetadata,
                        "Show Text" : ShowText,
                        "Set Widget Value" : SetWidget,
                        "Set Metadata from Widget" : SetMetadataFromWidget,
                      }

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

shutil.copytree(module_js_directory_metadata, application_web_extensions_directory, dirs_exist_ok=True)