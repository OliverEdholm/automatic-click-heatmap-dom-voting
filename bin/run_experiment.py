import sys
import random

from tqdm import tqdm

from pwaa.data import load_examples
from pwaa.validation import ExampleValidator
from pwaa.workflows.baselines import RandomWorkflow, PopularWorkflow
from pwaa.workflows.actionable_popular import ActionablePopularWorkflow

# random.seed(7)

class UndefinedMethodException(Exception):
    pass


def main():
    examples_path, method, top_n, test_fraction = sys.argv[1:]

    if method == 'random':
        workflow_fn = RandomWorkflow
    elif method == 'most_popular':
        workflow_fn = PopularWorkflow
    elif method == 'most_popular_actionable':
        workflow_fn = ActionablePopularWorkflow
    # elif method == 'most_popular_selector_page_actionable':
    #     workflow_fn = ActionablePopularWorkflow
    else:
        raise UndefinedMethodException()

    print('initializing workflow')
    workflow = workflow_fn(int(top_n))
    
    print('loading data')
    train, test = load_examples(examples_path, float(test_fraction))

    print('fitting')
    workflow.fit(train)

    print('evaluating')
    n_total = 0
    n_query_actions = 0
    n_correct = 0

    times = []
    for queries, actions in tqdm(test):
        n_total += 1

        validator = ExampleValidator((queries, actions))

        if validator.has_query_actions():
            n_query_actions += 1

            from time import time
            start = time()
            top_predictions = workflow.predict(queries)
            times.append(time() - start)
            for action in top_predictions:
                if validator.did_interact(action):
                    n_correct += 1
                    break   # not completely sure if this right thing to do

    import numpy as np
    print(np.average(times))

    print(f'has query actions: {n_query_actions / n_total}')
    print(f'accuracy: {n_correct / n_query_actions}')


if __name__ == '__main__':
    main()
