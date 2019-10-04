from pwaa.utils import get_html_tree
from pwaa.data import (
    load_examples,
    Query,
    Action
)
from pwaa.page_loading import PageLoad
from pwaa.selectors import VotingSelector


def test_action_selector():
    selector = VotingSelector(['.hej'])
    action = Action({'type': 'click'}, selector=selector)

    assert action.selector == selector
    assert action.row == {'type': 'click'}


def test_action_page_laod():
    page_load = PageLoad('https://reddit.com/r/Blindd')
    action = Action({'type': 'pageLoad'}, page_load=page_load)

    assert action.page_load == page_load
    assert action.row == {'type': 'pageLoad'}


def test_query():
    tree = get_html_tree('<div></div>')

    query = Query(tree, {'type': 'pageLoad'})

    assert query.tree == tree
    assert query.row == {'type': 'pageLoad'}


def test_load_examples():
    train, test = load_examples('tests/data/examples.pkl', 0.05)

    assert train[0][0][0] is not None  # query
    assert train[0][1][0] is not None  # action

    assert isinstance(train[0][1][0].selector, VotingSelector)
