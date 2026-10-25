# Task: rover; design variant 4.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=3
width=1.30
count=7
box('Chassis',(0,0,.3),(width,.5,.15))
for x in (-width*.35,0,width*.35):
    for y in (-.32,.32):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.14, depth=.09, location=(x,y,.14), rotation=(math.pi/2,0,0))
        bpy.context.object.name='Wheel' 
