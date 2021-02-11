from typing import Any

class PlayByPlayV2:
  def __init__(self, game_id: str) -> PlayByPlayV2:
    ...

  def get_data_frames(self) -> list[Any]:
    ...