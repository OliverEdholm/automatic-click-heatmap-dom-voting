from random import sample
from collections import defaultdict


class RandomWorkflow:
    def __init__(self, top_n):
        self._top_n = top_n

        self._all_actions = []

    def fit(self, train_examples):
        for queries, actions in train_examples:
            self._all_actions.extend(actions)

    def predict(self, queries):
        return sample(self._all_actions, self._top_n)


class PopularWorkflow:
    def __init__(self, top_n):
        self._top_n = top_n

        self._top_n_most_popular = []

    def fit(self, train_examples):
        target_frequencies = defaultdict(int)
        target_to_actions = defaultdict(list)

        for queries, actions in train_examples:
            for action in actions:
                target = action.row['value'].get('target')
                if target is not None:
                    target_frequencies[target] += 1
                    target_to_actions[target].append(action)

        targets_most_frequent = list(sorted(
            target_frequencies.items(), key=lambda x: x[1], reverse=True))[:self._top_n]

        for target, _ in targets_most_frequent:
            target_actions = target_to_actions[target]
            self._top_n_most_popular.append(sample(target_actions, 1)[0])
    
    def predict(self, queries):
        return self._top_n_most_popular