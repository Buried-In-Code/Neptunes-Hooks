__all__ = ["NeptunesPride"]

import logging
from typing import Any, Dict

from neptunes_hooks.models import PlayerStats, Stats
from neptunes_hooks.services._base import Service

LOGGER = logging.getLogger(__name__)


class NeptunesPride(Service):
    def __init__(self, game_number: int, code: str, timeout: int = 30):
        super().__init__(url="https://np.ironhelmet.com/api", timeout=timeout)
        self.game_number = game_number
        self.code = code

    def pull_data(self) -> Stats:
        data = self._get_stats()
        if not data:
            return {}
        players = []
        for player_data in data["players"].values():
            players.append(
                PlayerStats(
                    username=player_data["alias"],
                    active=player_data["conceded"] == 0,
                    stars=player_data["total_stars"],
                    ships=player_data["total_strength"],
                    economy=player_data["total_economy"],
                    economy_per_turn=int(
                        player_data["total_economy"] * 10.0
                        + player_data["tech"]["banking"]["level"] * 75.0,
                    ),
                    industry=player_data["total_industry"],
                    industry_per_turn=int(
                        player_data["total_industry"]
                        * (player_data["tech"]["manufacturing"]["level"] + 5.0)
                        / 2.0,
                    ),
                    science=player_data["total_science"],
                    scanning=player_data["tech"]["scanning"]["level"],
                    hyperspace_range=player_data["tech"]["propulsion"]["level"],
                    terraforming=player_data["tech"]["terraforming"]["level"],
                    experimentation=player_data["tech"]["research"]["level"],
                    weapons=player_data["tech"]["weapons"]["level"],
                    banking=player_data["tech"]["banking"]["level"],
                    manufacturing=player_data["tech"]["manufacturing"]["level"],
                ),
            )
        return Stats(
            title=data["name"],
            tick=data["tick"],
            active=data["game_over"] == 0,
            players=players,
        )

    def _get_stats(self) -> Dict[str, Any]:
        return self._perform_post_data_request(
            body={"api_version": "0.1", "game_number": self.game_number, "code": self.code},
        )
