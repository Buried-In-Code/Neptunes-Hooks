import logging
from typing import Any, Dict, List, Optional, Tuple

from requests import post
from requests.exceptions import ConnectionError, HTTPError

from neptunes_hooks.settings import WebhookConfig
from neptunes_hooks.utils import HEADERS, TIMEOUT

LOGGER = logging.getLogger(__name__)


def push_data(
    player_stats: Tuple[Dict[str, List[str]], List[str]],
    team_stats: Optional[Tuple[Dict[str, List[str]], List[str]]],
    turn: int,
    game_name: str,
    webhook: WebhookConfig,
):
    player_stats = __format_player_stats(
        leaders=player_stats[0], overall=player_stats[1], turn=turn, game_name=game_name
    )
    __post_stats(content=player_stats, webhook=webhook)

    if team_stats:
        team_stats = __format_team_stats(leaders=team_stats[0], overall=team_stats[1], turn=turn, game_name=game_name)
        __post_stats(content=team_stats, webhook=webhook)


def __format_player_stats(
    leaders: Dict[str, List[str]], overall: List[str], turn: int, game_name: str
) -> Dict[str, Any]:
    sections = [
        {
            "activityTitle": f"Welcome to Turn {turn:02}",
            "activitySubtitle": "I've crunched the numbers and here are the top Players for each stat.",
        },
        {"facts": [{"name": key, "value": ", ".join(sorted(value))} for key, value in leaders.items()]},
        {
            "text": "Looking at the above table it appears everyone should keep a close eye on "
            f"**{' and '.join(overall)}** as they seem to be all over this leaderboard"
        },
    ]

    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "title": f"{game_name} - Player Stats",
        "sections": sections,
    }


def __format_team_stats(leaders: Dict[str, List[str]], overall: List[str], turn: int, game_name: str) -> Dict[str, Any]:
    sections = [
        {
            "activityTitle": f"Welcome to Turn {turn:02}",
            "activitySubtitle": "I've crunched the numbers and here are the top Teams for each stat.",
        },
        {"facts": [{"name": key, "value": ", ".join(sorted(value))} for key, value in leaders.items()]},
        {
            "text": "Looking at the above table it appears everyone should keep a close eye on "
            + f"**{' and '.join(overall)}** as they seem to be all over this leaderboard"
        },
    ]

    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "title": f"{game_name} - Team Stats",
        "sections": sections,
    }


def __post_stats(content: Dict[str, Any], webhook: WebhookConfig):
    try:
        response = post(
            url=webhook.url,
            headers=HEADERS,
            timeout=TIMEOUT,
            json={
                "type": "message",
                "attachments": [
                    {"contentType": "application/vnd.microsoft.teams.card.o365connector", "content": content}
                ],
            },
        )
        response.raise_for_status()
        LOGGER.info(f"{response.status_code}: POST - {response.url}")
    except HTTPError as err:
        LOGGER.error(err)
    except ConnectionError:
        LOGGER.critical(f"Unable to access `{webhook.url}`")
