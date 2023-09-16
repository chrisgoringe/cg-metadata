import inspect, sys

class NodeAddressingException(Exception):
    pass

class Mapping:
    def __init__(self, key, node_title, input_name, skip_first_n_matches):
        self.key = key
        self.node_title = node_title
        self.input_name = input_name
        self.skip_first_n_matches:int = int(skip_first_n_matches)
        self.skip_repr = "" if skip_first_n_matches==0 else f"#{skip_first_n_matches+1}"
        self.node_id = None
        self.value = None

    def node_and_widget(self):
        return f"{self.node_title}{self.skip_repr}.{self.input_name}"

    def node_comma_meta(self):
        return f"{self.node_title}{self.skip_repr}.{self.input_name}, {self.key}"

    @classmethod
    def from_node_comma_meta(cls, string):
        rest, key = (s.strip() for s in string.split(",")) if "," in string else (string,None)
        return cls._from_key_and_rest(key,rest)
    
    def meta_to_node(self):
        return f"{self.key} -> {self.node_title}{self.skip_repr}.{self.input_name}"
    
    @classmethod
    def from_meta_to_node(cls, string):
        key, rest = (s.strip() for s in string.split('->'))
        return cls._from_key_and_rest(key,rest)
    
    @classmethod
    def _from_key_and_rest(cls, key, rest):
        rest, input_name = rest.split('.')
        node_title, nth_node = rest.split("#") if "#" in node_title else (node_title,1)
        skip_first_n_matches = int(nth_node) - 1
        return cls(key or input_name, node_title, input_name, skip_first_n_matches)


class NodeAddressing:
    _outputs = None

    @classmethod
    def _find_node(cls, extra_pnginfo, mapping:Mapping):
        skip = mapping.skip_first_n_matches
        for node in extra_pnginfo['workflow']['nodes']:
            if node.get('title', node.get('type'))==mapping.node_title:
                if not skip:
                    return node
                skip -= 1
        raise NodeAddressingException(f"Couldn't find node {node_title}")

    @classmethod
    def _find_input(cls, prompt, node, mapping:Mapping):
        try:
            input = prompt[str(node['id'])]['inputs'].get(mapping.input_name,None)
            if input is not None:
                return input
            raise NodeAddressingException(f"Couldn't find input {mapping.input_name}")
        except KeyError:
            raise NodeAddressingException(f"{node['id']} not in prompt - (is it bypassed?)")
        
    @classmethod
    def _set_input(cls, prompt, node, mapping:Mapping, value):
        try:
            input = prompt[str(node['id'])]['inputs'].get(mapping.input_name,None)
            if input is None:
                raise NodeAddressingException(f"Couldn't find input {mapping.input_name}")
            if isinstance(input,list):
                raise NodeAddressingException(f"Can't set an input, only a widget ({mapping.input_name})")
            prompt[str(node['id'])]['inputs'][mapping.input_name] = value
        except KeyError:
            raise NodeAddressingException(f"{node['id']} not in prompt - (is it bypassed?)")       

    @classmethod
    def get_key_and_value(cls, prompt, extra_pnginfo, mapping:Mapping, widgets_only=False):
        node = cls._find_node(extra_pnginfo, mapping)
        input = cls._find_input(prompt, node, mapping)
        if isinstance(input, list) and len(input)==1:
            input = input[0]
        if isinstance(input,list):
            if not widgets_only:
                if len(input)==1:
                    value = input[0]
                elif len(input)==2:
                    value = cls._get_output_value(*input)
                else:
                    value = str(value)
            else:
                raise NodeAddressingException(f"{mapping.node_and_widget()} is an input, not a widget")
        else:
            value = input
        mapping.value = value
        return mapping.key, value
    
    @classmethod
    def set_value(cls, prompt, extra_pnginfo, mapping:Mapping, value):
        node = cls._find_node(extra_pnginfo, mapping)
        cls._set_input(prompt, node, mapping.input_name, value)
        mapping.node_id = node['id']

    @classmethod
    def _prep_output_store(cls):
        if cls._outputs is not None:
            return
        for frame_info in inspect.stack():
            executor_maybe = frame_info.frame.f_locals.get("e",None)
            if hasattr(executor_maybe,'outputs'):
                cls._outputs = executor_maybe.outputs
                return
        raise NodeAddressingException("Failed to locate output store")
    
    @classmethod
    def _get_output_value(cls, node_id, output_index):
        cls._prep_output_store()
        node_id = str(node_id)
        if not node_id in cls._outputs:
            raise NodeAddressingException(f"{node_id} not found in output store - not yet evaluated?")
        if output_index<0 or output_index>len(cls._outputs[node_id]):
            raise NodeAddressingException(f"{output_index} out of range on {node_id} (len = {len(cls._outputs[node_id])})")
        return cls._outputs[str(node_id)][output_index]
    
    @classmethod
    def all_inputs(cls, extra_pnginfo, prompt, widgets_only=False):
        available = []
        unavailable = []
        node_titles = {}
        for node in extra_pnginfo['workflow']['nodes']:
            node_id = str(node['id'])
            title = node.get('title', node.get('type'))
            node_titles[title] = node_titles.get(title,0) + 1
            if node_id in prompt:  # some nodes aren't in the prompt - eg reroutes
                if 'inputs' in prompt[node_id]:
                    for name in prompt[node_id]['inputs']:
                        mapping = Mapping(key=None, node_title=title, input_name=name, skip_first_n_matches=node_titles[title]-1)
                        try:
                            cls.get_key_and_value(prompt, extra_pnginfo, mapping, widgets_only)
                            available.append((mapping.node_and_widget(), mapping.value))
                        except NodeAddressingException:
                            unavailable.append((mapping.node_and_widget(),sys.exc_info()[1].args[0] ))
        return available, unavailable
    
    @classmethod
    def print_input_details(cls, inputs):
        for a in inputs:
            print("{:>40.40} = {:<10.60}".format(*(str(v) for v in a)))
