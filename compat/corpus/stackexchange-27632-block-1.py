import bpy

# get the object
ob = bpy.context.active_object

# get the mesh
mesh = ob.data

# create a list with all faces
face_list = [face for face in mesh.polygons]

# select all faces for offset operator
for face in face_list:
    face.select = True

# toggle to edit mode
bpy.ops.object.mode_set(mode='EDIT')

# make sure face select mode is enabled
bpy.context.tool_settings.mesh_select_mode = [False, False, True]

# select every second face
bpy.ops.mesh.select_nth(offset=1)

# use second material slot
ob.active_material_index = 1

# assign the material
bpy.ops.object.material_slot_assign()

# toggle to object mode
bpy.ops.object.mode_set(mode='OBJECT')
