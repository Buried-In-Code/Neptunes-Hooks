import logging
from pathlib import Path
from typing import Dict, Any

import yaml

TOP_DIR = Path(__file__).resolve().parent.parent
LOGGER = logging.getLogger(__name__)


def get_config_file(testing: bool = False):
    if testing:
        return TOP_DIR.joinpath('config-test.yaml')
    return TOP_DIR.joinpath('config.yaml')


def save_config(data: Dict[str, Any], testing: bool = False):
    with open(get_config_file(testing), 'w', encoding='UTF-8') as yaml_file:
        yaml.safe_dump(data, yaml_file)


def load_config(testing: bool = False):
    if get_config_file(testing).exists():
        with open(get_config_file(testing), 'r', encoding='UTF-8') as yaml_file:
            data = yaml.safe_load(yaml_file) or {
                'Neptune\'s Pride': {
                    'Number': -1,
                    'Code': None,
                    'Tick Rate': 8,
                    'Last Tick': -1
                },
                'Teams Webhook': None,
                'Players': [
                    {
                        'Alias': 'Alias 1',
                        'Name': 'Name 1',
                        'Team': 'Team 1'
                    }
                ]
            }
    else:
        get_config_file(testing).touch()
        data = {
            'Neptune\'s Pride': {
                'Number': -1,
                'Code': None,
                'Tick Rate': 8,
                'Last Tick': -1
            },
            'Teams Webhook': None,
            'Players': [
                {
                    'Alias': 'Alias 1',
                    'Name': 'Name 1',
                    'Team': 'Team 1'
                }
            ]
        }
    save_config(data, testing)
    return data


def lookup_player(username: str, testing: bool = False) -> Dict[str, Any]:
    LOGGER.debug(f"is Testing: {testing}")
    for player in load_config(testing)['Players']:
        if player['Alias'] == username:
            return player
    return {}
