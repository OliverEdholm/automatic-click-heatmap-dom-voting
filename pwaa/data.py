import pickle
import numpy as np

from pwaa.utils import get_html_tree
from pwaa.selectors import VotingSelector
from pwaa.page_loading import PageLoad

# np.random.seed(7)


class Query:
    def __init__(self, tree, row):
        self.tree = tree
        self.row = row
    

class Action:
    def __init__(self, row, selector=None, page_load=None):
        assert selector is None or page_load is None, 'Only one action type is allowed'

        self.page_load = page_load
        self.selector = selector  # this is not a css selector but rather an object with the method "select"
        self.row = row


def load_examples(path, test_fraction):
    with open(path, 'rb') as f:
        users = pickle.load(f)
        
    train = []
    test = []
    for user in users:
        if user is None:
            continue

        examples = []
        for query_rows, action_rows in user: 
            queries = [Query(get_html_tree(row['html']), row)
                       for row in query_rows]
            actions = []
            for row in action_rows:
                if row['type'] == 'pageLoad':
                    actions.append(
                        Action(row, page_load=PageLoad(row['url'])))
                else:
                    actions.append(
                        Action(row, selector=VotingSelector.from_json(row.get('voting_selector'))))

            examples.append((queries, actions))

        if np.random.random() < test_fraction:
            test.extend(examples)
        else:
            train.extend(examples)

    return train, test
