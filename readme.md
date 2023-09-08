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

| Node | Purpose |
|------|---------|
| `Configure Metadata Sources` | creates a map between widgets in the workflow and keys in the metadata (can also be controlled using `configuration.yaml`) |
| `Store Metadata in Image` | saves all the metadata specified in the configuration, or manually added, into the image |
| `Load Image and Metadata` | load an image and any metadata saved with it |
| `Get/Set Metadata String` | manually set or get the value of metadata |
| `Show Metadata` | Show all the loaded metadata |
| `Send Metadata to Widgets` | Send the loaded metadata to the widgets as configured |
| `Set Widget Int/Float/String` | Set a widget to a value |
| `Set Widget from Metadata` | Get a widget from a key in the metadata |
| `Set Metadata from Widget` | Read a widget and save to the metadata |

## Viewer

A very simple metadata viewer is included [here](./viewer/index.html)

## Configuration

Metadata keys can be associated with widgets in the workflow. You configure this in `configuration.yaml`, or using the `Configure Metadata Sources` node. In this section (which is read as the node is executed, so you can change it without a restart):

```yaml
metadata_sources:
- CheckpointLoaderSimple.ckpt_name
- Two Clip Text Encode.prompt
- Two Clip Text Encode.negative_prompt
- KSampler.steps
- KSampler.seed
- KSampler.cfg
- KSampler.sampler_name, sampler
- KSampler.scheduler
- LoraLoader.lora_name, lora_name1
- LoraLoader.strength_model, lora_strength_model1
- LoraLoader.strength_clip, lora_strength_clip1
- LoraLoader#2.lora_name, lora_name2
- LoraLoader#2.strength_model, lora_strength_model2
- LoraLoader#2.strength_clip, lora_strength_clip2
```
each line consists of `node_name[#n].input_name[,key]`

The `key` is just the key for the metadata dictionary. 

The `node_name` is the node or title of node. You can set the title of a node in the GUI, in which case this is what gets matched, otherwise a default name for the node type is used, which may not be what gets displayed. `#n` appended to the `node_name` means "the n'th instance that matches".

The `input_name` is what it sounds like - it will match the name of an input or widget. 

If you set debug to on a list of all node_name and output_or_input_name values will be displayed by the `Store Metadata In Image` node on execution, with current value (if available). Debug is read at execution time, so you don't need to restart ComfyUI.


## Examples

to come...