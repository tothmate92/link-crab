import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tests.test_app import generate_mock_app
import time
import session_manager
import reporting
import exercise_url
import gather_links
import csv_reader
import sys

from urllib.request import urlparse
import yaml
from datetime import datetime
import colorama

# Colorama init https://pypi.org/project/colorama/
colorama.init()
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

exit_value = 0


# CLI interface:
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Link-Crab: A link crawler and permission testing tool, written in Python")
    parser.add_argument("config_yaml_path", metavar='path', type=str,
                        help="Path to the config yaml file.")
    parser.add_argument("-t" ,"--test", action='store_true', help="wind up the default test application for testing")

    args = parser.parse_args()
    config_yaml_path = args.config_yaml_path

    # setup:
    print('----------------setup---------------------')

    if args.test:
        generate_mock_app()

    starting_time = datetime.now()
    config = {}
    with open(config_yaml_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    user = None
    try:
        user = config['user']
    except:
        pass
    session = session_manager.make_session(user)

    starting_url = None
    try:
        starting_url = config['starting_url']
    except:
        pass

    path_to_link_perms = None
    try:
        path_to_link_perms = config['path_to_link_perms']
    except:
        pass

    links = set()

    links.add(starting_url)

    # gathering:
    if starting_url:
        print('----------------gather links---------------------')
        checked_domain = urlparse(starting_url).netloc
        links.add(starting_url)
        links = gather_links.gather_links(session, links, checked_domain)

    # exercising:
        print('----------------Excercise links---------------------')
        link_db = []
        # remake the session, because crawling through the log-out link logs us out :D
        session = session_manager.make_session(user)
        for link in links:
            link_db.append(exercise_url.exercise_url(session, link))

        reporting.save_linkdb_to_csv(link_db, checked_domain)

        print('----------------REPORT: Excercised links---------------------')
        for link in link_db:
            print(f"[*] {link[0]} - {GREEN if link[1]==200 else RED} {link[1]} {RESET} - {GREEN if link[0]==link[4] else YELLOW} {link[4]} {RESET} - {link[2]} ms - accessible: {GREEN if link[3]==True else YELLOW} {link[3]} {RESET}")

    # permission checking:

    
    if path_to_link_perms:
        print('----------------permission checking---------------------')
        link_perm_db = []
        link_perms = csv_reader.read_link_perms(path_to_link_perms)
        checked_domain = urlparse(link_perms[0][0]).netloc
        session = session_manager.make_session(user)
        for link_perm in link_perms:
            outcome = (exercise_url.exercise_url(session, link_perm[0]))
            assertion_outcome = 'FAILED'
            if outcome[3] == link_perm[1]:
                assertion_outcome = 'PASSED'
            outcome = outcome + [link_perm[1]] + [assertion_outcome]
            link_perm_db.append(outcome)

        reporting.save_permdb_to_csv(link_perm_db, checked_domain)

        print('----------------REPORT: Checked permissions---------------------')
        for link in link_perm_db:
            if link[6] != 'PASSED':
                exit_value = 1
            print(f"[*] {link[0]} - {GREEN if link[1]==200 else RED} {link[1]} {RESET} - {GREEN if link[0]==link[4] else YELLOW} {link[4]} {RESET} - {link[2]} ms - accessible: {GREEN if link[3]==True else YELLOW} {link[3]} {RESET} - should-be?: {link[5]} - assert:{GREEN if link[6]== 'PASSED' else RED} {link[6]} {RESET}")

    # Exit:
    print(f"finished, exit:{exit_value}")
    sys.exit(exit_value)


