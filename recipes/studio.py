import bpy
from mathutils import Vector
name = _cfg['name']
assert bpy.data.objects.get(name) is None, 'Recipe name already exists; edit it or choose a new name'
target = Vector(_cfg['target'])
span = _cfg['span']
camera = bpy.data.cameras.new(name)
camera.type = 'ORTHO'
camera.ortho_scale = span * 1.4
obj = bpy.data.objects.new(name, camera)
bpy.context.collection.objects.link(obj)
obj.location = target + Vector((1.1, -1.7, 1.1)) * span
obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = obj
for suffix, direction, color, energy in [(' Key', (-3, 4, -5), (1, .94, .86), 2.5), (' Fill', (3, -1, -2), (.74, .84, 1), .7), (' Rim', (-1, -2, -1), (1, 1, 1), .5)]:
    light = bpy.data.lights.new(name + suffix, 'SUN')
    light.color = color
    light.energy = energy
    light.use_shadow = _cfg['shadows'] and suffix == ' Key'
    lamp = bpy.data.objects.new(name + suffix, light)
    bpy.context.collection.objects.link(lamp)
    lamp.rotation_euler = Vector(direction).to_track_quat('-Z', 'Y').to_euler()
