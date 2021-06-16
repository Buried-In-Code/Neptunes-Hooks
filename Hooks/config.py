import logging
from pathlib import Path
from typing import Optional, List

from ruamel.yaml import YAML, CommentedMap

LOGGER = logging.getLogger(__name__)
TOP_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = {
    'Neptune\'s Pride': {
        'Number': -1,
        'Code': None,
        'Tick Rate': 12,
        'Last Tick': -1
    },
    'Players': {
        'Username 1': {
            'Team': None
        },
        'Username 2': {
            'Team': None
        },
        'Username 3': {
            'Team': None
        }
    },
    'Webhooks': {
        'Teams': None,
        'Discord': None
    }
}


def __yaml_setup() -> YAML:
    def null_representer(self, data):
        return self.represent_scalar(u'tag:yaml.org,2002:null', u'~')

    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.width = 2147483647
    yaml.representer.add_representer(type(None), null_representer)
    # yaml.emitter.alt_null = '~'
    yaml.version = (1, 2)
    return yaml


def save_config(data: CommentedMap, testing: bool = False):
    config_file = TOP_DIR.joinpath('config-test.yaml' if testing else 'config.yaml')
    with open(config_file, 'w', encoding='UTF-8') as yaml_file:
        __yaml_setup().dump(data, yaml_file)


def load_config(testing: bool = False) -> CommentedMap:
    def validate_config(config: CommentedMap) -> CommentedMap:
        for key, value in DEFAULT_CONFIG.copy().items():
            if key not in config:
                config[key] = value
            if isinstance(value, dict):
                for sub_key, sub_value in value.copy().items():
                    if sub_key not in config[key]:
                        config[key][sub_key] = sub_value
        return config

    config_file = TOP_DIR.joinpath('config-test.yaml' if testing else 'config.yaml')
    if config_file.exists():
        with open(config_file, 'r', encoding='UTF-8') as yaml_file:
            data = __yaml_setup().load(yaml_file) or DEFAULT_CONFIG
    else:
        config_file.touch()
        data = DEFAULT_CONFIG
    validate_config(data)
    save_config(data, testing)
    return data


def get_team(username: str, config: CommentedMap) -> Optional[str]:
    return config['Players'].get(username, {}).get('Team', None)


def get_members(team: str, config: CommentedMap) -> List[str]:
    members = []
    for username, details in config['Players'].items():
        if details['Team'] == team:
            members.append(username)
    return members


def is_teamed(config: CommentedMap) -> bool:
    teamed = False
    for username, player in config['Players'].items():
        if player['Team'] is not None:
            teamed = True
    return teamed


CONFIG = load_config()
