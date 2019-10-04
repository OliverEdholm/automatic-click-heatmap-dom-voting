import pytest

from cssselect import GenericTranslator
from lxml.etree import XPath

from pwaa.selectors import (
    get_css_selector,
    VotingSelector,
    FastSelector,
    FastVotingSelector
)
from pwaa.fast_tree import SelectorNode
from pwaa.utils import get_html_tree


def convert_to_xpath(css_selector):
    return str(XPath(GenericTranslator().css_to_xpath(css_selector)))


@pytest.fixture
def tree():
    html = '''
    <div>
        <div class="main">
            <h1 class="text1">
                Hello!
            </h1>
            <h1 class="text2">
                Hello!
            </h1>
            <div class="footer">
                <p> Info </p>
            </div>
        </div>
    </div>
    '''
    return get_html_tree(html)


def test_get_css_selector(tree):
    element1 = tree.findall('.//h1')[0]
    assert get_css_selector(element1, ['nth-child'], 1) == 'h1:nth-child(1)'
    assert get_css_selector(element1, ['none'], 100) == 'div > div > h1'
    assert get_css_selector(element1, ['class', 'id', 'none'], 2) == 'div[class="main"] > h1[class="text1"]'
    
    element2 = tree.findall('.//h1')[1]
    assert get_css_selector(element2, ['class', 'none'], 1) == 'h1[class="text2"]'


def test_voting_selector_correct(tree):
    css_selectors = ['.text1', 'h1:nth-child(1)', 'h1', 'div > div > h1']

    selector = VotingSelector(css_selectors)
    
    element = tree.findall('.//h1')[0]

    assert selector.select(tree) == element


def test_voting_selector_incorrect(tree):
    css_selectors = ['.wooo', 'nullspace', 'idk', 'variable']

    selector = VotingSelector(css_selectors)
    
    assert selector.select(tree) is None


def test_voting_selector_already_checked_override(tree):
    css_selectors = ['woaa', 'qweqweqew']  # does not exist in tree

    element = tree.findall('.//h1')[0]
    already_checked = {}
    already_checked[convert_to_xpath('woaa')] = set([element])

    selector = VotingSelector(css_selectors)

    assert selector.select(tree, already_checked) == (element, already_checked)


def test_voting_selector_already_checked_save(tree):
    css_selectors = ['.text1', 'h1:nth-child(1)']

    selector = VotingSelector(css_selectors)

    element, already_checked = selector.select(tree, {})

    expected_element = tree.findall('.//h1')[0]
    assert element == expected_element

    expected_already_checked = {}
    expected_already_checked[convert_to_xpath('.text1')] = set([element])
    expected_already_checked[convert_to_xpath('h1:nth-child(1)')] = set([element])

    assert already_checked == expected_already_checked


def test_voting_selector_save_load(tree):
    css_selectors = ['.wooo', 'nullspace', 'idk', 'variable']

    selector_before = VotingSelector(css_selectors)
    
    selector_after = VotingSelector.from_json(selector_before.to_json())

    assert selector_before.select(tree) == selector_after.select(tree)


@pytest.mark.parametrize('selector_nodes, expected_values',
    [
        (
            [SelectorNode(tag='h1', nth_child=1), SelectorNode(tag='div', class_attr='container')],
            [{
                'tag': 'h1',
                'id_attr': ['yo'],
                'class_attr': None,
                'nth_child': 1
            }]
        ),
        (
            [SelectorNode(tag='p'), SelectorNode(tag='div', nth_child=3), SelectorNode(tag='div', class_attr='content'), SelectorNode(tag='div', class_attr='main')],
            [{
                'tag': 'p',
                'id_attr': None,
                'class_attr': None,
                'nth_child': 1
            }]
        ),
        (
            [SelectorNode(tag='div', nth_child=1)],
            [
                {
                    'tag': 'div',
                    'id_attr': None,
                    'class_attr': ['main', 'section'],
                    'nth_child': 1
                },
                {
                    'tag': 'div',
                    'id_attr': ['highest'],
                    'class_attr': ['container'],
                    'nth_child': 1
                },
                {
                    'tag': 'div',
                    'id_attr': None,
                    'class_attr': None,
                    'nth_child': 1
                },
            ]
        )
    ]
)
def test_fast_selector(selector_nodes, expected_values):
    html = '''
    <div class="main section">
        <div id="highest" class="container">
            <h1 id="yo"> Yoo! </h1>
        </div>

        <div class="section content">
            <div></div>
            <p> something </p>
            <div id="something">
                <p> hello </p>
            </div>
        </div>

        <a> Hello </a>
    </div>
    '''
    tree = get_html_tree(html)
    
    fast_selector = FastSelector(selector_nodes)
    
    results = fast_selector.select(tree)

    result_values = []
    for tree_node in results:
        result_values.append({
            'tag': tree_node.tag,
            'id_attr': tree_node.id_attr,
            'class_attr': tree_node.class_attr,
            'nth_child': tree_node.nth_child,
        })

    assert expected_values == result_values


@pytest.mark.parametrize('css_selectors, expected_element_values', 
    [
        (
            ['div', 'div > div:nth-child(1)', 'div.footer', 'div > div > div', 'div.main > div'],
            {
                'tag': 'div',
                'class_attr': ['footer'],
                'id_attr': None,
                'nth_child': 3
            }
        ),
        (
            ['h1', 'div > h1', 'div > h1.text1', 'div > div > h1', 'h1:nth-child(1)'],
            {
                'tag': 'h1',
                'class_attr': ['text1'],
                'id_attr': None,
                'nth_child': 1
            }
        ),
        (
            ['div > button[id="clickme"]', 'div > div > button', 'div:nth-child(2) > button', 'div:nth-child(1) > div:nth-child(2) > button:nth-child(2)'],
            {
                'tag': 'button',
                'class_attr': None,
                'id_attr': ['clickme'],
                'nth_child': 2
            }
        ),
        (
            ['div > button[id="clickme"]', 'div > div > button', 'div:nth-child(2) > button', 'div:nth-child(1) > div:nth-child(2) > button:nth-child(2)'],
            {
                'tag': 'button',
                'class_attr': None,
                'id_attr': ['clickme'],
                'nth_child': 2
            }
        ),
        (
            ['h2', 'div > div > div > div > h2', 'div > div:nth-child(1) > h2', 'div > div > div > div.something > div > div:nth-child(1) > h2:nth-child(1)', 'randomiwllnotwork'],
            {
                'tag': 'h2',
                'class_attr': None,
                'id_attr': None,
                'nth_child': 1
            }
        ),
        (
            ['div > div:nth-child(2) > p', 'div.other-section > p', 'p', 'div:nth-child(1) > div[id="hello"] > p:nth-child(1)', 'div > div > p', 'div > p.text2'],
            {
                'tag': 'p',
                'class_attr': ['text2'],
                'id_attr': None,
                'nth_child': 1
            }
        )
    ]
)
def test_fast_voting_selector(css_selectors, expected_element_values):
    html = '''
    <div>
        <div class="main">
            <h1 class="text1">
                Hello!
            </h1>
            <h1 class="text2">
                Hello!
            </h1>
            <div class="footer">
                <p> Info </p>
            </div>
        </div>

        <div id="hello" class="other-section">
            <p class="text2"> Click button below </p>
            <button id="clickme"> Button </button>
        </div>

        <div>
            <div>
                <div class="something">
                    <div>
                        <div>
                            <h2>
                                <b> Hello </b>
                            </h2>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    tree = get_html_tree(html)

    fast_voting_selector = FastVotingSelector(css_selectors)

    element = fast_voting_selector.select(tree)[0]

    element_values = {
        'tag': element.tag,
        'class_attr': element.class_attr,
        'id_attr': element.id_attr,
        'nth_child': element.nth_child
    }
    
    assert element_values == expected_element_values