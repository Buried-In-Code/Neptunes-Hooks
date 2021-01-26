import logging
import threading
import time
from argparse import ArgumentParser, Namespace
from json.decoder import JSONDecodeError
from typing import Dict, Any, List

from requests import post
from requests.exceptions import ConnectionError, HTTPError

from Logger import init_logger
from Teams import load_config, save_config, lookup_player

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
            game_number=load_config(testing)['Neptune\'s Pride']['Number'],
            code=load_config(testing)['Neptune\'s Pride']['Code']
        )
        LOGGER.debug(f"Neptune's Response: {np_response}")
        if np_response:
            if np_response['tick'] <= 0:
                new_players = []
                np_players = [player['alias'] for player in np_response['players'].values() if player['alias']]
                for new_player in np_players:
                    if not lookup_player(new_player, testing):
                        config['Players'].append({
                            'Alias': new_player,
                            'Name': None,
                            'Team': None
                        })
                        save_config(config, testing)
                        new_players.append(new_player)
                if new_players:
                    generate_new_players_card(new_players)
            elif np_response['tick'] > config['Neptune\'s Pride']['Last Tick'] or testing:
                generate_players_card(np_response, config, testing)
                generate_teams_card(np_response, config, testing)
                config['Neptune\'s Pride']['Last Tick'] = np_response['tick']
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
        LOGGER.debug(f"{player['alias']} - {lookup_player(player['alias'], testing).get('Name', '~')} - {lookup_player(player['alias'], testing).get('Team', '~')} - "
                     f"{player['total_stars']:,} - {player['total_strength']:,} - {player['total_fleets']:,}")
        alias_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': player['alias'] or '~',
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        name_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': lookup_player(player['alias'], testing).get('Name', '~'),
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        team_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': lookup_player(player['alias'], testing).get('Team', '~'),
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        stars_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_stars']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        ships_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_strength']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        fleets_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_fleets']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
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
        LOGGER.debug(f"{player['alias']} - {lookup_player(player['alias'], testing).get('Name', '~')} - {lookup_player(player['alias'], testing).get('Team', '~')} - "
                     f"{player['total_economy']:,} - {player['total_industry']:,} - {player['total_science']:,}")
        alias_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': player['alias'] or '~',
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        name_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': lookup_player(player['alias'], testing).get('Name', '~'),
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        team_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': lookup_player(player['alias'], testing).get('Team', '~'),
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        economy_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_economy']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        industry_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_industry']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
        })
        science_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{player['total_science']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': player['conceded'] == 0
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
    tick_rate = config['Neptune\'s Pride']['Tick Rate']
    post_stats([
        {
            'type': 'TextBlock',
            'size': 'Large',
            'weight': 'Bolder',
            'text': f"{data['name']} - Player Stats"
        },
        {
            'type': 'TextBlock',
            'text': f"Hello Players,\n\nWelcome to Turn {int(data['tick'] / tick_rate)}, here are the Players stats:",
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
    team_data = {}
    for player in config['Players']:
        player_data = next(iter([it for it in data['players'].values() if it['alias'] == player['Alias']]), None)
        if not data:
            continue
        if (player['Team'] or '~') in team_data:
            team_data[player['Team']]['Stars'] += player_data['total_stars']
            team_data[player['Team']]['Ships'] += player_data['total_strength']
            team_data[player['Team']]['Fleets'] += player_data['total_fleets']
            team_data[player['Team']]['Economy'] += player_data['total_economy']
            team_data[player['Team']]['Industry'] += player_data['total_industry']
            team_data[player['Team']]['Science'] += player_data['total_science']
            team_data[player['Team']]['Active'] = team_data[player['Team']]['Active'] or player_data['conceded'] == 0
        else:
            team_data[player['Team']] = {
                'Name': player['Team'] or '~',
                'Stars': player_data['total_stars'],
                'Ships': player_data['total_strength'],
                'Fleets': player_data['total_fleets'],
                'Economy': player_data['total_economy'],
                'Industry': player_data['total_industry'],
                'Science': player_data['total_science'],
                'Active': player_data['conceded'] == 0
            }
    if len([team for team in team_data.values() if team['Name'] != '~']) <= 0:
        return
    # endregion

    sorted_teams = sorted(team_data.values(),
                          key=lambda x: (x['Stars'], x['Ships'], x['Fleets'], x['Name']),
                          reverse=True)[:12]
    # region First card title
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
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
    for index, team in enumerate(sorted_teams):
        LOGGER.debug(f"{team['Name']} - {team['Stars']:,} - {team['Ships']:,} - {team['Fleets']:,}")
        name_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'text': team['Name'] or '~',
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': team['Active']
        })
        stars_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Stars']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': team['Active']
        })
        ships_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Ships']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': team['Active']
        })
        fleets_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Fleets']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': team['Active']
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

    sorted_teams = sorted(team_data.values(),
                          key=lambda x: (x['Economy'], x['Industry'], x['Science'], x['Name']),
                          reverse=True)[:12]
    # region Second card title
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    economy_column = [
        {
            'type': 'TextBlock',
            'text': 'Economy',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    industry_column = [
        {
            'type': 'TextBlock',
            'text': 'Industry',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
        }
    ]
    science_column = [
        {
            'type': 'TextBlock',
            'text': 'Science',
            'weight': 'Bolder',
            'fontType': 'monospace',
            'size': 'small'
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
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': team['Active']
        })
        economy_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Economy']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': team['Active']
        })
        industry_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Industry']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': team['Active']
        })
        science_column.append({
            'type': 'TextBlock',
            "separator": index == 0,
            'horizontalAlignment': 'right',
            'text': f"{team['Science']:,}",
            'fontType': 'monospace',
            'size': 'small',
            'isSubtle': team['Active']
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
    tick_rate = config['Neptune\'s Pride']['Tick Rate']
    post_stats([
        {
            'type': 'TextBlock',
            'size': 'Large',
            'weight': 'Bolder',
            'text': f"{data['name']} - Team Stats"
        },
        {
            'type': 'TextBlock',
            'text': f"Hello Teams,\n\nWelcome to Turn {int(data['tick'] / tick_rate)}, here are the Teams stats:",
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
