import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

TOP_DIR = Path(__file__).resolve().parent.parent
LOGGER = logging.getLogger(__name__)
DEFAULT = {
    'Neptune\'s Pride': {
        'Number': -1,
        'Code': None,
        'Tick Rate': 12,
        'Last Tick': -1
    },
    'Players': {
        'Username 1': {
            'Name': None,
            'Team': None
        },
        'Username 2': {
            'Name': None,
            'Team': None
        },
        'Username 3': {
            'Name': None,
            'Team': None
        }
    },
    'Webhooks': {
        'Teams': None,
        'Discord': None
    }
}


def save_config(data: Dict[str, Any], testing: bool = False):
    config_file = TOP_DIR.joinpath('config-2-test.yaml' if testing else 'config-2.yaml')
    with open(config_file, 'w', encoding='UTF-8') as yaml_file:
        yaml.safe_dump(data, yaml_file)


def load_config(testing: bool = False) -> Dict[str, Any]:
    config_file = TOP_DIR.joinpath('config-2-test.yaml' if testing else 'config-2.yaml')
    if config_file.exists():
        with open(config_file, 'r', encoding='UTF-8') as yaml_file:
            data = yaml.safe_load(yaml_file) or DEFAULT
    else:
        config_file.touch()
        data = DEFAULT
    save_config(data, testing)
    return data


def get_name(username: str, config: Dict[str, Any]) -> Optional[str]:
    return config['Players'].get(username, {}).get('Name', None)


def get_team(username: str, config: Dict[str, Any]) -> Optional[str]:
    return config['Players'].get(username, {}).get('Team', None)


def get_members(team: str, config: Dict[str, Any]) -> List[str]:
    members = []
    for username, details in config['Players'].items():
        if details['Team'] == team:
            members.append(username)
    return members


def is_teamed(config: Dict[str, Any]) -> bool:
    teamed = False
    for username, player in config['Players'].items():
        if player['Team'] is not None:
            teamed = True
    return teamed
