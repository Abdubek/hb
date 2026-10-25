# Task: dominoes; design variant 2.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=1
width=1.10
count=5
for i in range(count): box('Domino',(i*.15,0,.15),(.05,width*.1,.3),(0,math.radians(i*2),0))
