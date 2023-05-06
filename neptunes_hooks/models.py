__all__ = ["Stats", "PlayerStats", "TeamStats"]

from dataclasses import dataclass, field
from typing import List


@dataclass
class PlayerStats:
    username: str
    active: bool = False
    stars: int = 0
    ships: int = 0
    economy: int = 0
    economy_per_turn: int = 0
    industry: int = 0
    industry_per_turn: int = 0
    science: int = 0
    scanning: int = 0
    hyperspace_range: int = 0
    terraforming: int = 0
    experimentation: int = 0
    weapons: int = 0
    banking: int = 0
    manufacturing: int = 0


@dataclass
class Stats:
    title: str
    tick: int = 0
    active: bool = False
    players: List[PlayerStats] = field(default_factory=list)


@dataclass
class TeamStats:
    name: str
    active: bool = False
    stars: int = 0
    ships: int = 0
    economy: int = 0
    economy_per_turn: int = 0
    industry: int = 0
    industry_per_turn: int = 0
    science: int = 0
    scanning: int = 0
    hyperspace_range: int = 0
    terraforming: int = 0
    experimentation: int = 0
    weapons: int = 0
    banking: int = 0
    manufacturing: int = 0
