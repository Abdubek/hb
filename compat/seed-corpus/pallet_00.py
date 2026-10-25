# Task: pallet; design variant 1.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=0
width=1.00
count=4
for i in range(count): box('TopSlat',((i/(count-1)-.5)*width,0,.15),(.08,.8,.03))
for y in (-.3,0,.3): box('Runner',(0,y,.07),(width,.06,.12))
