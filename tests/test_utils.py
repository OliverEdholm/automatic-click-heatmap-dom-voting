from pwaa.utils import get_html_tree


def test_get_html_tree():
    html = '''
    <div>
        <h1> Hello! </h1>
    </div>
    '''

    tree = get_html_tree(html)

    assert len(tree.findall('.//h1')) == 1
    assert len(tree.findall('.//html')) == 0