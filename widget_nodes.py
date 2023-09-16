import sys, json
from .common import AlwaysRerun
from custom_nodes.cg_custom_core.base import BaseNode, classproperty
from .metadata import Metadata
from .cg_node_addressing import NodeAddressing, NodeAddressingException, Mapping
from custom_nodes.cg_custom_core.ui_decorator import ui_signal

@ui_signal(['modify_other', 'display_text'])
class SetWidgetsFromSavedWorkflow(BaseNode):
    CATEGORY = "metadata/widgets"
    REQUIRED = { "image": ("IMAGE",{}) }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ("IMAGE", "STRING", )
    RETURN_NAMES = ("image", "results", ),
    
    def func(self, image, extra_pnginfo, prompt):
        updates = []
        results = []
        issues = set()
        names = set()

        def get_node_name(node):
            return node.get('title',None) or node['properties'].get('Node name for S&R',None) or node['type']

        def find_node_matching(original_node):
            name = get_node_name(original_node)
            matching_node = None
            for node in extra_pnginfo['workflow']['nodes']:
                if get_node_name(node) == name:
                    if matching_node is not None:
                        issues.add(f"{name} matched more than once")
                    matching_node = node
            return matching_node, name
        
        for node in Metadata.loaded_workflow['nodes']:
            matching_node, node_name = find_node_matching(node)
            inputs = Metadata.loaded_prompt[str(node['id'])].get('inputs',{}) if str(node['id']) in Metadata.loaded_prompt else {}
            widget_inputs = {input_name:inputs[input_name] for input_name in inputs if not isinstance(inputs[input_name],list) }
            if len(widget_inputs)==0:
                continue

            if node_name in names:
                issues.add(f"{node_name} was in metadata more than once")
            names.add(node_name)

            if matching_node:
                matching_node_id = str(matching_node['id'])
                for input_name in widget_inputs:
                    input_value = widget_inputs[input_name]
                    current_value = prompt[matching_node_id]['inputs'].get(input_name,[None, None])
                    if not isinstance(input_value,list):
                        if current_value is not None:
                            updates.append( (str(matching_node_id), input_name, str(input_value)) )
                            prompt[matching_node_id]['inputs'][input_name] = input_value
                            results.append(f"{node_name}.{input_name} set to {input_value}")
                        else:
                            if not isinstance(current_value, list):
                                results.append(f"{node_name}.{input_name} is an input in both workflows")
                            else:
                                results.append(f"{node_name}.{input_name} is an input, so was not set to {input_value}")
                                issues.add(f"{node_name}.{input_name} is an input, so could not be set to {input_value}")
                    else:
                        results.append(f"{node_name}.{input_name} was an input")
            else:
                results.append(f"{node_name} not found in this workflow")
                issues.add(f"{node_name} not found in this workflow")

        text = "Warnings:\n"+json.dumps(list(issues), indent=1) if issues else ""
        return (image, json.dumps(results, indent=1), updates, text)

class SetWidget(BaseNode, AlwaysRerun):
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
            mapping = Mapping.from_node_comma_meta(target)
            try:
                value = self.CAST(value)
            except ValueError:
                print(f"Failed to cast '{value}' as {self.TYPE}, using default value {self.DEFAULT}")
                value = self.DEFAULT
            NodeAddressing.set_value(prompt, extra_pnginfo, mapping, value)
            if Metadata.debug>1:
                print(f"Set {target} to {value} as {self.TYPE}")
            return [(str(mapping.node_id), mapping.input_name, str(value)),]
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

class SetMetadataFromWidget(BaseNode, AlwaysRerun):
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
            mapping = Mapping.from_node_comma_meta(source)
            _, value = NodeAddressing.get_key_and_value(prompt, extra_pnginfo, mapping)
            if key!="":
                Metadata.set(key, value)
        except NodeAddressingException:
            print(f"{sys.exc_info()[1].args[0]}")
            NodeAddressing.print_input_details(NodeAddressing.all_inputs(extra_pnginfo, prompt, widgets_only=True)[0])
        return (str(value),)