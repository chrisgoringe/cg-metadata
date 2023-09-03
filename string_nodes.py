import sys
from .common import Base_metadata, AlwaysRerun
from .metadata import Metadata
from .cg_node_addressing import NodeAddressing, NodeAddressingException

class ShowMetadata(Base_metadata, AlwaysRerun):
    CATEGORY = "metadata/display"
    OUTPUT_NODE = True
    OPTIONAL = { "trigger": ("*",{}) }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_displayed",)
    def func(self, **kwargs):
        return {"ui": {"text_displayed": Metadata.pretty()}}

class SetWidget(Base_metadata, AlwaysRerun):
    CATEGORY = "metadata/widgets"
    REQUIRED = {"target": ("STRING", {"default":"KSampler.sampler_name"}), 
                "cast": (["string","int","float"],{} )}
    OPTIONAL = { "value": ("*",{})}
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    PRIORITY = 2

    def func(self, target, cast, value, extra_pnginfo, prompt):
        try:
            try:
                value = int(value) if cast=="int" else float(value) if cast=="float" else str(value)
            except ValueError:
                print(f"Failed to cast '{value}' as {cast}, using default value")
                value = {"string":"","int":0,"float":0.0}[cast]
            node_id, widget_name = NodeAddressing.set_value(prompt, extra_pnginfo, target, value)
            if Metadata.debug>1:
                print(f"Set {target} to {value} as {cast}")
        except NodeAddressingException:
            print(f"{sys.exc_info()[1].args[0]}")
            NodeAddressing.print_input_details(NodeAddressing.all_inputs(extra_pnginfo, prompt, widgets_only=True)[0])
            return {}
        return {"ui": {"node_id": str(node_id), "widget_name": widget_name, "text": str(value)}}

class SetWidgetFromMetadata(SetWidget):
    REQUIRED = {"key": ("STRING", {"default":""}),
                "target": ("STRING", {"default":"KSampler.sampler_name"}), 
                "cast": (["string","int","float"],{} )}
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("value", )
    OPTIONAL = { "trigger": ("*",{}) }
    FUNCTION = "_func"
    def _func(self, **kwargs):
        text = str(Metadata.get(kwargs.pop('key'),return_type="STRING"))
        kwargs.pop('trigger',None)
        kwargs['value'] = text
        result = self.func( **kwargs )
        result['result'] = (text,)
        return result

class SetMetadataFromWidget(Base_metadata, AlwaysRerun):
    CATEGORY = "metadata/widgets"
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