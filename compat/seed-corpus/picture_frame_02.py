# Task: picture frame; design variant 3.
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
for z in (-.4,.4): box('Horizontal',(0,0,z),(width,.05,.04))
for x in (-width/2,width/2): box('Vertical',(x,0,0),(.04,.05,.8))
