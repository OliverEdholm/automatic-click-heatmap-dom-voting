import json
from random import sample
from copy import deepcopy
from collections import Counter, defaultdict

from cssselect import GenericTranslator
from lxml.etree import XPath

from pwaa.fast_tree import get_tree_node_tree, get_selector_nodes

ATTRIBUTE_PRIORITIES = ['class', 'id']


class UndefinedPriorityException(Exception):
    pass


def get_css_selector(tree_node, priorities, height):
    cur_element = tree_node

    parts = []
    for _ in range(height):
        if cur_element.tag == 'body':
            break

        for priority in priorities:
            if priority == 'id':
                if cur_element.id_attr:
                    extension = f'[id="{cur_element.id_attr[0]}"]'
                    break
            elif priority == 'class':
                if cur_element.class_attr:
                    c = sample(cur_element.class_attr, 1)[0]
                    extension = f'.{c}'   # better reverse
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


class VotingSelector:
    def __init__(self, css_selectors):
        self._xpaths = [XPath(GenericTranslator().css_to_xpath(css_selector))
                        for css_selector in css_selectors]

    def select(self, tree, already_checked=None):
        all_elements = []
        for xpath in self._xpaths:
            if already_checked is not None:
                if already_checked.get(str(xpath)) is not None:
                    all_elements.extend(list(already_checked[str(xpath)]))
                    continue

            results = xpath(tree)

            all_elements.extend(results)

            if already_checked is not None:
                if already_checked.get(str(xpath)) is not None:
                    for result in results:
                        already_checked[str(xpath)].add(result)
                else:
                    already_checked[str(xpath)] = set(results)

        frequent = Counter(all_elements).most_common(1)
        if frequent:
            element = frequent[0][0]
        else:
            element = None
        
        if already_checked is not None:
            return element, already_checked
        else:
            return element
        
    def to_json(self):
        return {
            'xpaths': [str(xpath)
                       for xpath in self._xpaths]
        }
    
    @classmethod
    def from_json(cls, json_obj):
        voting_selector = cls([])
        voting_selector._xpaths = [XPath(xpath)
                                   for xpath in json_obj['xpaths']]
        
        return voting_selector


class VotingTreeNode:
    def __init__(self, selector_node=None):
        self.n_satisfied = 0
        self.selector_node = selector_node

        self.parent = None
        self.children = []

    # TODO: make faster with dynamic programming
    def get_prev_path_identifier(self):
        identifier_parts = []

        cur_voting_tree_node = self
        while cur_voting_tree_node is not None:
            identifier_parts.append(cur_voting_tree_node.selector_node.get_identifier())
            cur_voting_tree_node = self.parent

        return ' > '.join(identifier_parts)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


from dataclasses import dataclass, field


@dataclass(unsafe_hash=True)
class ElementChecker:
    tag: str = field(default=None)
    class_attr: str = field(default=None)
    id_attr: str = field(default=None)
    nth_child: int = field(default=None)

    score: int = field(compare=False, default=0)

    def does_pass(self, tree_node):
        if self.tag is not None:
            if self.tag != tree_node.tag:
                return False

        if self.class_attr is not None:
            if tree_node.class_attr is None:
                return False

            if self.class_attr not in tree_node.class_attr:
                return False

        if self.id_attr is not None:
            if tree_node.id_attr is None:
                return False

            if self.id_attr not in tree_node.id_attr:
                return False

        if self.nth_child is not None:
            if self.nth_child != tree_node.nth_child:
                return False

        return True

    def __repr__(self):
        return f'ElementChecker(tag={self.tag}, class_attr={self.class_attr}, id_attr={self.id_attr}, nth_child={self.nth_child})'

START_PATH = 'START'


class FastVotingSelector:
    def __init__(self, css_selectors=[]):
        self._path_to_element_checkers = defaultdict(set)

        for css_selector in css_selectors:
            self.update(css_selector)

    def _get_element_checkers(self, css_selector):
        parts = css_selector.split(' > ')

        element_checkers = []
        for part in parts:
            element_checker = ElementChecker()
            
            tag = ''
            for char in part:
                if char == '.':  # class
                    element_checker.class_attr = part.split('.')[1].split(':')[0]
                    break
                elif char == '[':  # id
                    element_checker.id_attr = part.split('[id="')[1].split(':')[0].split('"]')[0]
                    break
                elif char == ':':  # nth-child
                    break  # nth-child is retrieved below
                else:
                    tag += char
                    
            element_checker.tag = tag

            if ':nth-child' in part:
                element_checker.nth_child = int(part.split(':nth-child(')[1][:-1])
            
            element_checkers.append(element_checker)
        
        return element_checkers[::-1]

    def _get_all_tree_nodes(self, lxml_tree):
        root_tree_node = get_tree_node_tree(lxml_tree.getroot())
       
        all_tree_nodes = []
        
        cur_tree_nodes = [root_tree_node]
        while cur_tree_nodes:
            next_tree_nodes = []
            
            for tree_node in cur_tree_nodes:
                all_tree_nodes.append(tree_node)
                next_tree_nodes.extend(tree_node.children)
                
            cur_tree_nodes = list(next_tree_nodes)

        return all_tree_nodes

    def _get_updated_path(self, path, element_checker):
        return path + ' > ' + str(element_checker)

    def _get_score(self, tree_node):
        score = 0

        cur_tree_node = tree_node

        cur_element_checkers = [(START_PATH, element_checker)
                                for element_checker in self._path_to_element_checkers[START_PATH]]
        while cur_element_checkers and cur_tree_node:
            next_element_checkers = []
            for path, element_checker in cur_element_checkers:
                if element_checker.does_pass(cur_tree_node):
                    score += element_checker.score

                    next_path = self._get_updated_path(path, element_checker)
                    for next_element_checker in self._path_to_element_checkers[next_path]:
                        next_element_checkers.append((
                            next_path,
                            next_element_checker
                        ))

            cur_tree_node = cur_tree_node.parent
            cur_element_checkers = list(next_element_checkers)  # copy

        return score

    def update(self, css_selector):
        element_checkers = self._get_element_checkers(css_selector)

        cur_path = START_PATH
        for idx, element_checker in enumerate(element_checkers):
            self._path_to_element_checkers[cur_path].add(element_checker)
            
            if idx == len(element_checkers) - 1:
                for other in self._path_to_element_checkers[cur_path]:
                    if element_checker == other:
                        other.score += 1
            else:
                cur_path = self._get_updated_path(cur_path, element_checker)

    def select(self, tree, score_threshold=1):
        all_tree_nodes = self._get_all_tree_nodes(tree)
        
        tree_node_scores = []
        for tree_node in all_tree_nodes:
            tree_node_scores.append((
                tree_node,
                self._get_score(tree_node)
            ))

        tree_node_scores.sort(key=lambda x: x[1], reverse=True)

        return [tree_node
                for tree_node, score in tree_node_scores
                if score >= score_threshold]
        