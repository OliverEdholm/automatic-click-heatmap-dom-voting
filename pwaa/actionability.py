from collections import defaultdict


class ActionabilityFilter:
    def __init__(self, queries):
        self._queries = queries

        self._queries_already_checked = defaultdict(dict)

    def is_actionable(self, action, return_element=False):
        is_actionable = False
        element = None
        if action.page_load is not None:
            for query in self._queries:
                if action.page_load.is_match(query.tree):
                    is_actionable = True
                    break
        else:
            for idx, query in enumerate(self._queries):
                already_checked = self._queries_already_checked[idx]

                element, updated_already_checked = action.selector.select(query.tree, already_checked)

                self._queries_already_checked[idx] = updated_already_checked

                if element is not None:
                    is_actionable = True
                    break

        if return_element:
            return is_actionable, element
        else:
            return is_actionable
