import sys, os, shutil
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from .metadata import *
from .common import *

NODE_CLASS_MAPPINGS = { "Store Metadata in Image" : AddMetadataToImage,
                        "Load Image and Metadata" : LoadImageWithMetadata,
                        "Get Metadata" : GetMetadata,
                        "Get Metadata String" : GetMetadataString,
                        "Set Metadata String" : SetMetadataString,
                      }

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

