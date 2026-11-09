from math import atan2, sqrt, degrees

def bearing2d(x1,y1,x2,y2): # atan yaptım başta atan2 daha mantıklıymış atan -90,+90 arası sonuç veriyormuş
  v_distance = y2-y1
  h_distance = x2-x1
  heading = degrees(atan2(v_distance, h_distance))
  return heading

def bearing3d(x1, y1, z1, x2, y2, z2):
  dx = x2 - x1
  dy = y2 - y1
  dz = z2 - z1
  yaw = degrees(atan2(dy, dx))                       # yatay yön (heading)
  pitch = degrees(atan2(dz, sqrt(dx**2 + dy**2)))    # yukarı/aşağı açı
  return yaw, pitch