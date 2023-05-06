__all__ = ["Settings"]

from pathlib import Path
from typing import ClassVar, List

try:
    import tomllib as tomlreader  # Python >= 3.11
except ModuleNotFoundError:
    import tomli as tomlreader  # Python < 3.11
import tomli_w as tomlwriter
from pydantic import BaseModel, Extra, Field

from neptunes_hooks import get_config_root


class SettingsModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.ignore


class NeptunesPrideSettings(SettingsModel):
    game_number: int = 0
    api_code: str = ""
    tick_rate: int = 12
    last_tick: int = 0


class WebhookSettings(SettingsModel):
    microsoft_teams: str = ""


class PlayerSettings(SettingsModel):
    username: str
    name: str = ""
    team: str = ""


class _Settings(SettingsModel):
    FILENAME: ClassVar[Path] = get_config_root() / "settings.toml"
    _instance: ClassVar["_Settings"] = None
    neptunes_pride: NeptunesPrideSettings = NeptunesPrideSettings()
    webhooks: WebhookSettings = WebhookSettings()
    players: List[PlayerSettings] = Field(default_factory=list)

    @classmethod
    def load(cls) -> "_Settings":
        if not cls.FILENAME.exists():
            _Settings().save()
        with cls.FILENAME.open("rb") as stream:
            content = tomlreader.load(stream)
        return _Settings(**content)

    def save(self) -> "_Settings":
        with self.FILENAME.open("wb") as stream:
            content = self.dict(by_alias=False)
            tomlwriter.dump(content, stream)
        return self


def Settings() -> _Settings:  # noqa: N802
    if _Settings._instance is None:
        _Settings._instance = _Settings.load()
    return _Settings._instance
