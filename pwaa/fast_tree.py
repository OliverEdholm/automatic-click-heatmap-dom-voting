class TreeNode:
    def __init__(
        self,
        tag,
        class_attr,
        id_attr,
        nth_child
    ):
        self.id_attr = id_attr
        self.class_attr = class_attr
        self.tag = tag
        self.nth_child = nth_child

        self.parent = None
        self.children = set()

    def add_child(self, child):
        child.parent = self
        self.children.add(child)


class SelectorNode:
    def __init__(
        self,
        tag=None,
        id_attr=None,
        class_attr=None,
        nth_child=None,
    ):
        self.tag = tag
        self.id_attr = id_attr
        self.class_attr = class_attr
        self.nth_child = nth_child

    def is_match(self, other):
        def is_mismatch(self_val, other_val):
            if self_val is not None:
                if isinstance(other_val, list):
                    if self_val not in other_val:
                        return True
                else:
                    if self_val != other_val:
                        return True
            
            return False
        
        vals = [
            (self.id_attr, other.id_attr),
            (self.class_attr, other.class_attr),
            (self.tag, other.tag),
            (self.nth_child, other.nth_child)
        ]
        for self_val, other_val in vals:
            if is_mismatch(self_val, other_val):
                return False
        
        return True

    def get_identifier(self):
        return self.__repr__()

    def __repr__(self):
        return f'SelectorNode(tag={self.tag}, id={self.id_attr}, class={self.class_attr}, nth_child={self.nth_child})'

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, SelectorNode):
            return (
                self.tag == other.tag and \
                self.class_attr == other.class_attr and \
                self.id_attr == other.id_attr and \
                self.nth_child == other.nth_child
            )
        else:
            return False


def get_tree_node_tree(root_element, nth_child=1):
    id_str = root_element.attrib.get('id')
    if id_str is None:
        id_attr = None
    else:
        id_attr = [a for a in id_str.split(' ') if a != '']

    class_str = root_element.attrib.get('class')
    if class_str is None:
        class_attr = None
    else:
        class_attr = [a for a in class_str.split(' ') if a != '']

    root_tree_node = TreeNode(
        tag=root_element.tag,
        id_attr=id_attr,
        class_attr=class_attr,
        nth_child=nth_child
    )

    # children = root_element.findall('*')
    children = root_element.getchildren()
    for idx, element in enumerate(children):
        root_tree_node.add_child(get_tree_node_tree(element, idx + 1))

    return root_tree_node


def get_selector_nodes(css_selector):
    parts = css_selector.split(' > ')
   
    selector_nodes = []
    for part in parts:
        selector_node = SelectorNode()
        
        tag = ''
        for char in part:
            if char == '.':  # class
                selector_node.class_attr = part.split('.')[1].split(':')[0]
                break
            elif char == '[':  # id
                selector_node.id_attr = part.split('[id="')[1].split(':')[0].split('"]')[0]
                break
            elif char == ':':  # nth-child
                break  # nth-child is retrieved below
            else:
                tag += char
                
        selector_node.tag = tag

        if ':nth-child' in part:
            selector_node.nth_child = int(part.split(':nth-child(')[1][:-1])
        
        selector_nodes.append(selector_node)
    
    return selector_nodes


def get_css_selector(tree_node, priorities, height):
    cur_element = tree_node

    parts = []
    for _ in range(height):
        for priority in priorities:
            if priority == 'id':
                if cur_element.id_attr is not None:
                    extension = f'[id="{cur_element.id_attr[0]}"]'
                    break
            elif priority == 'class':
                if cur_element.class_attr is not None:
                    c = ' '.join(cur_element.class_attr)
                    extension = f'[class="{c}"]'
                    break
            elif priority == 'nth-child':
                nth_child = cur_element.nth_child
                
                extension = f':nth-child({nth_child})'
                break
            elif priority == 'none':
                extension = ''
                break
            else:
                raise UndefinedPriorityException()
    
        parts.append(f'{cur_element.tag}{extension}')
        cur_element = cur_element.parent

        if cur_element.parent is None:
            break

    return ' > '.join(parts[::-1])