from pydantic import BaseModel
from typing import List, Dict

class Coordinates(BaseModel):
  south: float
  west: float
  north: float
  east: float
