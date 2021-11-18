import logging
from typing import Dict, List, Optional, Tuple

from neptunes_hooks.settings import WebhookConfig

LOGGER = logging.getLogger(__name__)


def push_data(
    player_stats: Tuple[Dict[str, List[str]], List[str]],
    team_stats: Optional[Tuple[Dict[str, List[str]], List[str]]],
    turn: int,
    game_name: str,
    webhook: WebhookConfig,
):
    pass
