# Task: keyboard; design variant 3.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=2
width=1.20
count=6
box('Base',(0,0,.02),(width,.35,.04))
for x in range(count):
    for y in range(4): box('Key',((x/(count-1)-.5)*(width-.1),(y-1.5)*.075,.06),(.055,.055,.035))
