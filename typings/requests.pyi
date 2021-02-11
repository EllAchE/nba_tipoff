from typing import Union

class Response:
  content: Union[bytes, str]
  status_code: int

def get(url: str) -> Response:
  ...