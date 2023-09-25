from .configure_nodes import get_config_metadata
from PIL import Image
import json, sys
from .cg_node_addressing import NodeAddressing

MASTER_KEY = get_config_metadata('metadata_master_key', True)[0]

class MetadataException(Exception):
    pass

class Metadata():
    DEFAULTS = { "STRING":"", "INT":0, "FLOAT":0 }
    _dictionary = {}
    loaded_prompt = None
    loaded_workflow = None
    debug = 0

    @classmethod
    def clear(cls):
        cls._dictionary = {}

    @classmethod
    def pretty(cls):
        return json.dumps(cls._dictionary, indent=2)

    @classmethod
    def set_debug(cls):
        try:
            cls.debug = int(get_config_metadata('debug')[0])
        except:
            print(f"Error '{sys.exc_info()[1].args[0]}' setting debug for Metadata - defaulting to on")
            cls.debug = 9
    
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
        if cls.debug > 1:
            message = f"Metadata - {key} set to {cls._dictionary[key]}"
            message += " (new)" if not old_value else " (no change)" if old_value==cls._dictionary[key] else f" (was {old_value})"
            print(message)

    @classmethod
    def add_dictionary_from_image(cls,filepath):
        try:
            with Image.open(filepath) as img:
                text = img.text
                dict = json.loads(text[MASTER_KEY])
                if cls.debug:
                    print(f"Metadata - loaded dictionary from {filepath}")
                for key in dict:
                    cls.set(key, dict[key])
                cls.loaded_prompt = json.loads(text.get('prompt',''))
                cls.loaded_workflow = json.loads(text.get('workflow',''))
                
        except AttributeError:
            raise MetadataException(f"Image loaded from {filepath} didn't have metadata")
        except KeyError:
           raise MetadataException(f"Image loaded from {filepath} had metadata which did not contain the master key {MASTER_KEY}")
        except FileNotFoundError:
            raise MetadataException(f"File not found at {filepath}")
        except json.decoder.JSONDecodeError:
            raise MetadataException(f"Image loaded from {filepath} didn't have metadata in json format")

    @classmethod
    def store(cls, extra_pnginfo):
        extra_pnginfo[MASTER_KEY] = Metadata._dictionary
        if cls.debug:
            print("Metadata stored in the image:")
            print(json.dumps(cls._dictionary, indent=2))

    @classmethod
    def debug_info(cls, extra_pnginfo, prompt):
        if cls.debug > 1:
            available, unavailable = NodeAddressing.all_inputs(extra_pnginfo, prompt)
            print(" ")
            print("Metadata Debugging info")
            print("=======================")
            print("Available sources:")
            NodeAddressing.print_input_details(available)
            print("Unavailable sources:")
            NodeAddressing.print_input_details(unavailable)
