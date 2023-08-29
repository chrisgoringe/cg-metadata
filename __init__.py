import sys, os, shutil
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from .metadata import *
from .common import *

NODE_CLASS_MAPPINGS = { "Metadata Controller" : Metadata,
                        "Load Metadata From Image" : LoadMetadataFromImage, 
                        "Load Image and Metadata" : LoadImageWithMetadata,
                        "Set Metadata" : SetMetadata,
                        "Set Arbitrary Metadata" : SetArbitraryMetadata,
                        "Get Metadata" : GetMetadata,
                        "Get Arbitrary Metadata" : GetArbitraryMetadata,
                        "Store Metadata in Image" : AddMetadataToImage,
                        "String to Int" : StringToInt,
                        "String to Float" : StringToFloat,
                      }

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

