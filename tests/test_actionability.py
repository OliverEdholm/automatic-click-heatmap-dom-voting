import pytest

from pwaa.utils import get_html_tree
from pwaa.data import Query, Action
from pwaa.selectors import VotingSelector
from pwaa.page_loading import PageLoad
from pwaa.actionability import ActionabilityFilter


def get_queries():
    def get_query(html):
        tree = get_html_tree(html)
        return Query(tree, {})

    queries = [
        get_query(
            '''
            <div>
                <div class="content">
                    <h1> Test </h1>
                </div>
            </div>
            '''
        ),
        get_query(
            '''
            <div>
                <div class="content">
                    <h1> Test </h1>
                </div>
                <div class="footer">
                    <div>
                        <a href="/logout"> Log out </a>
                    </div>
                </div>
            </div>
            '''
        ),
        get_query('''<div> </div>''')
    ]
    
    return queries


@pytest.fixture
def actionability_filter():
    queries = get_queries()
    return ActionabilityFilter(queries)


def test_actionability_filter_selector_actionable(actionability_filter):
    selector = VotingSelector(['.content', 'div:nth-child(1)'])
    action = Action({'type': 'click'}, selector=selector)

    assert actionability_filter.is_actionable(action) is True


def test_actionability_filter_selector_non_actionable(actionability_filter):
    selector = VotingSelector(['.header', 'div:nth-child(100)'])
    action = Action({'type': 'click'}, selector=selector)

    assert actionability_filter.is_actionable(action) is False


def test_actionability_filter_page_load_actionable(actionability_filter):
    page_load = PageLoad('https://hello.com/logout')
    action = Action({'type': 'pageLoad'}, page_load=page_load)

    assert actionability_filter.is_actionable(action) is True


def test_actionability_filter_page_load_non_actionable(actionability_filter):
    page_load = PageLoad('https://hello.com/login')
    action = Action({'type': 'pageLoad'}, page_load=page_load)

    assert actionability_filter.is_actionable(action) is False


def test_actionability_filter_selector_return_element():
    selector = VotingSelector(['h1'])
    action = Action({'type': 'click'}, selector=selector)

    queries = get_queries()
    actionability_filter = ActionabilityFilter(queries)

    element = queries[0].tree.findall('.//h1')[0]

    assert actionability_filter.is_actionable(action, return_element=True) == (True, element)


def test_actionability_filter_page_load_return_element():
    page_load = PageLoad('https://hello.com')
    action = Action({'type': 'pageLoad'}, page_load=page_load)

    queries = get_queries()
    actionability_filter = ActionabilityFilter(queries)

    assert actionability_filter.is_actionable(action, return_element=True)[1] is None
