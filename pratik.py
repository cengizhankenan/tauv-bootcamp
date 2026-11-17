import math

print ("Merhaba Dünya")
print (5+3)

hiz = 10
sicaklik = 23.5
isim = "Kerem"
print(hiz)
print(hiz + 5)

sayi = 15

if sayi > 10:
    print("Bu sayı 10'dan büyüktür")
else:
    print("Bu sayı 10'dan küçük veya eşittir")    

def check_number(value):
    if value < 0:
        return 0 
    elif value > 100:
        return 100
    else:
        return value  

print(check_number(-50))
print(check_number(250))
print(check_number(45))            


konum = (5 , 12)
x , y = konum
print(x)
print(y)

sayilar = [1 , 2 , 3 , 4]
for s in sayilar:
    print(s * 10)


def clamp(value, min_val, max_val):
    if min_val > max_val:
        raise ValueError("ALT SINIR UST SINIRDAN BUYUK OLAMAZ!")

    if value < min_val: 
        return min_val
    elif value > max_val:
        return max_val
    else:
        return value        

print(clamp(50, 0, 100))
print(clamp(-20, 0, 100))
print(clamp(250, 0, 100))


def wrap_angle(angle):
    return (angle + math.pi) % (2 * math.pi) -math.pi 

def distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def bearing(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return math.atan2(y2 - y1, x2 - x1)

def heading_error(current_heading, target_bearing):
    fark = target_bearing - current_heading
    return wrap_angle(fark)

print("Wrap Angle:", wrap_angle(math.pi * 1.5))
print("Distance:", distance((0, 0), (3, 4)))
print("Bearing:", bearing((0, 0), (1, 1)))
print("Heading Error:", heading_error(0.5, 1.5))  