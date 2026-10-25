# Task: shipping crate; design variant 4.
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
box('CrateBody',(0,0,.5),(width,.8,1))
for x in (-width*.4,width*.4): box('Brace',(x,-.42,.5),(.08,.04,1.1))
