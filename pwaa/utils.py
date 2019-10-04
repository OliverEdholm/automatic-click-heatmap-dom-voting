from io import StringIO

from lxml import etree


def _get_html_parser():
    return etree.HTMLParser(default_doctype=False)


def get_html_tree(html):
    parser = _get_html_parser()
    
    return etree.parse(StringIO(html), parser)
