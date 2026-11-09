import wrap_angle

def heading_error(heading:float,target:float) -> float:
  error = wrap_angle.wrap_angle(target - heading)
  
  return error