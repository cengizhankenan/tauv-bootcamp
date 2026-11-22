import math

def clamp(value, min_value, max_value):
    if min_value > max_value:
        raise ValueError("Alt sınır üst sınırdan büyük olamaz.")
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value

def wrap_angle(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi

def distance(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx**2 + dy**2)

def bearing(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.atan2(dy, dx)

def heading_error(target_heading, current_heading):
    return wrap_angle(target_heading - current_heading)

if __name__ == "__main__":
    arac_konumu = (0.0, 0.0)
    hedefler = [(1.0, 1.0), (-2.0, 3.0), (0.0, -5.0)]
    
    for hedef in hedefler:
        mesafe = distance(arac_konumu, hedef)
        hedef_aci = bearing(arac_konumu, hedef)
        mevcut_aci = 0.0
        hata = heading_error(hedef_aci, mevcut_aci)
        
        print(f"Hedef: {hedef}, Mesafe: {mesafe:.2f}, Açı Hatası: {hata:.2f}")