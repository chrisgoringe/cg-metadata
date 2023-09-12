from .common import AlwaysRerun
from custom_nodes.cg_custom_core.base import BaseNode
from custom_nodes.cg_custom_core.ui_decorator import ui_signal
from .configure_nodes import get_config_metadata
from .metadata import Metadata, MetadataException, MASTER_KEY
from .cg_node_addressing import NodeAddressing, NodeAddressingException
from nodes import LoadImage
from folder_paths import get_annotated_filepath
import sys, json

@ui_signal('display_text')
class ShowMetadata(BaseNode, AlwaysRerun):
    CATEGORY = "metadata"
    OPTIONAL = { "trigger": ("*",{}) }
    def func(self, **kwargs):
        return (Metadata.pretty(),)
    
class LoadImageWithMetadata(AlwaysRerun, LoadImage):
    OUTPUT_NODE = True
    FUNCTION = "func"
    CATEGORY = "metadata"
    def func(self, image):
        Metadata.set_debug()
        try:
            Metadata.add_dictionary_from_image(get_annotated_filepath(image))
        except MetadataException:
            print(sys.exc_info()[1].args[0])
        return self.load_image(image)
    
class GetMetadataString(BaseNode, AlwaysRerun):
    REQUIRED = { "key": ("STRING", {"default":"key"}) }
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("value", "key" )
    OPTIONAL = { "trigger": ("*",{}) }
    def func(self, key, trigger=None):
        return (str(Metadata.get(key,return_type="STRING")), key, )

class ClearMetadata(BaseNode, AlwaysRerun):
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("trigger", )
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO" }
    def func(self, extra_pnginfo:dict):
        Metadata.clear()
        extra_pnginfo.pop(MASTER_KEY, None)
        return ("",)
    
class SetMetadataString(BaseNode, AlwaysRerun):
    REQUIRED = { "key": ("STRING", {"default":"key"}), "value": ("STRING", {"default":""}) }
    OPTIONAL = { "trigger": ("*",{}) }
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("value", "key" )
    def func(self, key, value, trigger=None):
        Metadata.set_debug()
        Metadata.set(key,value)
        return (value, key, )

@ui_signal(['modify_other','display_text'])
class SendMetadataToWidgets(BaseNode, AlwaysRerun):
    REQUIRED = { "active": (["yes","no"],{}) }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    OPTIONAL = { "trigger": ("*",{}) }
    CATEGORY = "metadata/widgets"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_displayed",)
    OUTPUT_NODE = True
    def func(self, active, extra_pnginfo:dict, prompt, trigger=None):
        if not active=="yes":
            return ("off", [], "turned off")
        set = {}
        key_missing = {}
        error_setting = {}
        updates = []
        for target in get_config_metadata('metadata_sources'):
            try:
                key = ""
                display_target_name = target.split(",")[0]
                key, _, _, _ = NodeAddressing.parse_source(target)
                value = Metadata.get(key)
                if value is None:
                    key_missing[target] = f"{key}"
                    continue
                _, old_value = NodeAddressing.get_key_and_value(prompt, extra_pnginfo, target, widgets_only=True)
                if isinstance(old_value, float):
                    value = float(value)
                elif isinstance(old_value, int):
                    value = int(value)
                else:
                    value = str(value)
                node_id, widget_name = NodeAddressing.set_value(prompt, extra_pnginfo, target, value)
                set[target] = value
                updates.append((str(node_id), widget_name, str(value)))
            except NodeAddressingException:
                message = sys.exc_info()[1].args[0]
                print(message)
                error_setting[target] = f"  ** {key} {message}"

        text = json.dumps({"Set": set, "Keys not in metadata": key_missing, "Failed to set": error_setting}, indent=2)
        return(text, updates, text)

class AddMetadataToImage(BaseNode):
    REQUIRED = { "image": ("IMAGE", {}), }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ("IMAGE",)
    OUTPUT_NODE = True
    OPTIONAL = { "trigger": ("*",{}) }

    def func(self, image, extra_pnginfo:dict, prompt, trigger=None):
        Metadata.set_debug()
        Metadata.debug_info(extra_pnginfo, prompt)
        issues = False
  
        for source in get_config_metadata('metadata_sources'):
            try:
                key, value = NodeAddressing.get_key_and_value(prompt, extra_pnginfo, source)
                Metadata.set(key, value)
            except NodeAddressingException:
                print(sys.exc_info()[1].args[0])
                issues = True

        if issues and not Metadata.debug:
            print(f"Consider turning debug on in Metadata Controller to help locate the missing data.")

        Metadata.store(extra_pnginfo)

        return (image,)
