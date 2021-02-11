class Rating:
  mu: float
  sigma: float

  def __init__(self, mu: float, sigma: float) -> Rating:
    ...

class TrueSkill:
  def __init__(self, draw_probability: float, backend: str) -> TrueSkill:
    ...

  # TODO: What should this parameter be named?
  def cdf(self, _: float) -> float:
    pass

  def make_as_global(self) -> None:
    ...

def global_env() -> TrueSkill:
  ...