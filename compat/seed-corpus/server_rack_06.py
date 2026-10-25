# Task: server rack; design variant 7.
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
for x in (-width/2,width/2): box('Upright',(x,0,1),(.04,.6,2))
for i in range(count): box('Server',(0,0,.15+i*.18),(width-.06,.55,.14))
