from random import sample
from collections import defaultdict, Counter

from tqdm import tqdm

from pwaa.actionability import ActionabilityFilter


class ActionablePopularWorkflow:
    def __init__(self, top_n, sample_fraction=1.0, allow_page_load=True):
        self._top_n = top_n
        self._sample_fraction = sample_fraction
        self._allow_page_load = allow_page_load

        self._all_actions = []

    def fit(self, train_examples):
        for queries, actions in train_examples:
            self._all_actions.extend(actions)

    def predict(self, queries):
        all_elements = []
        element_to_actions = defaultdict(list)

        actionability_filter = ActionabilityFilter(queries)
        for action in tqdm(sample(self._all_actions, round(len(self._all_actions) * self._sample_fraction))):
            if not self._allow_page_load and action.page_load is not None:
                continue
            
            is_actionable, element = actionability_filter.is_actionable(action, return_element=True)

            if is_actionable:
                all_elements.append(element)
                element_to_actions[element].append(action)
            
        all_element_frequencies = Counter(all_elements)

        return [sample(element_to_actions[element], 1)[0]
                for element, _ in all_element_frequencies.most_common(self._top_n)]
