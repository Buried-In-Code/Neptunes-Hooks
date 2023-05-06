__all__ = ["MicrosoftTeams"]

import logging
from typing import Any, Dict, List, Optional, Tuple

from neptunes_hooks.services._base import Service

LOGGER = logging.getLogger(__name__)


def _format_player_stats(
    leaders: Dict[str, List[str]],
    overall: List[str],
    turn: int,
    game_name: str,
) -> Dict[str, Any]:
    sections = [
        {
            "activityTitle": f"Welcome to Turn {turn:02}",
            "activitySubtitle": "I've crunched the numbers and here are the top Players for each stat.",
        },
        {
            "facts": [
                {"name": key, "value": ", ".join(sorted(value))} for key, value in leaders.items()
            ],
        },
        {
            "text": "Looking at the above table it appears everyone should keep a close eye on "
            f"**{' and '.join(overall)}** as they seem to be all over this leaderboard",
        },
    ]

    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "title": f"{game_name} - Player Stats",
        "sections": sections,
    }


def _format_team_stats(
    leaders: Dict[str, List[str]],
    overall: List[str],
    turn: int,
    game_name: str,
) -> Dict[str, Any]:
    sections = [
        {
            "activityTitle": f"Welcome to Turn {turn:02}",
            "activitySubtitle": "I've crunched the numbers and here are the top Teams for each stat.",
        },
        {
            "facts": [
                {"name": key, "value": ", ".join(sorted(value))} for key, value in leaders.items()
            ],
        },
        {
            "text": f"Looking at the above table it appears everyone should keep a close eye on **{' and '.join(overall)}** as they seem to be all over this leaderboard",
        },
    ]

    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "title": f"{game_name} - Team Stats",
        "sections": sections,
    }


class MicrosoftTeams(Service):
    def __init__(self, url: str, timeout: int = 30):
        super().__init__(url=url, timeout=timeout)

    def push_data(
        self,
        player_stats: Tuple[Dict[str, List[str]], List[str]],
        team_stats: Optional[Tuple[Dict[str, List[str]], List[str]]],
        turn: int,
        game_name: str,
    ) -> None:
        player_stats = _format_player_stats(
            leaders=player_stats[0],
            overall=player_stats[1],
            turn=turn,
            game_name=game_name,
        )
        self.post_stats(stats=player_stats)
        LOGGER.info("Pushed player stats to Microsoft Teams")

        if team_stats:
            team_stats = _format_team_stats(
                leaders=team_stats[0],
                overall=team_stats[1],
                turn=turn,
                game_name=game_name,
            )
            self.post_stats(stats=team_stats)
            LOGGER.info("Pushed team stats to Microsoft Teams")

    def _post_stats(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        return self._perform_post_json_request(
            body={
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.teams.card.o365connector",
                        "content": stats,
                    },
                ],
            },
        )
