from json.decoder import JSONDecodeError
from typing import Any, Dict

from requests import post
from requests.exceptions import ConnectionError, HTTPError

from neptunes_hooks.console import ConsoleLog
from neptunes_hooks.utils import HEADERS, STATS, TIMEOUT

CONSOLE = ConsoleLog(__name__)


def pull_data(game_id: str, api_code: str) -> Dict[str, Any]:
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


def __request_data(game_id: str, api_code: str) -> Dict[str, Any]:
    try:
        response = post(
            url="https://np.ironhelmet.com/api",
            headers={"User-Agent": HEADERS["User-Agent"]},
            data={"api_version": "0.1", "game_number": game_id, "code": api_code},
            timeout=TIMEOUT,
        )
        if response.status_code == 200:
            try:
                data = response.json()["scanning_data"]
                return data
            except (JSONDecodeError, KeyError):
                CONSOLE.critical(f"Unable to parse the response message: {response.text}")
        else:
            CONSOLE.error(f"{response.status_code}: POST - {response.url} - {response.text}")
    except (ConnectionError, HTTPError):
        CONSOLE.error("Unable to access: `https://np.ironhelmet.com/api`")
    return {}
