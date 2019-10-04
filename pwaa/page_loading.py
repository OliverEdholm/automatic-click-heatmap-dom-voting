from purl import URL
from lxml.html import tostring


class PageLoad:
    def __init__(self, url):
        assert 'http' in url

        self.url = url

        self._path = URL(url).path()[1:-1]

    def is_match(self, tree):
        html = tostring(tree)

        for idx in range(len(html) - len(self._path)):
            window = html[idx: idx + len(self._path)].decode()
            if window == self._path:
                return True

        return False