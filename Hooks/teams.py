import logging
from typing import Any, Dict, List, Optional, Tuple

from requests import post
from requests.exceptions import ConnectionError, HTTPError

LOGGER = logging.getLogger(__name__)
TIMEOUT = 100


def post_results(player_results: Tuple[Dict[str, List[str]], List[str]],
                 team_results: Optional[Tuple[Dict[str, List[str]], List[str]]], turn: int, game_name: str,
                 config: Dict[str, Any]):
    post_player_results(leaders=player_results[0], overall=player_results[1], turn=turn, game_name=game_name,
                        config=config)
    if team_results:
        post_team_results(leaders=team_results[0], overall=team_results[1], turn=turn, game_name=game_name,
                          config=config)


def post_player_results(leaders: Dict[str, List[str]], overall: List[str], turn: int, game_name: str,
                        config: Dict[str, Any]):
    sections = [{
        'activityTitle': f"Welcome to Turn {turn:02}",
        'activitySubtitle': 'I\'ve crunched the numbers and here are the top Players for each stat.'
    }, {
        'facts': [{
            'name': key,
            'value': ', '.join(sorted(value))
        } for key, value in leaders.items()]
    }, {
        'text': f"Looking at the above table it appears everyone should keep a close eye on **{' and '.join(overall)}** as they seem to be all over this leaderboard"
    }]

    post_stats({
        '@type': 'MessageCard',
        '@context': 'http://schema.org/extensions',
        'title': f"{game_name} - Player Stats",
        'sections': sections
    }, config)


def post_team_results(leaders: Dict[str, List[str]], overall: List[str], turn: int, game_name: str,
                      config: Dict[str, Any]):
    sections = [{
        'activityTitle': f"Welcome to Turn {turn:02}",
        'activitySubtitle': 'I\'ve crunched the numbers and here are the top Teams for each stat.'
    }, {
        'facts': [{
            'name': key,
            'value': ', '.join(sorted(value))
        } for key, value in leaders.items()]
    }, {
        'text': f"Looking at the above table it appears everyone should keep a close eye on **{' and '.join(overall)}** as they seem to be all over this leaderboard"
    }]

    post_stats({
        '@type': 'MessageCard',
        '@context': 'http://schema.org/extensions',
        'title': f"{game_name} - Team Stats",
        'sections': sections
    }, config)


def post_stats(content: Dict[str, Any], config: Dict[str, Any]):
    try:
        if not config['Hooks']['Teams']:
            raise ConnectionError
        response = post(url=config['Hooks']['Teams'], headers={
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
        LOGGER.critical(f"Unable to access `{config['Hooks']['Teams']}`")
