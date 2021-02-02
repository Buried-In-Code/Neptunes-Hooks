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
            # region New Player Notification
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
                generate_new_players_card(new_players, testing)
            # endregion
            if np_response['tick'] > config['Neptune\'s Pride']['Last Tick'] or testing:
                generate_top_players(np_response, config, testing)
                generate_top_teams(np_response, config, testing)
                # generate_players_card(np_response, config, testing)
                # generate_teams_card(np_response, config, testing)
                config['Neptune\'s Pride']['Last Tick'] = np_response['tick']
                save_config(config, testing)
            else:
                LOGGER.info("No need to update Teams yet")
        else:
            break
        if np_response['game_over'] != 0 or testing:
            break
        time.sleep(poll_rate * 60)


def generate_new_players_card(players: List[str], testing: bool = False):
    post_stats({
        '@type': 'MessageCard',
        '@context': 'http://schema.org/extensions',
        'title': 'Welcome New Players',
        'sections': [{
            'activityTitle': 'The following players have now joined the game:'
        }, {
            'text': '\n\n - '.join(sorted(players))
        }]
    }, testing)


def generate_top_players(data: Dict[str, Any], config: Dict[str, Any], testing: bool = False):
    # region Player Stats
    title_fields = ['Stars', 'Ships', 'Economy', '$/Turn', 'Industry', 'Ships/Turn', 'Science', 'Scanning',
                    'Hyperspace Range', 'Terraforming', 'Experimentation', 'Weapons', 'Banking', 'Manufacturing']
    player_fields = ['total_stars', 'total_strength', 'total_economy', '$/Turn', 'total_industry', 'Ships/Turn',
                     'total_science', 'scanning', 'propulsion', 'terraforming', 'research', 'weapons', 'banking',
                     'manufacturing']
    player_facts = {}
    for index, field in enumerate(player_fields):
        max_value = -1
        max_players = []
        for player in data['players'].values():
            if '/Turn' in field:
                value = player['total_economy'] * 10.0 + player['tech']['banking']['level'] * 75.0 \
                    if field.startswith('$') else \
                    player['total_industry'] * (player['tech']['manufacturing']['level'] + 5.0) / 2.0
            else:
                value = player[field] if field.startswith("total_") else player['tech'][field]['level']
            if value > max_value:
                max_value = value
                max_players = [player]
            elif value == max_value:
                max_players.append(player)
        title = f"{title_fields[index]} ({max_value:,})" if field.startswith('total') or '/Turn' in field else \
            f"{title_fields[index]} (Lvl {max_value:,})"
        player_facts[title] = [f"{x['alias']} [{lookup_player(x['alias'], testing).get('Name', None) or '~'}]"
                               for x in max_players]
    # endregion

    # region Top Player/s
    player_count = {}
    for key, value in player_facts.items():
        for player in value:
            if player in player_count:
                player_count[player] += 1
            else:
                player_count[player] = 1
    LOGGER.debug(f"Leading Count: {player_count}")
    leading = []
    max_count = -1
    for player, count in player_count.items():
        if count > max_count:
            leading = [player]
            max_count = count
        elif count == max_count:
            leading.append(player)
    LOGGER.debug(f"Leader: {leading}") \
        # endregion

    # region Output
    tick_rate = config['Neptune\'s Pride']['Tick Rate']
    sections = [{
        'activityTitle': f"Welcome to turn {int(data['tick'] / tick_rate)}",
        'activitySubtitle': 'I\'ve crunched the numbers and here are the top Players for each stat.'
    }, {
        'facts': [{
            'name': key,
            'value': ', '.join(sorted(value))
        } for key, value in player_facts.items()]
    }, {
        'text': f"Looking at the above table it appears everyone should keep a close eye on **{' and '.join(leading)}** as they seem to be all over this leaderboard"
    }]

    post_stats({
        '@type': 'MessageCard',
        '@context': 'http://schema.org/extensions',
        'title': f"{data['name']} - Player Stats",
        'sections': sections
    }, testing)
    # endregion


def generate_top_teams(data: Dict[str, Any], config: Dict[str, Any], testing: bool = False):
    # region Generate teams
    team_data = {}
    for player in config['Players']:
        player_data = next(iter([it for it in data['players'].values() if it['alias'] == player['Alias']]), None)
        if not player_data:
            continue
        if (player['Team'] or '~') in team_data:
            team_data[player['Team']]['Stars'] += player_data['total_stars']
            team_data[player['Team']]['Ships'] += player_data['total_strength']
            team_data[player['Team']]['Fleets'] += player_data['total_fleets']
            team_data[player['Team']]['Economy'] += player_data['total_economy']
            team_data[player['Team']]['Industry'] += player_data['total_industry']
            team_data[player['Team']]['Science'] += player_data['total_science']
            team_data[player['Team']]['Scanning'] = max(player_data['tech']['scanning']['level'],
                                                        team_data[player['Team']]['Scanning'])
            team_data[player['Team']]['Hyperspace Range'] = max(player_data['tech']['propulsion']['level'],
                                                                team_data[player['Team']]['Hyperspace Range'])
            team_data[player['Team']]['Terraforming'] = max(player_data['tech']['terraforming']['level'],
                                                            team_data[player['Team']]['Terraforming'])
            team_data[player['Team']]['Experimentation'] = max(player_data['tech']['research']['level'],
                                                               team_data[player['Team']]['Experimentation'])
            team_data[player['Team']]['Weapons'] = max(player_data['tech']['weapons']['level'],
                                                       team_data[player['Team']]['Weapons'])
            team_data[player['Team']]['Banking'] = max(player_data['tech']['banking']['level'],
                                                       team_data[player['Team']]['Banking'])
            team_data[player['Team']]['Manufacturing'] = max(player_data['tech']['manufacturing']['level'],
                                                             team_data[player['Team']]['Manufacturing'])
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
                'Scanning': player_data['tech']['scanning']['level'],
                'Hyperspace Range': player_data['tech']['propulsion']['level'],
                'Terraforming': player_data['tech']['terraforming']['level'],
                'Experimentation': player_data['tech']['research']['level'],
                'Weapons': player_data['tech']['weapons']['level'],
                'Banking': player_data['tech']['banking']['level'],
                'Manufacturing': player_data['tech']['manufacturing']['level'],
                'Active': player_data['conceded'] == 0
            }
    if len([team for team in team_data.values() if team['Name'] != '~']) <= 0:
        return
    # endregion

    # region Teams Stats
    team_fields = ['Stars', 'Ships', 'Economy', '$/Turn', 'Industry', 'Ships/Turn', 'Science', 'Scanning',
                   'Hyperspace Range', 'Terraforming', 'Experimentation', 'Weapons', 'Banking', 'Manufacturing']
    team_facts = {}
    for index, field in enumerate(team_fields):
        max_value = -1
        max_teams = []
        for team in team_data.values():
            if '/Turn' in field:
                value = team['Economy'] * 10.0 + team['Banking'] * 75.0 if field.startswith('$') else \
                    team['Industry'] * (team['Manufacturing'] + 5.0) / 2.0
            else:
                value = team[field]
            if value > max_value:
                max_value = value
                max_teams = [team]
            elif value == max_value:
                max_teams.append(team)
        title = f"{field} ({max_value:,})" if index < 7 else f"{field} (Lvl {max_value:,})"
        team_facts[title] = [x['Name'] for x in max_teams]
    # endregion

    # region Top Team/s
    team_count = {}
    for key, value in team_facts.items():
        for player in value:
            if player in team_count:
                team_count[player] += 1
            else:
                team_count[player] = 1
    LOGGER.debug(f"Leading Count: {team_count}")
    leading = []
    max_count = -1
    for team, count in team_count.items():
        if count > max_count:
            leading = [team]
            max_count = count
        elif count == max_count:
            leading.append(team)
    LOGGER.debug(f"Leader: {leading}")
    # endregion

    # region Output
    tick_rate = config['Neptune\'s Pride']['Tick Rate']
    sections = [{
        'activityTitle': f"Welcome to turn {int(data['tick'] / tick_rate)}",
        'activitySubtitle': f"I've crunched the numbers and here are the top Teams for each stat."
    }, {
        'facts': [{
            'name': key,
            'value': ', '.join(sorted(value))
        } for key, value in team_facts.items()]
    }, {
        'text': f"Looking at the above table it appears everyone should keep a close eye on **{' and '.join(leading)}** as they seem to be all over this leaderboard"
    }]

    post_stats({
        '@type': 'MessageCard',
        '@context': 'http://schema.org/extensions',
        'title': f"{data['name']} - Team Stats",
        'sections': sections
    }, testing)
    # endregion


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


def post_stats(content: Dict[str, Any], testing: bool = False):
    try:
        response = post(url=load_config(testing)['Teams Webhook'], headers={
            'Content-Type': 'application/json; charset=UTF-8',
            'User-Agent': 'Neptune\'s Hooks'
        }, timeout=TIMEOUT, json={
            'type': 'message',
            'attachments': [{
                'contentType': 'application/vnd.microsoft.teams.card.o365connector',
                'content': content
            }]
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
