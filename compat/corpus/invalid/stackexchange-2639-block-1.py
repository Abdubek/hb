import bpy

scene = bpy.context.scene
for ob in scene.objects:
    if ob.type == 'MESH':
        scene.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')

        # execute any editmode tool
        bpy.ops.mesh.tris_convert_to_quads(limit=0.9,
                                           uvs=False,
                                           vcols=False,
                                           sharp=False,
                                           materials=False)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
