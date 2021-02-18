import logging
import threading
import time
from argparse import ArgumentParser, Namespace
from typing import List

from Hooks.common import parse_player_stats, parse_team_stats, request_data
from Hooks.config import is_teamed, load_config, save_config
from Hooks.discord import post_results as post_results_on_discord
from Hooks.teams import post_results as post_results_on_teams
from Logger import init_logger

LOGGER = logging.getLogger(__name__)

TIMEOUT = 100


def get_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('poll_rate', nargs='?', const=30, type=int, default=30)
    parser.add_argument('--hooks', choices=['teams', 'discord'], nargs='+', required=True)
    parser.add_argument('--testing', action='store_true')
    return parser.parse_args()


def main():
    try:
        args = get_arguments()
        poll_thread = threading.Thread(target=thread_func,
                                       args=(args.poll_rate, args.hooks, args.testing,),
                                       daemon=True)
        poll_thread.start()
        while poll_thread.is_alive():
            time.sleep(10)
    except BaseException:
        LOGGER.info(f"Stopping threads")


def thread_func(poll_rate: int, hooks: List[str], testing: bool = False):
    while True:
        config = load_config(testing)
        np_response = request_data(config)
        LOGGER.debug(f"Neptune's Response: {np_response}")
        if np_response:
            new_players = []
            np_players = [player['Username'] for player in np_response['Players'] if player['Username']]
            for new_player in np_players:
                if new_player not in config['Players'].keys():
                    config['Players'][new_player] = {
                        'Team': None
                    }
                    save_config(config, testing)
                    new_players.append(new_player)
            if np_response['Tick'] > config['Neptune\'s Pride']['Last Tick'] or testing:
                player_stats = parse_player_stats(np_response, config)
                LOGGER.debug(player_stats)

                team_stats = parse_team_stats(np_response, config) if is_teamed(config) else None
                LOGGER.debug(team_stats)

                turn = int(np_response['Tick'] / config['Neptune\'s Pride']['Tick Rate'])

                if 'teams' in hooks:
                    post_results_on_teams(player_stats, team_stats, turn, np_response['Title'], config)
                if 'discord' in hooks:
                    post_results_on_discord(player_stats, team_stats, turn, np_response['Title'], config)
                config['Neptune\'s Pride']['Last Tick'] = np_response['Tick']
                save_config(config, testing)
                LOGGER.info('Waiting for next turn...')
        else:
            break
        if not np_response['Active'] or testing:
            break
        time.sleep(poll_rate * 60)


if __name__ == '__main__':
    init_logger('Neptunes-Hooks')
    main()
