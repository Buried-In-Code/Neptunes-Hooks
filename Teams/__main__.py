import logging
import threading
import time
from argparse import ArgumentParser, Namespace
from json.decoder import JSONDecodeError
from typing import Dict, Any, List

from requests import post
from requests.exceptions import ConnectionError, HTTPError

from Logger import init_logger
from Teams import CONFIG, save_config, lookup_player, lookup_team

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


def thread_func(poll_rate: int, testing: bool):
    while True:
        np_response = np_request(
            game_number=CONFIG['Game Number'],
            code=CONFIG['API Code']
        )
        LOGGER.debug(f"Neptune's Response: {np_response}")
        if np_response:
            if np_response['tick'] > CONFIG['Last Tick'] or testing:
                generate_players_card(np_response)
                generate_teams_card(np_response)
                CONFIG['Last Tick'] = np_response['tick']
                save_config()
            else:
                LOGGER.info("No need to update Teams yet")
        else:
            break
        if np_response['game_over'] != 0 or testing:
            break
        time.sleep(poll_rate * 60)


def generate_players_card(data: Dict[str, Any]):
    sorted_players = sorted(data['players'].values(),
                            key=lambda x: (x['total_stars'], x['total_strength'], x['total_fleets'], x['alias']),
                            reverse=True)[:12]
    # region Alias Column
    alias_column = [
        {
            'type': 'TextBlock',
            'text': 'Alias',
            'weight': 'Bolder'
        }
    ]
    alias_column.extend([
        {
            'type': 'TextBlock',
            'text': player['alias'] or '~'
        } for player in sorted_players
    ])
    # endregion
    # region Name Column
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder'
        }
    ]
    name_column.extend([
        {
            'type': 'TextBlock',
            'text': lookup_player(player['alias'] or '~') or '~'
        } for player in sorted_players
    ])
    # endregion
    # region Team Column
    team_column = [
        {
            'type': 'TextBlock',
            'text': 'Team',
            'weight': 'Bolder'
        }
    ]
    team_column.extend([
        {
            'type': 'TextBlock',
            'text': lookup_team(player['alias'] or '~') or '~'
        } for player in sorted_players
    ])
    # endregion
    # region Stars Column
    stars_column = [
        {
            'type': 'TextBlock',
            'text': 'Stars',
            'weight': 'Bolder'
        }
    ]
    stars_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{player['total_stars']:,}"
        } for player in sorted_players
    ])
    # endregion
    # region Ships Column
    ships_column = [
        {
            'type': 'TextBlock',
            'text': 'Ships',
            'weight': 'Bolder'
        }
    ]
    ships_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{player['total_strength']:,}"
        } for player in sorted_players
    ])
    # endregion
    # region Carriers Column
    carriers_column = [
        {
            'type': 'TextBlock',
            'text': 'Carriers',
            'weight': 'Bolder'
        }
    ]
    carriers_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{player['total_fleets']:,}"
        } for player in sorted_players
    ])
    # endregion
    sorted_players = sorted(data['players'].values(),
                            key=lambda x: (x['total_economy'], x['total_industry'], x['total_science'], x['alias']),
                            reverse=True)[:12]
    # region Alias Column
    alias_column = [
        {
            'type': 'TextBlock',
            'text': 'Alias',
            'weight': 'Bolder'
        }
    ]
    alias_column.extend([
        {
            'type': 'TextBlock',
            'text': player['alias'] or '~'
        } for player in sorted_players
    ])
    # endregion
    # region Name Column
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder'
        }
    ]
    name_column.extend([
        {
            'type': 'TextBlock',
            'text': lookup_player(player['alias'] or '~') or '~'
        } for player in sorted_players
    ])
    # endregion
    # region Team Column
    team_column = [
        {
            'type': 'TextBlock',
            'text': 'Team',
            'weight': 'Bolder'
        }
    ]
    team_column.extend([
        {
            'type': 'TextBlock',
            'text': lookup_team(player['alias'] or '~') or '~'
        } for player in sorted_players
    ])
    # endregion
    # region Economy Column
    economy_column = [
        {
            'type': 'TextBlock',
            'text': 'Eco',
            'weight': 'Bolder'
        }
    ]
    economy_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{player['total_economy']:,}"
        } for player in sorted_players
    ])
    # endregion
    # region Industry Column
    industry_column = [
        {
            'type': 'TextBlock',
            'text': 'Ind',
            'weight': 'Bolder'
        }
    ]
    industry_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{player['total_industry']:,}"
        } for player in sorted_players
    ])
    # endregion
    # region Science Column
    science_column = [
        {
            'type': 'TextBlock',
            'text': 'Sci',
            'weight': 'Bolder'
        }
    ]
    science_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{player['total_science']:,}"
        } for player in sorted_players
    ])
    # endregion
    teams_request([
        {
            'type': 'TextBlock',
            'size': 'Large',
            'weight': 'Bolder',
            'text': f"{data['name']} - Player Stats"
        },
        {
            'type': 'TextBlock',
            'text': f"Hello Players,\n\nWelcome to Turn {int(data['tick'] / CONFIG['Tick Rate'])}, here are the Players stats:",
            'wrap': True
        },
        {
            'type': 'ColumnSet',
            'columns': [
                {
                    'type': 'Column',
                    'items': alias_column,
                    'width': 'stretch'
                },
                {
                    'type': 'Column',
                    'items': name_column,
                    'width': 'stretch'
                },
                {
                    'type': 'Column',
                    'items': team_column,
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
                    'items': carriers_column,
                    'width': 'auto'
                }
            ]
        },
        {
            'type': 'TextBlock',
            'text': '\n\n',
            'wrap': True
        },
        {
            'type': 'ColumnSet',
            'columns': [
                {
                    'type': 'Column',
                    'items': alias_column,
                    'width': 'stretch'
                },
                {
                    'type': 'Column',
                    'items': name_column,
                    'width': 'stretch'
                },
                {
                    'type': 'Column',
                    'items': team_column,
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
        }
    ])


def generate_teams_card(data: Dict[str, Any]):
    # region Calculate Team Stats
    team_data = []
    no_team = {
        'Name': '~',
        'Stars': 0,
        'Ships': 0,
        'Carriers': 0,
        'Economy': 0,
        'Industry': 0,
        'Science': 0,
        'Active': False
    }
    for name, members in CONFIG['Teams'].items():
        temp = {
            'Name': name,
            'Stars': 0,
            'Ships': 0,
            'Carriers': 0,
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
                temp['Carriers'] += player['total_fleets']
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
            no_team['Carriers'] += player['total_fleets']
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
                          key=lambda x: (x['Stars'], x['Ships'], x['Carriers'], x['Name']),
                          reverse=True)[:12]
    # region Name Column
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder'
        }
    ]
    name_column.extend([
        {
            'type': 'TextBlock',
            'text': team['Name'] or '~'
        } for team in sorted_teams
    ])
    # endregion
    # region Stars Column
    stars_column = [
        {
            'type': 'TextBlock',
            'text': 'Stars',
            'weight': 'Bolder'
        }
    ]
    stars_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{team['Stars']:,}"
        } for team in sorted_teams
    ])
    # endregion
    # region Ships Column
    ships_column = [
        {
            'type': 'TextBlock',
            'text': 'Ships',
            'weight': 'Bolder'
        }
    ]
    ships_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{team['Ships']:,}"
        } for team in sorted_teams
    ])
    # endregion
    # region Carrier Column
    carrier_column = [
        {
            'type': 'TextBlock',
            'text': 'Carriers',
            'weight': 'Bolder'
        }
    ]
    carrier_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{team['Carriers']:,}"
        } for team in sorted_teams
    ])
    # endregion
    sorted_teams = sorted(team_data,
                          key=lambda x: (x['Economy'], x['Industry'], x['Science'], x['Name']),
                          reverse=True)[:12]
    # region Name Column
    name_column = [
        {
            'type': 'TextBlock',
            'text': 'Name',
            'weight': 'Bolder'
        }
    ]
    name_column.extend([
        {
            'type': 'TextBlock',
            'text': team['Name'] or '~'
        } for team in sorted_teams
    ])
    # endregion
    # region Economy Column
    economy_column = [
        {
            'type': 'TextBlock',
            'text': 'Eco',
            'weight': 'Bolder'
        }
    ]
    economy_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{team['Economy']:,}"
        } for team in sorted_teams
    ])
    # endregion
    # region Industry Column
    industry_column = [
        {
            'type': 'TextBlock',
            'text': 'Ind',
            'weight': 'Bolder'
        }
    ]
    industry_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{team['Industry']:,}"
        } for team in sorted_teams
    ])
    # endregion
    # region Science Column
    science_column = [
        {
            'type': 'TextBlock',
            'text': 'Sci',
            'weight': 'Bolder'
        }
    ]
    science_column.extend([
        {
            'type': 'TextBlock',
            'text': f"{team['Science']:,}"
        } for team in sorted_teams
    ])
    # endregion
    teams_request([
        {
            'type': 'TextBlock',
            'size': 'Large',
            'weight': 'Bolder',
            'text': f"{data['name']} - Team Stats"
        },
        {
            'type': 'TextBlock',
            'text': f"Hello Teams,\n\nWelcome to Turn {int(data['tick'] / CONFIG['Tick Rate'])}, here are the Teams stats:",
            'wrap': True
        },
        {
            'type': 'ColumnSet',
            'columns': [
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
                    'items': carrier_column,
                    'width': 'auto'
                }
            ]
        },
        {
            'type': 'TextBlock',
            'text': "\n\n"
        },
        {
            'type': 'ColumnSet',
            'columns': [
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
        }
    ])


def np_request(game_number: int, code: str) -> Dict[str, Any]:
    try:
        response = post(url='https://np.ironhelmet.com/api', timeout=TIMEOUT, data={
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


def teams_request(body: List[Dict[str, Any]]):
    request_body = {
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
    }
    try:
        response = post(url=CONFIG['Teams Webhook'], headers={
            'Content-Type': 'application/json'
        }, timeout=TIMEOUT, json=request_body)
        response.raise_for_status()
        LOGGER.info(f"{response.status_code}: POST - {response.url}")
    except HTTPError as err:
        LOGGER.error(err)
    except ConnectionError:
        LOGGER.critical(f"Unable to access `{CONFIG['Teams Webhook']}`")


if __name__ == '__main__':
    init_logger('Neptunes-Hooks')
    main()
