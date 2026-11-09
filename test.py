import clamp,bearing,distance,wrap_angle,heading_error
from random import randint
print("testler\n")

print("1-clamp(min,max,val)")


for i in range(3):
  min = randint(1,10)
  max = randint(11,20)
  val = randint(min,max)
  print(f"clamp({min},{max},{val}) = {clamp.clamp(min,max,val)}")

print("\n2-wrap_angle(angle)")
for i in range(3):
  angle = randint(-720,720)
  print(f"wrap_angle({angle}) = {wrap_angle.wrap_angle(angle)}")

print("\n3-distance")
print("distance2d(x1,y1,x2,y2) -> distance")
x1 = 0
y1 = 0
x2 = 3
y2 = 4
print(f"distance2d({x1},{y1},{x2},{y2}) = {distance.distance2d(x1,y1,x2,y2)}")
print("\ndistance3d(x1,y1,z1,x2,y2,z2) -> distance")
z1 = 0
z2 = 5
print(f"distance3d({x1},{y1},{z1},{x2},{y2},{z2}) = {distance.distance3d(x1,y1,z1,x2,y2,z2)}")

print("\n4-bearing")
print("bearing2d(x1,y1,x2,y2) -> heading")
x1 = 0
y1 = 0
x2 = 1
y2 = 1
print(f"bearing2d({x1},{y1},{x2},{y2}) = {bearing.bearing2d(x1,y1,x2,y2)}")
print("\nbearing3d(x1,y1,z1,x2,y2,z2) -> (yaw,pitch)")
z1 = 0
z2 = 1
print(f"bearing3d({x1},{y1},{z1},{x2},{y2},{z2}) = {bearing.bearing3d(x1,y1,z1,x2,y2,z2)}")

print("\n5-heading_error(target,current)")
target = 450
current = 30
print(f"heading_error({target},{current}) = {heading_error.heading_error(current,target)}")
