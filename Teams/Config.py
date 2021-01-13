import logging
from typing import Optional

import yaml

from Teams import TOP_DIR

LOGGER = logging.getLogger(__name__)
CONFIG_FILE = TOP_DIR.joinpath('config.yaml')
CONFIG = {}


def save_config():
    with open(CONFIG_FILE, 'w', encoding='UTF-8') as yaml_file:
        yaml.safe_dump(CONFIG, yaml_file)


def load_config():
    global CONFIG
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='UTF-8') as yaml_file:
            CONFIG = yaml.safe_load(yaml_file) or {
                'Teams Webhook': None,
                'Game Number': -1,
                'API Code': None,
                'Tick Rate': 8,
                'Last Tick': -1,
                'Players': {},
                'Teams': {}
            }
    else:
        CONFIG_FILE.touch()
        CONFIG = {
            'Teams Webhook': None,
            'Game Number': -1,
            'API Code': None,
            'Tick Rate': 8,
            'Last Tick': -1,
            'Players': {},
            'Teams': {}
        }
    save_config()


load_config()


def lookup_player(username: str) -> Optional[str]:
    return CONFIG['Players'].get(username, None)


def lookup_team(username: str) -> Optional[str]:
    for name, members in CONFIG['Teams'].items():
        if username in members:
            return name
    return None
