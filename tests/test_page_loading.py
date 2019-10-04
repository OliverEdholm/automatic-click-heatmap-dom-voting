import pytest

from pwaa.data import Query
from pwaa.utils import get_html_tree
from pwaa.page_loading import PageLoad


def get_query(html):
    tree = get_html_tree(html)
    return Query(tree, {'type': 'pageLoad'})


@pytest.mark.parametrize('url, html_section, expected', 
    [
        ('http://reddit.com/r/Blind/', 'r/Blind/', True),
        ('http://reddit.com/r/Blind', '/r/Blind/', True),
        ('http://google.com/r/Blind/', 'r/Blind/', True),
        ('http://reddit.com/r/Deaf/', 'r/Blind/', False)
    ]
)
def test_page_load_is_match(url, html_section, expected):
    page_load = PageLoad(url)

    query = get_query(
        f'''
        <div>
            <h1> {html_section} </h1>
        </div>
        '''
    )

    assert page_load.is_match(query.tree) is expected
