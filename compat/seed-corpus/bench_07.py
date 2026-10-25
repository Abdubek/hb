# Task: bench; design variant 8.
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
box('Seat', (0,0,.45), (width,.4,.05))
box('Backrest', (0,.18,.7), (width,.04,.5), (math.radians(-10),0,0))
for x in (-width*.4,width*.4): box('Support', (x,0,.21), (.08,.36,.42))
