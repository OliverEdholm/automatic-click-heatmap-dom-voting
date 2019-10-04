import sys
import pickle
from time import time
from copy import deepcopy
from multiprocessing import Pool

import requests

from pwaa.selectors import VotingSelector


def get_correct_selector(incorrect, html):
    valid = ' > '.join(incorrect.split(' > ')[1:])

    url = "https://us-central1-icon-classifier.cloudfunctions.net/selectors/getCorrectSelector"

    payload = {
        "incorrectSelector": valid, 
        "html": html
    }

    header = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }

    try:
        response_decoded_json = requests.post(url, data=payload, headers=header)
        response_json = response_decoded_json.json()
    except Exception as e:
        print(f'error in response: {e}')
        return
    
    return response_json.get('correctSelectors')


def get_voting_selector(action_row):
    target = action_row['value'].get('target')
    if target:
        css_selectors = get_correct_selector(target, action_row['html'])

        if css_selectors:
            return VotingSelector(css_selectors)


def get_session_with_voting_selectors(session, max_time=60 * 10):
    try:
        extension_id = session[0][0][0]['extensionId']
        tab_id = session[0][0][0]['tabId']

        print(f'starting {extension_id}, {tab_id}')

        start_time = time()

        new_session = []
        for queries, actions in session:
            new_actions = []
            for action in actions:
                if action['type'] == 'pageLoad':
                    new_actions.append(action)
                else:
                    for row in queries + actions:  # any of the pages could satisfy
                        if time() - start_time > max_time:
                            print(f'took too long {extension_id} {tab_id}')
                            return

                        voting_selector = get_voting_selector(row)

                        if voting_selector:
                            new_action = deepcopy(action)
                            new_action['voting_selector'] = voting_selector.to_json()

                            new_actions.append(new_action)
                            
                            break

            new_session.append((queries, new_actions)) 

        print(f'finished {extension_id}, {tab_id}')

        return new_session
    except Exception as e:
        print(f'unknown error occured: {e}')


def main():
    examples_path, output_path = sys.argv[1:]

    print('loading sessions')
    with open(examples_path, 'rb') as f:
        sessions = pickle.load(f)

    pool = Pool(processes=500)
    sessions_with_voting_selectors = pool.map(get_session_with_voting_selectors, sessions)

    with open(output_path, 'wb') as f:
        pickle.dump(sessions_with_voting_selectors, f)


if __name__ == '__main__':
    main()
