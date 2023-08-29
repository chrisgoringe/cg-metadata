from .common import Base_metadata, get_config_metadata
from nodes import LoadImage
from folder_paths import get_annotated_filepath
from PIL import Image
import json, re

MASTER_KEY = get_config_metadata('metadata_master_key')[0]
LABELS_AND_TYPES = get_config_metadata('metadata_common_keys')
LABELS = tuple([l.split(',')[0].strip() for l in LABELS_AND_TYPES])
TYPES = tuple([(l+",STRING").split(',')[1].strip() for l in LABELS_AND_TYPES])

class Metadata(Base_metadata):
    dictionary = {}
    duplicates = "replace"
    REQUIRED = { 
                "at_start": (["keep_existing", "clear_existing", ], {}),
                "duplicates": (["replace", "append", ], {}),
               }
    HIDDEN = {"extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT"}
    PRIORITY = 2
    OUTPUT_NODE = True
    REGEX = re.compile("(.*):(.*)")
    
    @classmethod
    def func(cls, at_start, duplicates, extra_pnginfo, prompt):
        Metadata.extra_pnginfo = extra_pnginfo
        Metadata.prompt = prompt
        if at_start=="clear_existing":
            cls.dictionary = {}
        cls.duplicates = duplicates
        return ()

    @classmethod
    def set(cls, key, value):
        if key in cls.dictionary and cls.duplicates=="append":
            if isinstance(cls.dictionary[key], list):
                cls.dictionary[key].append(value)
            else:
                cls.dictionary[key] = [cls.dictionary[key], value, ]
        else:
            cls.dictionary[key] = value

def add_dictionary_from_image(filepath):
    try:
        dict = json.loads(Image.open(filepath).text[MASTER_KEY])
        for key in dict:
            Metadata.set(key, dict[key])
    except:
        pass
    
class LoadImageWithMetadata(Base_metadata, LoadImage):
    RETURN_TYPES = ("IMAGE", "MASK", )
    RETURN_NAMES = ("image", "mask", )

    def func(self, image):
        add_dictionary_from_image(get_annotated_filepath(image))
        return LoadImage.load_image(image)

class SetMetadata(Base_metadata):
    OPTIONAL = { "key1": (LABELS, {}), "value1": ("*", {}), "key2": (LABELS, {}), "value2": ("*", {}), }
    PRIORITY = 1
    OUTPUT_NODE = True

    def func(self, key1=None, value1=None, key2=None, value2=None):
        if key1 is not None and value1 is not None:
            Metadata.set(key1, value1) 
        if key2 is not None and value2 is not None:
            Metadata.set(key2, value2) 
        return ()
    
class SetArbitraryMetadata(Base_metadata):
    REQUIRED = { "key": ("STRING", {"default":"key"}) }
    OPTIONAL = { "value": ("*", {}) }
    PRIORITY = 1
    OUTPUT_NODE = True

    def func(self, key, value=None):
        if value is not None:
            Metadata.set(key, value) 
        return ()

class GetMetadata(Base_metadata):
    REQUIRED = { "key1": (LABELS, {}), "key2": (LABELS, {}) }
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("value1", "value2", )
    def func(self, key1, key2):
        return (Metadata.dictionary.get(key1,""), Metadata.dictionary.get(key2,""))
    
class GetArbitraryMetadata(Base_metadata):
    REQUIRED = { "key": ("STRING", {"default":"key"}) }
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("value", )
    def func(self, key):
        return (Metadata.dictionary.get(key,""), )

class AddMetadataToImage(Base_metadata):
    REQUIRED = { "image": ("IMAGE", {}), }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO" }
    RETURN_TYPES = ("IMAGE",)
    def func(self, image, extra_pnginfo:dict=None):
        extra_pnginfo[MASTER_KEY] = Metadata.dictionary
        return (image,)
    
class StringToInt(Base_metadata):
    REQUIRED = { "string": ("STRING", {"default":0}) }
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("int",)
    def func(self, string):
        try:
            return (int(string),)
        except:
            return (0,)
        
class StringToFloat(Base_metadata):
    REQUIRED = { "string": ("STRING", {"default":0}) }
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("float",)
    def func(self, string):
        try:
            return (float(string),)
        except:
            return (0,)