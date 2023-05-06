__all__ = ["parse_player_stats", "parse_team_stats"]

import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from neptunes_hooks.models import Stats, TeamStats
from neptunes_hooks.settings import PlayerSettings

LOGGER = logging.getLogger(__name__)
STAT_NAMES = [
    "stars",
    "ships",
    "economy",
    "economy_per_turn",
    "industry",
    "industry_per_turn",
    "science",
    "scanning",
    "hyperspace_range",
    "terraforming",
    "experimentation",
    "weapons",
    "banking",
    "manufacturing",
]


def _calculate_overall(data: Dict[str, List[str]]) -> List[str]:
    leading_count = {}
    for _stats, leaders in data.items():
        for player in leaders:
            if player in leading_count:
                leading_count[player] += 1
            else:
                leading_count[player] = 1
    leading = []
    max_count = -1
    for player, count in leading_count.items():
        if count > max_count:
            leading = [player]
            max_count = count
        elif count == max_count:
            leading.append(player)
    return leading


def parse_player_stats(
    stats: Stats,
    players: List[PlayerSettings],
) -> Tuple[Dict[str, List[str]], List[str]]:
    player_stats = {}
    for index, stat in enumerate(STAT_NAMES):
        max_value = -1
        max_players = []
        for player in [x for x in stats.players if x.active]:
            player_data = asdict(player)
            if player_data[stat] > max_value:
                max_value = player_data[stat]
                max_players = [player.username]
            elif player_data[stat] == max_value:
                max_players.append(player.username)

        player_titles = []
        for username in max_players:
            player_title = username
            if name := safe_get([x.name for x in players if x.username == username]):
                player_title += f" ({name})"
            if team_name := safe_get([x.team for x in players if x.username == username]):
                player_title += f" [{team_name}]"
            player_titles.append(player_title)

        stat_title = f"{stat} ({max_value:,})" if index < 7 else f"{stat} (Lvl {max_value:,})"
        player_stats[stat_title] = player_titles

    return player_stats, _calculate_overall(player_stats)


def safe_get(data: List[Any], default: Optional[str] = None) -> Optional[Any]:
    return next(iter(data), default)


def _generate_teams(stats: Stats, players: List[PlayerSettings]) -> List[TeamStats]:
    team_list = []
    for username in [x.username for x in players]:
        player = safe_get([x for x in stats.players if x.username == username])
        if not player:
            continue

        team_name = safe_get([x.team for x in players if x.username == username]) or "~"
        team = safe_get([x for x in team_list if x.name == team_name]) or TeamStats(name=team_name)
        team.active = team.active or player.active
        team.stars += player.stars
        team.ships += player.ships
        team.economy += player.economy
        team.economy_per_turn += player.economy_per_turn
        team.industry += player.industry
        team.industry_per_turn += player.industry_per_turn
        team.science += player.science
        team.scanning = max(team.scanning, player.scanning)
        team.hyperspace_range = max(team.hyperspace_range, player.hyperspace_range)
        team.terraforming = max(team.terraforming, player.terraforming)
        team.experimentation = max(team.experimentation, player.experimentation)
        team.weapons = max(team.weapons, player.weapons)
        team.banking = max(team.banking, player.banking)
        team.manufacturing = max(team.manufacturing, player.manufacturing)
    if len({x.name for x in team_list}) >= 1:
        return team_list
    return {}


def parse_team_stats(
    stats: Stats,
    players: List[PlayerSettings],
) -> Optional[Tuple[Dict[str, List[str]], List[str]]]:
    teams = _generate_teams(stats, players)
    if not teams:
        return None

    team_stats = {}
    for index, stat in enumerate(STAT_NAMES):
        max_value = -1
        max_teams = []
        for team in [x for x in teams if x.active]:
            team_data = asdict(team)
            if team_data[stat] > max_value:
                max_value = team_data[stat]
                max_teams = [team.name]
            elif team_data[stat] == max_value:
                max_teams.append(team.name)
        stat_title = f"{stat} ({max_value:,})" if index < 7 else f"{stat} (Lvl {max_value:,})"
        team_stats[stat_title] = max_teams

    return team_stats, _calculate_overall(team_stats)
