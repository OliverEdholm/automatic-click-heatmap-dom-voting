import pytest

from pwaa.utils import get_html_tree
from pwaa.fast_tree import (
    get_tree_node_tree,
    get_selector_nodes,
    TreeNode,
    SelectorNode
)


def test_tree_node():
    tree_node = TreeNode(
        tag='h1',
        id_attr='message1',
        class_attr='big',
        nth_child=1
    )

    assert tree_node.tag == 'h1'
    assert tree_node.id_attr == 'message1'
    assert tree_node.class_attr == 'big'
    assert tree_node.nth_child == 1

    assert tree_node.children == set()
    assert tree_node.parent is None


def test_get_tree_node_tree():
    html = '''
    <div>
        <div class="primary info">
            <button id="send"> Send </button>
        </div>
    </div>
    '''
    tree = get_html_tree(html)
    root_element = tree.getroot().findall('*')[0].findall('*')[0]

    div_tree_node = get_tree_node_tree(root_element)

    assert div_tree_node.tag == 'div'
    assert div_tree_node.id_attr is None
    assert div_tree_node.class_attr is None
    assert div_tree_node.nth_child == 1
    assert div_tree_node.parent is None
    assert len(div_tree_node.children) == 1
    
    primary_tree_node = list(div_tree_node.children)[0]

    assert primary_tree_node.tag == 'div'
    assert primary_tree_node.id_attr is None
    assert primary_tree_node.class_attr == ['primary', 'info']
    assert primary_tree_node.nth_child == 1
    assert primary_tree_node.parent == div_tree_node
    assert len(primary_tree_node.children) == 1

    button_tree_node = list(primary_tree_node.children)[0]

    assert button_tree_node.tag == 'button'
    assert button_tree_node.id_attr == ['send']
    assert button_tree_node.class_attr is None
    assert button_tree_node.nth_child == 1
    assert button_tree_node.parent == primary_tree_node
    assert button_tree_node.children == set()


def test_tree_node_add_child():
    tree_node1 = TreeNode(
        tag='div',
        id_attr=None,
        class_attr=None,
        nth_child=1
    )
    tree_node2 = TreeNode(
        tag='h1',
        id_attr=['message1'],
        class_attr=['big'],
        nth_child=1
    )
    tree_node3 = TreeNode(
        tag='h1',
        id_attr=['message2'],
        class_attr=['small'],
        nth_child=1
    )
    
    tree_node1.add_child(tree_node2)
    tree_node2.add_child(tree_node3)

    assert tree_node1.parent is None
    assert tree_node1.children == set([tree_node2])

    assert tree_node2.parent == tree_node1
    assert tree_node2.children == set([tree_node3])

    assert tree_node3.parent == tree_node2
    assert tree_node3.children == set([])


def test_selector_node():
    selector_node = SelectorNode(
        tag='div',
        id_attr=None,
        class_attr='item',
        nth_child=None
    )
    
    assert selector_node.tag == 'div'
    assert selector_node.id_attr is None
    assert selector_node.class_attr == 'item'
    assert selector_node.nth_child is None


@pytest.mark.parametrize('selector_node, tree_node, expected',
    [
        (
            SelectorNode(tag='h1'),
            TreeNode('h1', ['some_class'], ['some_id'], 2),
            True
        ),
        (
            SelectorNode(tag='h2'),
            TreeNode('h1', ['some_class'], ['some_id'], 2),
            False
        ),
        (
            SelectorNode(tag='div', class_attr='header'),
            TreeNode('div', ['header', 'info'], None, 2),
            True
        ),
        (
            SelectorNode(tag='div', nth_child=2),
            TreeNode('div', ['header'], None, 1),
            False
        )
    ]
)
def test_selector_node_is_match(selector_node, tree_node, expected):
    assert selector_node.is_match(tree_node) is expected


@pytest.mark.parametrize('css_selector, expected_selector_nodes',
    [
        (
            'div > h1:nth-child(4)',
            [
                SelectorNode(tag='div'),
                SelectorNode(tag='h1', nth_child=4)
            ]
        ),
        (
            'h1.yo-yo:nth-child(3) > b[id="hello"]',
            [
                SelectorNode(tag='h1', class_attr='yo-yo', nth_child=3),
                SelectorNode(tag='b', id_attr='hello')
            ]
        ),
        (
            'div > div > div > button',
            [
                SelectorNode(tag='div'),
                SelectorNode(tag='div'),
                SelectorNode(tag='div'),
                SelectorNode(tag='button')
            ]
        )
    ]
)
def test_get_selector_nodes(css_selector, expected_selector_nodes):
    assert get_selector_nodes(css_selector) == expected_selector_nodes
