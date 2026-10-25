# Task: game console; design variant 4.
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
box('Shell',(0,0,.1),(.09,.15,.02))
box('Screen',(0,.025,.112),(.065,.055,.004))
for x,y in ((-.023,-.032),(-.012,-.032),(-.023,-.043)):
    box('Dpad',(x,y,.115),(.01,.01,.005))
