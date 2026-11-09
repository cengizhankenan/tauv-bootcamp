from math import sqrt
def distance2d(x1: float, y1: float, x2: float, y2: float) -> float:
  return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def distance3d(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
  return sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)