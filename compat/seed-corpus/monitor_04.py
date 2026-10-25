# Task: monitor; design variant 5.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=4
width=1.40
count=8
box('Screen',(0,0,.6),(width,.05,width*.5625))
box('Stand',(0,.02,.2),(.06,.06,.4))
box('Foot',(0,0,.025),(.4,.25,.05))
