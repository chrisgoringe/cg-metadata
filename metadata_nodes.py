from .common import Base_metadata, AlwaysRerun
from .configure_nodes import get_config_metadata
from .metadata import Metadata, MetadataException, MASTER_KEY
from .cg_node_addressing import NodeAddressing, NodeAddressingException
from nodes import LoadImage
from folder_paths import get_annotated_filepath
import sys, json

class ShowMetadata(Base_metadata, AlwaysRerun):
    CATEGORY = "metadata/display"
    OUTPUT_NODE = True
    OPTIONAL = { "trigger": ("*",{}) }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_displayed",)
    def func(self, **kwargs):
        return {"ui": {"text_displayed": Metadata.pretty()}, "result":(Metadata.pretty(),)}
    
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
    
class GetMetadataString(Base_metadata, AlwaysRerun):
    REQUIRED = { "key": ("STRING", {"default":"key"}) }
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("value", "key" )
    OPTIONAL = { "trigger": ("*",{}) }
    def func(self, key, trigger=None):
        return (str(Metadata.get(key,return_type="STRING")), key, )

class ClearMetadata(Base_metadata, AlwaysRerun):
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("trigger", )
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO" }
    def func(self, extra_pnginfo:dict):
        Metadata.clear()
        extra_pnginfo.pop(MASTER_KEY, None)
        return ("",)
    
class SetMetadataString(Base_metadata, AlwaysRerun):
    REQUIRED = { "key": ("STRING", {"default":"key"}), "value": ("STRING", {"default":""}) }
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("value", "key" )
    def func(self, key, value):
        Metadata.set_debug()
        Metadata.set(key,value)
        return (value, key, )

class SendMetadataToWidgets(Base_metadata, AlwaysRerun):
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    OPTIONAL = { "trigger": ("*",{}) }
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("text_displayed",)
    OUTPUT_NODE = True
    def func(self, extra_pnginfo:dict, prompt, trigger=None):
        sent = {}
        not_sent = {}
        updates = []
        for target in get_config_metadata('metadata_sources'):
            try:
                display_target_name = target.split(",")[0]
                key, _, _, _ = NodeAddressing.parse_source(target)
                _, old_value = NodeAddressing.get_key_and_value(prompt, extra_pnginfo, target, widgets_only=True)
                value = Metadata.get(key)
                if value is None:
                    not_sent[display_target_name] = f"  ** Not set ** {key} was not in metadata"
                    continue
                if isinstance(old_value, float):
                    value = float(value)
                elif isinstance(old_value, int):
                    value = int(value)
                else:
                    value = str(value)
                node_id, widget_name = NodeAddressing.set_value(prompt, extra_pnginfo, target, value)
                sent[display_target_name] = value
                updates.append((str(node_id), widget_name, str(value)))
            except NodeAddressingException:
                message = sys.exc_info()[1].args[0]
                print(message)
                not_sent[display_target_name] = f"  ** Not set ** {message}"

        text = {"Set": sent, "Not set": not_sent}
        return {"ui": {"text_displayed": json.dumps(text, indent=2), "updates": updates}, "result":(json.dumps(text, indent=2),)}

class AddMetadataToImage(Base_metadata):
    REQUIRED = { "image": ("IMAGE", {}), }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ("IMAGE",)
    OUTPUT_NODE = True

    def func(self, image, extra_pnginfo:dict, prompt):
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
