import inspect, sys

class NodeAddressingException(Exception):
    pass

class NodeAddressing:
    _outputs = None

    @classmethod
    def _find_node(cls, extra_pnginfo, node_title, skip):
        for node in extra_pnginfo['workflow']['nodes']:
            if node.get('title', node.get('type'))==node_title:
                if skip==0:
                    return node
                skip -= 1
        raise NodeAddressingException(f"Couldn't find node {node_title}")

    @classmethod
    def _find_input(cls, prompt, node, input_name):
        try:
            input = prompt[str(node['id'])]['inputs'].get(input_name,None)
            if input is not None:
                return input
            raise NodeAddressingException(f"Couldn't find input {input_name}")
        except KeyError:
            raise NodeAddressingException(f"{node['id']} not in prompt - maybe need to refresh?")
        
    @classmethod
    def _set_input(cls, prompt, node, input_name, value):
        try:
            input = prompt[str(node['id'])]['inputs'].get(input_name,None)
            if input is None:
                raise NodeAddressingException(f"Couldn't find input {input_name}")
            if isinstance(input,list):
                raise NodeAddressingException(f"Can't set an input, only a widget ({input_name})")
            prompt[str(node['id'])]['inputs'][input_name] = value
        except KeyError:
            raise NodeAddressingException(f"{node['id']} not in prompt - maybe need to refresh?")       
        
    @classmethod
    def parse_source(cls, source):
        location, key = (s.strip() for s in source.split(",")) if "," in source else (source,None)
        if not "." in location:
            raise NodeAddressingException(f"{source} isn't valid - datasource format is node_name[#n].input_name")
        
        node_title, input_name = location.split(".",1)
        node_title, skip_first_n_matches = node_title.split("#",1) if "#" in node_title else (node_title,1)
        try:
            skip_first_n_matches = int(skip_first_n_matches) - 1
        except ValueError:
            raise NodeAddressingException(f"{source} isn't valid - n must be an integer in node_name[#n].input_name")
        key = key or input_name
            
        return key, node_title, input_name, skip_first_n_matches

    @classmethod
    def get_key_and_value(cls, prompt, extra_pnginfo, source, widgets_only=False):
        key, node_title, input_name, skip_first_n_matches = cls.parse_source(source)
        node = cls._find_node(extra_pnginfo, node_title, skip_first_n_matches)
        input = cls._find_input(prompt, node, input_name)
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
                raise NodeAddressingException(f"{source} is an input, not a widget")
        else:
            value = input
        return key, value
    
    @classmethod
    def set_value(cls, prompt, extra_pnginfo, target, value):
        _, node_title, input_name, skip_first_n_matches = cls.parse_source(target)
        node = cls._find_node(extra_pnginfo, node_title, skip_first_n_matches)
        cls._set_input(prompt, node, input_name, value)
        return node['id'], input_name

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
            if node_titles[title]>1:
                title = f"{title}#{node_titles[title]}"
            if node_id in prompt:  # some nodes aren't in the prompt - eg reroutes
                if 'inputs' in prompt[node_id]:
                    for name in prompt[node_id]['inputs']:
                        source = f"{title}.{name}"
                        try:
                            _, value = cls.get_key_and_value(prompt, extra_pnginfo, source, widgets_only)
                            available.append((source, value))
                        except NodeAddressingException:
                            unavailable.append((source,sys.exc_info()[1].args[0] ))
        return available, unavailable
    
    @classmethod
    def print_input_details(cls, inputs):
        for a in inputs:
            print("{:>40.40} = {:<10.60}".format(*(str(v) for v in a)))
