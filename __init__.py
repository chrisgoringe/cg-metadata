import sys, os
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from .metadata import *
from .widget_nodes import *
from .metadata_nodes import *
from .configure_nodes import *
from .common import *

NODE_CLASS_MAPPINGS = { 
                        "Configure Metadata Sources" : ConfigureMetadataSources,
                        "Clear Metadata" : ClearMetadata,
                        "Store Metadata in Image" : AddMetadataToImage,
                        "Load Image and Metadata" : LoadImageWithMetadata,
                        "Get Metadata String" : GetMetadataString,
                        "Set Metadata String" : SetMetadataString,
                        "Show Metadata" : ShowMetadata,
                        "Send Metadata to Widgets": SendMetadataToWidgets,
                        "Set Widget Int" : SetWidgetInt,
                        "Set Widget Float" : SetWidgetFloat,
                        "Set Widget String" : SetWidgetString,
                        "Set Widget from Metadata" : SetWidgetFromMetadata,
                        "Set Metadata from Widget" : SetMetadataFromWidget,
                      }

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
