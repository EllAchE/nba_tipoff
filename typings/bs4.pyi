from typing import Union

class BeautifulSoup(Node):
  def __init__(self, html: Union[str, bytes], parser: str) -> BeautifulSoup:
    ...

class Node:
  text: str

  def find(self, tag: str, attrs: dict[str, str] = ...) -> Node:
    ...