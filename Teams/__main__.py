import logging
import threading
import time
from json.decoder import JSONDecodeError
from typing import Dict, Any, List

from requests import post
from requests.exceptions import ConnectionError, HTTPError

from Logger import init_logger
from Teams import CONFIG, save_config, lookup_player, lookup_team

LOGGER = logging.getLogger(__name__)

TIMEOUT = 100


def main():
    try:
        poll_thread = threading.Thread(target=thread_func, daemon=True)
        poll_thread.start()
        while True:
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info('Received Keyboard Interrupt, stopping threads')


def thread_func():
    while True:
        np_response = np_request(
            game_number=CONFIG['Game Number'],
            code=CONFIG['API Code']
        )
        LOGGER.debug(f"Neptune's Response: {np_response}")
        if np_response and np_response['tick'] > CONFIG['Last Tick']:
            generate_players_card(np_response)
            generate_teams_card(np_response)
            CONFIG['Last Tick'] = np_response['tick']
            save_config()
        else:
            LOGGER.info("No need to update Teams yet")
        time.sleep(30 * 60)


def generate_players_card(data: Dict[str, Any]):
    sorted_players = sorted(data['players'].values(),
                            key=lambda x: (x['total_stars'], x['total_strength'], x['alias']),
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
            'text': player['total_stars']
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
            'text': player['total_strength']
        } for player in sorted_players
    ])
    # endregion
    # region Active Column
    active_column = [
        {
            'type': 'TextBlock',
            'text': 'Active',
            'weight': 'Bolder'
        }
    ]
    active_column.extend([
        {
            'type': 'TextBlock',
            'text': player['conceded'] == 0
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
            'text': f"Hello Players,\n\nWelcome to Turn {int(data['tick'] / CONFIG['Tick Rate'])}, here are the Players stats:"
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
                    'items': active_column,
                    'width': 'auto'
                }
            ]
        },
        {
            'type': 'TextBlock',
            'text': f"Looks like {sorted_players[0]['alias']} has the lead, with {sorted_players[1]['alias']} and {sorted_players[2]['alias']} on their heels.",
            'wrap': True
        }
    ])


def generate_teams_card(data: Dict[str, Any]):
    # region Calculate Team Stats
    team_data = []
    no_team = {
        'Name': '~',
        'Stars': 0,
        'Ships': 0,
        'Active': False
    }
    for name, members in CONFIG['Teams'].items():
        temp = {
            'Name': name,
            'Stars': 0,
            'Ships': 0,
            'Active': False
        }
        for member in members:
            player = next(iter([it for it in data['players'].values() if it['alias'] == member]), None)
            if player:
                temp['Stars'] += player['total_stars']
                temp['Ships'] += player['total_strength']
                temp['Active'] = temp['Active'] or player['conceded'] == 0
        team_data.append(temp)
    teamless_count = 0
    for player in data['players'].values():
        if not lookup_team(player['alias']):
            no_team['Stars'] += player['total_stars']
            no_team['Ships'] += player['total_strength']
            no_team['Active'] = no_team['Active'] or player['conceded'] == 0
            teamless_count += 1
    if teamless_count > 0:
        team_data.append(no_team)
    if teamless_count >= len(data['players'].values()):
        return
    # endregion
    sorted_teams = sorted(team_data, key=lambda x: (x['Stars'], x['Ships'], x['Name']), reverse=True)[:12]
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
            'text': team['Stars']
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
            'text': team['Ships']
        } for team in sorted_teams
    ])
    # endregion
    # region Active Column
    active_column = [
        {
            'type': 'TextBlock',
            'text': 'Active',
            'weight': 'Bolder'
        }
    ]
    active_column.extend([
        {
            'type': 'TextBlock',
            'text': team['Active']
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
            'text': f"Hello Teams,\n\nWelcome to Turn {int(data['tick'] / CONFIG['Tick Rate'])}, here are the Teams stats:"
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
                    'items': active_column,
                    'width': 'auto'
                }
            ]
        },
        {
            'type': 'TextBlock',
            'text': f"Looks like {sorted_teams[0]['Name']} has the lead, with {sorted_teams[1]['Name']} and {sorted_teams[2]['Name']} on their heels.",
            'wrap': True
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
