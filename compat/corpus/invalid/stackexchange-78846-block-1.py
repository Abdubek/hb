import bpy 
import  mathutils

object = bpy.data.objects["Cube"]


# translate
translation = mathutils.Vector((5.0, 0.0, 0.0))

inv = object.matrix_world.copy()
inv.invert()
vec_rot = translation * inv
object.location = object.location + vec_rot

# rotate
euler = mathutils.Euler((0.0, 0.0, 45.0))
object.rotation_euler.rotate(euler)

###### SCENE UPDATE ######    
bpy.context.scene.update()
##########################

# translate again
translation = mathutils.Vector((5.0, 0.0, 0.0))

inv = object.matrix_world.copy()
inv.invert()
vec_rot = translation * inv
object.location = object.location + vec_rot
