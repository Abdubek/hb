# Task: pergola; design variant 1.
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
for x in (-width,width):
    for y in (-1,1): box('Post',(x,y,1.2),(.1,.1,2.4))
for i in range(count): box('RoofBeam',((i/(count-1)-.5)*width*2,0,2.45),(.08,2.3,.12))
