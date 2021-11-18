import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ruamel.yaml import YAML
from yamale import YamaleError, make_data, make_schema, validate

LOGGER = logging.getLogger(__name__)
TOP_DIR = Path(__file__).resolve().parent.parent


def _yaml_setup() -> YAML:
    def null_representer(self, data):
        return self.represent_scalar("tag:yaml.org,2002:null", "~")

    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.width = 2147483647
    yaml.representer.add_representer(type(None), null_representer)
    # yaml.emitter.alt_null = '~'
    yaml.version = (1, 2)
    return yaml


class PlayerConfig:
    def __init__(self, username: str = "", team: Optional[str] = None):
        self.username = username
        self.team: Optional[str] = team

    def dump(self) -> Dict[str, Any]:
        return {"Username": self.username, "Team": self.team}


class WebhookConfig:
    def __init__(self, service: str = "", url: Optional[str] = None):
        self.service = service
        self.url: Optional[str] = url

    def dump(self) -> Dict[str, Any]:
        return {"Service": self.service, "Url": self.url}


class Settings:
    def __init__(self):
        self.game_id: Optional[str] = None
        self.api_code: Optional[str] = None
        self.tick_rate = 12
        self.last_tick: Optional[int] = None
        self.players: List[PlayerConfig] = [PlayerConfig("BuriedInCode")]
        self.webhooks: List[WebhookConfig] = [WebhookConfig("Discord")]

        folder = Path.home().joinpath(".config").joinpath("Neptunes-Hooks")
        self.settings_file = folder.joinpath("settings.yaml")
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)

        if not self.settings_file.exists():
            self.save()
        else:
            self.load()

    def dump(self) -> Dict[str, Any]:
        return {
            "Neptune's Pride": {
                "Game ID": self.game_id,
                "API Code": self.api_code,
                "Tick Rate": self.tick_rate,
                "Last Tick": self.last_tick,
            },
            "Players": [x.dump() for x in self.players],
            "Webhooks": [x.dump() for x in self.webhooks],
        }

    def save(self):
        with open(self.settings_file, "w", encoding="UTF-8") as yaml_file:
            _yaml_setup().dump(self.dump(), yaml_file)

    def _validate(self) -> bool:
        schema_file = TOP_DIR.joinpath("config.schema.yaml")
        schema = make_schema(schema_file, parser="ruamel")
        data = make_data(self.settings_file, parser="ruamel")

        try:
            validate(schema, data)
            return True
        except YamaleError as ye:
            LOGGER.error("Validation failed")
            for result in ye.results:
                LOGGER.error(f"Error validating data '{result.data}' with '{result.schema}'")
                for error in result.errors:
                    LOGGER.error(f"\t{error}")
        return False

    def load(self):
        if not self._validate():
            return
        data = make_data(self.settings_file, parser="ruamel")[0][0]

        game_data = data["Neptune's Pride"]
        self.game_id = game_data["Game ID"]
        self.api_code = game_data["API Code"]
        self.tick_rate = game_data["Tick Rate"]
        self.last_tick = game_data["Last Tick"]

        players_data = data["Players"]
        players = []
        for player in players_data:
            players.append(PlayerConfig(username=player["Username"], team=player["Team"]))
        self.players = players

        webhooks_data = data["Webhooks"]
        webhooks = []
        for webhook in webhooks_data:
            webhooks.append(WebhookConfig(service=webhook["Service"], url=webhook["Url"]))
        self.webhooks = webhooks
