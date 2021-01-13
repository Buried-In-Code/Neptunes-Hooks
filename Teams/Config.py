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
                'Teams Webhook': '',
                'Game Number': -1,
                'API Code': '',
                'Tick Rate': 8,
                'Last Tick': -1,
                'Players': {
                    'Alias 1': 'Name 1'
                },
                'Teams': {
                    'Team 1': [
                        'Alias 1'
                    ]
                }
            }
    else:
        CONFIG_FILE.touch()
        CONFIG = {
            'Teams Webhook': '',
            'Game Number': -1,
            'API Code': '',
            'Tick Rate': 8,
            'Last Tick': -1,
            'Players': {
                'Alias 1': 'Name 1'
            },
            'Teams': {
                'Team 1': [
                    'Alias 1'
                ]
            }
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
