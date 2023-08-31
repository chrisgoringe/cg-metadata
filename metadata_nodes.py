from .common import Base_metadata, get_config_metadata
from .metadata import Metadata, MetadataException, MASTER_KEY
from .cg_node_addressing import NodeAddressing, NodeAddressingException
from nodes import LoadImage
from folder_paths import get_annotated_filepath
import sys

class LoadImageWithMetadata(Base_metadata, LoadImage):
    @classmethod
    def INPUT_TYPES(s):
        return LoadImage.INPUT_TYPES()
    RETURN_TYPES = ("IMAGE", "MASK", )
    RETURN_NAMES = ("image", "mask", )

    def func(self, image):
        Metadata.set_debug()
        try:
            Metadata.add_dictionary_from_image(get_annotated_filepath(image))
        except MetadataException:
            print(sys.exc_info()[1].args[0])
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

class ClearMetadataAtStart(Base_metadata):
    OUTPUT_NODE = True
    PRIORITY = 5
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO" }
    def func(self, extra_pnginfo:dict):
        Metadata.clear()
        extra_pnginfo.pop(MASTER_KEY, None)
        return ()
    
class SetMetadataString(Base_metadata):
    REQUIRED = { "key": ("STRING", {"default":"key"}), "value": ("STRING", {"default":""}) }
    OUTPUT_NODE = True
    PRIORITY = 1
    def func(self, key, value):
        Metadata.set_debug()
        Metadata.set(key,value)
        return ( )

class AddMetadataToImage(Base_metadata):
    REQUIRED = { "image": ("IMAGE", {}), }
    HIDDEN = { "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT" }
    RETURN_TYPES = ("IMAGE",)
    OPTIONAL = { "trigger": ("*",{}) }
    OUTPUT_NODE = True
    PRIORITY = 0

    def func(self, image, extra_pnginfo:dict, prompt, trigger=None):
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
