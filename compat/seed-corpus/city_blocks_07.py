# Task: city blocks; design variant 8.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=7
width=1.70
count=11
for x in range(count):
    for y in range(3):
        height=.5+((x*7+y*3)%5)*.4
        box('Building',(x*width,y*width,height/2),(.7,.7,height))
