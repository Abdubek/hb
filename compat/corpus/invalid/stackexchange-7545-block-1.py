import bpy

#+ grab the current area
original_area = bpy.context.area.type

view_layer = bpy.context.view_layer
for count, ob in enumerate(bpy.context.selected_objects):
    if ob.type == 'MESH':
        view_layer.objects.active = ob
        #+ switch to the UV editor to perform transforms etc
        bpy.context.area.ui_type = 'UV'
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        #+ select the uvs
        bpy.ops.uv.select_all(action='SELECT')

        bpy.ops.transform.translate(value=(0.125, 0, 0), constraint_axis=(True, False, False))

        #+ return to the original mode where the script was run
        bpy.context.area.type = original_area
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
