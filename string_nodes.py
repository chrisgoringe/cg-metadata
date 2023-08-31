import random, sys
from .common import Base_metadata, AlwaysRerun
from .metadata import Metadata
from .cg_node_addressing import NodeAddressing, NodeAddressingException

class ShowMetadata(Base_metadata, AlwaysRerun):
    OUTPUT_NODE = True
    PRIORITY = -1
    def func(self):
        return {"ui": {"text": Metadata.pretty()}}

class SetWidget(Base_metadata, AlwaysRerun):
    REQUIRED = {"target": ("STRING", {"default":"KSampler.sampler_name"}), 
                "text": ("STRING", {"forceInput": True}), 
                "cast": (["string","int","float"],{} )}
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    PRIORITY = 2

    def func(self, target, text, cast, extra_pnginfo, prompt):
        try:
            value = int(text) if cast=="int" else float(text) if cast=="float" else text
            node_id, widget_name = NodeAddressing.set_value(prompt, extra_pnginfo, target, value)
            if Metadata.debug>1:
                print(f"Set {target} to {text} as {cast}")
        except NodeAddressingException:
            print(f"{sys.exc_info()[1].args[0]}")
            NodeAddressing.print_input_details(NodeAddressing.all_inputs(extra_pnginfo, prompt, widgets_only=True)[0])
            return ()
        return {"ui": {"node_id": str(node_id), "widget_name": widget_name, "text": text}}
    
class SetMetadataFromWidget(Base_metadata, AlwaysRerun):
    REQUIRED = { "source": ("STRING", {"default":"KSampler.sampler_name"}), "key": ("STRING", {"default":""}) }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)
    OUTPUT_NODE = True
    PRIORITY = 1
    OPTIONAL = { "trigger": ("*",{}) }

    def func(self, source, key, extra_pnginfo, prompt, trigger=None):
        try:
            value = ""
            _, value = NodeAddressing.get_key_and_value(prompt, extra_pnginfo, source)
            if key!="":
                Metadata.set(key, value)
        except NodeAddressingException:
            print(f"{sys.exc_info()[1].args[0]}")
            NodeAddressing.print_input_details(NodeAddressing.all_inputs(extra_pnginfo, prompt, widgets_only=True)[0])
        return (str(value),)