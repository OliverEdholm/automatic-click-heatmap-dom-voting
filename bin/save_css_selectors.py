import re
import sys
import pickle
from time import time
from copy import deepcopy
from multiprocessing import Pool

import requests


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


def get_css_selectors(action_row):
    target = action_row['value'].get('target')
    if target:
        html = action_row['html']
        html = re.sub('(?<=(<style>))(\w|\d|\n|[().,\-:;@#$%^&*\[\]"\'+–\/\/®°⁰!?{}|`~]| )+?(?=(<\/style>))', '', html)
        html = re.sub('(?<=(<script>))(\w|\d|\n|[().,\-:;@#$%^&*\[\]"\'+–\/\/®°⁰!?{}|`~]| )+?(?=(<\/script>))', '', html)
        
        # css_selectors = get_correct_selector(target, action_row['html'])
        css_selectors = get_correct_selector(target, html)

        if css_selectors:
            return css_selectors


def get_session_with_css_selectors(session, max_time=60 * 10):
    try:
        try:
            extension_id = session[0][0][0]['extensionId']
            tab_id = session[0][0][0]['tabId']

            print(f'starting {extension_id}, {tab_id}')
        except:  # not good :))
            pass

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
                            try:
                                print(f'took too long {extension_id} {tab_id}')
                            except:
                                pass
                            return

                        css_selectors = get_css_selectors(row)

                        if css_selectors:
                            new_action = deepcopy(action)
                            new_action['css_selectors'] = css_selectors

                            new_actions.append(new_action)
                            
                            break

            new_session.append((queries, new_actions)) 

        try:
            print(f'finished {extension_id}, {tab_id}')
        except:
            pass

        return new_session
    except Exception as e:
        print(f'unknown error occured: {e}')


def main():
    examples_path, output_path = sys.argv[1:]

    print('loading sessions')
    with open(examples_path, 'rb') as f:
        sessions = pickle.load(f)
  
    pool = Pool(processes=500)
    sessions_with_css_selectors = pool.map(get_session_with_css_selectors, sessions)

    with open(output_path, 'wb') as f:
        pickle.dump(sessions_with_css_selectors, f)


if __name__ == '__main__':
    main()
