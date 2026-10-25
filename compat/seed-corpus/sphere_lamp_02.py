# Task: sphere lamp; design variant 3.
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
HB_EQUIVALENT_MESH_PREFIXES=('Sphere',)
box('Base',(0,0,.03),(.3,.3,.06))
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=.2, location=(0,0,.4))
bpy.context.object.name='Globe'
bpy.ops.object.shade_smooth()
