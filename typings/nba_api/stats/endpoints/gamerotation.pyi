from typing import Any

class Team:
  def get_dict(self) -> dict[str, Any]:
    ...

class GameRotation:
  away_team: Team
  home_team: Team

  def __init__(self, game_id: str) -> GameRotation:
    ...