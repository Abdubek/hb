import bpy
from mathutils import Matrix
from math import radians

# Translation matrices
T0 = T1 = Matrix.Translation((5, 0, 0))

# Rotation matrix
R0 = Matrix.Rotation(radians(45), 4, 'Z')

obj = bpy.context.object

#  
M = T0 * R0 * T1

obj.matrix_world = M * obj.matrix_world
