from .common import AlwaysRerun
from custom_nodes.cg_custom_core.base import BaseNode, classproperty
from custom_nodes.cg_custom_core.ui_decorator import ui_signal
from .configure_nodes import get_config_metadata
from .metadata import Metadata, MetadataException, MASTER_KEY
from .cg_node_addressing import NodeAddressing, NodeAddressingException, Mapping
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
    RETURN_TYPES = LoadImage.RETURN_TYPES + ("STRING",)
    RETURN_NAMES = ("image", "mask", "filename")
    def func(self, image):
        Metadata.set_debug()
        try:
            Metadata.add_dictionary_from_image(get_annotated_filepath(image))
        except MetadataException:
            print(sys.exc_info()[1].args[0])
        return self.load_image(image) + (image,)
    
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

@ui_signal(['modify_other','display_text','set_title_color'])
class SendMetadataToWidgets(BaseNode, AlwaysRerun):
    CONFIGURATION = get_config_metadata('metadata_sources', True)
    @classproperty
    def REQUIRED(cls):
        return {
            "active": (["yes","no"],{}), 
            "configuration": ("STRING", {"default":cls.display(get_config_metadata('metadata_sources', True)), "multiline":True})
        }
    
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    OPTIONAL = { "trigger": ("*",{}) }
    CATEGORY = "metadata/widgets"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_displayed",)

    @classmethod
    def display(cls, thelist):
        mappings = [Mapping.from_node_comma_meta(source).meta_to_node() for source in thelist]
        return "\n".join(['metadata mapping:',]+mappings)
    
    @classmethod
    def parse(cls, string):
        return [Mapping.from_meta_to_node(mapper) for mapper in string.split("\n")[1:]]
    
    def func(self, active, configuration, extra_pnginfo:dict, prompt, trigger=None):
        if not active=="yes":
            return ("off", [], "turned off", None)
        set = {}
        key_missing = {}
        error_setting = {}
        updates = []
        for mapping in self.parse(configuration):
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

        text = json.dumps({"Set": set, "Keys not in metadata": key_missing, "Failed to set": error_setting}, indent=2)
        color = "#337733" if len(key_missing)==0 and len(error_setting)==0 else "#773333"
        return(text, updates, text, color)

class AddMetadataToImage(BaseNode):
    REQUIRED = { "image": ("IMAGE", {}), }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ("IMAGE",)
    OUTPUT_NODE = True
    OPTIONAL = { "trigger": ("*",{}) }
    CATEGORY = "metadata"

    def func(self, image, extra_pnginfo:dict, prompt, trigger=None):
        Metadata.set_debug()
        Metadata.debug_info(extra_pnginfo, prompt)
        issues = False
  
        for source in get_config_metadata('metadata_sources'):
            try:
                mapping = Mapping.from_node_comma_meta(source)
                NodeAddressing.get_key_and_value(prompt, extra_pnginfo, mapping)
                Metadata.set(mapping.key, mapping.value)
            except NodeAddressingException:
                print(sys.exc_info()[1].args[0])
                issues = True

        if issues and not Metadata.debug:
            print(f"Consider turning debug on in Metadata Controller to help locate the missing data.")

        Metadata.store(extra_pnginfo)

        return (image,)
