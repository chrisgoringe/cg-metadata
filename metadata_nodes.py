from .common import AlwaysRerun
from custom_nodes.cg_custom_core.base import BaseNode, classproperty
from custom_nodes.cg_custom_core.ui_decorator import ui_signal
from .configure_nodes import get_config_metadata
from .metadata import Metadata, MetadataException, MASTER_KEY
from .cg_node_addressing import NodeAddressing, NodeAddressingException, Mapping
from nodes import LoadImage
from folder_paths import get_annotated_filepath
import sys, json

_bad  = "#773333"
_good = "#114411"

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
    RETURN_TYPES = LoadImage.RETURN_TYPES + ("STRING","STRING",)
    RETURN_NAMES = ("image", "mask", "filename", "metadata")
    def func(self, image):
        Metadata.set_debug()
        try:
            Metadata.add_dictionary_from_image(get_annotated_filepath(image))
        except MetadataException:
            print(sys.exc_info()[1].args[0])
        return self.load_image(image) + (image,Metadata.pretty())
    
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

@ui_signal(['modify_other','set_title_color'])
class SendMetadataToWidgets(BaseNode, AlwaysRerun):
    CONFIGURATION = get_config_metadata('metadata_sources', True)
    @classproperty
    def REQUIRED(cls):
        return {
            "image": ("IMAGE", {}),
            "active": (["yes","no"],{}), 
            "configuration": ("STRING", {"default":Mapping.as_yaml(get_config_metadata('metadata_sources', True)), "multiline":True})
        }
    
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    CATEGORY = "metadata/widgets"
    RETURN_TYPES = ("IMAGE","STRING",)
    RETURN_NAMES = ("image","results",)
    
    def func(self, image, active, configuration, extra_pnginfo:dict, prompt, trigger=None):
        if not active=="yes":
            return (image, "off", [], None)
        set = {}
        key_missing = {}
        error_setting = {}
        updates = []
        mappings, issues = Mapping.parse_yaml(configuration)
        for mapping in mappings:
            try:
                value = Metadata.get(mapping.key)
                if value is None:
                    key_missing[mapping.meta_to_node()] = f"{mapping.key}"
                    continue
                NodeAddressing.get_key_and_value(prompt, extra_pnginfo, mapping, widgets_only=True)
                value = float(value) if isinstance(mapping.value, float) else int(value) if isinstance(mapping.value, int) else str(value)
                NodeAddressing.set_value(prompt, extra_pnginfo, mapping, value)
                set[mapping.node_comma_meta()] = value
                updates.append((str(mapping.node_id), mapping.input_name, str(value)))
            except NodeAddressingException:
                message = sys.exc_info()[1].args[0]
                print(message)
                error_setting[mapping.node_comma_meta()] = f"  ** {mapping.key} {message}"

        labels = [('Set', set), ('Key not in metadata', key_missing), ('Failed to set', error_setting), ('Parse error', issues)]
        text = json.dumps({label:ob for label, ob in labels if ob}, indent=2)
        color = _bad if key_missing or error_setting or issues else _good
        return(image, text, updates, color)

@ui_signal('set_title_color')
class AddMetadataToImage(BaseNode):
    CONFIGURATION = get_config_metadata('metadata_sources', True)
    @classproperty
    def REQUIRED(cls):
        return {
            "image": ("IMAGE", {}),
            "configuration": ("STRING", {"default":Mapping.as_yaml(get_config_metadata('metadata_sources', True)), "multiline":True})
        }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ("IMAGE", "STRING", "STRING",)
    RETURN_NAMES = ("image", "metadata", "problems",)
    OUTPUT_NODE = True
    CATEGORY = "metadata"

    def func(self, image, configuration, extra_pnginfo:dict, prompt):
        Metadata.set_debug()
        Metadata.debug_info(extra_pnginfo, prompt)

        mappings, issues = Mapping.parse_yaml(configuration)
        for mapping in mappings:
            try:
                NodeAddressing.get_key_and_value(prompt, extra_pnginfo, mapping)
                Metadata.set(mapping.key, mapping.value)
            except NodeAddressingException:
                print(sys.exc_info()[1].args[0])
                issues = issues+f"\n{sys.exc_info()[1].args[0]}"

        if issues and not Metadata.debug:
            print(f"Consider turning debug on in Metadata Controller to help locate the missing data.")

        Metadata.store(extra_pnginfo)

        return (image, Metadata.pretty(), issues, _bad if issues else _good)
