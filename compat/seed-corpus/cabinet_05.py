# Task: cabinet; design variant 6.
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
box('Body',(0,0,.5),(width,.5,1))
for x in (-width*.25,width*.25):
    box('Door',(x,-.27,.5),(width*.48,.03,.94))
    box('Handle',(x*.25,-.31,.5),(.025,.035,.2))
