from random import sample
from collections import defaultdict, Counter

import pandas as pd

from pwaa.html_embedding import get_jpf_embedding
from pwaa.nn_search import HTMLNNSearch
from pwaa.actionability import ActionabilityFilter


class ActionableSimilar:
    def __init__(self, top_n, n_neighbors=500, length=10, offset=5):
        self._top_n = top_n
        self._n_neighbors = n_neighbors
        self._length = length
        self._offset = offset

        self._row_id_to_example_id = {}
        self._example_id_to_actions = {}

        self._nn_search = None

    def fit(self, training_examples):
        all_query_rows = []
        all_query_embeddings = []

        example_id = 0
        from tqdm import tqdm
        for queries, actions in tqdm(training_examples):
            all_query_rows.extend([query.row for query in queries])
            all_query_embeddings.extend([get_jpf_embedding(query.tree, self._length, self._offset) for query in queries])

            for query in queries:
                self._row_id_to_example_id[query.row.name] = example_id
                
            self._example_id_to_actions[example_id] = actions
            
            example_id += 1

        all_idxs = pd.DataFrame(all_query_rows).index.values

        self._nn_search = HTMLNNSearch(all_idxs, all_query_embeddings, self._n_neighbors)

    def predict(self, queries):
        voting_row_ids = []
        for query in queries:
            embedding = get_jpf_embedding(query.tree, self._length, self._offset)
            row_ids = self._nn_search.get_nn_row_ids(embedding)
            voting_row_ids.extend(row_ids)

        all_elements = []
        element_to_actions = defaultdict(list)

        all_example_ids = [self._row_id_to_example_id[row_id]
                           for row_id in voting_row_ids]
        unique_example_ids = list(set(all_example_ids))
        
        all_actions = [action
                       for example_id in unique_example_ids
                       for action in self._example_id_to_actions[example_id]]

        actionability_filter = ActionabilityFilter(queries)
        for action in all_actions:
            if action.page_load is not None:
                continue

            is_actionable, element = actionability_filter.is_actionable(action, return_element=True)

            if is_actionable:
                all_elements.append(element)
                element_to_actions[element].append(action)
            
        all_element_frequencies = Counter(all_elements)

        # return [sample(element_to_actions[element], 1)[0]
        #         for element, _ in all_element_frequencies.most_common(self._top_n)]

