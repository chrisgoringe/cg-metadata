import sys, os, git
import folder_paths
try:
    import custom_nodes.cg_custom_core
except:
    print("Installing cg_custom_nodes")
    repo_path = os.path.join(os.path.dirname(folder_paths.__file__), 'custom_nodes', 'cg_custom_core')  
    repo = git.Repo.clone_from('https://github.com/chrisgoringe/cg-custom-core.git/', repo_path)
    repo.git.clear_cache()
    repo.close()
    
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from .metadata import *
from .widget_nodes import *
from .metadata_nodes import *
from .configure_nodes import *
from .common import *

NODE_CLASS_MAPPINGS = { 
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
                        "Set Widgets from Saved Workflow" : SetWidgetsFromSavedWorkflow,
                      }

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
