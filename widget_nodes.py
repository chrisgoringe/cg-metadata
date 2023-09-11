import sys
from .common import Base_metadata, AlwaysRerun, classproperty
from .metadata import Metadata
from .cg_node_addressing import NodeAddressing, NodeAddressingException
from custom_nodes.cg_custom_core.ui_decorator import ui_signal

class SetWidget(Base_metadata, AlwaysRerun):
    CATEGORY = "metadata/widgets"
    @classproperty
    def REQUIRED(cls):
        return {"target": ("STRING", {"default":"node.widget"}), 
                "value": (cls.TYPE, { "default":cls.DEFAULT })}
    OPTIONAL = { "trigger": ("*",{}) }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    OUTPUT_NODE = True
    TYPE = DEFAULT = CAST = None

    def func(self, target, value, extra_pnginfo, prompt, trigger=None):
        try:
            try:
                value = self.CAST(value)
            except ValueError:
                print(f"Failed to cast '{value}' as {self.TYPE}, using default value {self.DEFAULT}")
                value = self.DEFAULT
            node_id, widget_name = NodeAddressing.set_value(prompt, extra_pnginfo, target, value)
            if Metadata.debug>1:
                print(f"Set {target} to {value} as {self.TYPE}")
            return [(str(node_id), widget_name, str(value)),]
        except NodeAddressingException:
            print(f"{sys.exc_info()[1].args[0]}")
            if Metadata.debug>1:
                NodeAddressing.print_input_details(NodeAddressing.all_inputs(extra_pnginfo, prompt, widgets_only=True)[0])
            return []

@ui_signal('modify_other')
class SetWidgetInt(SetWidget):
    TYPE = "INT"
    DEFAULT = 0
    CAST = int

@ui_signal('modify_other')
class SetWidgetFloat(SetWidget):
    TYPE = "FLOAT"
    DEFAULT = 0.0
    CAST = float

@ui_signal('modify_other')    
class SetWidgetString(SetWidget):
    TYPE = "STRING"
    DEFAULT = ""
    CAST = str
    @classproperty
    def REQUIRED(cls):
        return {"target": ("STRING", {"default":"node.widget"}), 
                "value": (cls.TYPE, { "default":cls.DEFAULT, "multiline": True })}

@ui_signal('modify_other')
class SetWidgetFromMetadata(SetWidget):
    @classproperty
    def REQUIRED(cls):
        return {"key": ("STRING", {"default":""}),
                "target": ("STRING", {"default":"KSampler.sampler_name"}), 
                "cast": (["string","int","float"],{} )}
    FUNCTION = "_func"

    def _func(self, key, target, cast, extra_pnginfo, prompt, trigger=None):
        text = str(Metadata.get(key,return_type="STRING"))
        self.CAST = float if cast=="float" else int if cast=="int" else str
        self.DEFAULT = 0.0 if cast=="float" else 0 if cast=="int" else ""
        return self.func(target, text, extra_pnginfo, prompt)

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