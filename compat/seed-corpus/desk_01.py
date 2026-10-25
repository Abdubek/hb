# Task: desk; design variant 2.
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
box('Desktop', (0, 0, .75), (width, .7, .06))
for x in (-width/2+.08, width/2-.08):
    for y in (-.27, .27): box('Leg', (x,y,.36), (.06,.06,.72))
