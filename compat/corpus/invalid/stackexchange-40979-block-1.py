import bpy
import bmesh

L = 0.5 # distance limit
sphere = bpy.data.objects.get("Sphere")
mesh_obj = bpy.context.edit_object
me = mesh_obj.data
smwi = sphere.matrix_world.inverted()

bm = bmesh.from_edit_mesh(me)

for face in bm.faces:
    v1 = mesh_obj.matrix_world * face.calc_center_median() # global face median
    localPos = smwi * v1  # face cent in sphere local space

    (hit, loc, norm, face_index) = sphere.closest_point_on_mesh(localPos)
    # Edited for new hit success return val.  
    v2 = sphere.matrix_world * loc
    face.select = ((v2 - v1).length > L)
