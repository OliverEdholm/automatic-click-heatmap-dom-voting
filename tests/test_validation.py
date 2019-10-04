import pytest

from pwaa.utils import get_html_tree
from pwaa.selectors import VotingSelector
from pwaa.page_loading import PageLoad
from pwaa.data import Query, Action
from pwaa.validation import ExampleValidator


def get_query(html):
    tree = get_html_tree(html)
    return Query(tree, {'type': 'pageLoad'})


def get_action_selector(css_selector):
    voting_selector = VotingSelector([css_selector])
    return Action({'type': 'click'}, selector=voting_selector)


def get_action_page_load(url):
    page_load = PageLoad(url)
    return Action({'type': 'pageLoad'}, page_load=page_load)


@pytest.fixture
def example_validator():
    html1 = '''
    <div>
        <div id="info">
            <h1> Hi! </h1>
        </div>
        <div id="action">
            <button class="send"> Send </button>
        </div>
        <div id="link">
            <a href="/logout/"> Log out </a>
        </div>
    </div>
    '''
    html2 = '''
    <div></div>
    '''

    queries = [
        get_query(html1),
        get_query(html2)
    ]
    actions = [
        get_action_selector('div.noexist'),
        get_action_selector('button.send')
    ]

    return ExampleValidator((queries, actions))


def test_example_validator_did_interact_selector(example_validator):
    selector = VotingSelector(['button'])
    action = Action({'type': 'click'}, selector=selector)

    assert example_validator.did_interact(action) is True


def test_example_validator_did_not_interact_selector(example_validator):
    selector = VotingSelector(['button.login'])
    action = Action({'type': 'click'}, selector=selector)

    assert example_validator.did_interact(action) is False


def test_example_validator_did_interact_page_load(example_validator):
    page_load = PageLoad('https://google.com/logout')
    action = Action({'type': 'pageLoad'}, page_load=page_load)

    assert example_validator.did_interact(action) is True


def test_example_validator_did_not_interact_page_load(example_validator):
    page_load = PageLoad('https://google.com/login')
    action = Action({'type': 'pageLoad'}, page_load=page_load)

    assert example_validator.did_interact(action) is False


def test_example_validator_has_query_actions_selector(example_validator):
    assert example_validator.has_query_actions() is True


def test_example_validator_has_no_query_actions_selector():
    html1 = '''
    <div id="info">
        <h1> Hi! </h1>
    </div>
    '''
    html2 = '''
    <div></div>
    '''

    queries = [
        get_query(html1),
        get_query(html2)
    ]

    actions = [
        get_action_selector('div.noexist'),
        get_action_selector('button.send')
    ]

    example_validator = ExampleValidator((queries, actions))

    assert example_validator.has_query_actions() is False


def test_example_validator_has_query_actions_page_load():
    html1 = '''
    <div id="info">
        <h1> Hi! </h1>
        <a href="/logout/"> Log out </a>
    </div>
    '''
    html2 = '''
    <div></div>
    '''

    queries = [
        get_query(html1),
        get_query(html2)
    ]

    actions = [
        get_action_page_load('https://google.com/logout/'),
        get_action_page_load('https://google.com/home')
    ]

    example_validator = ExampleValidator((queries, actions))

    assert example_validator.has_query_actions() is True


def test_example_validator_has_no_query_actions_page_load():
    html1 = '''
    <div id="info">
        <h1> Hi! </h1>
        <a href="/logout/"> Log out </a>
    </div>
    '''
    html2 = '''
    <div></div>
    '''

    queries = [
        get_query(html1),
        get_query(html2)
    ]

    actions = [
        get_action_page_load('https://google.com/login/'),
        get_action_page_load('https://google.com/home')
    ]

    example_validator = ExampleValidator((queries, actions))

    assert example_validator.has_query_actions() is False
