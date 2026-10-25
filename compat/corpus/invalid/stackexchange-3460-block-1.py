import bpy

scene = bpy.context.scene
scene.layers = [True] * 20 # Show all layers

for obj in scene.objects:
    if obj.type == 'MESH':
        scene.objects.active = obj

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.mode_set(mode='OBJECT')
