# Task: product material; design variant 7.
import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

variant=6
width=1.60
count=10
box('Product',(0,0,.5),(width,.5,1))
material=bpy.data.materials.new('Enamel')
material.diffuse_color=(.1,.3,.8,1)
bpy.context.object.data.materials.append(material)
