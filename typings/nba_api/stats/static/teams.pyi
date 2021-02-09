from typing import TypedDict

class Team(TypedDict):
  abbreviation: str
  full_name: str
  id: str

def get_teams() -> list[Team]:
  ...