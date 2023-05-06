__all__ = ["Settings"]

from pathlib import Path
from typing import ClassVar, List, Optional

import tomli_w as tomlwriter
import tomllib as tomlreader
from neptunes_hook import get_config_root
from pydantic import BaseModel, Extra, Field


class SettingsModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.ignore


class NeptunesPrideSettings(SettingsModel):
    game_number: Optional[int] = None
    api_code: Optional[str] = None
    tick_rate: int = 12
    last_tick: Optional[int] = None


class WebhookSettings(SettingsModel):
    microsoft_teams: Optional[str] = None


class PlayerSettings(SettingsModel):
    username: str
    name: Optional[str] = None
    team: Optional[str] = None


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
