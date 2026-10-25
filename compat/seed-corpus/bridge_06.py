# Task: bridge; design variant 7.
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
box('Deck',(0,0,1),(width*3,1,.15))
for side in (-.5,.5):
    box('Railing',(0,side,1.5),(width*3,.05,.05))
    for i in range(count): box('Post',((i/(count-1)-.5)*width*3,side,1.25),(.05,.05,.5))
