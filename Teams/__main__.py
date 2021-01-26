import logging
import threading
import time
from argparse import ArgumentParser, Namespace
from json.decoder import JSONDecodeError
from typing import Dict, Any, List

from requests import post
from requests.exceptions import ConnectionError, HTTPError

from Logger import init_logger
from Teams import load_config, save_config, lookup_player, lookup_team

LOGGER = logging.getLogger(__name__)

TIMEOUT = 100


def get_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('poll_rate', nargs='?', const=30, type=int, default=30)
    parser.add_argument('--testing', action='store_true')
    return parser.parse_args()


def main():
    try:
        args = get_arguments()
        poll_thread = threading.Thread(target=thread_func, args=(args.poll_rate, args.testing,), daemon=True)
        poll_thread.start()
        while poll_thread.is_alive():
            time.sleep(30)
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info('Received Keyboard Interrupt, stopping threads')


def thread_func(poll_rate: int, testing: bool = False):
    while True:
        config = load_config(testing)
        np_response = request_data(
            game_number=load_config(testing)['Game Number'],
            code=load_config(testing)['API Code']
        )
        LOGGER.debug(f"Neptune's Response: {np_response}")
        if np_response:
            if np_response['tick'] <= 0:
                new_players = []
                np_players = [player['alias'] for player in np_response['players'].values() if player['alias']]
                for new_player in np_players:
                    if new_player not in config['Players'].keys():
                        config['Players'][new_player] = None
                        save_config(config, testing)
                        new_players.append(new_player)
                if new_players:
                    generate_new_players_card(new_players)
            elif np_response['tick'] > config['Last Tick'] or testing:
                generate_players_card(np_response, config, testing)
                generate_teams_card(np_response, config, testing)
                config['Last Tick'] = np_response['tick']
                save_config(config, testing)
            else:
                LOGGER.info("No need to update Teams yet")
        else:
            break
        if np_response['game_over'] != 0 or testing:
            break
        time.sleep(poll_rate * 60)


def generate_new_players_card(players: List[str]):
    post_stats([
        {
            'type': 'TextBlock',
            'text': 'The following players have now joined the game:',
            'fontType': 'monospace'
        },
        {
            'type': 'TextBlock',
            'text': '\n\n'.join(players),
            'fontType': 'monospace'
        }
    ])


def generate_players_card(data: Dict[str, Any], config: Dict[str, Any], testing: bool = False):
    sorted_players = sorted(data['players'].values(),
                            key=lambda x: (x['total_stars'], x['total_strength'], x['total_fleets'], x['alias']),
                            reverse=True)[:12]

    # region First card title
    alias_column = [
        {
            'type': 'TextBlock',
            'text': 'Alias',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    team_column = [
        {
            'type': 'TextBlock',
            'text': 'Team',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    stars_column = [
        {
            'type': 'TextBlock',
            'text': 'Stars',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    ships_column = [
        {
            'type': 'TextBlock',
            'text': 'Ships',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    fleets_column = [
        {
            'type': 'TextBlock',
            'text': 'Fleets',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    # endregion
    # region First card data
    for index, player in enumerate(sorted_players):
        LOGGER.debug(f"{player['alias']} - {lookup_player(player['alias'])} - {lookup_team(player['alias'])} - "
                     f"{player['total_stars']:,} - {player['total_strength']:,} - {player['total_fleets']:,}")
        alias_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': player['alias'] or '~',
            'fontType': 'monospace',
            'size': 'small'
        })
        name_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': lookup_player(player['alias'] or '~') or '~',
            'fontType': 'monospace',
            'size': 'small'
        })
        team_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': lookup_team(player['alias'] or '~') or '~',
            'fontType': 'monospace',
            'size': 'small'
        })
        stars_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_stars']:,}",
            'fontType': 'monospace',
            'size': 'small'
        })
        ships_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_strength']:,}",
            'fontType': 'monospace',
            'size': 'small'
        })
        fleets_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_fleets']:,}",
            'fontType': 'monospace',
            'size': 'small'
        })
    # endregion
    first_card_columns = [
        {
            'type': 'Column',
            'items': alias_column,
            'width': 'stretch'
        },
        {
            'type': 'Column',
            'items': name_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': team_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': stars_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': ships_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': fleets_column,
            'width': 'auto'
        }
    ]

    sorted_players = sorted(data['players'].values(),
                            key=lambda x: (x['total_economy'], x['total_industry'], x['total_science'], x['alias']),
                            reverse=True)[:12]
    # region Second card title
    alias_column = [
        {
            'type': 'TextBlock',
            'text': 'Alias',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    team_column = [
        {
            'type': 'TextBlock',
            'text': 'Team',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    economy_column = [
        {
            'type': 'TextBlock',
            'text': 'Econ',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    industry_column = [
        {
            'type': 'TextBlock',
            'text': 'Indu',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    science_column = [
        {
            'type': 'TextBlock',
            'text': 'Scie',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    # endregion
    # region Second card data
    for index, player in enumerate(sorted_players):
        LOGGER.debug(f"{player['alias']} - {lookup_player(player['alias'])} - {lookup_team(player['alias'])} - "
                     f"{player['total_economy']:,} - {player['total_industry']:,} - {player['total_science']:,}")
        alias_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': player['alias'] or '~',
            'fontType': 'monospace',
            'size': 'small'
        })
        name_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': lookup_player(player['alias'] or '~') or '~',
            'fontType': 'monospace',
            'size': 'small'
        })
        team_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': lookup_team(player['alias'] or '~') or '~',
            'fontType': 'monospace',
            'size': 'small'
        })
        economy_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_economy']:,}",
            'fontType': 'monospace',
            'size': 'small'
        })
        industry_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_industry']:,}",
            'fontType': 'monospace',
            'size': 'small'
        })
        science_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_science']:,}",
            'fontType': 'monospace',
            'size': 'small'
        })
    # endregion
    second_card_columns = [
        {
            'type': 'Column',
            'items': alias_column,
            'width': 'stretch'
        },
        {
            'type': 'Column',
            'items': name_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': team_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': economy_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': industry_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': science_column,
            'width': 'auto'
        }
    ]
    post_stats([
        {
            'type': 'TextBlock',
            'size': 'Large',
            'weight': 'Bolder',
            'text': f"{data['name']} - Player Stats"
        },
        {
            'type': 'TextBlock',
            'text': f"Hello Players,\n\nWelcome to Turn {int(data['tick'] / config['Tick Rate'])}, here are the Players stats:",
            'wrap': True
        },
        {
            'type': 'ColumnSet',
            'columns': first_card_columns
        },
        {
            'type': 'TextBlock',
            'text': '\n\n',
            'wrap': True
        },
        {
            'type': 'ColumnSet',
            'columns': second_card_columns
        }
    ], testing)


def generate_teams_card(data: Dict[str, Any], config: Dict[str, Any], testing: bool = False):
    # region Calculate Team Stats
    team_data = []
    no_team = {
        'Name': '~',
        'Stars': 0,
        'Ships': 0,
        'Fleets': 0,
        'Economy': 0,
        'Industry': 0,
        'Science': 0,
        'Active': False
    }
    for name, members in config['Teams'].items():
        temp = {
            'Name': name,
            'Stars': 0,
            'Ships': 0,
            'Fleets': 0,
            'Economy': 0,
            'Industry': 0,
            'Science': 0,
            'Active': False
        }
        for member in members:
            player = next(iter([it for it in data['players'].values() if it['alias'] == member]), None)
            if player:
                temp['Stars'] += player['total_stars']
                temp['Ships'] += player['total_strength']
                temp['Fleets'] += player['total_fleets']
                temp['Economy'] += player['total_economy']
                temp['Industry'] += player['total_industry']
                temp['Science'] += player['total_science']
                temp['Active'] = temp['Active'] or player['conceded'] == 0
        team_data.append(temp)
    teamless_count = 0
    for player in data['players'].values():
        if not lookup_team(player['alias']):
            no_team['Stars'] += player['total_stars']
            no_team['Ships'] += player['total_strength']
            no_team['Fleets'] += player['total_fleets']
            no_team['Economy'] += player['total_economy']
            no_team['Industry'] += player['total_industry']
            no_team['Science'] += player['total_science']
            no_team['Active'] = no_team['Active'] or player['conceded'] == 0
            teamless_count += 1
    if teamless_count > 0:
        team_data.append(no_team)
    if teamless_count >= len(data['players'].values()):
        return
    # endregion

    sorted_teams = sorted(team_data,
                          key=lambda x: (x['Stars'], x['Ships'], x['Fleets'], x['Name']),
                          reverse=True)[:12]
    # region First card title
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder',
            'fontType': 'monospace'
        }
    ]
    stars_column = [
        {
            'type': 'TextBlock',
            'text': 'Stars',
            'weight': 'Bolder',
            'fontType': 'monospace'
        }
    ]
    ships_column = [
        {
            'type': 'TextBlock',
            'text': 'Ships',
            'weight': 'Bolder',
            'fontType': 'monospace'
        }
    ]
    fleets_column = [
        {
            'type': 'TextBlock',
            'text': 'Fleets',
            'weight': 'Bolder',
            'fontType': 'monospace'
        }
    ]
    # endregion
    # region First card data
    for index, team in enumerate(sorted_teams):
        LOGGER.debug(f"{team['Name']} - {team['Stars']:,} - {team['Ships']:,} - {team['Fleets']:,}")
        name_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': team['Name'] or '~',
            'fontType': 'monospace'
        })
        stars_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Stars']:,}",
            'fontType': 'monospace'
        })
        ships_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Ships']:,}",
            'fontType': 'monospace'
        })
        fleets_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Fleets']:,}",
            'fontType': 'monospace'
        })
    # endregion
    first_card_columns = [
        {
            'type': 'Column',
            'items': name_column,
            'width': 'stretch'
        },
        {
            'type': 'Column',
            'items': stars_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': ships_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': fleets_column,
            'width': 'auto'
        }
    ]

    sorted_teams = sorted(team_data,
                          key=lambda x: (x['Economy'], x['Industry'], x['Science'], x['Name']),
                          reverse=True)[:12]
    # region Second card title
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder',
            'fontType': 'monospace'
        }
    ]
    economy_column = [
        {
            'type': 'TextBlock',
            'text': 'Economy',
            'weight': 'Bolder',
            'fontType': 'monospace'
        }
    ]
    industry_column = [
        {
            'type': 'TextBlock',
            'text': 'Industry',
            'weight': 'Bolder',
            'fontType': 'monospace'
        }
    ]
    science_column = [
        {
            'type': 'TextBlock',
            'text': 'Science',
            'weight': 'Bolder',
            'fontType': 'monospace'
        }
    ]
    # endregion
    # region Second card data
    for index, team in enumerate(sorted_teams):
        LOGGER.debug(f"{team['Name']} - {team['Economy']:,} - {team['Industry']:,} - {team['Science']:,}")
        name_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': team['Name'] or '~',
            'fontType': 'monospace'
        })
        economy_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Economy']:,}",
            'fontType': 'monospace'
        })
        industry_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Industry']:,}",
            'fontType': 'monospace'
        })
        science_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Science']:,}",
            'fontType': 'monospace'
        })
    # endregion
    second_card_columns = [
        {
            'type': 'Column',
            'items': name_column,
            'width': 'stretch'
        },
        {
            'type': 'Column',
            'items': economy_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': industry_column,
            'width': 'auto'
        },
        {
            'type': 'Column',
            'items': science_column,
            'width': 'auto'
        }
    ]
    post_stats([
        {
            'type': 'TextBlock',
            'size': 'Large',
            'weight': 'Bolder',
            'text': f"{data['name']} - Team Stats"
        },
        {
            'type': 'TextBlock',
            'text': f"Hello Teams,\n\nWelcome to Turn {int(data['tick'] / config['Tick Rate'])}, here are the Teams stats:",
            'wrap': True
        },
        {
            'type': 'ColumnSet',
            'columns': first_card_columns
        },
        {
            'type': 'TextBlock',
            'text': "\n\n"
        },
        {
            'type': 'ColumnSet',
            'columns': second_card_columns
        }
    ], testing)


def request_data(game_number: int, code: str) -> Dict[str, Any]:
    LOGGER.debug(f"{game_number}, {code}")
    try:
        response = post(url='https://np.ironhelmet.com/api', headers={
            'User-Agent': 'Neptune\'s Hooks'
        }, timeout=TIMEOUT, data={
            'api_version': '0.1',
            'game_number': game_number,
            'code': code
        })
        response.raise_for_status()
        LOGGER.info(f"{response.status_code}: POST - {response.url}")
        try:
            return response.json()['scanning_data']
        except JSONDecodeError:
            LOGGER.critical('Unable to parse the response message')
            LOGGER.critical(f"Response: {response.text}")
            return {}
        except KeyError:
            LOGGER.critical('Unable to parse the response message')
            LOGGER.critical(f"Response: {response.text}")
            return {}
    except HTTPError as err:
        LOGGER.error(err)
        return {}
    except ConnectionError:
        LOGGER.critical(f"Unable to access `https://np.ironhelmet.com/api`")
        return {}


def post_stats(body: List[Dict[str, Any]], testing: bool = False):
    try:
        response = post(url=load_config(testing)['Teams Webhook'], headers={
            'Content-Type': 'application/json; charset=UTF-8',
            'User-Agent': 'Neptune\'s Hooks'
        }, timeout=TIMEOUT, json={
            'type': 'message',
            'attachments': [
                {
                    'contentType': 'application/vnd.microsoft.card.adaptive',
                    'contentUrl': None,
                    'content': {
                        '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                        'type': 'AdaptiveCard',
                        'version': '1.2',
                        'body': body
                    }
                }
            ]
        })
        response.raise_for_status()
        LOGGER.info(f"{response.status_code}: POST - {response.url}")
    except HTTPError as err:
        LOGGER.error(err)
    except ConnectionError:
        LOGGER.critical(f"Unable to access `{load_config(testing)['Teams Webhook']}`")


if __name__ == '__main__':
    init_logger('Neptunes-Hooks')
    main()
