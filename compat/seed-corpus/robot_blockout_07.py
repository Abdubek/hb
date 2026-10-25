# Task: robot blockout; design variant 8.
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
box('Torso',(0,0,1.1),(.5,.3,.6))
box('Head',(0,0,1.6),(.3,.3,.3))
for side in (-1,1):
    box('Arm',(side*.38,0,1.1),(.15,.2,.6))
    box('Leg',(side*.15,0,.5),(.18,.2,.6))
