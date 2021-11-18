import logging
from typing import Any, Dict, List, Optional, Tuple

from neptunes_hooks.settings import PlayerConfig

LOGGER = logging.getLogger(__name__)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json", "User-Agent": "Neptune's Hooks"}
TIMEOUT = 100
STATS = [
    "Stars",
    "Ships",
    "Economy",
    "$/Turn",
    "Industry",
    "Ships/Turn",
    "Science",
    "Scanning",
    "Hyperspace Range",
    "Terraforming",
    "Experimentation",
    "Weapons",
    "Banking",
    "Manufacturing",
]


def __calculate_overall(data: Dict[str, List[str]]) -> List[str]:
    leading_count = {}
    for stats, leaders in data.items():
        for player in leaders:
            if player in leading_count:
                leading_count[player] += 1
            else:
                leading_count[player] = 1
    LOGGER.debug(f"Leading Count: {leading_count}")
    leading = []
    max_count = -1
    for player, count in leading_count.items():
        if count > max_count:
            leading = [player]
            max_count = count
        elif count == max_count:
            leading.append(player)
    LOGGER.debug(f"Leader/s: {leading}")
    return leading


def safe_get(data: List[Any], default: Optional[str] = None) -> Optional[Any]:
    return next(iter(data), default)


def parse_player_stats(data: Dict[str, Any], players: List[PlayerConfig]) -> Tuple[Dict[str, List[str]], List[str]]:
    player_stats = {}
    for index, stat in enumerate(STATS):
        max_value = -1
        max_players = []
        for player_data in [x for x in data["Players"] if x["Active"]]:
            if player_data[stat] > max_value:
                max_value = player_data[stat]
                max_players = [player_data["Username"]]
            elif player_data[stat] == max_value:
                max_players.append(player_data["Username"])

        player_titles = []
        for username in max_players:
            player_title = username
            team_name = safe_get([x.team for x in players if x.username == username])
            if team_name:
                player_title += f" [{team_name}]"
            player_titles.append(player_title)

        stat_title = f"{stat} ({max_value:,})" if index < 7 else f"{stat} (Lvl {max_value:,})"
        player_stats[stat_title] = player_titles

    return player_stats, __calculate_overall(player_stats)


def generate_teams(data: Dict[str, Any], players: List[PlayerConfig]) -> Dict[str, Any]:
    team_stats = {}
    for username in [x.username for x in players]:
        player_data = safe_get([it for it in data["Players"] if it["Username"] == username])
        if not player_data:
            continue

        team_name = safe_get([x.team for x in players if x.username == username]) or "~"
        if team_name in team_stats:
            for index, stat in enumerate(STATS):
                if index < 7:
                    team_stats[team_name][stat] += player_data[stat]
                else:
                    team_stats[team_name][stat] = max(player_data[stat], team_stats[team_name][stat])
            team_stats[team_name]["Active"] = team_stats[team_name]["Active"] or player_data["Active"]
        else:
            team_stats[team_name] = {}
            for stat in STATS:
                team_stats[team_name][stat] = player_data[stat]
            team_stats[team_name]["Name"] = team_name
            team_stats[team_name]["Active"] = player_data["Active"]
    if len([team for team in team_stats.values() if team["Name"] != "~"]) <= 0:
        return {}
    return team_stats


def parse_team_stats(
    data: Dict[str, Any], players: List[PlayerConfig]
) -> Optional[Tuple[Dict[str, List[str]], List[str]]]:
    teams = generate_teams(data, players)
    if not teams:
        return None

    team_stats = {}
    for index, stat in enumerate(STATS):
        max_value = -1
        max_teams = []
        for team in teams.values():
            if team[stat] > max_value:
                max_value = team[stat]
                max_teams = [team]
            elif team[stat] == max_value:
                max_teams.append(team)
        stat_title = f"{stat} ({max_value:,})" if index < 7 else f"{stat} (Lvl {max_value:,})"
        team_stats[stat_title] = [x["Name"] for x in max_teams]

    return team_stats, __calculate_overall(team_stats)
