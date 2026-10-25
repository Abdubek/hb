# Task: product camera; design variant 4.
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
box('Product',(0,0,.5),(width,.5,1))
data=bpy.data.cameras.new('ProductCamera')
camera=bpy.data.objects.new('ProductCamera',data)
bpy.context.collection.objects.link(camera)
camera.location=(3,-4,2)
bpy.context.scene.camera=camera
