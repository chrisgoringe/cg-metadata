# CG's custom nodes: Metadata

[Index of my custom nodes](https://github.com/chrisgoringe/cg-nodes-index)

## Metadata

To install:
```
cd [path to ComfyUI]/custom_nodes
git clone https://github.com/chrisgoringe/cg-metadata.git
```

A set of custom nodes to add a custom metadata dictionary to images. The dictionary is added to the pngInfo of the file under the key `cg` (which can be changed in `configuration.yaml`). I use this when prompts etc. are randomised, and the workflow might not be captured in the image sufficiently completely.

- `Metadata Controller` *optional* - used to determine whether the metadata dictionary is kept between runs (the default) or cleared, and whether duplicate entries replace (the default) or are appended. 
- `Load Metadata From Image` - load the custom metadata from an existing image.
- `Load Image with Metadata` - load the image and the custom metadata.
- `Set Metadata` - set the value of one or two metadata entries. The drop down list contains a number of common keys, which can be configured in `configuration.yaml`.
- `Set Arbitrary Metadata` - set the value of one metadata entry with an arbitrary key. Both Set... nodes take any input (but anything that can't be serialised isn't a good idea)
- `Get Metadata`, `Get Arbitrary Metadata` - read the metadata (always as a string)
- `String To Int`, `String To Float` - convenience nodes for converting back
- `Store Metadata In Image` - inserted just upstream of an image save, this node ensures that the dictionary is included in the pngInfo
