# Task: acoustic panels; design variant 1.
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
for x in range(count):
    for z in range(3): box('Panel',((x-count/2)*.32,0,z*.32),(.3,.08,.3),(0,0,math.radians(variant)))
