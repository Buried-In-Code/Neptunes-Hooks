import logging
from typing import Any, Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)
TIMEOUT = 100


def post_results(player_results: Tuple[Dict[str, List[str]], List[str]],
                 team_results: Optional[Tuple[Dict[str, List[str]], List[str]]], turn: int, game_name: str,
                 config: Dict[str, Any]):
    pass
