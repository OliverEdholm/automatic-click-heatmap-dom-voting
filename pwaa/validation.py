from pwaa.actionability import ActionabilityFilter


class ExampleValidator:
    def __init__(self, example):
        queries, actions = example

        self._actionability_filter = ActionabilityFilter(queries)

        self._interacted_query_elements = []
        for action in actions:
            is_actionable, element = self._actionability_filter.is_actionable(action, return_element=True)

            if is_actionable:
                self._interacted_query_elements.append(element)
                
    def _find_element(self, selector):
        for query in self._queries:
            element = selector.select(query.tree)

            if element is not None:
                return element

    def has_query_actions(self):
        return bool(self._interacted_query_elements)

    def did_interact(self, action):
        is_actionable, element = self._actionability_filter.is_actionable(action, return_element=True)

        if action.selector is not None:
            return is_actionable and element in self._interacted_query_elements
        else:
            return is_actionable
