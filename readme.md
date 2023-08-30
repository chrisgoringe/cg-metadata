# CG's custom nodes: Metadata

[Index of my custom nodes](https://github.com/chrisgoringe/cg-nodes-index)

## Metadata

To install:
```
cd [path to ComfyUI]/custom_nodes
git clone https://github.com/chrisgoringe/cg-metadata.git
```

A set of custom nodes to add a custom metadata dictionary to images. The dictionary is added to the pngInfo of the file under the key `cg` (which can be changed in `configuration.yaml`). 

Any key-value pair can be added to the custom dictionary, but the real power is that nodes can also directly extract values from pretty much any other node in the workflow.

## The nodes

- `Store Metadata In Image` - inserted just upstream of an image save, this node adds metadata to the pnginfo. 
- `Load Image with Metadata` - load the image and its metadata. 
- `Get Metadata` - read the metadata that has been stored or loaded. 
- `Set/Get Metadata String` - set or get a custom key-value pair. 

## Note on sequencing and triggers

When loading an image and reading its metadata, you want to ensure the load node runs first. To do this, connect any output from the image loader to the `trigger`. The value on this input is ignored, but it ensures the load node executes before the read node. You can also use the `trigger` on `Store Metadata In Image` to ensure anything else you want happens first.

## Configuration

### Store Metadata

The `Store Metadata In Image` node will save and key-value strings added with the `Set Metadata String` nodes, but it can also read data directly from pretty much any other node. You configure this in `configuration.yaml`. In this section (which is read as the node is executed, so you can change it without a restart):

```yaml
metadata_sources:
- image_name, Load Image and Metadata, image!
- prompt, CLIPTextEncode, text
- negative_prompt, CLIPTextEncode#2, text
- ckpt_name, CheckpointLoaderSimple, ckpt_name
- steps, KSampler, steps
- seed, KSampler, seed
- cfg, KSampler, cfg
```
each line consists of `[key_name],[node_name],[output_or_input_name]` (spaces around the names are trimmed)

The `key` is just the key for the metadata dictionary. 

The `node_name` is the node or title of node. You can set the title of a node in the GUI, in which case this is what gets matched, otherwise a default name for the node type is used, which may not be what gets displayed. Use `Metadata Controller` to switch on debug to get some help finding names (or just use titles!). `#n` appended to the `node_name` means "the n'th instance that matches".

The `output_or_input_name` is what it sounds like - it will match the name of an output, or if there is no match, the name of an input or widget. Input/Widget names are unique, as are output names, but a node can have an input/widget and an output using the same name: append `!` to ignore outputs if you want the input.

If you set debug to on a list of all node_name and output_or_input_name values will be displayed by the `Store Metadata In Image` node on execution, with current value (if available). Debug is read at execution time, so you don't need to restart ComfyUI.

### Get Metadata

The `Get Metadata` node can also be configured with the outputs you want to read. In this section (which is read at startup, so changes require ComfyUI to be restarted):
```yaml
get_metadata_outputs:
- ckpt_name
- prompt
- negative_prompt
- seed, INT
- cfg, FLOAT
- steps, INT
- comment
```
each line consists of `[output_name],[type]`, with `,STRING` assumed if the type is not specified.