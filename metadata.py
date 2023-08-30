from .common import Base_metadata, get_config_metadata
from nodes import LoadImage
from folder_paths import get_annotated_filepath
from PIL import Image
import json, inspect

MASTER_KEY = get_config_metadata('metadata_master_key')[0]

class Metadata():
    DEFAULTS = { "STRING":"", "INT":0, "FLOAT":0 }
    _dictionary = {}
    debug = False

    @classmethod
    def set_debug(cls):
        try:
            cls.debug = get_config_metadata('debug')[0]
        except:
            print("Error setting debug for Metadata - defaulting to on")
            cls.debug = True
    
    @classmethod
    def get(cls, key, return_type=None):
        return cls._dictionary[key] if key in cls._dictionary else cls.DEFAULTS.get(return_type,None)

    @classmethod
    def set(cls, key, value):
        old_value = cls._dictionary.get(key, None)
        if isinstance(value,list) and len(value)==1:
            value = value[0]
        try:
            json.dumps(value)  # not using the output, just checking it can be serialized
            cls._dictionary[key] = value
        except TypeError:
            if cls.debug:
                print(f"Metadata - tried to set {key} to an object of class {value.__class__} that isn't JSON-serializable.")
            cls._dictionary[key] = value.__repr__()
        if cls.debug:
            message = f"Metadata - {key} set to {cls._dictionary[key]}"
            if old_value:
                message += f" replacing old value of {old_value}"
            print(message)

    @classmethod
    def add_dictionary_from_image(cls,filepath):
        try:
            dict = json.loads(Image.open(filepath).text[MASTER_KEY])
            if cls.debug:
                print(f"Metadata - loaded dictionary from {filepath}")
            for key in dict:
                cls.set(key, dict[key])
        except AttributeError:
            if cls.debug:
                print(f"Metadata - image loaded from {filepath} didn't have metadata")
        except KeyError:
            if cls.debug:
                print(f"Metadata - image loaded from {filepath} had metadata which did not contain the master key {MASTER_KEY}")
        except FileNotFoundError:
            if cls.debug:
                print(f"Metadata - file not found at {filepath}")

    @classmethod
    def store(cls, extra_pnginfo):
        extra_pnginfo[MASTER_KEY] = Metadata._dictionary
        cls._log_info()

    @classmethod
    def _format(cls, in_or_out, title, name, value_getter):
        ok, key, value = value_getter(f"key,{title},{name}")
        fmt = "{:>30}, {:<24} {:>6} = {:<40} {:>8}"
        if ok:
            class_name = value.__class__.__name__
            value = str(value)
            value = value if len(value)<40 else value[:30]+"..."+value[-7:]
            print(fmt.format(title,name,in_or_out,value,class_name))
        else:
            print(fmt.format(title,name,in_or_out,"not available (yet?)","unknown"))

    @classmethod
    def debug_info(cls, extra_pnginfo, prompt, value_getter):
        if not cls.debug:
            return
        print("Metadata Debugging info")
        print("Titles of nodes in workflow, and the names of their outputs and inputs.")
        node_titles = {}
        for node in extra_pnginfo['workflow']['nodes']:
            title = node.get('title', node.get('type'))
            node_titles[title] = node_titles.get(title,0) + 1
            if node_titles[title]>1:
                title = f"{title}#{node_titles[title]}"
            output_names = []
            if 'outputs' in node:
                for name in node['outputs']:
                    name = name['name']
                    cls._format('output', title, name, value_getter)
                    output_names.append(name)
            if 'inputs' in prompt[str(node['id'])]:
                for name in prompt[str(node['id'])]['inputs']:
                    if name in output_names:
                        name += '!'
                    cls._format('input ', title, name, value_getter)

    @classmethod
    def _log_info(cls):
        if not cls.debug:
            return
        print("Metadata stored in the image:")
        print(json.dumps(cls._dictionary, indent=2))
    
class LoadImageWithMetadata(Base_metadata, LoadImage):
    @classmethod
    def INPUT_TYPES(s):
        return LoadImage.INPUT_TYPES()
    
    RETURN_TYPES = ("IMAGE", "MASK", )
    RETURN_NAMES = ("image", "mask", )

    def func(self, image):
        Metadata.set_debug()
        Metadata.add_dictionary_from_image(get_annotated_filepath(image))
        return self.load_image(image)

class GetMetadata(Base_metadata):
    LABELS_AND_TYPES = get_config_metadata('get_metadata_outputs')
    RETURN_NAMES = tuple([l.split(',')[0].strip() for l in LABELS_AND_TYPES])
    RETURN_TYPES = tuple([(l+",STRING").split(',')[1].strip() for l in LABELS_AND_TYPES])
    OPTIONAL = { "trigger": ("*",{}) }

    @classmethod
    def func(cls, trigger=None):
        return tuple( [Metadata.get(cls.RETURN_NAMES[i],return_type=cls.RETURN_TYPES[i]) for i in range(len(cls.RETURN_NAMES))] )
    
class GetMetadataString(Base_metadata):
    REQUIRED = { "key": ("STRING", {"default":"key"}) }
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("value", )
    OPTIONAL = { "trigger": ("*",{}) }
    def func(self, key, trigger=None):
        return (Metadata.get(key,return_type="STRING"), )
    
class SetMetadataString(Base_metadata):
    REQUIRED = { "key": ("STRING", {"default":"key"}), "value": ("STRING", {"default":""}) }
    def func(self, key, value):
        Metadata.set_debug()
        Metadata.set(key,value)
        return ( )

def find_node(extra_pnginfo, node_title, skip):
    for node in extra_pnginfo['workflow']['nodes']:
        if node.get('title', node.get('type'))==node_title:
            if skip==0:
                return node
            skip -= 1
    return None

def find_node_output_index(node, output_name):
    if 'outputs' in node:
        for i, output in enumerate(node['outputs']):
            if output['name']==output_name:
                return i
    return None

class AddMetadataToImage(Base_metadata):
    REQUIRED = { "image": ("IMAGE", {}), }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ("IMAGE",)
    OPTIONAL = { "trigger": ("*",{}) }
    _outputs = None

    @classmethod
    def output_store(cls):
        if cls._outputs is None:
            for frame_info in inspect.stack():
                executor_maybe = frame_info.frame.f_locals.get("e",None)
                if hasattr(executor_maybe,'outputs'):
                    cls._outputs = executor_maybe.outputs
        return cls._outputs
    
    @classmethod
    def parse_source(cls, source):
        key, full_node_title, full_name = (s.strip() for s in source.split(","))

        if '#' in full_node_title:
            node_title, skip_first_n_matches = full_node_title.split("#")
            skip_first_n_matches = int(skip_first_n_matches) - 1
        else:
            node_title = full_node_title
            skip_first_n_matches = 0

        if full_name.endswith("!"):
            name = full_name[:-1]
            skip_outputs = True
        else:
            name = full_name
            skip_outputs = False

        return key, full_node_title, node_title, full_name, name, skip_first_n_matches, skip_outputs
    
    @classmethod
    def get_value(cls, prompt, extra_pnginfo, source):
        key, full_node_title, node_title, full_name, name, skip_first_n_matches, skip_outputs = cls.parse_source(source)
        
        outputs = cls.output_store()
        if not outputs:
            return False, key, "AddMetadataToImage was unable to locate execution context output store. Raise a ticket."

        node = find_node(extra_pnginfo, node_title, skip_first_n_matches)
        if node is None and full_node_title:
            return False, key, f"node '{full_node_title}' wasn't found in the workflow."

        if not skip_outputs:
            output_index = find_node_output_index(node, name)
            if output_index is not None:
                try:
                    return True, key, outputs[str(node['id'])][output_index]
                except KeyError:
                    return False, key, f"node '{full_node_title}' output '{full_name}' has not been evalauted yet."

        input_or_widget = prompt[str(node['id'])]['inputs'].get(name,None)
        if input_or_widget is None and full_node_title:
            return False, key, f"node '{full_node_title}' was found, but no input, output, or widget '{full_name}' was found."
            
        if isinstance(input_or_widget,list):
            (node_id, output_index) = input_or_widget
            try:
                return True, key, outputs[str(node_id)][output_index]
            except KeyError:
                return False, key, f"'{full_node_title}' output '{full_name}' has not been evalauted yet."
        return True, key, input_or_widget

    def func(self, image, extra_pnginfo:dict, prompt, trigger=None):
        Metadata.set_debug()
        value_getter = lambda source : self.get_value(prompt, extra_pnginfo, source)
        Metadata.debug_info(extra_pnginfo, prompt, value_getter)
        issues = False
  
        for source in get_config_metadata('metadata_sources'):
            ok, key, value = value_getter(source)
            if not ok:
                print(value)
                issues = True
            else:
                Metadata.set(key, value)

        if issues and not Metadata.debug:
            print(f"Consider turning debug on in Metadata Controller to help locate the missing data.")

        Metadata.store(extra_pnginfo)

        return (image,)
