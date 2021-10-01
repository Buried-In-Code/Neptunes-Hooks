import logging
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Tuple

from requests import post
from requests.exceptions import ConnectionError, HTTPError
from ruamel.yaml import CommentedMap

from neptunes_hooks.config import get_team

LOGGER = logging.getLogger(__name__)
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


def parse_player_stats(data: Dict[str, Any], config: CommentedMap) -> Tuple[Dict[str, List[str]], List[str]]:
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
        # region Clean Titles
        player_titles = []
        for username in max_players:
            player_title = username
            if get_team(username, config):
                player_title += f" [{get_team(username, config)}]"
            player_titles.append(player_title)
        # endregion
        stat_title = f"{stat} ({max_value:,})" if index < 7 else f"{stat} (Lvl {max_value:,})"
        player_stats[stat_title] = player_titles

    return player_stats, __calculate_overall(player_stats)


def generate_teams(data: Dict[str, Any], config: CommentedMap) -> Dict[str, Any]:
    team_stats = {}
    for username in config["Players"].keys():
        player_data = next(iter([it for it in data["Players"] if it["Username"] == username]), None)
        if not player_data:
            continue
        team_name = get_team(username, config) or "~"
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


def parse_team_stats(data: Dict[str, Any], config: CommentedMap) -> Optional[Tuple[Dict[str, List[str]], List[str]]]:
    teams = generate_teams(data, config)
    if not teams:
        return None

    # region Calculate Stat Leader/s
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
    # endregion

    return team_stats, __calculate_overall(team_stats)


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


def request_data(game_id: int, api_code: str) -> Dict[str, Any]:
    data = __request_data(game_id, api_code)
    if not data:
        return {}
    fields = [
        "total_stars",
        "total_strength",
        "total_economy",
        "$/Turn",
        "total_industry",
        "Ships/Turn",
        "total_science",
        "scanning",
        "propulsion",
        "terraforming",
        "research",
        "weapons",
        "banking",
        "manufacturing",
    ]
    output = []
    for player_data in data["players"].values():
        temp = {"Username": player_data["alias"], "Active": player_data["conceded"] == 0}
        for index, title in enumerate(fields):
            if title == "$/Turn":
                temp[STATS[index]] = int(
                    player_data["total_economy"] * 10.0 + player_data["tech"]["banking"]["level"] * 75.0
                )
            elif title == "Ships/Turn":
                temp[STATS[index]] = int(
                    player_data["total_industry"] * (player_data["tech"]["manufacturing"]["level"] + 5.0) / 2.0
                )
            elif title.startswith("total_"):
                temp[STATS[index]] = player_data[title]
            else:
                temp[STATS[index]] = player_data["tech"][title]["level"]
        output.append(temp)
    return {"Title": data["name"], "Tick": data["tick"], "Active": data["game_over"] == 0, "Players": output}


def __request_data(game_id: int, api_code: str) -> Dict[str, Any]:
    LOGGER.debug(f"Looking for Game: `{game_id}`, using the key: `{api_code}`")
    try:
        response = post(
            url="https://np.ironhelmet.com/api",
            headers={"User-Agent": "Neptune's Hooks"},
            timeout=TIMEOUT,
            data={"api_version": "0.1", "game_number": game_id, "code": api_code},
        )
        response.raise_for_status()
        LOGGER.info(f"{response.status_code}: POST - {response.url}")
        try:
            return response.json()["scanning_data"]
        except (JSONDecodeError, KeyError):
            LOGGER.error(f"Unable to parse the response message: {response.text}")
            return {}
    except (HTTPError, ConnectionError) as err:
        LOGGER.error(f"Unable to access `https://np.ironhelmet.com/api`: {err}")
        return {}
