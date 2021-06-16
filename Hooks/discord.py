import logging
from typing import Dict, List, Optional, Tuple

from ruamel.yaml import CommentedMap

LOGGER = logging.getLogger(__name__)
TIMEOUT = 100


def post_results(player_results: Tuple[Dict[str, List[str]], List[str]],
                 team_results: Optional[Tuple[Dict[str, List[str]], List[str]]], turn: int, game_name: str,
                 config: CommentedMap):
    pass
