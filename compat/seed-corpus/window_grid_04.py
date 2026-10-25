# Task: window grid; design variant 5.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=4
width=1.40
count=8
for x in range(count+1): box('Mullion',((x/count-.5)*width,0,1),(.025,.06,2))
for z in (0,1,2): box('Transom',(0,0,z),(width,.06,.025))
