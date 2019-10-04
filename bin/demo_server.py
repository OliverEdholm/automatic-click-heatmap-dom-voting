import json
import pickle

import tldextract
from flask import (
    Flask,
    request,
    jsonify
)

from pwaa.utils import get_html_tree
from pwaa.selectors import get_css_selector
from pwaa.data import load_examples, Query

app = Flask(__name__)

with open('data/serving_fast_voting_selector.pkl', 'rb') as f:
    fast_voting_selector = pickle.load(f)


@app.route('/')
def empty():
    return 'Hello world'


@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    html = json.loads(request.json)['html']
    tree = get_html_tree(html)

    to_return = []
    # for tree_node in fast_voting_selector.select(tree):
    for tree_node in fast_voting_selector.select(tree)[:100]:
        print(tree_node)
        to_return.append({
            'type': 'interact',
            'cssSelector': get_css_selector(tree_node, ['class', 'id', 'none'], 1000)
        })

    return jsonify(to_return)


if __name__ == '__main__':
    app.run(ssl_context='adhoc', debug=True)
