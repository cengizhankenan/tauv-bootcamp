def wrap_angle(angle: float) -> float:
  while angle > 180:
    angle -= 360
  while angle < -180:
    angle += 360
  return angle