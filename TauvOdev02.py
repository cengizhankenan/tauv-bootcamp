import math

#clamp
def clamp(value, a, b):
    if a > b:               #hhhhhhh büyük belirlemece
        a,b = b,a
    if value < a:
        return a
    if value > b:
        return b
    return value


#wrap angle
def wrapAngle(angle):
    #return (angle + math.pi) % (2*math.pi) - math.pi          #sonuç [-pi, pi)
    return math.pi - (math.pi - angle) % (2 * math.pi)         #sonuç (-pi, pi]


#wrap angle extra
def degreeToRad(angle):
    return angle*math.pi/180       #aka math.radians


#distance
def distanceSquared(origin: tuple[float,float] , target: tuple [float,float]):
    ox, oy = origin
    tx, ty = target
    dx = tx - ox
    dy = ty - oy          
    return dx*dx + dy*dy  #kare almaktan daha rahat diye biliyorum


def distance(origin: tuple[float,float] , target: tuple [float,float]): 
    return distanceSquared(origin, target) ** 0.5


#bearing
def bearing(origin: tuple[float,float] , target: tuple [float,float]):
    ox, oy = origin
    tx, ty = target
    dx = tx - ox
    dy = ty - oy  
    return math.atan2(dy,dx)


#heading error
def headingError(current, target):
    return wrapAngle(target - current)


#testground
while True:

    islem = input("\nclamp 1\nwrap angle 2\ndistance 3\nbearing 4\nheading error 5\nişlem numarasını girin: ")    #gereksiz show ahh
    match islem:

        case "1":
            value = float(input("değer: "))
            a = float(input("ilk sınırı gir: "))
            b = float(input("ikinci sınırı gir: "))
            print(clamp(value,a,b))

        case "2":
            value = float(input("değer: "))
            valueType = input ("değerin türü? pi/r/d: ")

            match valueType:
                case "pi":
                    print(wrapAngle(value * math.pi)/math.pi,"π")

                case "r":
                    print(wrapAngle(value)/math.pi,"π")

                case "d":
                    print(wrapAngle(degreeToRad(value))/math.pi,"π")
                    
                case _:
                    print("yanlış girdin")

        case "3":
            origin = tuple(map(float, input("Konum x,y: ").split(",")))
            target = tuple(map(float, input("Konum x,y: ").split(",")))
            print(distance(origin,target))

        case "4":
            origin = tuple(map(float, input("Konum x,y: ").split(",")))
            target = tuple(map(float, input("Konum x,y: ").split(",")))
            print(bearing(origin,target))
        
        case "5":
            origin = float(input("mevcut yön r: "))
            target = float(input("hedef yön r: "))
            result = headingError(origin,target)
            print(result, " r yada ", result/math.pi, " π")

        case _:
            print("yanlış girdin")



    if input("bitsin mi? y/n: ") == "y":
        break


    # try except üşendim zerre sevmem zaten