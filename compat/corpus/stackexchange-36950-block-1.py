import bpy
from mathutils import Vector

def insert_keyframe(fcurves, frame, values):
    for fcu, val in zip(fcurves, values):
        fcu.keyframe_points.insert(frame, val, options={'FAST'})

obj = bpy.context.active_object
mesh = obj.data
action = bpy.data.actions.new("MeshAnimation")

mesh.animation_data_create()
mesh.animation_data.action = action

data_path = "vertices[%d].co"
vec_z = Vector((0.0, 0.0, 1.0))

frames = 0, 25, 50, 75, 100
values = 0.0, 3.0, 5.0, 3.0, 0.0

for v in mesh.vertices:
    fcurves = [action.fcurves.new(data_path % v.index, index =  i) for i in range(3)]
    co_rest = v.co

    for t, value in zip(frames, values):
        co_kf = co_rest + value * vec_z
        insert_keyframe(fcurves, t, co_kf)     
