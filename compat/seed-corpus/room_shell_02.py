# Task: room shell; design variant 3.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=2
width=1.20
count=6
box('Floor',(0,0,-.05),(width*3,4,.1))
box('BackWall',(0,2,1.4),(width*3,.1,2.8))
for side in (-1,1): box('SideWall',(side*width*1.5,0,1.4),(.1,4,2.8))
