import random
from .common import Base_metadata
from .metadata import Metadata, find_node

# see text.js
class ShowText(Base_metadata):
    REQUIRED = { "text": ("STRING", {"forceInput": True}), }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    OUTPUT_NODE = True

    def func(self, text):
        return {"ui": {"text": text}, "result": (text,)}
    
class ShowMetadata(Base_metadata):
    OUTPUT_NODE = True
    PRIORITY = -1
    def func(self):
        return {"ui": {"text": Metadata.pretty()}}

class SendText(Base_metadata):
    REQUIRED = { "target": ("STRING", {"default":"KSampler.sampler_name"}), "text": ("STRING", {"forceInput": True}), }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    PRIORITY = 1

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return random.random()

    def func(self, target, text, extra_pnginfo, prompt):
        if not '.' in target:
            print("Target must be of the form node_title.widget_name")
            return ()
        node_title, widget_name = target.split('.')

        if '#' in node_title:
            node_title, skip_first_n_matches = node_title.split("#")
            skip_first_n_matches = int(skip_first_n_matches) - 1
        else:
            skip_first_n_matches = 0

        node = find_node(extra_pnginfo, node_title, skip_first_n_matches)
        if node is not None:
            node_id = str(node['id'])
            input_or_widget = prompt[node_id]['inputs'].get(widget_name,None)
            if input_or_widget is not None and isinstance(input_or_widget,str):
                prompt[node_id]['inputs'][widget_name] = text
                return {"ui": {"text": text, "node_id":node_id, "widget_name":widget_name}}
            else:
                print(f"{widget_name} wasn't found on {node_title}. Here's a list of widget names:")
                for name in prompt[node_id]['inputs']:
                    print(name)
        else:
            print(f"{node_title} not found. Here's a list of node titles:")
            for node in extra_pnginfo['workflow']['nodes']:
                print(node.get('title', node.get('type')))
        return ()
    