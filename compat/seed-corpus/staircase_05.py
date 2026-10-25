# Task: staircase; design variant 6.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=5
width=1.50
count=9
for i in range(count): box('Step', (0,i*.28,i*.09), (width,.28,(i+1)*.18))
