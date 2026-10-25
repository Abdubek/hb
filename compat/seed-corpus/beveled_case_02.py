# Task: beveled case; design variant 3.
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
box('Case',(0,0,.1),(width,.7,.2))
modifier=bpy.context.object.modifiers.new('Edge highlights','BEVEL')
modifier.width=.02
modifier.segments=3
