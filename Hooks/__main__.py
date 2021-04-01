import logging
import time
from argparse import ArgumentParser, Namespace

from Hooks.common import parse_player_stats, parse_team_stats, request_data
from Hooks.config import is_teamed, load_config, save_config
from Hooks.discord import post_results as post_results_on_discord
from Hooks.teams import post_results as post_results_on_teams
import PyLogger

LOGGER = logging.getLogger(__name__)

TIMEOUT = 100


def get_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('poll', nargs='?', const=30, type=int, default=30)
    parser.add_argument('--hooks', choices=['teams', 'discord'], nargs='+', required=True)
    parser.add_argument('--testing', action='store_true')
    return parser.parse_args()


def main():
    try:
        args = get_arguments()
        LOGGER.debug(args)
        config = load_config(args.testing)
        np_response = request_data(config)
        LOGGER.debug(f"Neptune's Response: {np_response}")
        while np_response and np_response['Active']:
            new_players = []
            np_players = [player['Username'] for player in np_response['Players'] if player['Username']]
            for new_player in np_players:
                if new_player not in config['Players'].keys():
                    config['Players'][new_player] = {
                        'Team': None
                    }
                    save_config(config, args.testing)
                    new_players.append(new_player)
            if np_response['Tick'] > config['Neptune\'s Pride']['Last Tick'] or args.testing:
                player_stats = parse_player_stats(np_response, config)
                LOGGER.debug(player_stats)

                team_stats = parse_team_stats(np_response, config) if is_teamed(config) else None
                LOGGER.debug(team_stats)

                turn = int(np_response['Tick'] / config['Neptune\'s Pride']['Tick Rate'])

                if 'teams' in args.hooks:
                    post_results_on_teams(player_stats, team_stats, turn, np_response['Title'], config)
                if 'discord' in args.hooks:
                    post_results_on_discord(player_stats, team_stats, turn, np_response['Title'], config)
                config['Neptune\'s Pride']['Last Tick'] = np_response['Tick']
                save_config(config, args.testing)
                LOGGER.info('Waiting for next turn...')
            if args.testing:
                break
            time.sleep(args.poll * 60)
            np_response = request_data(config)
            LOGGER.debug(f"Neptune's Response: {np_response}")
    except KeyboardInterrupt:
        LOGGER.info(f"Stopping script")


if __name__ == '__main__':
    PyLogger.init('Neptunes-Hooks')
    main()
