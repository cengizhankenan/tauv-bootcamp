def clamp(min: float, max: float, number: float) -> float:
  if number < min:
    return min
  elif number > max:
    return max
  else:
    return number
