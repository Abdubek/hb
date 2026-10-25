# Task: bookcase; design variant 7.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=6
width=1.60
count=10
for x in (-width/2, width/2): box('Side', (x,0,1), (.04,.3,2))
for z in (0,.4,.8,1.2,1.6,2): box('Shelf', (0,0,z), (width,.3,.04))
box('Back', (0,.16,1), (width,.02,2))
